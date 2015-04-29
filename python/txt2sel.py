#!/usr/bin/python3
'''
同花顺自选股文件格式：

0000000: 0900 0721 3030 3039 3731 0711 3630 3036  ...!000971..6006
0000010: 3738 0721 3030 3231 3134 0721 3030 3232  78.!002114.!0022
0000020: 3336 0721 3330 3031 3034 0711 3630 3031  36.!300104..6001
0000030: 3133 0711 3630 3033 3638 0711 3630 3032  13..600368..6002
0000040: 3030 0711 3630 3030 3630 0a              00..600060.

0x00-0x07 自选股个数
0x08-0x0F NULL(分隔符)
0x10-0x17 '\x07'(分隔符)
0x18-0x1F 市场代码: '\x21'(上海) | '\x11'(深圳)
0x20-0x4F 证券代码
0x50-0x57 '\x07'(分隔符)
0x58-0x5F 市场代码: '\x21'(上海) | '\x11'(深圳)
0x60-0x8F 证券代码
......

'''


import re
import sys
import os


if __name__ == '__main__':

    num_in = sys.argv[1]
    num_out = sys.argv[2]

    market = {
        "6":b"\x21",
        "9":b"\x21",
        "5":b"\x21",
        "0":b"\x11",
        "2":b"\x11",
        "3":b"\x11",
        "1":b"\x11",
    }
    

    with open(num_in, 'rb') as f:
        nums = f.read().decode('ascii', 'ignore')
        num_re = re.compile(r"\d{6}")
        file_num = num_re.findall(nums)


    with open(num_out, 'wb') as f:
        count = len(file_num)
        f.write(chr(count).encode('ascii')+b'\x00')
        for num in file_num:
            f.write(b'\x07' + market[num[0]] + num.encode('ascii'))


