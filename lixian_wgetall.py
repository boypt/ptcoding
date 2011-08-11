import re
import os
import time
import subprocess
import logging

LOG_FILE = "/tmp/lixian_wgetall.log"
log = None

def log_init(log_file, quiet = False):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    hdlr = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    if not quiet:
        hdlr = logging.StreamHandler()
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
    return logger


def wget_all_lixian(html, cookies_file, output_dir, only_bturls = False, quiet = False):

    urls = []

    #bt page
    urls = re.findall(
        r"<a.+?name=\"bturls\" title=\"(.+?)\".+?href=\"(.+?)\">", html)

    #normal page
    if not only_bturls:
        for id, name in re.findall(
                r'<input id="durl(\w+?)".+title="(.+)" .+', html):
            url = re.search(
                    r'<input id="dl_url%s".+value="(.*?)">' % id,
                    html).group(1)
            urls.append((name, url))

    log.info("Filter get %d links" % len(urls))
    for name, url in urls:
        if len(url) == 0:
            log.debug("Empty Link, Name: " + name)
            continue
        url = url.replace("&amp;", "&")
        cmd = ["wget", "--load-cookies", cookies_file, "-c", "-t", "5", "-O", os.path.join(output_dir, name), url]
        if quiet:
            cmd.insert(1, "-q")
        log.info("wget cmd: '%s'" % ' '.join(cmd))
        ret = subprocess.call(cmd)
        if ret != 0:
            log.debug("wget returned %d." % ret)
            if ret == 8:
                log.info("Give up %s, may be already finished download." % name)
            else:
                urls.append((name, url))
                log.debug("will retry for %s later." % name)
            continue
        else:
            log.info("Finished %s" % name)
        time.sleep(2)

if __name__ == "__main__":

    import getopt
    import sys

    help_info = """Usage:
-p  page file.
-c  cookie file.
-o  output dir.

-b  bt files only.
-q  quiet, only log to file.
"""

    bt_url = False
    quiet = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:c:o:bq')

        only_bturls = False

        for op, val in opts:
            if op == "-p":
                page_file = os.path.expanduser(val)
            elif op == "-c":
                cookies_file = os.path.realpath(os.path.expanduser(val))
            elif op == "-o":
                output_dir = os.path.expanduser(val)
            elif op == "-b":
                only_bturls = True
            elif op == "-q":
                quiet =  True

        log = log_init(LOG_FILE, quiet = quiet)
        with open(page_file) as f:
            page_html = f.read()
        wget_all_lixian(page_html, cookies_file, 
                output_dir, only_bturls, quiet)

    except (getopt.GetoptError, NameError), e:
        print e
        print help_info


