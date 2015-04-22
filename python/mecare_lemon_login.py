#
# Script for getting Mecare Lemon weight data via their web interface
#
#   Black box analysed from captured stream from their android client.
#

import json
import urllib
import urllib2
import hashlib
from pprint import pprint,pformat
from time import localtime, strftime

DEVNAME="test-name" #random name
TOKEN=hashlib.md5(DEVNAME).hexdigest()
ACCOUNT=raw_input("Email:")
PASSWD=hashlib.md5(raw_input('Password:')).hexdigest()

def post_process(url, data):
    post = urllib.urlencode(data)
    u = urllib2.urlopen(url, post, timeout=10)
    ret = json.load(u)
    return ret

def do_login():
    url = "http://lemon.mecare.cn/users/login"
    data = dict(token=TOKEN, uaccount=ACCOUNT, upwd=PASSWD, ptoken="12345678910", ptype="12")
    user = post_process(url, data)

    return user

def get_wdata(uid):
    url = "http://lemon.mecare.cn/wdata/data-show"
    data = dict(token=TOKEN, uid=uid)
    wdata = post_process(url, data)

    return wdata

def print_wdata(wdata):

    print "-" * 65

    for wd in wdata:
        date = wd["wdate"]
        weigh = min( [ w['value'] for w in wd["wdata"]]  )
        #print "%s,%s" % (date,weigh)
        print "{0},{1:.1f}".format(date,weigh)

def write_wdata(wdata):

    print "-" * 65
    fn = 'wdata_{0}.csv'.format(strftime("%Y-%m-%d_%H%M%S", localtime()))
    wdt =  [ "{0},{1:.1f}".format(wd["wdate"], sum( [ w['value'] for w in wd["wdata"] ] ) / len(wd["wdata"])) for wd in wdata ]
    with open(fn, 'w') as f:
        f.write("\n".join(wdt))

    print "Done. See '{0}'".format(fn)

def main():

    print TOKEN
    print ACCOUNT
    print PASSWD
    print "-" * 65

    u = do_login()
    pprint(u)

    if "msg" in u:
        print u["msg"]
    
    if "uid" in u:
        w = get_wdata(u["uid"])
        #pprint(w)
        #print_wdata(w)
        write_wdata(w)

if __name__ == "__main__":
    main()

