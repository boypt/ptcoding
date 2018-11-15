#!/usr/bin/env python3

import asyncio
import aiofiles
import urllib
import requests
import pprint
import sys
import os
import re
import glob
import logging
import argparse
import bencode3
import hashlib

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

async def torrent2mag(idx, fn):
    async with aiofiles.open(fn, mode='rb') as f:
        contents = await f.read()
        metadata = bencode3.bdecode(contents)
        hash_contents = bencode3.bencode(metadata['info'])
        digest = hashlib.sha1(hash_contents).digest().hex()

        if 'name' in metadata['info']:
            name = '&dn='+urllib.parse.quote_plus(metadata['info']['name'])
        else:
            name = ''

        print('[{}] {} --> {}'.format(idx, os.path.basename(fn), metadata['info']['name']))
        return 'magnet:?xt=urn:btih:{}{}'.format(digest, name)

async def mag2cloud(idx, mag):
    loop = asyncio.get_event_loop()
    req_headers = requests.utils.default_headers()
    req_headers.update({
            'Cookie':CLDCOOKIE[8:],
            'Content-Type': 'application/json'
    })
    url = CLDTORRENT+"/api/magnet"
    r = await loop.run_in_executor(None, lambda :requests.post(url, headers=req_headers, data=mag))

    assert r.status_code == 200
    print("[{}] {}".format(idx, r.text))
    return r.text

async def main():
    futures = [
        asyncio.ensure_future(mag2cloud(idx, await torrent2mag(idx, local_fn)))
        for idx, local_fn in enumerate(glob.glob(torrent_local_path))
    ]
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
        from http.client import HTTPConnection
        HTTPConnection.debuglevel = 1

    readconf()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

