#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
    PyETGO - 0.3   2009.03.16
    
    A Python Script for Downloading albums from music.etgo.cn
     with given page URL.
    
    -h, --help          Show this help message.
                        显示本帮助。
                                
    -a, --album=        An album page URL. MUST Given.
                        要下载的专辑页面地址URL。必须给定。
                                
    -u, --username=     A valid account of ETGO.CN. 
    -p, --password=     MUST Given for the first time.
                        一个可用的ETGO账户。首次使用必须给定。
    
    
    An exercise work by apt-blog.co.cc PT.
    Blog: http://apt-blog.co.cc
    Twitter: BOYPT
"""
import sys
import urllib2
import os
import re
import getopt

from getAlbum import getAlbumInfo
from getCookie import getCookie
from getPlayListXML import getPlayListXML
    
def downloadFile(url, cookie, filename):
    """
    Download a file using wget, with cookie, and the given filename.
    """
    command = u"wget -c --header=\"Cookie: %s\" -O \"%s\" %s"\
                % (cookie, filename, url)
    execute = command.encode(sys.getfilesystemencoding())
    return os.system(execute)

def constructFileName(listInfo, artist):
    """
    Construct all the file names with infomation
    form the URL and the title.
    The file name various while the album has mutiple CD or
    a single CD, judged by the URL.
    """

    muti_CD = 0
    for item in listInfo:
        cd = re.sub(".+?cd|/.+", "", item[0])
        if cd != '1':
            muti_CD = 1
            break

    for item in listInfo:
        p, t = item
        
        track = re.sub(".+_|\.mp3", "", p)
        sufix = re.sub(".+\.", "", p)
        if muti_CD:
            cd = re.sub(".+?cd|/.+", "", p)
            filename = u"%s-%s_%s - %s.%s" % (cd, track, artist, t, sufix)
        else:
            filename = u"%s_%s - %s.%s" % (track, artist, t, sufix)

        filename = re.sub("[/\\:*?\"<>|]", "_", filename) #filter illegal symble
        item[1] = filename


def main(album, username, password):
    """
    Parse album infomation from web page. Then download them 
    with permission from the user.
    """
    try:
        cookie = getCookie(username, password)
        if len(cookie) == 0:
            print "Error...Cookie."
            sys.exit(1)
        parsedInfo = getAlbumInfo(album, cookie)
        musicList = getPlayListXML(parsedInfo.uid, cookie)
    except BaseException, e:
        print e
        sys.exit(1)
        
    #Make filename for each music, replace the title in the list
    constructFileName(musicList, parsedInfo.artist)

    #Code for local command executing
    code = sys.getfilesystemencoding()
    
    #Location of the files
    albumDirectory = "%s/%s - %s/" % (os.getcwd() ,parsedInfo.artist ,parsedInfo.album)

    print u"""
*************************************************
将要下载专辑：
Album to Download:
%s

专辑信息：
Album Info. :
%s
 
存放路径：
Storage Location:
%s
*************************************************
    """ % (parsedInfo.album, parsedInfo.info, albumDirectory)
    
    #Ask for permission
    while 1:
        print u"Sure to Download? 确认下载？(y/n)"
        ans = sys.stdin.readline()
        if 'y' in ans:
            break
        elif 'n' in ans:
            sys.exit(0)

    #Prepare the album directory
    if not os.path.exists(albumDirectory):
        os.makedirs(albumDirectory, 0755)
   
    #Download CD covers
    for img in parsedInfo.imgs:
        #Create file 'cover.jpg' and 'coverback.jpg'
        name = albumDirectory + re.sub(".+/|[\d_]+", "", img)  
        if downloadFile(img, cookie, name) != 0:
            print u"Download Interrupted. 下载终止。 "
            break    

    #Make the introduction file
    path = albumDirectory + "Intro.txt"
    text = parsedInfo.info + parsedInfo.intro
    writefile = open(path, 'w')
    writefile.writelines(text.encode(code))
    writefile.close()

    
    #Download all the music
    for path, filename in musicList:
        name = albumDirectory + filename
        print filename
        if downloadFile(path, cookie, name) != 0:
            print u"Download Interrupted. 下载终止。"
            break


if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "ha:u:p:", \
                ["help", "album=", "username=", "password="])
    except getopt.GetoptError:
        print __doc__
        sys.exit(2)

    if not len(opts):
        print __doc__
        sys.exit(2)

    album = ""
    username = ""
    password = ""
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif opt in ("-a", "album="):
            album = arg
            if not re.match("http://music.etgo.cn/album/\d+?/index.html", album):
                print u"It seemed an invalid ETGO album page UTL. 非ETGO专辑页面地址：",album
                sys.exit(1) 
        elif opt in ("-u","--username="):
            username = arg
        elif opt in ("-p","--password="):
            password = arg
   
    main(album, username, password)
