#!/usr/bin/python


from xml.dom import minidom
import urllib, urllib2
import re
import StringIO

def getPlayListXML(uids, cookie):
    """
    Construct the cookie header and send them to the server,
    and we will get a list of the musics in the XML format.
    """
    uid = "|".join(["%s" % v for v in uids])
    playlist = urllib.urlencode([('playlist', uid)])
    player_cookie = "%s; %s" % (cookie, playlist)
    req = urllib2.Request("http://music.etgo.cn/mp3player.php")
    req.add_header('Cookie',player_cookie)

    print "Receiving File List..."
    try:
        data = urllib2.urlopen(req).read()
    except urllib2.HTTPError, e:
        print "Error... Invalid URL or Network malfunctioned.", e
        print e.read()
        
    # Filter illeagle characters.
    xmldata = data.decode("utf-8",'ignore')
    xmldata = re.sub("& ", "&amp; ", xmldata)
    
    strfile = StringIO.StringIO(xmldata.encode("utf-8"))
    
    doc = minidom.parse(strfile)
    songs = doc.getElementsByTagName("song")
    
    songsinfo = []
    for e in songs:
        songsinfo.append(\
        [info.value for info in e.attributes.values()])
    
    return songsinfo
    
if __name__ == "__main__":
#    uids = ['20274', '20275', '20276', '20277', '20278', '20279', '20280', '20281', '20282', '20283', '20284', '20285', '20286', '20287', '20288', '20289', '20290', '20291', '20292', '20293', '20294', '20295', '20296', '20297', '20298', '20299', '20300']
    uids = ['37671', '37672', '37673', '37674', '37675', '37676', '37677', '37678', '37679', '37680', '37681', '37682', '37683', '37684', '37685', '37686']
#    uids = ['40699']
    fco = open("cookie",'r')
    info = getPlayListXML(uids, fco.read())
    for p,t in info:
        print p,t
