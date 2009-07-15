使用方法：终端内运行 ./PyETGO.py -a http://..... -u user -p password

    -a, --album=        An album page URL. MUST Given.
                                要下载的专辑页面地址URL。必须给定。
                                
    -u, --username=     A valid account of ETGO.CN. 
    -p, --password=     MUST Given for the first time.
                                一个可用的ETGO账户。首次使用必须给定。

专辑页面地址必须是http://music.etgo.cn/上的一个音乐专辑，帐号可免费在网站申请。

本脚本可跨平台使用，在Win下需要wget for Windows， 把wget.exe放在脚本所在目录即可。

Wget下载：http://www.interlog.com/~tcharron/wgetwin-1_5_3_1-binary.zip

更新：

v0.3
2009.03.16
    -对获取的XML列表中存在的非法字符进行过滤（解决曲名含"&"等不规则字符导致无法下载）

v0.2
2009.03.11  
    -为在Win下使用本脚本，全部使用Unicode的字符串来提示（0.1有部分乱码）
    -修改写入Intro.txt文件的方法，使用writelines，会根据操作系统不同写入不同换行符，减少乱码
    -写入文件名前过滤Win下的非法文件名字符/\:<>?|等
    
v0.1
2009.03.10
    首次实现以下功能：
   -下载http://music.etgo.cn/上的任意专辑的音乐文件
   -专辑的存放目录命名为“歌手名 - 专辑名”
   -多CD的专辑，音乐文件命名为“CD号-轨号_歌手 - 歌名”，单CD则为“轨号_歌手 - 歌名”
   -下载专辑的封面和封底文件cover.jpg、coverback.jpg
   -从页面中抽出的专辑信息和介绍文字写入Intro.txt
   -首次使用需要用-u和-p输入一个ETGO账户以获取Cookie，以后下载只需用-a指定一个专辑的页面
   -下载时可随时使用Ctrl + C中断，重新下载时自动从断点续传。
