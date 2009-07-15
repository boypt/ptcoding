#!/usr/bin/python

import sqlite3

con = sqlite3.connect('/usr/share/ibus-pinyin/engine/py.db')
c = con.cursor()

diclib = open("Freq/SogouLabDic.dic",'r')
rec_notexist = open('notexist','w')

seachCounter = 0
notExistCounter = 0

while 1:
    line = diclib.readline()
    if not len(line):
        break
    data = line.split('\t')
    try:
        phrase = data[0].decode("gbk")
        
        c.execute("select *\
            from py_phrase\
            where phrase = ?", [phrase.encode('utf-8')])

        rows = c.fetchall()
        seachCounter += 1
    except UnicodeDecodeError, e:
        print e
        print data[0]
        rec_notexist.writelines(line)
        continue
    except BaseException, e:
        print e
        break

    if not rows:
        notExistCounter += 1
        rec_notexist.writelines(line)
        print phrase

print "Seached: %d times. %d phrases not in the database, \n \
written in file 'notexist'" %(seachCounter, notExistCounter)

rec_notexist.close()
diclib.close()
con.close()
