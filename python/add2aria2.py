#!/usr/bin/env python
from __future__ import print_function

import urllib
import urllib2
import json
import sys
import os

aria2_url=""
aria2_token=""
sourceroot=""

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
    
def main():
    assert "CLD_PATH" in os.environ
    url = "{}/{}".format(sourceroot, urllib.quote(os.environ["CLD_PATH"]))
    print("URL: "+url)
    try:
        print(aria2_getInfo())
        print(aria2_addUri(url))
    except:
        with open('/tmp/url2aria.log', 'a+') as f:
            f.write(url+'\n')

if __name__ == "__main__":
    readconf()
    main()

