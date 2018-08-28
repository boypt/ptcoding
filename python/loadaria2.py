#!/usr/bin/env python3

import requests
import json
import pprint
import sys
import os

aria2_url=""
aria2_token=""
sourceroot=""

def do_recur_getlist(root):
    fulluris = []

    rst = requests.get(root, headers={'accept': 'application/json'})
    if rst.text != "null":
        for item in rst.json():
            uri = "{}{}".format(root, item["URL"][2:])
            if item["IsDir"]:
                fulluris.extend(do_recur_getlist(uri))
            else:
                if item["Size"] < 10*1024*1024:
                    continue
                    
                fulluris.append(uri)
            
    return fulluris

def aria2_do_jsonrpc(method, params = []):

    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": method,
        "params": ["token:{}".format(aria2_token), params],
        "jsonrpc": "2.0",
        "id": 0,
    }
    data = json.dumps(payload)
    
    #print(data)
    response = requests.post(
        aria2_url, data=data, headers=headers, verify=False).json()

    return response
    
def aria2_addUri(uris):
    return aria2_do_jsonrpc("aria2.addUri", [uris])

def aria2_getInfo():
    rsp =  aria2_do_jsonrpc("aria2.getVersion")
    if "result" in rsp:
        print(rsp["result"]["version"])
        
    rsp =  aria2_do_jsonrpc("aria2.getGlobalStat")
    if "result" in rsp:
        print("""
Active:  {}
DownSpeed: {:.2f} M/s
""".format(rsp["result"]["numActive"], int(rsp["result"]["downloadSpeed"])/1024/1024))
    
def aria2_tellActive():
    rsp = aria2_do_jsonrpc("aria2.tellActive")
    #print(rsp['result'])
    progs = [ 
        "{:.0f}% - {}".format(
            int(t['files'][0]['completedLength']) / int(t['files'][0]['length']) * 100,
            os.path.basename(t['files'][0]['path'])
        )
        for t in rsp['result'] ]
    
    [ print(p) for p in progs ]
    
def main():

    conf = os.path.expanduser("~/.ptutils.config")
    if os.path.exists(conf):
        with open(conf) as f:
            configs = f.readlines()
        
        glbs = globals()
        for f in configs:
            if len(f) < 2:
                continue
            
            key ,val = f.strip().split('=', 1)
            if key in glbs:
                glbs[key] = val.strip('"')
                
    else:
        print("~/.ptutils.config not found")
        sys.exit(1)

    aria2_getInfo()
    print("==="*20)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            aria2_tellActive()
                    
        return
            
    uris = do_recur_getlist(sourceroot)
    for uri in uris:
        ret = aria2_addUri(uri)
        print(ret)

    print("==="*20)
    aria2_getInfo()

if __name__ == "__main__":
    main()
