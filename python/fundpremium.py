#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse


def sina_fund(num):

    if num[0:2] != '15':
        raise TypeError('Number must be 15xxxx')

    query_str="s_sz{0},f_{0}".format(num)
    req = urllib.request.Request("http://hq.sinajs.cn/list="+query_str)
    data = urllib.request.urlopen(req).read().decode('gbk')

    fundval = re.search(r'var hq_str_f_\d{6}="(.+?)";\n', data).groups()[0].split(',');
    marketval = re.search(r'var hq_str_s_sz\d{6}="(.+?)";\n', data).groups()[0].split(',');

    return (fundval, marketval)


if __name__ == '__main__':

    num = sys.argv[1]

    fundval, marketval = sina_fund(num)
    #print(fundval)
    #print(marketval)

    lastval = float(fundval[1])
    curval = float(marketval[1])
    rate = (curval-lastval)/lastval
    
    print("{0:.2%}\t{1:.4f}\t{2:.4f}".format(rate,curval,lastval))
    print("---------")        
    if os.name == 'nt':
        os.system("pause")
    
