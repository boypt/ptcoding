import os
import sys
import fcntl
import time
import logging
from collections import deque
from threading import Thread
from subprocess import Popen, PIPE
from select import select
from tempfile import NamedTemporaryFile

import bottle
bottle.debug(True)

from bottle import route, run, redirect, request, abort, get, view
import Cookie
import json

logging.basicConfig(filename = "/tmp/thunderbatch.log",
        format = "%(asctime)s %(threadName)s(%(thread)s):%(name)s:%(message)s",
                            level = logging.DEBUG)

logger = logging.getLogger()

class DownloadThread(Thread):

    def __init__(self, cmd_args, cwd = None):
        super(DownloadThread, self).__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.daemon = True
        self.cmd_args = cmd_args
        self.cwd = cwd
        self.deque = deque(maxlen = 100)

    def run(self):
        logger = self.logger
        logger.debug("init")
        p = Popen(self.cmd_args, bufsize = 4096, cwd = self.cwd, stdout=PIPE, stderr=PIPE, close_fds=True)
        out, err= p.stdout, p.stderr
        wait_list = [out, err]
         
        #async
#        fcntl.fcntl(out, fcntl.F_SETFL, os.O_NONBLOCK)
#        fcntl.fcntl(err, fcntl.F_SETFL, os.O_NONBLOCK)

        logger.debug("run cmd: " + str(self.cmd_args))

        line_cache = []

        while True:
            try:
                rlist, wl, el = select(wait_list, [], [], 8)
                for fd in rlist:
                    o = fd.readline(80)
                    if o.endswith('\n'):
                        if len(line_cache) > 0:
                            line_cache.append(o)
                            o = ''.join(line_cache)
                            line_cache = []
                        logger.debug("read out:" + o)
                        self.deque.append(("OUT", o))
                    else:
                        line_cache.append(o)

            except IOError, e:
                logger.debug("IOError" + str(e))
                continue

            if p.poll() is not None:
                logger.debug("subprocess end.")
                if len(line_cache) > 0:
                    o = ''.join(line_cache)
                    self.deque.append(("OUT", o))
                break

            logger.debug("next line")

        ret = p.returncode
        self.deque.append(("RETCODE", ret))

        logger.debug("wget returned %d." % ret)

    pop = lambda s:s.deque.popleft()



class ThunderTaskManager(object):

    DOWNLOAD_DIR = "/home/boypt/Downloads"

    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.cookies_pool = {}
        self.thread_pool = []

    def make_cookies_file(self, gdriveid):
        if gdriveid in self.cookies_pool:
            return self.cookies_pool[gdriveid]

        cookie_line = ".vip.xunlei.com\tTRUE\t/\tFALSE\t0\tgdriveid\t%s\n" % gdriveid 
        tmp_file = NamedTemporaryFile(suffix='.txt', delete=False)
        tmp_file.write(cookie_line)
        tmp_file.close()
        self.cookies_pool[gdriveid] = tmp_file.name
        return tmp_file.name

    def new_thunder_task(self, filename, dl_url, gdriveid):
        log = self.logger

        cookies_file = self.make_cookies_file(gdriveid)
        wget_cmd = ['/usr/bin/wget', '-O', filename, 
                '--progress=dot', '--load-cookies', cookies_file,  dl_url]

        log.debug("cmd shell: " + str(wget_cmd))

        dl_thread = DownloadThread(wget_cmd, self.DOWNLOAD_DIR)
        dl_thread.start()

        self.thread_pool.append((filename, dl_url, gdriveid, cookies_file, dl_thread))

        log.debug("thread id :" + str(dl_thread.ident))
        return dl_thread.ident

    def list_all_tasks(self):
        return map(lambda t:(t[0], t[4].is_alive()), self.thread_pool)



@route("/new_single_file_task")
def new_single_file_task():
    filename = request.GET.get("name")
    dl_url = request.GET.get("url")
    cookies_str = request.GET.get("cookies")
    cookie = Cookie.BaseCookie(cookies_str)
    gdriveid = cookie["gdriveid"].value
    tid = task_mgr.new_thunder_task(filename, dl_url, gdriveid)
    return dict(tid = tid)

@route("/list_all_tasks")
def list_all_tasks():
    tasks = task_mgr.list_all_tasks()
    return dict(tasks = tasks)

@route("/test_json")
def test_json():
    cb = request.GET.get("callback")
    return cb + "(%s)" %json.dumps(dict(platform = sys.platform, ls = [1,2]))


@route("/query_task_log/:tid")
def query_task_log(tid = None):
    assert tid is not None, "need tid"

    thread = task_mgr.thread_pool.get(int(tid))
    if thread is None:
        code, line = "EMPTY", ""
    else:
        try:
            code, line = thread.pop()
        except IndexError:
            code, line = "EMPTY", ""

    return dict(code = code, line = line)

@route("/")
@view('mointor')
def root():
    return {}

if __name__ == "__main__":
    task_mgr = ThunderTaskManager()
    run(host='localhost', port=8080)



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
        tid = m.new_thunder_task(filename, dl_url, "/tmp", gdriveid)
        t = m.thread_pool[tid]

        while True:
            try:
                c, o = t.pop()
                print c, o

            except IndexError:
                if not t.is_alive():
                    break

                time.sleep(.1)




