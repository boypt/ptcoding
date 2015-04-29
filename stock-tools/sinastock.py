#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse
import colorama
colorama.init()

from colorama import Fore, Back, Style

MARKET_PREFIX = {
        "6":"sh",
        "9":"sh",
        "5":"sh",
        "0":"sz",
        "2":"sz",
        "3":"sz",
        "1":"sz",
    }

def sina_stock(all_num):
    reg = re.compile(r'var hq_str_s_[szh]{2}(\d{6})="(.+?)";\n')
    market_num = map(lambda num: "s_{}{}".format(MARKET_PREFIX[num[0]], num), all_num)
    query_str = ",".join(market_num)
    req = urllib.request.Request("http://hq.sinajs.cn/list="+query_str)
    data = urllib.request.urlopen(req).read().decode('gbk')
    stall = reg.findall(data)

    return stall
    

def print_stock(stock_list):

    for num, stock in stock_list:

        q = stock.split(',')

        # for n,v in enumerate(q): print (n,v)
        name = q[0]
        curval = float(q[1])
        incr = float(q[2])
        incr_pct = float(q[3])

        color = Style.BRIGHT + (Fore.RED if incr >= 0 else Fore.GREEN)

        if curval == 0:
            curval=1

        curval_str = "{:.4f}".format(curval).rjust(8)
        incr_str = "{:+.4f}".format(incr).rjust(7)
        incr_pct_str = "{:+.2f}%".format(incr_pct).rjust(7)

        print("{}{}  {}  {}     {}{}{}".format(color,curval_str,incr_str,incr_pct_str,num,name,Style.RESET_ALL))

if __name__ == '__main__':

    num_fn = sys.argv[1]

    with open(num_fn, 'rb') as f:
        nums = f.read().decode('ascii', 'ignore')
        num_re = re.compile(r"\d{6}")
        file_num = num_re.findall(nums)
        stall = sina_stock(file_num)

        print("---最新-----涨跌-----涨幅------名称-----------------------------------")
        print_stock(stall)
        print("-"*70)
        if os.name == 'nt':
            os.system("pause")

