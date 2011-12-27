import os
import sys
import fcntl
import time
import logging
from collections import deque 
import threading
from threading import Thread
from subprocess import Popen, PIPE
from select import select
from tempfile import NamedTemporaryFile
import hashlib

import bottle
bottle.debug(True)

from bottle import route, run, request, view, abort
import Cookie
import cStringIO

logging.basicConfig(filename = "/tmp/thunderbatch.log",
        format = "%(asctime)s %(threadName)s(%(thread)s):%(name)s:%(message)s",
                            level = logging.DEBUG)

DEFAULT_DOWN_DIR = os.path.expanduser("~/Downloads")

if not os.path.isdir(DEFAULT_DOWN_DIR):
    DEFAULT_DOWN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads")
    if not os.path.exists(DEFAULT_DOWN_DIR):
        os.mkdir(DEFAULT_DOWN_DIR)


logger = logging.getLogger()

task_mgr = None

def LogException(func):
    def __check(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            logger.debug("Exception", exc_info = True)
            raise
    return __check


class DownloadThread(Thread):

    def __init__(self, cmd_args, cwd = None):
        super(DownloadThread, self).__init__(name = type(self).__name__)
        self.logger = logging.getLogger(type(self).__name__)
        self.daemon = True
        self.cmd_args = cmd_args
        self.cwd = cwd
        self.deque = deque(maxlen = 2048)
        self.retcode = None
        self.subprocess = None

    def run(self):
        logger = self.logger
        logger.debug("init")
        self.subprocess = p = Popen(self.cmd_args, bufsize = 4096, cwd = self.cwd, stdout=PIPE, stderr=PIPE, close_fds=True)
        out, err= p.stdout, p.stderr
        wait_list = [out, err]
         
        #async
        fcntl.fcntl(out, fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(err, fcntl.F_SETFL, os.O_NONBLOCK)

        logger.debug("run cmd: " + str(self.cmd_args))

        while True:
            try:
                rlist, wl, el = select(wait_list, [], [], 8)
                for fd in rlist:
                    o = fd.read()
                    self.deque.append(o)

            except IOError, e:
                logger.debug("IOError" + str(e))
                continue

            if p.poll() is not None:
                ret = self.retcode = p.returncode
                last_log = ''

                for pipe in wait_list:
                    o = pipe.read()
                    if len(o) > 0:
                        self.deque.append(o)
                        last_log += o
                    pipe.close()

                logger.debug("wget ended. exit code: '%d'" % ret)
                if ret != 0:
                    logger.debug("wget lastlog: " + last_log)

                break

    pop = lambda s:s.deque.popleft()

    @property
    def status(self):
        status = ''
        if self.is_alive():
            status = "Running"
        else:
            if self.retcode == 0:
                status = "Done"
            elif self.retcode == 3:
                status = "IO Error"
            else:
                status = "Error"

        return status

    @property
    def need_retry(self):
        retcode = self.retcode
        if not self.is_alive() and (retcode is not None) and (retcode != 0) and (retcode != 3):
            return True
        else:
            return False

    is_finished = property(lambda s:s.retcode == 0)

    def suicide(self):
        log = self.logger
        log.debug("thread suicide")
        if self.is_alive():
            if self.subprocess.poll() is None:
                log.debug("subprocess living.. terminate it")
                self.subprocess.terminate()
                while self.subprocess.poll() is None:
                    log.debug("wait for subprocess end.")
                    time.sleep(0.5)

class TaskMointorThread(Thread):

    def __init__(self, task_mgr):
        super(TaskMointorThread, self).__init__(name = type(self).__name__)
        self.logger = logging.getLogger(type(self).__name__)
        self.daemon = True
        self.task_mgr = task_mgr

    def run(self):
        logger = self.logger
        task_pool = self.task_mgr.thread_pool

        logger.info("init")

        while True:
            keys = tuple(task_pool.keys())
            for k in keys:
                t = task_pool[k]

                if "dl_thread" not in t:
                    logger.info("skiped " + str(k))
                    continue

                dl_thread = t["dl_thread"]

                if dl_thread.is_finished:
                    logger.info("task finished, remove thread obj" + str(k))
                    del t["dl_thread"]

                if dl_thread.need_retry:
                    filepath = os.path.join(t["dl_dir"], t["filename"])
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0 and t["retry_time"] > 5:
                        logger.info("task '%s' might finished. if not, try remove this file: '%s'" % (k, filepath))
                    elif t["retry_time"] > 10:
                        logger.info("task '%s' failed for 10 times. skip forever" % k)
                    else:
                        logger.info("retry task " + str(k))
                        t["retry_time"] += 1
                        t["dl_thread"] = dl_thread = self.task_mgr.new_task_thread(t)

            time.sleep(3)


class ThunderTaskManager(object):

    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.thread_pool = {}

    def new_wget_task(self, tasktype, filename, dl_url, cookies_values):
        log = self.logger

        uid = str(time.time()).replace('.', '')

        taskinfo = dict(uid = uid,
                        tasktype = tasktype,
                        filename = filename,
                        dl_dir = DEFAULT_DOWN_DIR,
                        dl_url = dl_url,
                        dl_headers = "Cookie: " + "".join(map(lambda s:"%s=%s; " % s, cookies_values)),
                        retry_time = 0,
                        thread_lock = threading.Lock()
                        )

        dl_thread = self.new_task_thread(taskinfo)
        taskinfo["dl_thread"] = dl_thread

        self.thread_pool[uid] = taskinfo

        log.debug("task %s thread id :%s" % (uid, str(dl_thread.ident)))

        return uid

    def new_task_thread(self, taskinfo):
        filename = taskinfo["filename"]
        dl_url = taskinfo["dl_url"]
        dl_dir = taskinfo["dl_dir"]
        dl_headers = taskinfo["dl_headers"]

        wget_cmd = ['/usr/bin/wget', '--continue', '--header', dl_headers, '-O', filename, 
                '--progress=dot', dl_url]

        dl_thread = DownloadThread(wget_cmd, dl_dir)
        dl_thread.start()

        return dl_thread

    def force_restart(self, uid):
        log = self.logger
        taskinfo = self.thread_pool[uid]

        lock = taskinfo["thread_lock"]
        log.debug("force restart acquire lock")
        lock.acquire()

        thread = taskinfo["dl_thread"]
        thread.suicide()
        if thread.is_alive():
            log.debug("thread is alive, join")
            thread.join()

        taskinfo["dl_thread"] = None
        taskinfo["retry_time"] = 0
        dl_thread = taskinfo["dl_thread"] = self.new_task_thread(taskinfo)
        lock.release()
        log.debug("force restart release lock")
        log.debug("thread restarted, id :%s" % str(dl_thread.ident))


    def list_all_tasks(self):
        p = self.thread_pool
        self.logger.debug("list all keys: " + str(self.thread_pool.keys()))
        return map(lambda k:dict(uid = p[k]["uid"], 
            tasktype = p[k]["tasktype"],
            filename = p[k]["filename"], 
            status = p[k]["dl_thread"].status if "dl_thread" in p[k] else "Done"), 
            sorted(self.thread_pool.keys()))


@route("/thunder_single_task")
@LogException
def thunder_single_task():
    filename = request.GET.get("name")
    dl_url = request.GET.get("url")
    cookies_str = request.GET.get("cookies")
    cookie = Cookie.BaseCookie(cookies_str)
    gdriveid = cookie["gdriveid"].value
    tid = task_mgr.new_wget_task("thunder", filename, dl_url, [("gdriveid", gdriveid)])
    return dict(tid = tid)

@route("/qq_single_task")
@LogException
def qq_single_task():
    filename = request.GET.get("name")
    dl_url = request.GET.get("url")
    cookies_str = request.GET.get("cookies")
    cookie = Cookie.BaseCookie(cookies_str)
    tid = task_mgr.new_wget_task("qq", filename, dl_url, [("FTN5K", cookie["FTN5K"].value)])
    return dict(tid = tid)

@route("/list_all_tasks")
@LogException
def list_all_tasks():
    return dict(tasks = task_mgr.list_all_tasks())


@route("/query_task_log/:tid")
@LogException
def query_task_log(tid = None):
    assert tid is not None, "need tid"

    taskinfo = task_mgr.thread_pool.get(tid)
    if taskinfo is None:
        abort(404, "taskid not found, " + tid)

    if "dl_thread" in taskinfo:
        lock = taskinfo["thread_lock"]

        logger.debug("query acquire lock")

        lock.acquire()
        thread = taskinfo["dl_thread"]
        output = cStringIO.StringIO()

        while True:
            try:
                line = thread.pop()
                output.write(line)
            except IndexError:
                break
       
        lock.release()
        logger.debug("query release lock")
        line = output.getvalue()
        output.close()
        ret = dict(status = thread.status, line = line, retry_time = taskinfo["retry_time"], need_retry = (taskinfo["retry_time"] < 6))
    else:
        ret = dict(status = "Done", line = "", retry_time = taskinfo["retry_time"], need_retry = False)

    return ret

@route("/force_restart/:tid")
@LogException
def force_restart(tid = None):
    assert tid is not None, "need tid"
    task_mgr.force_restart(tid)
    return ""



@route("/")
@view('mointor')
def root():
    return {}


if __name__ == "__main__":


    task_mgr = ThunderTaskManager()
    mointor = TaskMointorThread(task_mgr)
    mointor.start()

    import webbrowser
    webbrowser.open_new_tab("http://127.0.0.1:8080")
    print "Default Download Dir: '%s'" % DEFAULT_DOWN_DIR

    run(host='0.0.0.0', port=8080)


import unittest

class test_wget(unittest.TestCase):
    def setUp(self):

        import shlex
        cmd = 'wget -O /dev/null --progress=dot http://ftp.tw.debian.org/debian/ls-lR.gz'
        cmd = 'wget -O /dev/null --progress=dot http://ftp.tw.debian.org/debian/ls-lR.patch.gz'

        self.shell_cmd = shlex.split(cmd)
        print self.shell_cmd

    def test_wget(self):
        t = DownloadThread(self.shell_cmd)
        t.start()

        while True:
            try:
                c, o = t.pop()
                print c, o

            except IndexError:
                if not t.is_alive():
                    break

                time.sleep(.1)


    def test_notget(self):

        t = DownloadThread(self.shell_cmd)
        t.start()
        t.join()

    def test_taskmgr(self):

        filename = "13. Hiding My Heart.mp3"
        dl_url = "http://gdl.lixian.vip.xunlei.com/download?fid=qyh37P2CIFsIwt/RgbLulXGzJo27TH8AAAAAAHLX9VaTzNJL1DkuNS5iEzxbyGLZ&mid=666&threshold=150&tid=F4F3C6EE85C70547FDA4D027E0E895D5&srcid=4&verno=1&g=72D7F55693CCD24BD4392E352E62133C5BC862D9&scn=t7&i=71F8AE377D07F36D04350171D3BB8FD33E162150&t=6&ui=169602995&ti=42518759750&s=8342715&m=0&n=015002CA7F486964690F56C41279204865004390716D703300"
        gdriveid = "7617B8D05D955EA55C05EF3908D8162F"

        m = ThunderTaskManager()
        tid = m.new_thunder_task(filename, dl_url, gdriveid)
        t = m.thread_pool[tid].dl_thread

        while True:
            try:
                c, o = t.pop()
                if c == "OUT":
                    sys.stdout.write(o)
                else:
                    print c, o

            except IndexError:
                if not t.is_alive():
                    break

                time.sleep(.1)




