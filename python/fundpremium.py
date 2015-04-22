#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse


def sina_fund(num):

    if num[0:2] not in ('15', '16'):
        raise TypeError('Number must be 15xxxx 16xxxx')

    query_str="s_sz{0},f_{0}".format(num)
    req = urllib.request.Request("http://hq.sinajs.cn/list="+query_str)
    data = urllib.request.urlopen(req).read().decode('gbk')

    fcnt = re.search(r'var hq_str_f_\d{6}="(.+?)";\n', data)
    mcnt = re.search(r'var hq_str_s_sz\d{6}="(.+?)";\n', data)

    if fcnt is None or mcnt is None:
        raise TypeError("Number '{0}' invalid.".format(num))

    fundval = fcnt.groups()[0].split(',');
    marketval = mcnt.groups()[0].split(',');

    return (fundval, marketval)

def fund_premium_val(num):
    fval,mval = sina_fund(num)
    lastval = float(fval[1])
    curval = float(mval[1])
    rate = (curval-lastval)/lastval
    return "{0:.2%}\t{1:.4f}\t{2:.4f}\t{3},{4}".format(rate,curval,lastval,fval[0],mval[0])

def interactive_lookup():
    try:
        import readline
    except ImportError:
        pass
    while True:
        try:
            if sys.version_info[0] == 3:
                words = input('> ')
            else:
                words = raw_input('> ')
            words = words.strip()
            if len(words)==6 and re.match(r'\d{6}', words):
                try:
                    print(fund_premium_val(words))
                except TypeError as e:
                    print(e)
                    continue
            else:
                print("6 numbers only")
                continue
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            break


if __name__ == '__main__':

    if len(sys.argv) == 2:
        num = sys.argv[1]
        print(fund_premium_val(num))
    else:
        interactive_lookup()
    
    if os.name == 'nt':
        os.system("pause")

