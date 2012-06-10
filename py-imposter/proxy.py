#!/usr/bin/env python2

import bottle
from bottle import request, response, HTTPResponse, post, redirect, error, get
from cStringIO import StringIO
import pycurl
import re
from wsgiref.util import is_hop_by_hop

STRIP_HEADERS = frozenset(("host", "via", "x-forwarded-for"))

bottle.debug()

class CurlNon200Status(Exception):
    pass

def curl_http(uri, headers):

    headerbuf = StringIO()
    bodybuf = StringIO()
    c = pycurl.Curl()
    try:
        c.setopt(c.URL, uri)
        c.setopt(c.CONNECTTIMEOUT, 30)
        c.setopt(c.TIMEOUT, 30)
        c.setopt(c.FAILONERROR, True)

        c.setopt(c.HTTPHEADER, headers)
        c.setopt(pycurl.HEADERFUNCTION, headerbuf.write)
        c.setopt(pycurl.WRITEFUNCTION, bodybuf.write)
        c.perform()

        if c.getinfo(pycurl.HTTP_CODE) != 200:
            raise CurlNon200Status()

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
#        import ipdb;ipdb.set_trace()    
        headret = [(k,v) for k,v in headtuple if not is_hop_by_hop(k)]
        raise HTTPResponse(output = content, header = headret)
    except (pycurl.error, CurlNon200Status):
        redirect(url)

    except Exception, e:
        raise


bottle.run(debug = True)

