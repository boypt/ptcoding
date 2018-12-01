import sys,os,time
from progressbar import DataTransferBar
from requests_download import download, ProgressTracker
import requests,os,time,sys,re
from scrapy.selector import Selector
progress = ProgressTracker(DataTransferBar())


class wangyiyun():
    def __init__(self):
            self.headers = {
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
                 'Referer': 'http://music.163.com/'}
            self.main_url='http://music.163.com/'
            self.session = requests.Session()
            self.session.headers=self.headers

    def get_songurls(self,playlist):
            '''进入所选歌单页面，得出歌单里每首歌各自的ID 形式就是“song?id=64006"'''
            url=self.main_url+'playlist?id=%s'% playlist
            re= self.session.get(url)   #直接用session进入网页，懒得构造了
            sel=Selector(text=re.text)   #用scrapy的Selector，懒得用BS4了
            listname = sel.xpath("/html/head/meta[@property='og:title']/@content").extract()[0]
            songurls=sel.xpath('//ul[@class="f-hide"]/li/a/@href').extract()
            return listname, songurls   #所有歌曲组成的list
            ##['/song?id=64006', '/song?id=63959', '/song?id=25642714', '/song?id=63914', '/song?id=4878122', '/song?id=63650']

    def get_songinfo(self,songurl):
            '''根据songid进入每首歌信息的网址，得到歌曲的信息
            return：'64006'，'陈小春-失恋王'''
            url=self.main_url+songurl
            re=self.session.get(url)
            sel=Selector(text=re.text)
            _, song_id = songurl.split('=')
            song_name = sel.xpath("//em[@class='f-ff2']/text()").extract_first()
            singer= '_'.join(sel.xpath("//p[@class='des s-fc4']/span/a/text()").extract())
            songname=singer+'-'+song_name
            return str(song_id),songname

    def download_song(self, songurl, dir_path, idx, maxlen):
            '''根据歌曲url，下载mp3文件'''
            song_id, songname = self.get_songinfo(songurl)  # 根据歌曲url得出ID、歌名
            song_url = 'http://music.163.com/song/media/outer/url?id=%s.mp3'%song_id

            filenametpl = '{{:0{}}}_{{}}.mp3'.format(maxlen)

            path = os.path.join(dir_path, filenametpl.format(idx, songname))
            if os.path.exists(path):
                print('!! skiped: {}'.format(songname))
                return
            print("-> {}".format(songname))
            download(song_url, path, trackers=(progress,))


    def work(self, playlist, dir_path):
            listname, songurls = self.get_songurls(playlist)  # 输入歌单编号，得到歌单所有歌曲的url
            print("{}--> {} songs found.".format(listname, len(songurls)))
            dir_path = os.path.join(dir_path, listname)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            for idx, songurl in enumerate(songurls, start=1):
                self.download_song(songurl, dir_path, idx, len(str(len(songurls))))  # 下载歌曲
                time.sleep(1)

if __name__ == '__main__':
    listid = sys.argv[1]
    dir_path = sys.argv[2]
    d = wangyiyun()
    d.work(listid, dir_path)

