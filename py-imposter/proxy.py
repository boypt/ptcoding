#!/usr/bin/env python2

import bottle
from bottle import request, response, HTTPResponse, post, redirect, error, get
from cStringIO import StringIO
import pycurl
import re
import hashlib
import logging
from wsgiref.util import is_hop_by_hop

import pylibmc
mc = pylibmc.Client(["127.0.0.1"], binary=True,
                        behaviors={"tcp_nodelay": True,
                        "ketama": True})

markurl = lambda u:mc.set(hashlib.md5(u).hexdigest(), 1, time = 3600)

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

log = log_init("/tmp/proxy.log")

STRIP_HEADERS = frozenset(("host", "via", "x-forwarded-for"))




class CurlNon200Status(Exception):
    pass

def curl_http(uri, headers):

    headerbuf = StringIO()
    bodybuf = StringIO()
    c = pycurl.Curl()
    try:
        c.setopt(c.URL, uri)
        c.setopt(c.CONNECTTIMEOUT, 10)
        c.setopt(c.TIMEOUT, 10)
        c.setopt(c.FAILONERROR, True)

        c.setopt(c.HTTPHEADER, headers)
        c.setopt(pycurl.HEADERFUNCTION, headerbuf.write)
        c.setopt(pycurl.WRITEFUNCTION, bodybuf.write)
        c.perform()

        if c.getinfo(pycurl.HTTP_CODE) != 200:
            raise CurlNon200Status()

        if not c.getinfo(pycurl.CONTENT_TYPE).startswith("text/html"):
            log.debug("non-html: " + uri)
            markurl(uri)

        headers = headerbuf.getvalue()
        content = bodybuf.getvalue()

        headtuple = re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers)

    finally:
        c.close()
        headerbuf.close()
        bodybuf.close()

    return headtuple, content


@get('/proxy')
def proxy():
    url = request.GET.get("url")
    headers = ["{0}: {1}".format(k,v) for k,v in request.headers.iteritems() if k.lower() not in STRIP_HEADERS]

    try:
        headtuple, content = curl_http(url, headers)
        import ipdb;ipdb.set_trace()    

        headret = [(k,v) for k,v in headtuple if not is_hop_by_hop(k)]
        html = content.replace("<body>", "<body><!-- test -->")
        log.debug(html)
        raise HTTPResponse(output = content, header = headret)
    except pycurl.error, e:
        log.debug("curl error: " + str(e))
        markurl(url)
        redirect(url)
    except CurlNon200Status:
        log.debug("non 200: ")
        markurl(url)
        redirect(url)
    except Exception, e:
        raise


bottle.run(host = "0.0.0.0", debug = True)

