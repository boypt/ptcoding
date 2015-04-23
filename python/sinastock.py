#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse

reg = re.compile(r'var hq_str_s_[szh]{2}\d{6}="(.+?)";\n')

def a_stock(num):
    req = urllib.request.Request("http://hq.sinajs.cn/list=%s" % num)
    data = urllib.request.urlopen(req).read().decode('gbk')
    #with open('/tmp/st.txt', 'rb') as f: data = f.read().decode('gbk')
    
    stval = reg.findall(data)
    stall = tuple(map(lambda q:tuple(q.split(',')), stval))

    return stall
    
def market(num):
    markets = {
        "6":"sh",
        "9":"sh",
        "5":"sh",
        "0":"sz",
        "2":"sz",
        "3":"sz",
        "1":"sz",
    }

    return "s_{0}{1}".format(markets[num[0]], num)

if __name__ == '__main__':

    num_fn = sys.argv[1]

    with open(num_fn, 'rb') as f:
        nums = f.read()
        num_re = re.compile(b"\d{6}")

        file_num = num_re.findall(nums)
        all_num = map(lambda z:z.decode('ascii'), file_num)
        market_num = map(market, all_num)
        stock_num = ",".join(market_num)
        # print(stock_num)
        stall = a_stock(stock_num)

        print("-Cur-------Incr------Rate------Name------")
        for q in stall:
            # for n,v in enumerate(q): print (n,v)
            name = q[0]
            curval = float(q[1])
            incr = float(q[2])
            incr_pct = float(q[3])

            if curval == 0:
                curval=1

            curval_str = "{:.4f}".format(curval).rjust(8)
            incr_str = "{:+.4f}".format(incr).rjust(7)
            incr_pct_str = "{:+.2f}%".format(incr_pct).rjust(7)
            print("{0}  {1}  {2}     {3}".format(curval_str,incr_str,incr_pct_str,name))

        print("-"*70)
        if os.name == 'nt':
            os.system("pause")
