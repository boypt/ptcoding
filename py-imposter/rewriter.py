#!/usr/bin/env python2

import sys
import logging
import urllib
import hashlib
import pylibmc
import urlparse
import posixpath
mc = pylibmc.Client(["127.0.0.1"], binary=True,
                        behaviors={"tcp_nodelay": True,
                        "ketama": True})

def log_init(log_file, quiet = False, name = __name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    if not quiet:
        hdlr = logging.StreamHandler()
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
    return logger

log = log_init("/tmp/rewriter.log", quiet = True)

log.info("init")


RWHOSTS = frozenset(("weibo.com", "baidu.com", "qq.com"))
NORWTYPES = frozenset(("js", "css", "gif", "jpg", "png", "swf", "flv", "f4v"))

def is_url_non_html(url):
    path = urlparse.urlparse(url).path
    ext = posixpath.splitext(path)[1]
    return (ext != '') and ext[1:] in NORWTYPES

def modify_url(line):
    #log.debug("ORIGLINE: " + line)

    lst = line.split(' ')
    if len(lst) == 1:
        return ""

    old_url = lst[0]
    url = old_url
    ret_url = None

    try:
        if lst[3] != "GET":
            ret_url = old_url
            log.debug("NOT GET: " + ret_url)
        elif mc.get(hashlib.md5(url).hexdigest()) == 1:
            ret_url = old_url
            log.debug("MEMCACHED: " + ret_url)
        elif is_url_non_html(old_url):
            ret_url = old_url
            log.debug("NON HTML: " + ret_url)
        else:
            ret_url = "http://127.0.0.1:8080/proxy?url={0}".format(urllib.quote(old_url))
            log.debug("rewrite: " + ret_url)

#            idx = url[7:].find('/')
#            host = url[7:7+idx]
#        if host in RWHOSTS:
#            ret_url = "http://127.0.0.1:8080/proxy?url={0}".format(urllib.quote(old_url))
#        else:
#            ret_url = old_url + "\n"


    except MemcachedError:
        ret_url = old_url

    return ret_url + "\n"
 
while True:
    try:
        # the format of the line read from stdin is
        # URL ip-address/fqdn ident method
        # for example
        # http://saini.co.in 172.17.8.175/saini.co.in - GET -
        line = sys.stdin.readline().strip()
        if len(line) == 0:
            sys.exit(0)
        # new_url is a simple URL only
        # for example
        # http://fedora.co.in
        new_url = modify_url(line)
    except Exception, e:
        log.critical(str(e), exc_info = True)
        lst = line.split(' ')
        new_url = lst[0]
    finally:
        sys.stdout.write(new_url)
        sys.stdout.flush()

