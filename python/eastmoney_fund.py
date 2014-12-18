#!/usr/bin/python3

import re
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
            fund_db[key] = dict(num=cols[0], name=cols[1], valdate=cols[17], val=cols[18])
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

    #pprint(dtdb)
    with open(num_fn) as f:
        nums = f.readlines()
        vals = []
        for ln in nums:
            key = re.match(r"\d+", ln).group()
            if key in dtdb:
                print("{num: <10}\t{name: <20}\t{val}\t{valdate}".format(**dtdb[key]))
                vals.append(dtdb[key]['val'])

        print("---------")
        print("\n".join(vals))

