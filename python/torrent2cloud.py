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
import re
import glob
import logging
import urllib
import argparse
from http.client import HTTPConnection

CLDTORRENT=""
CLDCOOKIE=""
torrent_local_path="/mnt/d/*.torrent"

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

async def torrent2mag(local_fn):
    req_headers = requests.utils.default_headers()
    req_headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    })
    re_mag = re.compile(r'(?<=href=")(magnet:[^"]+)(?=")')
    url = "http://torrent2magnet.com/upload/"
    bsname = os.path.basename(local_fn)
    loop = asyncio.get_event_loop()
    magurl = ""
    with open(local_fn, 'rb') as torrent:
        r = await loop.run_in_executor(None, lambda : requests.post(url, headers=req_headers, files={'torrent_file': (bsname, torrent)}))
        assert r.status_code == 200
        mag = re_mag.search(r.text)
        assert mag is not None
        magurl = mag[0]

    return await mag2cloud(magurl)
    
async def mag2cloud(mag):
    _re_name = re.compile(r';dn=(\S+)$')
    fn = _re_name.search(mag)
    if fn:
        fn = urllib.parse.unquote_plus(fn[1])
        print("-->> ", fn, )

    loop = asyncio.get_event_loop()
    req_headers = requests.utils.default_headers()
    req_headers.update({
            'Cookie':CLDCOOKIE[8:],
            'Content-Type': 'application/json'
    })
    url = CLDTORRENT+"/api/magnet"
    r = await loop.run_in_executor(None, lambda :requests.post(url, headers=req_headers, data=mag))

    assert r.status_code == 200
    print(r.text, fn)
    return r.text

async def main():
    futures = [
        asyncio.ensure_future(torrent2mag(local_fn))
        for local_fn in glob.glob(torrent_local_path)
    ]
    print("==="*20)
    await asyncio.wait(futures)
    print("==="*20)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='count', dest='verbose', help='verbose request process')
    results = parser.parse_args()

    if results.verbose and results.verbose > 0:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
    
    if results.verbose and results.verbose > 1:
        HTTPConnection.debuglevel = 1

    readconf()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

