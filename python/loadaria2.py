#!/usr/bin/env python3

import asyncio
import concurrent.futures
import urllib
import functools
import requests
import json
import pprint
import sys
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
    rsp = aria2_do_jsonrpc("aria2.addUri", [uris])
    assert "result" in rsp, 'result in resp'

    fn = os.path.basename(uris)
    fn = urllib.parse.unquote(fn, encoding='utf-8', errors='replace') 
    return fn

def aria2_getInfo():
    rsp =  aria2_do_jsonrpc("aria2.getGlobalStat")

    assert "result" in rsp, 'result in resp'
    return """
Active:  {}
DownSpeed: {:.2f} M/s
""".format(rsp["result"]["numActive"], int(rsp["result"]["downloadSpeed"])/1024/1024)
    
def aria2_tellActive():
    rsp = aria2_do_jsonrpc("aria2.tellActive")
    progs = [ 
        "{:.0f}% - {}".format(
            int(t['files'][0]['completedLength']) / int(t['files'][0]['length']) * 100,
            os.path.basename(t['files'][0]['path'])
        )
        for t in rsp['result'] if int(t['files'][0]['length']) > 0 ]
    
    return "\n".join(progs)
    
async def main():
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
    loop = asyncio.get_event_loop()

    fu_info = loop.run_in_executor(None, aria2_getInfo)
    fu_info.add_done_callback(lambda x: print(x.result()))
    print("==="*20)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            fu_act = loop.run_in_executor(None, aria2_tellActive)
            fu_act.add_done_callback(lambda x: print(x.result()))
            await asyncio.gather(fu_info, fu_act)
        return
            
    uris = await loop.run_in_executor(None, do_recur_getlist, sourceroot)
    print("Get: URLs ({})".format(len(uris)))
    futures = []
    for idx, uri in enumerate(uris):
        fut = loop.run_in_executor(None, aria2_addUri, uri)
        fut.add_done_callback(functools.partial(
            lambda idx, fut: print("{}:{}".format(idx+1, fut.result())),
            idx)
        )

        #fut.add_done_callback(print)
        futures.append(fut)

    asyncio.gather(*futures)
    print(await loop.run_in_executor(None, aria2_getInfo))
    print("==="*20)

if __name__ == "__main__":
    #main()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

