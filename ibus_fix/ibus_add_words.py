#!/usr/bin/python
# -*- encoding: utf-8 -*-
#phrases_converter_for_ibus version 0.9
#code by fracting
#Anyone who want to help please contact to fracting@gmail.com
#Thanks to the Developers of IBUS !

import os
import sqlite3 as sqlite
INV_PINYIN_DICT = {
1 : "a",2 : "ai",3 : "an",4 : "ang",5 : "ao",6 : "ba",7 : "bai",8 : "ban",9 : "bang",10 : "bao",11 : "bei",12 : "ben",13 : "beng",14 : "bi",15 : "bian",16 : "biao",17 : "bie",18 : "bin",19 : "bing",20 : "bo",21 : "bu",22 : "ca",23 : "cai",24 : "can",25 : "cang",26 : "cao",27 : "ce",28 : "cen",29 : "ceng",30 : "ci",31 : "cong",32 : "cou",33 : "cu",34 : "cuan",35 : "cui",36 : "cun",37 : "cuo",38 : "cha",39 : "chai",40 : "chan",41 : "chang",42 : "chao",43 : "che",44 : "chen",45 : "cheng",46 : "chi",47 : "chong",48 : "chou",49 : "chu",50 : "chuai",51 : "chuan",52 : "chuang",53 : "chui",54 : "chun",55 : "chuo",56 : "da",57 : "dai",58 : "dan",59 : "dang",60 : "dao",61 : "de",62 : "dei",63 : "den",64 : "deng",65 : "di",66 : "dia",67 : "dian",68 : "diao",69 : "die",70 : "ding",71 : "diu",72 : "dong",73 : "dou",74 : "du",75 : "duan",76 : "dui",77 : "dun",78 : "duo",79 : "e",80 : "ei",81 : "en",82 : "er",83 : "fa",84 : "fan",85 : "fang",86 : "fei",87 : "fen",88 : "feng",89 : "fo",90 : "fou",91 : "fu",92 : "ga",93 : "gai",94 : "gan",95 : "gang",96 : "gao",97 : "ge",98 : "gei",99 : "gen",100 : "geng",101 : "gong",102 : "gou",103 : "gu",104 : "gua",105 : "guai",106 : "guan",107 : "guang",108 : "gui",109 : "gun",110 : "guo",111 : "ha",112 : "hai",113 : "han",114 : "hang",115 : "hao",116 : "he",117 : "hei",118 : "hen",119 : "heng",120 : "hong",121 : "hou",122 : "hu",123 : "hua",124 : "huai",125 : "huan",126 : "huang",127 : "hui",128 : "hun",129 : "huo",130 : "ji",131 : "jia",132 : "jian",133 : "jiang",134 : "jiao",135 : "jie",136 : "jin",137 : "jing",138 : "jiong",139 : "jiu",140 : "ju",141 : "juan",142 : "jue",143 : "jun",144 : "ka",145 : "kai",146 : "kan",147 : "kang",148 : "kao",149 : "ke",150 : "kei",151 : "ken",152 : "keng",153 : "kong",154 : "kou",155 : "ku",156 : "kua",157 : "kuai",158 : "kuan",159 : "kuang",160 : "kui",161 : "kun",162 : "kuo",163 : "la",164 : "lai",165 : "lan",166 : "lang",167 : "lao",168 : "le",169 : "lei",170 : "leng",171 : "li",172 : "lia",173 : "lian",174 : "liang",175 : "liao",176 : "lie",177 : "lin",178 : "ling",179 : "liu",180 : "lo",181 : "long",182 : "lou",183 : "lu",184 : "luan",185 : "lue",186 : "lun",187 : "luo",188 : "lv",189 : "lve",190 : "ma",191 : "mai",192 : "man",193 : "mang",194 : "mao",195 : "me",196 : "mei",197 : "men",198 : "meng",199 : "mi",200 : "mian",201 : "miao",202 : "mie",203 : "min",204 : "ming",205 : "miu",206 : "mo",207 : "mou",208 : "mu",209 : "na",210 : "nai",211 : "nan",212 : "nang",213 : "nao",214 : "ne",215 : "nei",216 : "nen",217 : "neng",218 : "ni",219 : "nian",220 : "niang",221 : "niao",222 : "nie",223 : "nin",224 : "ning",225 : "niu",226 : "ng",227 : "nong",228 : "nou",229 : "nu",230 : "nuan",231 : "nue",232 : "nuo",233 : "nv",234 : "nve",235 : "o",236 : "ou",237 : "pa",238 : "pai",239 : "pan",240 : "pang",241 : "pao",242 : "pei",243 : "pen",244 : "peng",245 : "pi",246 : "pian",247 : "piao",248 : "pie",249 : "pin",250 : "ping",251 : "po",252 : "pou",253 : "pu",254 : "qi",255 : "qia",256 : "qian",257 : "qiang",258 : "qiao",259 : "qie",260 : "qin",261 : "qing",262 : "qiong",263 : "qiu",264 : "qu",265 : "quan",266 : "que",267 : "qun",268 : "ran",269 : "rang",270 : "rao",271 : "re",272 : "ren",273 : "reng",274 : "ri",275 : "rong",276 : "rou",277 : "ru",278 : "ruan",279 : "rui",280 : "run",281 : "ruo",282 : "sa",283 : "sai",284 : "san",285 : "sang",286 : "sao",287 : "se",288 : "sen",289 : "seng",290 : "si",291 : "song",292 : "sou",293 : "su",294 : "suan",295 : "sui",296 : "sun",297 : "suo",298 : "sha",299 : "shai",300 : "shan",301 : "shang",302 : "shao",303 : "she",304 : "shei",305 : "shen",306 : "sheng",307 : "shi",308 : "shou",309 : "shu",310 : "shua",311 : "shuai",312 : "shuan",313 : "shuang",314 : "shui",315 : "shun",316 : "shuo",317 : "ta",318 : "tai",319 : "tan",320 : "tang",321 : "tao",322 : "te",323 : "tei",324 : "teng",325 : "ti",326 : "tian",327 : "tiao",328 : "tie",329 : "ting",330 : "tong",331 : "tou",332 : "tu",333 : "tuan",334 : "tui",335 : "tun",336 : "tuo",337 : "wa",338 : "wai",339 : "wan",340 : "wang",341 : "wei",342 : "wen",343 : "weng",344 : "wo",345 : "wu",346 : "xi",347 : "xia",348 : "xian",349 : "xiang",350 : "xiao",351 : "xie",352 : "xin",353 : "xing",354 : "xiong",355 : "xiu",356 : "xu",357 : "xuan",358 : "xue",359 : "xun",360 : "ya",361 : "yan",362 : "yang",363 : "yao",364 : "ye",365 : "yi",366 : "yin",367 : "ying",368 : "yo",369 : "yong",370 : "you",371 : "yu",372 : "yuan",373 : "yue",374 : "yun",375 : "za",376 : "zai",377 : "zan",378 : "zang",379 : "zao",380 : "ze",381 : "zei",382 : "zen",383 : "zeng",384 : "zi",385 : "zong",386 : "zou",387 : "zu",388 : "zuan",389 : "zui",390 : "zun",391 : "zuo",392 : "zha",393 : "zhai",394 : "zhan",395 : "zhang",396 : "zhao",397 : "zhe",398 : "zhen",399 : "zheng",400 : "zhi",401 : "zhong",402 : "zhou",403 : "zhu",404 : "zhua",405 : "zhuai",406 : "zhuan",407 : "zhuang",408 : "zhui",409 : "zhun",410 : "zhuo"
              }
   
   
db_in=sqlite.connect('/usr/share/ibus-pinyin/engine/py.db')
cur_in=db_in.cursor()

homedir=os.environ['HOME']
dbname=homedir+'/.ibus/pinyin/user.db'
# dbname='/home/fracting/.ibus/pinyin/user.db'# for test
db_out=sqlite.connect(dbname)
cur_out=db_out.cursor()

filename=raw_input('Please input the filename of the phrase table\n such as: /home/your_account/phrase.txt \n')
# filename='/home/fracting/1.txt' # for test
filename = "/home/pentie/Desktop/ch.txt"
f=file(filename,'r')


record_num=0
py_db_num=0
user_db_num=0
error_num=0
pinyin=[]
while True:
  record=['','','','','','','','','','','','','']
  line = f.readline()
  l=len(line)-1
  phrase=line[0:l]
  if l == -1: # Zero length indicates EOF
    break
  elif l==0:
    continue
  else:
    cur_in.execute('select * from py_phrase where phrase=?',[phrase])
    exist1=cur_in.fetchone()
    cur_out.execute('select * from py_phrase where phrase=?',[phrase])
    exist2=cur_out.fetchone()
    if exist1 == None and exist2 == None: #判断短语是否已存在
      record_num +=1
      record[0]=l/3
      record[10]=phrase
      record[12]=1
      yx=[]
      for i in range(0,l/3):
        cur_in.execute('select * from py_phrase  where phrase =?',[phrase[i*3:i*3+3]])
        pinyin=cur_in.fetchall()
        if pinyin == []:
          record_num -= 1
          error_num +=1
          break
        if i<4 :
          record[i+1]=pinyin[0][1]
          record[i+6]=pinyin[0][6]
        else:
          yx.append(INV_PINYIN_DICT[pinyin[0][1]])
      record[5]="'".join(yx)
      if pinyin == []:
        print phrase
        continue
      cur_out.execute('insert into py_phrase values (?,?,?,?,?,?,?,?,?,?,?,?,?)',record)
    elif exist1 !=None:
      py_db_num +=1
    elif exist2 !=None:
      user_db_num +=1   

       
cur_in.close()
db_out.commit()
cur_out.close()
f.close()


print py_db_num ,"phrases are already included in py.db"
print user_db_num ,"phrases are already included in user.db"
print record_num ,"new phrases have been imported to user.db"
print error_num ,"phrases can't be imported to user.db since some words of those phrases are not exist in py.db"

