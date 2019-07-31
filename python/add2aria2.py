#!/usr/bin/env python2
from __future__ import print_function

import urllib
import urllib2
import time
import json
import sys
import os

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
    	"text": title,
    	"desp": desp
    }
    req = urllib2.Request(url)
    ret = urllib2.urlopen(req, urllib.urlencode(data).encode('utf-8'))
    return ret

def aria2_do_jsonrpc(method, params = []):

    # Example echo method
    payload = {
        "method": method,
        "params": ["token:{}".format(aria2_token), params],
        "jsonrpc": "2.0",
        "id": 0,
    }
    data = json.dumps(payload)
    req = urllib2.Request(aria2_url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36')
    response = urllib2.urlopen(req, data)
    return json.load(response)
    
def aria2_addUri(uris):
    rsp = aria2_do_jsonrpc("aria2.addUri", [uris])
    assert "result" in rsp, 'result in resp'
    return rsp

def aria2_getInfo():
    rsp = aria2_do_jsonrpc("aria2.getGlobalStat")
    assert "result" in rsp, 'result in resp'
    return """
Active:  {}
DownSpeed: {:.2f} M/s
""".format(rsp["result"]["numActive"], int(rsp["result"]["downloadSpeed"])/1024/1024)

def genUrl2aria2(fn):
    url = "{}/{}".format(sourceroot, urllib.quote(fn))
    print("AddURL: "+url)
    #print(aria2_getInfo())
    try:
        return aria2_addUri(url)
    except:
        with open('/tmp/url2aria.log', 'a+') as f:
            f.write(url+'\n')
        return {}
    
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
        desp = """
* Task: **{}**
* Size: **{}**
""".format(cld_path, sizeof_fmt(int(cld_size), "B"))

        while True:
            try:
                r = noti_serverchan(cld_path, desp)
            except Exception:
                pass
            else:
                print("serverchan notified:", r)
                break
        return

    if cld_type != "file":
        print("unknown cld_type")
        return

    if int(cld_size) < 5*1024**2:
        print("file size {} too small".format(cld_size))
        return

    retry = 10
    while retry > 0:
        retry -= 1
        ret = genUrl2aria2(cld_path)
        if "jsonrpc" in ret:
            break
        else:
            print("genUrl2aria2 retry in 3 secs")

        time.sleep(3)

if __name__ == "__main__":
    readconf()
    main()

