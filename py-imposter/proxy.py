#!/usr/bin/env python2

import bottle
from bottle import request, post, redirect, error, get
from cStringIO import StringIO
import pycurl

bottle.debug(1)

class CurlNon200Status(Exception):
    pass

def curl_http(uri, headers):

    buf = StringIO()
    c = pycurl.Curl()
    try:
        c.setopt(c.URL, uri)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 8)
        c.setopt(c.FAILONERROR, True)

        c.setopt(c.HTTPHEADER, headers)
        c.setopt(pycurl.WRITEFUNCTION, buf.write)
        c.perform()

        if c.getinfo(pycurl.HTTP_CODE) != 200:
            raise CurlNon200Status()

        content = buf.getvalue()

    finally:
        c.close()
        buf.close()

    return content


@get('/proxy')
def proxy():
    url = request.GET.get("url")
    headers = ["{0}: {1}".format(k,v) for k,v in request.headers.iteritems()]
    import ipdb; ipdb.set_trace()

    try:
        content = curl_http(url, headers)
    except Exception, e:
        raise


bottle.run(bottle.app())

