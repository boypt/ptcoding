#!/usr/bin/python

import sys
sys.path.append("./build/lib.linux-x86_64-2.6/")
import cytest

cytest.call_c_hello()

cytest.call_with_args("-i video.avi -ar 22050 -ab 32 -f flv -s 320x240 video.flv")
