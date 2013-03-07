#coding:utf8

import random


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

def botreply(raw_msg):

    msglow = raw_msg.lower()
    for k in resps_ascii.keys():
        if k in msglow:
            v = resps_ascii[k]
            return v() if callable(v) else v
    else:
        msguni = raw_msg.decode('utf-8')
        for k in resps_unicode.keys():
            if k in msguni:
                v = resps_unicode[k]
                return v() if callable(v) else v

    return None

