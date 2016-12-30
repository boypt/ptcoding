#!/usr/bin/env python3

import requests
from pyquery import PyQuery as pq
import sys
import shutil
from os.path import basename


req_hdrs = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Referer': 'http://www.waybig.com/blog/'
}

upld_hdrs = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Referer': 'http://www.imagebam.com/basic-upload',
    'Origin': 'http://www.imagebam.com',
    'Cookie': '__utmz=187550128.1479696868.1.1.utmccn=(direct)|utmcsr=(direct)|utmcmd=(none); IBsession=621396e45175fcf796ab80543eb92a09; __utma=187550128.1910678221.1479696868.1483059542.1483084225.10; __utmc=187550128; __utmb=187550128'
}

def main():

    url=sys.argv[1]
    print("PostUrl: \n", url)

    page = requests.get(url, req_hdrs)
    content = page.content
    # with open('/tmp/men.html') as f:
    #     content = f.read()

    doc = pq(content)

    title = doc('.entry-title').text()

    coverimg = doc('.entry-content img:first').attr('src')

    print("Title: \n", title)
    print("Coverimg Url:\n", coverimg)

    # print(" ---download coverimg")
    imgresp = requests.get(coverimg, req_hdrs , stream=True)
    text = upload(coverimg, imgresp.raw)

    print("BB Code:\n", text)

def upload(url, file_obj):
    # print(" ---post coverimg")
    imgbamresp = requests.post('http://www.imagebam.com/sys/upload/save',
        {
            'content_type': '1',
            'thumb_size':'350',
            'thumb_aspect_ratio':'resize',
            'thumb_file_type': 'jpg',
            'gallery_options': '0',
            'gallery_title':'',
            'gallery_description':'',
            'gallery_existing':'',
        },
        headers = upld_hdrs,
        files = [
            ('file[]', (basename(url), file_obj)),
        ]);

    # print(imgbamresp.content)
    # import pdb; pdb.set_trace()
    doc = pq(imgbamresp.content)
    text = doc('table textarea:first').text()

    return text

if __name__ == '__main__':
    main()
