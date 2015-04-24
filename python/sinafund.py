#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse


def sina_fund(num):
    query_str = ",".join(map(lambda z:'f_{}'.format(z), num))
    req = urllib.request.Request("http://hq.sinajs.cn/list="+query_str)
    data = urllib.request.urlopen(req).read().decode('gbk')
    reg = re.compile(r'var hq_str_f_(\d{6})="(.+?)";\n')
    stall = reg.findall(data)

    return stall


def print_fund(fund_all):

    for num,fund in fund_all:
        q=fund.split(',')
        name = q[0]
        curval = float(q[1])
        lastval = float(q[3])
        date = q[4]
        incr = (curval-lastval)/lastval

        s_curval = "{:.4f}".format(curval).rjust(7)
        s_lastval = "{:.4f}".format(lastval).rjust(7)
        s_incr = "{:+.2%}".format(incr).rjust(7)

        print("{}  {}  {}   {} -- {}{}".format(s_curval,s_incr,s_lastval,date,num,name))


if __name__ == '__main__':

    num_fn = sys.argv[1]

    with open(num_fn, 'rb') as f:
        nums = f.read().decode('ascii', 'ignore')
        num_re = re.compile(r"\d{6}")
        file_num = num_re.findall(nums)
        stall = sina_fund(file_num)

        print("--净值-----涨幅-----昨净-----净值日期-----------基金全称--------------")
        print_fund(stall)
        print("-"*70)
        if os.name == 'nt':
            os.system("pause")

