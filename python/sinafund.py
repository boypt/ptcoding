
#!/usr/bin/python3

import re
import sys
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

        for q in stall:
            #for n,v in enumerate(q): print (n,v)
            name = q[0]
            curval = q[1]
            date = q[4]

            print("{0} \t {1} {2}".format(curval, name, date))

        print("---------")
        
