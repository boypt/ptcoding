#!/usr/bin/python3

import re
import os
import sys
import urllib.request
from pprint import pprint

def eastmoney_get(cookies):

    url = 'http://fund.eastmoney.com/Data/FavorCenter_v3.aspx?o=r'
    headers = { 
            "Referer": "http://fund.eastmoney.com/favor/", 
            "Cookie": cookies
            }

    req = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(req)
    data = response.read().decode("utf-8")
    return data

def parse_js_obj(est_js):
    kfdata = re.sub(r".*kfdatas:\[\[(.+?)]].*", r"[\1]", est_js).strip()
    line_all = re.findall("\[.+?\]", kfdata)
    fund_data = [ l[1:-1].replace('"','') for l in line_all if l.find(',') > 2 ]
    fund_db = {}

    for ln in fund_data:
        cols = ln.split(',')
        key=cols[0]
        try:
            fund_db[key] = dict(num=cols[0], name=cols[1], valdate=cols[17], val=cols[18], incr=cols[23])
        except IndexError:
            print('---------')
            pprint(cols)
            print('---------')

    return fund_db


if __name__ == '__main__':

    num_fn = sys.argv[1]
    with open("eastmoney.cookies") as f: cookies = f.read()

    dtstr = eastmoney_get(cookies)
    #with open("example.txt") as f: dtstr = f.read()
    dtdb = parse_js_obj(dtstr)

    with open(num_fn, 'rb') as f:
        nums = f.read()
        #vals = []
        num_re = re.compile(b"\d{6}")

        for ln in num_re.findall(nums):
            key = ln.decode('ascii')
            if key in dtdb:
                print("{num:<6}\t{val:6}\t{incr:6}%\t{valdate}\t{name:<20}".format(**dtdb[key]))
                #vals.append(dtdb[key]['val'])
            else:
                print("****** {0} Not Selected ******".format(key))

        print("---------")
        
