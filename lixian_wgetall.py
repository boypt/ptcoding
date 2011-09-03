import re
import os
import time
import subprocess
from subprocess import PIPE
import logging

LOG_FILE = "/tmp/lixian_wgetall.log"
COOKIE_FILE = os.path.expanduser("~/.lixian_cookie.txt")
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


def wget_all_lixian(html, cookies_file, output_dir, only_bturls = False, quiet = False, list_callback = None):

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

    if callable(list_callback):
        list_callback(urls)

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
            if ret in (3, 8):
                log.error("Give up '%s', may be already finished download, or something wrong with disk." % name)
            else:
                urls.append((name, url))
                log.error("will retry for %s later." % name)
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
-s  not to show names in a list after parse HTML.
"""

    page_file = None
    cookies_file = None
    output_dir = None
    only_bturls = False
    quiet = False
    show_list = True

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:c:o:bqs')

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
            elif op == "-s":
                show_list = not show_list 

        log = log_init(LOG_FILE, quiet = quiet)

        if page_file is None:
            subprocess.call(["zenity", "--info", "--text", "Copy Lixian HTML into clipboard."])
            p = subprocess.Popen(["xclip", "-selection", "c", "-o"],
                        stdout=PIPE, stderr=PIPE)
            stdo, stdi = p.communicate()
            page_html = stdo
        else:
            with open(page_file) as f:
                page_html = f.read()

        if not os.path.exists(COOKIE_FILE):
            if cookies_file is None:
                subprocess.call(["zenity", "--info", "--text", 
                    "Copy Lixian Cookies into clipboard."])
                p = subprocess.Popen(["xclip", "-selection", "c", "-o"],
                            stdout=PIPE, stderr=PIPE)
                stdo, stdi = p.communicate()
                with open(COOKIE_FILE, 'w') as f:
                    f.write(stdo)

            else:
                COOKIE_FILE =  cookies_file

        if output_dir is None:
            p = subprocess.Popen(["zenity", "--file-selection", "--directory", "--save"], 
                    stdout=PIPE, stderr=PIPE)
            stdo, stdi = p.communicate()
            output_dir = stdo.strip()

        
        if show_list:
            def show_list(urls):
                names = [u[0] for u in urls]
                args = ["zenity", "--list", "--title", "Files", "--column", "Files to Downlaod"]
                args.extend(names)
                if subprocess.call(args) == 1:
                    log.info("User Cancled download.")
                    sys.exit(0)
        else:
            show_list = None

        wget_all_lixian(page_html, COOKIE_FILE, 
                output_dir, only_bturls, quiet, list_callback = show_list)

    except (getopt.GetoptError, NameError), e:
        print e
        print help_info


