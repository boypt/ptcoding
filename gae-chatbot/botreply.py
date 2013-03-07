#coding:utf8

import random
import time
from google.appengine.api import memcache


resps_ascii = {
        "bot": lambda : random.choice((u"我在！", u"干嘛？", u"别叫我。")),
        "233": lambda : "2{0} ~".format('3' * random.randint(2, 6)),
        "pia": u"Pia!<(=ｏ ‵-′)ノ☆",
        }

resps_unicode = {
        u"噗": u"噗！",
        u"喵": lambda : random.choice((u"喵～", u"nyan ~", u"meow ~")),
        u"你猜": u"你猜~",
        u"膜拜": lambda :u"膜拜 +{0}".format(random.choice((233,10086,1024,1069))),
        u"自己写": u"自己写个",
        }

def to_response(reply):
    MEM_KEY = 'resp_time_%d' % hash(reply)
    resp_time = memcache.get(MEM_KEY)
    now = time.time()
    if resp_time is None or now - resp_time > 60:
        memcache.set(MEM_KEY, now)
        return True
    else:
        return False

def botreply(raw_msg):

    msglow = raw_msg.lower()
    for k in resps_ascii.keys():
        if k in msglow:
            v = resps_ascii[k]
            rep = v() if callable(v) else v
            if to_response(rep):
                return rep

    else:
        msguni = raw_msg.decode('utf-8')
        for k in resps_unicode.keys():
            if k in msguni:
                v = resps_unicode[k]
                rep = v() if callable(v) else v
                if to_response(rep):
                    return rep

    return None

