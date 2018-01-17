#!/usr/bin/env python3

import requests
from pyquery import PyQuery as pq
import sys
import shutil
from os.path import basename

chrome_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36';

req_hdrs = {
    'User-Agent': chrome_ua,
    'Referer': 'http://www.waybig.com/blog/'
}


proxies = { 'http': 'http://localhost:7070' }

def main():

    if len(sys.argv) == 2:
        pg = sys.argv[1]
        url = "http://www.waybig.com/blog/page/"+pg
    else:
        url = "http://www.waybig.com/blog/"

    print("--------->\n"+url)
    print("--------->\n")
    page = requests.get(url, req_hdrs, proxies=proxies)
    content = page.content
    # with open('/tmp/men.html') as f:
    #     content = f.read()

    doc = pq(content)

    for node in doc('.entry-title'):
        # import pdb; pdb.set_trace()
        title = pq(node).text()
        link = pq(node).find('a').attr('href')
        print("Title:\n {0}\nLink: \n {1}\n\n".format(title, link))

if __name__ == '__main__':
    main()
