#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse


def sina_fund(num):
    req = urllib.request.Request("http://hq.sinajs.cn/list=%s" % num)
    data = urllib.request.urlopen(req).read().decode('gbk')
    reg = re.compile(r'var hq_str_f_\d{6}="(.+?)";\n')
    #with open('/tmp/st.txt', 'rb') as f: data = f.read().decode('gbk')
    stval = reg.findall(data)
    stall = tuple(map(lambda q:tuple(q.split(',')), stval))

    return stall




if __name__ == '__main__':

    num_fn = sys.argv[1]

    with open(num_fn, 'rb') as f:
        nums = f.read()
        num_re = re.compile(b"\d{6}")
        file_num = num_re.findall(nums)
        item_num = ",".join(map(lambda z:'f_'+z.decode('ascii'), file_num))
        stall = sina_fund(item_num)

        print("--净值-----涨幅-----昨净-----净值日期-----------基金全称-----------")

        for q in stall:
            #for n,v in enumerate(q): print (n,v)
            name = q[0]
            curval = float(q[1])
            lastval = float(q[3])
            date = q[4]
            incr = (curval-lastval)/lastval

            s_curval = "{:.4f}".format(curval).rjust(7)
            s_lastval = "{:.4f}".format(lastval).rjust(7)
            s_incr = "{:+.2%}".format(incr).rjust(7)

            print("{0}  {1}  {2}   {3} -- {4}".format(s_curval,s_incr,s_lastval,date,name))
            
        print("-"*70)
        if os.name == 'nt':
            os.system("pause")
        
