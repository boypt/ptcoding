#!/usr/bin/env python2
from __future__ import print_function

import urllib
import urllib2
import random
import time
import json
import sys
import os
import re

aria2_url=""
aria2_token=""
sourceroot=""
serverchansec = ""

def readconf():
    conf = os.path.expanduser("~/.ptutils.config")
    if os.path.exists(conf):
        with open(conf) as f:
            configs = f.readlines()
        
        glbs = globals()
        for f in configs:
            if len(f) < 2:
                continue
            
            key, val = f.strip().split('=', 1)
            if key in glbs:
                glbs[key] = val.strip('"')
                
    else:
        print("~/.ptutils.config not found")
        sys.exit(1)

def noti_serverchan(title, desp):
    if serverchansec == "":
        return

    url = "https://sc.ftqq.com/{}.send".format(serverchansec)
    data = {
        "text": re.sub(r"[\s\-\\\/]", '_', title),
        "desp": desp
    }
    req = urllib2.Request(url)
    ret = urllib2.urlopen(req, urllib.urlencode(data).encode('utf-8'))
    return ret.read()

class MaxTried(IOError):
    pass

def max_try(maxtry, func, *argv):
    maxt = maxtry
    while maxt > 0:
        maxt -= 1
        try:
            ret = func(*argv)
        except Exception as e:
            print("Exception raised, retry in 3 secs ", e)
        else:
            if ret is not None:
                print(ret)
            return
        time.sleep(3)
    else:
        raise MaxTried("Max Tried")

def try_serverchan(cld_path, cld_size):
    desp = """
* Task: **{}**
* Size: **{}**
""".format(cld_path, sizeof_fmt(int(cld_size), "B"))
    max_try(3, noti_serverchan, cld_path, desp)

def try_add_task(cld_path):
    url = "{}/{}".format(sourceroot, urllib.quote(cld_path))
    try:
        max_try(3, genUrl2aria2, url)
    except MaxTried:
        with open('/tmp/url2aria.log', 'a+') as f:
            f.write(url+'\n')
        print("Max tried, url logged to /tmp/url2aria.log")

def aria2_do_jsonrpc(_id, method, params = []):

    # Example echo method
    payload = {
        "method": method,
        "params": ["token:{}".format(aria2_token), params],
        "jsonrpc": "2.0",
        "id": _id,
    }
    data = json.dumps(payload)
    req = urllib2.Request(aria2_url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, data)
    return json.load(response)
    
def aria2_addUri(_id, uris):
    rsp = aria2_do_jsonrpc(_id, "aria2.addUri", [uris])
    return rsp

def aria2_getInfo(_id):
    rsp = aria2_do_jsonrpc(_id, "aria2.getGlobalStat")
    return """
Active:  {}
DownSpeed: {:.2f} M/s
""".format(rsp["result"]["numActive"], int(rsp["result"]["downloadSpeed"])/1024/1024)

def genUrl2aria2(url):
    _id = random.randint(100, 999)
    print("ID:[{}] AddURL: {}".format(_id, url))
    r = aria2_addUri(_id, url)
    return "Aria2Jsonrpc Return: {}".format(r)
    
def sizeof_fmt(num, suffix='o'):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Unit suffix (optionnal) default = o
    :type suffix: str
    :rtype: str
    """
    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def main():

    # cld_dir = os.environ.get('CLD_DIR', '')
    cld_path = os.environ.get('CLD_PATH', '')
    cld_type = os.environ.get('CLD_TYPE', '')
    cld_size = os.environ.get('CLD_SIZE', '')

    if cld_type == "torrent":
        return try_serverchan(cld_path, cld_size)

    if cld_type != "file":
        print("unknown cld_type")
        return

    if int(cld_size) < 5*1024**2:
        print("file size {} too small".format(cld_size))
        return

    return try_add_task(cld_path)

if __name__ == "__main__":
    readconf()
    main()

