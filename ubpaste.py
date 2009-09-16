#!/usr/bin/env python
"""
upaste: Paste text and images to http://paste.ubuntu.org.cn.

Usage:
    upaste [OPTION]... [FILES]

Options:
    -l, --lang LANGUAGE  set the language used for highlighting. refer 
                         http://paste.ubuntu.org.cn for available languages.
    -i, --image FILE     screenshot image to upload.
    -n, --name NAME      poster's name.
    -h, --help           show this message.
    -e, --empty          no code to post(ignore any FILE arguments).

If FILES is - , code will be read from standard input(Press Ctrl+D to finishe.).
Ether image or code or both should prompted, or the program does nothing.
"""

import sys
import getopt

class muti_upload:
    
    data = []

    def __init__(self, boundary='----tHe[BoUnDaRy]_$'):
        self.boundary = '--' + boundary

    def add_text(self, key, value):
        self.data.append(self.boundary)
        self.data.append('Content-Disposition: form-data; name="%s"' % key)
        self.data.append('')
        self.data.append(value)

    def add_file(self, key, filename, filedata):
        import mimetypes
        self.data.append(self.boundary)
        self.data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key,filename))
        content_type = (mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        self.data.append('Content-Type: %s' % content_type)
        self.data.append('')
        self.data.append(filedata)

    def get_upload_data(self):
        if not self.data:
            return None
        if self.data[-1] != '':
            self.data.append(self.boundary + '--')
            self.data.append('')
        return "\r\n".join(self.data)

    def get_upload_header(self):
        return {'Content-Type':"multipart/form-data; boundary=%s" % self.boundary[2:]}


class ubuntu_cn_paster(muti_upload):
    
    info = {'paste':"Send",
            'code2':'',         #user codes
            'class':'bash',     #code type[for rendering]
            'poster':''         #username
            }

    snapshot_image = ''

    def __init__(self):
        muti_upload.__init__(self, '----UbP73R_$')

    def set_code(self, code):
        if code:
            self.info['code2'] = code

    def set_code_type(self, type):
        self.info['class'] = type

    def set_name(self, name):
        self.info['poster'] = name

    def set_image(self, filename):
        self.snapshot_image = filename

    def sent(self):
        import httplib
        for k,v in self.info.items():
            self.add_text(k,v)
        if self.snapshot_image != '':
            try:
                filedata = open(self.snapshot_image, 'rb').read()
            except EnvironmentError,err:
                print err
                filedata = ''

            if filedata:
                self.add_file('screenshot', self.snapshot_image, filedata)

        try: 
            conn = httplib.HTTPConnection("paste.ubuntu.org.cn")
            conn.request("POST", "/", self.get_upload_data(), self.get_upload_header())
            response = conn.getresponse()
        except httplib.HTTPException, err:
            print >> sys.stderr, err

        if response.status == 302:
            return 'http://paste.ubuntu.org.cn' + response.getheader('Location')
        else:
            return 'Error Response: ', response.status

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hel:n:i:", \
                ["help", "empty", "lang=", "name=", "image="])
    except getopt.GetoptError, err:
        print >> sys.stderr, err
        sys.exit(2)
   
    ub = ubuntu_cn_paster()
    code = ''
    read_code_from_file = True

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif opt in ("-e", "--empty"):
            read_code_from_file = False
        elif opt in ("-l", "--lang"):
            ub.set_code_type(arg)
        elif opt in ("-n", "--name"):
            ub.set_name(arg)
        elif opt in ("-i", "--image"):
            ub.set_image (arg)

    if read_code_from_file:
        if len(args):
            if args[0] == '-':
                try:
                    code = sys.stdin.read()
                except KeyboardInterrupt, err:
                    print >> sys.stderr, err
            else:
                try:
                    code = open(args[0], 'r').read()
                except EnvironmentError, err:
                    print >> sys.stderr, err
                    code = ''

            ub.set_code(code)

    if not ub.info['code2'] and not ub.snapshot_image:
        print >> sys.stderr, "Nothing to post!"
        sys.exit(1)

    print ub.sent()

if __name__ == "__main__":
    main(sys.argv[1:])
