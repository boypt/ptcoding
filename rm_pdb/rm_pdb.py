#!/usr/bin/env python

import socket
import sys
import threading
import pdb as _pdb

def server(addr = 'localhost', port = 18964):
    
    def __output(conn):
        while True:
            try:
                data = conn.recv(1024)
                if not data:break
                sys.stdout.write(data)
                sys.stdout.flush()
            except socket.error:
                print "Connection close."
                break
            except:
                break

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((addr, port))
    sock.listen(1)

    print "Remote Pdb listening at %s:%d\n" % (addr, port)

    try:
        conn, addr = sock.accept()
    except KeyboardInterrupt:
        sys.exit(0)

    print "Connect from %s\n" % str(addr)

    threading.Thread(target = __output, args = (conn,)).start()
    
    try:
        while 1:
            i = sys.stdin.readline()
            conn.sendall(i)
    except socket.error:
        print "Connection close."
    finally:
        conn.close()

def pdb(addr = 'localhost', port = 18964):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))

    return _pdb.Pdb(stdin = sock.makefile('r+', 0), stdout = sock.makefile('w+', 0))


