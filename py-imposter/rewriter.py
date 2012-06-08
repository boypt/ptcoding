#!/usr/bin/env python2

import sys
import logging

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

def modify_url(line):
    lst = line.split(' ')
    old_url = lst[0]
    url = old_url

    ret_url = None

    if lst[3] != "GET":
        ret_url = old_url + "\n"
    else:
#        log.debug(str(lst))
        idx = url[7:].find('/')
        host = url[7:7+idx]

        if host in RWHOSTS:
            ret_url = "http://127.0.0.1:8080/proxy?url={0}".format(old_url)
        else:
            ret_url = old_url + "\n"

    log.debug(ret_url)
    return ret_url
 
while True:
    try:
        # the format of the line read from stdin is
        # URL ip-address/fqdn ident method
        # for example
        # http://saini.co.in 172.17.8.175/saini.co.in - GET -
        line = sys.stdin.readline().strip()
        # new_url is a simple URL only
        # for example
        # http://fedora.co.in
        new_url = modify_url(line)
        sys.stdout.write(new_url)
        sys.stdout.flush()
    except Exception, e:
        log.critical(str(e), exc_info = True)

