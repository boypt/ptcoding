import sqlite3
import json

conn = sqlite3.connect('/tmp/mecare.db')
c = conn.cursor()
c.execute('select date,datainfo from weight_table order by date;');
db = c.fetchall()
conn.close()


for date,datainfo in db:

    w = json.loads(datainfo)['datainfo']
    weight = [ l['value'] for l in w ]
    print "{0},{1}".format(date, min(weight))


