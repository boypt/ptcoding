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
import argparse
import logging
from http.client import HTTPConnection


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

async def do_recur_getlist(root):
    fulluris = []

    rst = await loop.run_in_executor(None, lambda:requests.get(root,
         headers={'accept': 'application/json'}))

    if rst.text != "null":

        futs = []
        for item in rst.json():
            uri = "{}{}".format(root, item["URL"][2:])
            if item["IsDir"]:
                futs.append( asyncio.ensure_future(do_recur_getlist(uri)) )
            else:
                if item["Size"] < 10*1024*1024:
                    continue
                    
                fulluris.append(uri)

        if len(futs) > 0:
            fulluris.extend(*await asyncio.gather(*futs))
            
    return fulluris

async def aria2_do_jsonrpc(method, params = []):

    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": method,
        "params": ["token:{}".format(aria2_token), params],
        "jsonrpc": "2.0",
        "id": 0,
    }
    data = json.dumps(payload)
    
    resp = await loop.run_in_executor(None, lambda: requests.post(
        aria2_url, data=data, headers=headers))
    return resp.json()
    
async def aria2_addUri(uris):
    rsp = await aria2_do_jsonrpc("aria2.addUri", [uris])
    assert "result" in rsp, 'result in resp'

    fn = os.path.basename(uris)
    fn = urllib.parse.unquote_plus(fn, encoding='utf-8', errors='replace') 
    return fn

async def aria2_getInfo():
    rsp = await aria2_do_jsonrpc("aria2.getGlobalStat")

    assert "result" in rsp, 'result in resp'
    return """
Active:  {}
DownSpeed: {:.2f} M/s
""".format(rsp["result"]["numActive"], int(rsp["result"]["downloadSpeed"])/1024/1024)
    
async def aria2_tellActive():
    rsp = await aria2_do_jsonrpc("aria2.tellActive")
    progs = [ 
        "{:.0f}% - {}".format(
            int(t['files'][0]['completedLength']) / int(t['files'][0]['length']) * 100,
            os.path.basename(t['files'][0]['path'])
        )
        for t in rsp['result'] if int(t['files'][0]['length']) > 0 ]
    
    return "\n".join(progs)
    
async def do_list(loop):
    futus = [
        asyncio.ensure_future(fn)
        for fn in (aria2_getInfo, aria2_tellActive)
    ]
    for fu in futus:
        fu.add_done_callback(lambda x: print(x.result()))

    await asyncio.wait(futus)

async def do_load(loop):
    _fu = asyncio.ensure_future(aria2_getInfo())
    _fu.add_done_callback(lambda f:print(f.result()))
    uris = await do_recur_getlist(sourceroot)
    print("==="*20)
    print("Get: URLs ({})".format(len(uris)))
    futures = []
    for idx, uri in enumerate(uris):
        fut = asyncio.ensure_future(aria2_addUri(uri))
        fut.add_done_callback(functools.partial(
            lambda idx, fut: print("[{:^3}] {}".format(idx+1, fut.result())),
            idx)
        )
        
        futures.append(fut)

    await asyncio.wait(futures)
    print("==="*20)

async def main(loop):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', dest='verbose', help='verbose request process')
    parser.add_argument('-l', '--list', action='store_true', dest='list', help='list')
    args = parser.parse_args()
    if args.verbose:
        if args.verbose > 0:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
        if args.verbose > 1:
            HTTPConnection.debuglevel = 1

    if args.list:
        await do_list(loop)
    else:
        await do_load(loop)

if __name__ == "__main__":
    readconf()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

