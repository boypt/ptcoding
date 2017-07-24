#!/usr/bin/env python3.6
import re
import sys
import os
import json
import datetime
import urllib.request, urllib.error, urllib.parse

class MarketClosed(Exception):
    pass

def sina_stock(all_num):
    reg = re.compile(r'var hq_str_(.+?)="(.+?)";\n')
    query_str = ",".join(all_num)
    url = "http://hq.sinajs.cn/list="+query_str
    req = urllib.request.Request(url)
    data = urllib.request.urlopen(req).read().decode('gbk')
    stall = reg.findall(data)
    return stall

def noti_serverchan(title, desp):
    url = "https://pushbear.ftqq.com/sub"
    data = {
    	"sendkey": "522-f933512d43abe659548998b284ceec89",
    	"text": title,
    	"desp": desp
    }
    req = urllib.request.Request(url, data = urllib.parse.urlencode(data).encode('utf-8'), method="POST")
    ret = urllib.request.urlopen(req).read()
    return json.loads(ret.decode())


def format_stockindex():

    #indexs = ['sh000001','sz399001','hkHSI','gb_$dji','hkHSI_i']
    indexs = ['sh000001','sz399001', 'sz399006']
    vals = sina_stock(indexs)
    content = []
    title = []
    for num, inx in vals:
        q = inx.split(',')
#"上证指数,3236.5881,3244.8647,3237.9817,3247.7122,3231.9556,0,0,206003251,221956909910,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2017-07-21,15:01:03,00";
        name = q[0]
        nameshort = name[:2]

        dateoffer = q[30]
        if dateoffer != '{:%Y-%m-%d}'.format(datetime.datetime.now()):
            raise MarketClosed()

        preclose = float(q[2])
        curval = float(q[3])
        vol = int(round(float(q[9])/100000000, 0))
        incr = curval - preclose
        incr_pct = (incr/preclose)*100
        if incr_pct > 0:
            changechn = '涨'
        elif incr_pct < 0:
            changechn = '跌'
        else:
            changechn = '平'

        title.append((nameshort, changechn, incr_pct))
        content.append((name, curval, incr_pct, vol))

    return title, content


if __name__ == '__main__':

     try:
         title, content = format_stockindex()
     except MarketClosed:
         sys.exit(0)

     tit = [ "{0}{1}{2:.2f}".format(*val) for val in title ]
     desp = ["## {0} {1:.2f} {2:+.2f}% {3}亿".format(*val) for val in content]
     noti_serverchan('__'.join(tit), '\n'.join(desp))
