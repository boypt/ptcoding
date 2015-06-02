#!/usr/bin/python3

import re
import sys
import os
import urllib.request, urllib.error, urllib.parse
import colorama
colorama.init()

from colorama import Fore, Back, Style

FUNDSHORT = {
"sxb" : "150013",
"sxa" : "150012",
"hra" : "150016",
"hrb" : "150017",
"yhwj" : "150018",
"yhrj" : "150019",
"scza" : "150022",
"sczb" : "150023",
"zz500a" : "150028",
"zz500b" : "150029",
"zz90a" : "150030",
"zz90b" : "150031",
"dlyx" : "150032",
"dljq": ("150120","150033"),
"jxwj" : "150036",
"jxjq" : "150037",
"dla" : "150039",
"dlb" : "150040",
"xfa" : "150047",
"xfb" : "150048",
"xfsy" : "150049",
"xfjq" : "150050",
"hs300a" : "150051",
"hs300b" : "150052",
"sdwj" : "150053",
"sdjq" : "150054",
"500a" : "150055",
"500b" : "150056",
"jzwj" : "150057",
"jzjj" : "150058",
"zyaj" : "150059",
"zybj" : "150060",
"tra" : "150064",
"trb" : "150065",
"hla" : "150066",
"hlb" : "150067",
"nawj" : "150073",
"najq" : "150075",
"zswj" : "150076",
"zsjq" : "150077",
"sz100a" : "150083",
"sz100b" : "150084",
"zxba" : "150085",
"zxbb" : "150086",
"jy500a" : "150088",
"jy500b" : "150089",
"wjca" : "150090",
"wjcb" : "150091",
"nd300a" : "150092",
"nd300b" : "150093",
"sx400a" : "150094",
"sx400b" : "150095",
"zya" : "150100",
"zyb" : "150101",
"hs300a" : "150104",
"hs300b" : "150105",
"zxa" : "150106",
"zxb" : "150107",
"th100a" : "150108",
"th100b" : "150109",
"gy100a" : "150112",
"gy100b" : "150113",
"fdca" : "150117",
"fdcb" : "150118",
"yhyx" : "150121",
"yhjq" : "150122",
"jx50a" : "150123",
"jx50b" : "150124",
"yya" : "150130",
"yyb" : "150131",
"dxa" : "150133",
"dxb" : "150134",
"gf100a" : "150135",
"gf100b" : "150136",
"zz800a" : "150138",
"zz800b" : "150139",
"gj300a" : "150140",
"gj300b" : "150141",
"zzaj" : "150143",
"zzbj" : "150144",
"gbsa" : "150145",
"gbsb" : "150146",
"yy800a" : "150148",
"yy800b" : "150149",
"ys800a" : "150150",
"ys800b" : "150151",
"cyba" : "150152",
"cybb" : "150153",
"jra" : "150157",
"jrb" : "150158",
"kzza" : "150164",
"kzzb" : "150165",
"yh300a" : "150167",
"yh300b" : "150168",
"hsa" : "150169",
"hsb" : "150170",
"zqa" : "150171",
"zqb" : "150172",
"tmtzza" : "150173",
"tmtzzb" : "150174",
"hga" : "150175",
"hgb" : "150176",
"zba" : "150177",
"zbb" : "150178",
"xxa" : "150179",
"xxb" : "150180",
"jga" : "150181",
"jgb" : "150182",
"hba" : "150184",
"hbb" : "150185",
"jgaj" : "150186",
"jgbj" : "150187",
"zzyx" : "150188",
"zzjq" : "150189",
"ncfhba" : "150190",
"ncfhbb" : "150191",
"dca" : "150192",
"dcb" : "150193",
"hlwa" : "150194",
"hlwb" : "150195",
"ysa" : "150196",
"ysb" : "150197",
"qsa" : "150200",
"qsb" : "150201",
"cma" : "150203",
"cmb" : "150204",
"gfa" : "150205",
"gfb" : "150206",
"dcad" : "150207",
"dcbd" : "150208",
"gqga" : "150209",
"gqgb" : "150210",
"xnca" : "150211",
"xncb" : "150212",
"gtca" : "150213",
"gtcb" : "150214",
"tmt a" : "150215",
"tmt b" : "150216",
"xnya" : "150217",
"xnyb" : "150218",
"jka" : "150219",
"jkb" : "150220",
"zhja" : "150221",
"zhjb" : "150222",
"zqaj" : "150223",
"zqbj" : "150224",
"zbaj" : "150225",
"zbbj" : "150226",
"yxa" : "150227",
"yxb" : "150228",
"ja" : "150229",
"jb" : "150230",
"dza" : "150231",
"dzb" : "150232",
"qsaj" : "150235",
"qsbj" : "150236",
"yxaj" : "150241",
"yxbj" : "150242",
"cmaj" : "150247",
"cmbj" : "150248",
"yxad" : "150249",
"yxbd" : "150250",
"msa" : "150251",
"msb" : "150252",
"yda" : "150265",
"ydb" : "150266",
"dla" : "150273",
"dlb" : "150274",
"ydya" : "150275",
"ydyb" : "150276",
"500dqa" : "502001",
"500dqb" : "502002",
"sz50a" : "502049",
"sz50b" : "502050",
"spb": ("150199","150097"),
"spa": ("150198","150096"),
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

    print("--涨幅%----当前---溢折率%----净值---日期------------名称--------------------")

    for key,vs in fund_cnt.items():
        fval,mval = vs
        fval=fval.split(',')
        mval=mval.split(',')

        netval = float(fval[1])
        curval = float(mval[1])

        netval_str = "{:.4f}".format(netval).rjust(7)
        curval_str = "{:.4f}".format(curval).rjust(7)
        rate = "{:+.2%}".format((curval-netval)/netval).rjust(7)

        curval_chg = float(mval[2])
        curval_ptg = mval[3].rjust(6)
        date = fval[4][5:]
        name = "{}{},{}".format(key,mval[0],fval[0])

        if len(name) > 35:
            name = name[35:]

        color = Style.BRIGHT + (Fore.RED if curval_chg >= 0 else Fore.GREEN)
    
        print("{}{}%  {}  {}  {} {} {}{}".format(color,curval_ptg, curval_str, rate, netval_str, date, name,Style.RESET_ALL))


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
        print('-'*76)
    else:
        interactive_lookup()
    
    if os.name == 'nt':
        os.system("pause")

