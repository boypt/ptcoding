#!/usr/bin/python

import sys
sys.path.append("build/lib.linux-x86_64-2.6/") #Take care this path, different system and version of python have diff directories.
import looptest
import thread
import threading
import time
import signal

end = 0

class c_loop_thread(threading.Thread):
    def run(self):
        looptest.c_loop()

class cy_loop_thread(threading.Thread):
    def run(self):
        looptest.cy_loop()

class py_loop_thread(threading.Thread):
    def run(self):
        global end
        while not end:
            print "Print from Python loop"
            time.sleep(1)
        print "Python loop ENDED"




t0 = py_loop_thread()
t1 = c_loop_thread()
t2 = cy_loop_thread()
t0.start()
t1.start()
t2.start()


try:
    signal.pause()
except KeyboardInterrupt:
    end = 1
    looptest.set_end(end)

t0.join()
t1.join()
t2.join()



