#!/usr/bin/python

import re
from xml.dom import minidom
f = open("data.xml", 'r')
data = f.read()
doc = minidom.parseString(data)
songs = doc.getElementsByTagName("song")
songsinfo = []
for e in songs:
    songsinfo.append(\
    [info.value for info in e.attributes.values()])
    
for p,t in songsinfo:
    print p
    print t
