#!/usr/bin/python

import os
import sys
import urllib2


def getCookie(username, password):
    """
    This function gets the cookie of loginning etgo.cn.
    If never login before, this will sent login request
    and sotre the cookie info in file "cookie", which 
    will be read directly from the file next time.
    """
    cookie = ""
    
    def getNewWebCookie():
        if username == "" or password == "":
            print "Error...Need Account to Login."
            sys.exit(1)
        print "Read Cookie from Site..."
        ref_head = {'Referer':'http://music.etgo.cn/'}
        login_post = "username=%s&password=%s&action=dologin&cookietime=3600" % (username, password)
        login_req = urllib2.Request("http://member.etgo.cn/member.php",login_post,ref_head)
        info = urllib2.urlopen(login_req).info()
        cookie = info['set-cookie']

        return cookie

    if not os.path.exists("cookie"):
        cookie = getNewWebCookie()       
    else:
        print "Read Cookie from File..."
        cookiefile = open("cookie",'r')
        cookie = cookiefile.readline()
        cookiefile.close()
        if len(cookie) < 50:
            print "Error...Invalid Cookie File."
            os.remove("cookie")
            cookie = getNewWebCookie()

    if len(cookie) < 50:
        print "Error...Login Denied. Please Check Your Account."         
        cookie = ""
    else:
        cookiefile = open("cookie",'w')
        cookiefile.write(cookie)
        cookiefile.close()

    return cookie

if __name__ == "__main__":
    u,p = sys.argv[1:]
    c = getCookie(u, p)
    print c
