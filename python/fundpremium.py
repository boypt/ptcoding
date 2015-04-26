#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse

FUNDSHORT = {
"hjetf": "518880",
"gshj": "518800",
"hst": "513660",
"hzetf": "513600",
"bp500": "513500",
"nzetf": "513100",
"dg30": "513030",
"msciag": "512990",
"jrdc": "512640",
"yyws": "512610",
"zyxf": "512600",
"500yy": "512300",
"jsyy": "512230",
"jstmt": "512220",
"jssp": "512210",
"fyetf": "512070",
"yyetf": ("512010","159929"),
"hbty": "511990",
"yhrl": "511880",
"bshb": "511860",
"yhb": ("511800","150228"),
"yha": "150227",
"ctetf": "511220",
"qzetf": "511210",
"gzetf": ("511010","159926"),
"hgetf": "510900",
"hletf": "510880",
"bqetf": "510700",
"wj380": "510680",
"yyxy": "510660",
"jrxy": "510650",
"xfxy": "510630",
"clxy": "510620",
"nyxy": "510610",
"na500": "510520",
"gf500": "510510",
"500etf": ("510500","159922"),
"180getf": "510450",
"500hs": "510440",
"50dq": "510430",
"180ewetf": "510420",
"zyetf": "510410",
"hx300": "510330",
"hs300etf": "510310",
"300etf": ("510300","159919"),
"380etf": "510290",
"ccetf": "510280",
"gqetf": "510270",
"xxetf": "510260",
"jretf": ("510230","159931"),
"zxetf": "510220",
"zzetf": "510210",
"ltetf": "510190",
"180etf": "510180",
"spetf": "510170",
"xketf": "510160",
"zpetf": "510130",
"fzetf": "510120",
"zqetf": "510110",
"zretf": "510090",
"mqetf": "510070",
"yqetf": "510060",
"50etf": "510050",
"jzetf": "510030",
"cdetf": "510020",
"zletf": "510010",
"jsyh": "505888",
"jjyf": "500058",
"jjkr": "500056",
"jjtq": "500038",
"jjhy": "184728",
"jjjj": "184722",
"jjfh": "184721",
"dzrf": "169101",
"hc300": "167901",
"mstl": "166904",
"mszl": "166902",
"pyzl": "166401",
"zoss": "166011",
"zoqz": "166008",
"zo300": "166007",
"zocc": "166006",
"zoqs": "166001",
"ndsy": "165705",
"xcsy": "165517",
"xczq": ("165516","165509"),
"xcsd": "165508",
"jxys": "165313",
"jx300": "165309",
"jytl": "164902",
"gyzy": "164815",
"gysz": "164814",
"gycz": "164810",
"gysj": "164808",
"tfhs": "164705",
"tfjh": "164702",
"thfl": "164208",
"hfqz": "164105",
"zycz": "163827",
"zysl": "163824",
"zy300e": "163821",
"zyxy": "163819",
"zyzg": "163801",
"tzhx": "163503",
"xqms": "163415",
"xqqz": "163412",
"xq300": "163407",
"xqqs": "163402",
"dmzy": "163302",
"nacz": "163210",
"nayq": "163208",
"swzq": "163112",
"cx100": "163001",
"gfjy": "162715",
"gf500l": "162711",
"gfxp": "162703",
"jszy": "162607",
"jsdy": "162605",
"hbyq": "162411",
"hfzl": "162308",
"hf100": "162307",
"sdxl": "162207",
"cjzl": "162105",
"ccjf": "162006",
"wjqz": "161911",
"wjtl": "161908",
"wjyx": "161903",
"hgfj": "161831",
"yh50a": "161821",
"yhcz": "161820",
"yhxy": "161813",
"yhnx": "161810",
"zssz": "161716",
"zsjz": "161714",
"zsxy": "161713",
"zscc": "161706",
"rttl": "161614",
"rtlx": "161610",
"rtjc": "161607",
"yhtl": "161505",
"sza": "161216",
"gtxf": "161213",
"gtxx": "161210",
"yjzz": "161119",
"yjyx": "161117",
"fgtf": ("161019","161010"),
"fgty": "161015",
"fgth": "161005",
"dccy": "160919",
"dcxp": "160918",
"yxlof": "160916",
"dcjf": "160915",
"dccx": "160910",
"csts": "160813",
"csty": "160812",
"cstf": "160810",
"cs300": "160807",
"cstz": "160805",
"zqqz": "160720",
"hshg": "160717",
"js50": "160716",
"js300": "160706",
"zxqz": "160621",
"phfz": "160618",
"phfr": "160617",
"ph500": "160616",
"ph300": "160615",
"phcx": "160613",
"phzl": "160611",
"phdl": "160610",
"phjz": "160607",
"af18": "160515",
"wjza": "160513",
"bszt": "160505",
"hxxy": "160314",
"hxlc": "160311",
"gsmy": "160220",
"gssp": "160216",
"gsjz": "160215",
"gsgz": "160212",
"gsxp": "160211",
"nfty": "160133",
"nfjl": ("160131","160128"),
"nfyl": "160130",
"nf500": "160119",
"nfgz": "160106",
"nfjp": "160105",
"qzjr": "159940",
"xxjs": "159939",
"gfyy": "159938",
"bshj": "159937",
"kxxf": "159936",
"js500": "159935",
"hjetf": "159934",
"jdetf": "159933",
"nyetf": "159930",
"xfetf": ("159928","510150"),
"a300etf": "159927",
"nf300": "159925",
"300dq": "159924",
"zxdq": "159921",
"hsetf": "159920",
"zc400": "159918",
"zxcc": "159917",
"sf60": "159916",
"cyb": "159915",
"sjz": "159913",
"s300etf": "159912",
"myetf": "159911",
"sf120": "159910",
"stmt": "159909",
"sf200": "159908",
"zx300": "159907",
"scc": "159906",
"shl": "159905",
"scetf": "159903",
"s100etf": "159901",
"tfkq": "159005",
"zskx": "159003",
"bzj": "159001",
"zqbj": "150224",
"zqaj": "150223",
"zhjb": "150222",
"zhja": "150221",
"xnyb": "150218",
"xnya": "150217",
"tmtb": "150216",
"tmta": "150215",
"gtcb": "150214",
"gtca": "150213",
"xncb": "150212",
"xnca": "150211",
"gqgb": "150210",
"gqga": "150209",
"300dcb": "150208",
"300dca": "150207",
"gfb": "150206",
"gfa": "150205",
"cmb": "150204",
"cma": "150203",
"qsb": "150201",
"qsa": "150200",
"spb": ("150199","150097"),
"spa": ("150198","150096"),
"ysb": ("150197","150132"),
"ysa": "150196",
"hlwb": "150195",
"hlwa": "150194",
"dcb": "150193",
"dca": "150192",
"ncfhbb": "150191",
"ncfhba": "150190",
"zzjq": "150189",
"zzyx": "150188",
"jgbj": "150187",
"jgaj": "150186",
"hbb": "150185",
"hba": "150184",
"jgb": "150182",
"jga": "150181",
"xxb": "150180",
"xxa": "150179",
"zbb": "150178",
"zba": "150177",
"hgb": "150176",
"hga": "150175",
"tmtzzb": "150174",
"tmtzza": "150173",
"zqb": "150172",
"zqa": "150171",
"hsb": "150170",
"hsa": "150169",
"yh300b": "150168",
"yh300a": "150167",
"kzzb": "150165",
"kzza": "150164",
"hjb": "150161",
"tfb": "150160",
"jrb": "150158",
"jra": "150157",
"zyhb": "150156",
"hfb": "150154",
"cybb": "150153",
"cyba": "150152",
"ys800b": "150151",
"ys800a": "150150",
"yy800b": "150149",
"yy800a": "150148",
"tlb": ("150147","150027"),
"300gbb": "150146",
"300gba": "150145",
"zzbj": "150144",
"zzaj": "150143",
"hlzb": "150142",
"gj300b": "150141",
"gj300a": "150140",
"zz800b": "150139",
"zz800a": "150138",
"blb": "150137",
"gf100b": ("150136","150084"),
"gf100a": ("150135","150083"),
"dxb": "150134",
"dxa": "150133",
"yyb": "150131",
"yya": "150130",
"gyzb": "150128",
"jx50b": "150124",
"jx50a": "150123",
"yhjq": "150122",
"yhyx": "150121",
"dljq": ("150120","150033"),
"fdcb": "150118",
"fdca": "150117",
"hyb": "150114",
"gy100b": "150113",
"gy100a": "150112",
"hs500b": "150111",
"hs500a": "150110",
"th100b": "150109",
"th100a": "150108",
"zxb": ("150107","159902"),
"zxa": "150106",
"ha300b": "150105",
"ha300a": "150104",
"lzb": "150102",
"zyb": "150101",
"zya": "150100",
"tq800b": "150099",
"tq800a": "150098",
"sx400b": "150095",
"sx400a": "150094",
"nd300b": "150093",
"nd300a": "150092",
"wjcb": "150091",
"wjca": "150090",
"jy500b": "150089",
"jy500a": "150088",
"zxbb": "150086",
"zxba": "150085",
"xdlb": "150082",
"sjb": "150080",
"zsjq": "150077",
"zswj": "150076",
"najq": "150075",
"nawj": "150073",
"hlb": ("150067","150021"),
"hla": ("150066","150020"),
"trb": "150065",
"tra": "150064",
"yhzyb": "150060",
"yhzya": "150059",
"jzjj": "150058",
"jzwj": "150057",
"500b": "150056",
"500a": "150055",
"sdjq": "150054",
"sdwj": "150053",
"hs300b": "150052",
"hs300a": "150051",
"xfjq": "150050",
"xfsy": "150049",
"xfb": "150048",
"xfa": "150047",
"ljb": "150042",
"dlb": "150040",
"dla": "150039",
"jxjq": "150037",
"jxwj": "150036",
"jla": "150034",
"dlyx": "150032",
"zz90b": "150031",
"zz90a": "150030",
"zz500b": "150029",
"zz500a": "150028",
"sczb": "150023",
"scza": "150022",
"yhrj": "150019",
"yhwj": "150018",
"hrb": "150017",
"hra": "150016",
"sxb": "150013",
"sxa": "150012",
"rhyj": "150009",
"rhxk": "150008",
"rfjq": "150001",
"flzb": "150129",
"yh300": "161811",
"thsc": "164205",
"yqss": "510061",

}

def guess_num(words):

    num = None

    if len(words)==6 and re.match(r'\d{6}', words):
        num = (words,)

    if words in FUNDSHORT:
        num = FUNDSHORT[words]
        if type(num) is str:
            num = (FUNDSHORT[words],)
        elif type(num) is tuple:
            num = FUNDSHORT[words]

    return num

def sina_fund(num):

    query_str = ",".join(map(lambda x:("s_sh{0},f_{0}" if x[0] == '5' else "s_sz{0},f_{0}").format(x), num))
    req = urllib.request.Request("http://hq.sinajs.cn/list="+query_str)
    data = urllib.request.urlopen(req).read().decode('gbk')

    fcnt = re.findall(r'var hq_str_f_(\d{6})="(.+?)";\n', data)
    mcnt = re.findall(r'var hq_str_s_[szh]{2}(\d{6})="(.+?)";\n', data)

    if len(fcnt)+len(mcnt) == 0:
        raise TypeError('invalid number')

    fcnt=dict(fcnt)
    mcnt=dict(mcnt)
    rst = {}

    for k in fcnt.keys():
        rst[k] = (fcnt[k],mcnt[k])

    return rst

def print_fund_val(fund_cnt):

    print("----涨幅%----当前----溢折率%----净值---净值日期------------名称--")

    for key,vs in fund_cnt.items():
        fval,mval = vs
        fval=fval.split(',')
        mval=mval.split(',')
        #import ipdb;ipdb.set_trace()

        netval = float(fval[1])
        curval = float(mval[1])

        netval_str = "{:.4f}".format(netval).rjust(7)
        curval_str = "{:.4f}".format(curval).rjust(7)
        rate = "{:+.2%}".format((curval-netval)/netval).rjust(7)

        curval_chg = mval[2].rjust(8)
        curval_ptg = mval[3].rjust(8)
        date = fval[4]
        name = "{} {}".format(mval[0],fval[0])
    
        #print("{0:+.2%}\t{1:.4f}\t{2:.4f}[{3}]\t{4},{5} ".format(rate,curval,lastval,fval[4],fval[0],mval[0]))
        print("{}%  {}  {}  {} {} -- {}".format(curval_ptg, curval_str, rate, netval_str, date, name))


def interactive_lookup():
    try:
        import readline
    except ImportError:
        pass
    while True:
        try:
            if sys.version_info[0] == 3:
                words = input('> ')
            else:
                words = raw_input('> ')
            words = words.strip()
            num = guess_num(words)
            if num is not None:
                print_fund_val(sina_fund(num))
            else:
                print("invalid input")
        except TypeError as e:
            print(e)
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            break


if __name__ == '__main__':

    if len(sys.argv) == 2:
        num = sys.argv[1]
        num = guess_num(num)
        if num is not None:
            print_fund_val(sina_fund(num))
        else:
            print("invalid input")
    else:
        interactive_lookup()
    
    if os.name == 'nt':
        os.system("pause")

