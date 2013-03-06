#coding:utf8


resps_ascii = {
        "bot": u"我在！",
        "233": u"23333~",
        "pia": u"Pia!<(=ｏ ‵-′)ノ☆",
        }

resps_unicode = {
        u"噗": u"噗！",
        u"喵": u"喵~",
        u"你猜": u"你猜~",
        u"自己写个": u"自己写个",
        }

def botreply(raw_msg):

    msglow = raw_msg.lower()
    for k in resps_ascii.keys():
        if k in msglow:
            return k, resps_ascii[k]
    else:
        msguni = raw_msg.decode('utf-8')
        for k in resps_unicode.keys():
            if k in msguni:
                return k, resps_unicode[k]

    return None,None

