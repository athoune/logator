import zmq

import weblog
import log
from mongo import MongoStore

c = zmq.Context()
s = c.socket(zmq.REQ)
#s.connect('tcp://127.0.0.1:10001')
s.connect('ipc:///tmp/logator')

class Logs(object):
    def __iter__(self):
        while True:
            s.send('', copy=False)
            line = s.recv(copy=False)
            if line == '': break
            yield str(line)

class Line(weblog.Lighttpd, weblog.IP2Something, weblog.UserAgent): pass

store = MongoStore()

store.bulk_insert(log.log(Line, Logs()))
