#!/usr/bin/python
#coding=utf-8
from HTMLParser import HTMLParser
import re
import sys, urllib2

class albumParser(HTMLParser):
    """
    A specified HTML parser for etgo.cn music album pages.
    """
    def reset(self):
        HTMLParser.reset(self)
        self.uid = []
        self.imgs = []
        self.album = ""
        self.info = ""
        self.intro = ""
        self.artist = ""
        self.getIntro = 0
        self.getTitle = 0
        self.getInfo = 0
        
    def handle_startendtag(self, tag, attrs):
        if tag == 'img':
            src = ""
    	    for k, v in attrs:
    	        if k == "src":
    	            src = v
    	        if k == "alt" and v == "album_name":
    	            self.imgs.append(re.sub("/small_","/",src))
    	            
        elif tag == 'input':
    	    music_list = 0
    	    for k, v in attrs:
    	        if k == 'name' and v == 'file_id[]':
    	            music_list = 1
    	        if k == 'value' and music_list:
    	            self.uid.append(v.encode("utf-8"))

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.getTitle = 1
            
        elif tag == 'div':
            for k, v in attrs:
                if k == 'class' and v == 'papers':
                    self.getIntro = 1
                elif k == 'id' and v == 'base-info':
                    self.getInfo = 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self.getTitle = 0
            
        elif tag == 'div':
            self.getIntro = 0
            self.getInfo = 0

    def handle_data(self, data):
        if self.getTitle:
            t = re.sub("\s+|->.+", "",data) #filter spaces and site name
            self.artist = re.sub(".+?-", "",t) #get the artist name
            self.album = re.sub(u"《|》|-.+", "",t) #get album name
        elif self.getIntro:
            self.intro += data
        elif self.getInfo:
            self.info += data

def getAlbumInfo(url, cookie):
    """
    Open the webpage, and feed it to the HTML parser.
    """
    req = urllib2.Request(url)
    try:
        fd = urllib2.urlopen(req)
        data = fd.read()
    except urllib2.HTTPError, e:
        print "Error...Invalid URL or Network malfunctioned.", e
        print e.read()
        raise e

    fd.close()
    parser = albumParser()
    print "Processing Album Page..."
    parser.feed(data.decode("gbk"))
    parser.close()
    
    return parser

if __name__ == "__main__":
    f = open("album3.html",'r')
    parser = albumParser()
    parser.feed(f.read())
    parser.close()
    f.close()
    print parser.uid
    print parser.album
    print parser.artist
    print parser.imgs

