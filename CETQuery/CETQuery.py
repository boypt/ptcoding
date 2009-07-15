#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, urllib2

def CetQuery(band, exam_id):
    """CETQuery version 0.1  2009.2.24
    
    An Exercise Program by PT, GZ University
    Author Blog: http://apt-blog.co.cc , Welcome to Drop by.
    """

    #查询连接
    cet = "http://cet.99sushe.com/cetscore_99sushe0902.html?t=" + band + "&id=" + exam_id

    print "Connecting..."

    #构造HTTP头
    header = {'Referer':'http://cet.99sushe.com/'}
    
    #第二个参数出现则使用post方式提交
    req = urllib2.Request(cet, '', header)

    try:
        data = urllib2.urlopen(req).read()
    except BaseException, e:
        print "Error retrieving data:", e
        return -1

    if not len(data):
        print "Error Occured. Maybe record not existed."
        return -1

    #解码字符串
    result = data.decode("gb2312").encode("utf8")

    res_tu = tuple(result.split(','))
    score_tu = ("听力", "阅读", "综合", "写作", "总分", "学校", "姓名")

    print "\n***** CET %s 成绩清单 *****" % (band)
    print "-准考证号: %s" % (exam_id)
    for i in range(7):
        print "-%s: %s" % (score_tu[i], res_tu[i])
    print "**************************\n"
    print "准考证号前一位同学： %s\n后两位同学分别是: %s、%s" % (res_tu[-3], res_tu[-2], res_tu[-1])

    return 0


if __name__ == "__main__":
    if (len(sys.argv) != 3) or \
        (sys.argv[1] != '4' and sys.argv[1] != '6') or \
        (len(sys.argv[2]) != 15):
        print "Error: 程序参数错误，考试类型（4、6），准考证号长度（15位）"
        print "\nExample:\n\nCETQuery.py 4 123456789012345\n\n"
        print CetQuery.__doc__
        sys.exit(1)
    
    statue = CetQuery(sys.argv[1], sys.argv[2])
    sys.exit(statue)

