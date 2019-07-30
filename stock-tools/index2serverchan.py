#!/usr/bin/env python3
import re
import sys
import os
import json
import datetime
import urllib.request, urllib.error, urllib.parse

class MarketClosed(Exception):
    pass

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

def sina_stock(all_num):
    reg = re.compile(r'var hq_str_(.+?)="(.+?)";\n')
    query_str = ",".join(all_num)
    url = "http://hq.sinajs.cn/list="+query_str
    req = urllib.request.Request(url)
    data = urllib.request.urlopen(req).read().decode('gbk')
    stall = reg.findall(data)
    return stall

def noti_serverchan(title, desp):
    url = "https://sc.ftqq.com/{}.send".format(serverchansec)
    data = {
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
        nameshort = name[:1]

        dateoffer = q[30]
        timenow = datetime.datetime.now()
        if dateoffer != '{:%Y-%m-%d}'.format(timenow):
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

        content.append((nameshort, curval, changechn, incr_pct, vol))

    return timenow, content


if __name__ == '__main__':

    readconf()

    try:
        timenow, content = format_stockindex()
    except MarketClosed:
        sys.exit(0)

    tit = [ "{0}{2}{3:.2f}".format(*val) for val in content]
    #vol = [ "{0}{4}亿".format(*val) for val in content]
    #desp = ["## {0}丨 {1:.2f} 丨{2:+.2f}%丨{3}亿".format(*val) for val in content]
    #print(tit, vol)
    time = timenow.strftime('%Y{y}%m{m}%d{d} %H{h}%M{mm}').format(y='年', m='月', d='日', h='时', mm='分')
    noti_serverchan('丨'.join(tit), time)
