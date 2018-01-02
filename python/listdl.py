#!/usr/bin/env python3

import threading
import urllib.request, urllib.parse, json 

threads = []

def parseindex(src):
    with urllib.request.urlopen(src) as url:
        data = json.loads(url.read().decode())
        for item in data:
            item_uri = "{0}{1}".format(src, urllib.parse.quote(item['name']))
            if item['type'] == 'file' and item['size'] > 1024*1024:
                print(item_uri)
            elif item['type'] == 'directory':
                t = threading.Thread(target=parseindex, args=(item_uri+'/',))
                t.start()
                threads.append(t)
                #parseindex()

    print("  ")




if __name__ == "__main__":
    
    rooturi = "https://"+"lit"+".ptsang."+"net"+":8443/"+"dl/"

    t = threading.Thread(target=parseindex, args=(rooturi,))
    t.start()
    threads.append(t)

    for t in threads:
        t.join()

