#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3

DB = os.getenv("HOME") + "/.ibus/pinyin/user.db"

if not os.path.exists(DB):
     print "囧……似乎没有安装ibus……PT发来贺电……"
     exit(1)

# ------ Backup database file --------
import time
nowtime = time.strftime("_%Y-%m-%d-%H_%M_%S", time.localtime())
DB_BK = DB + nowtime
execute = "cp -v %s %s" % (DB, DB_BK)
os.system(execute)
print "ibus用户数据库已备份到",DB_BK


# ------ Connect to Database ---------
con = sqlite3.connect(DB)
c = con.cursor()
c.execute("""SELECT * FROM py_phrase 
            WHERE phrase IN
                (SELECT phrase 
                    FROM py_phrase 
                    GROUP BY phrase 
                    HAVING COUNT(*) = 2)""")

rows = c.fetchall()
badphrase = []

# ------ Detemine bad phrases -------
for i in range(0, len(rows), 2):
    flag = True
    phrase = rows[i:i+2]
    for j in range(1, 5):
        if phrase[0][j] != phrase[1][j]:
            flag = False
    if flag:
        badphrase.append(phrase[1])


if not len(badphrase):
    print "没有发现错误词条……PT发来贺电…… http://apt-blog.co.cc"
else:
    print "发现以下错误词条, 共%d个：" % len(badphrase)
    for row in badphrase:
        print "**[%s]**" % row[-3]
    print "\n执行优化清理……"

    # ------  Clean work to Database
    try:
        for row in badphrase:
            sql = "DELETE FROM py_phrase WHERE phrase = \"%s\" AND user_freq = %s" % (row[-3], row[-1])
            #print sql
            c.execute(sql)

        con.commit()
        print "清理完成……PT发来贺电…… http://apt-blog.co.cc"
    except sqlite3.OperationalError:
        print "清理无法完成，请先退出ibus..."

con.close()

