import zmq

import weblog
import log
from mongo import MongoStore

c = zmq.Context()
s = c.socket(zmq.REQ)
s.connect('tcp://127.0.0.1:10001')

class Machin(object):
	def __iter__(self):
		while True:
			s.send('', copy=False)
			msg2 = s.recv(copy=False)
			if msg2 == '': break
			yield str(msg2)

class Line(weblog.Lighttpd, weblog.IP2Something, weblog.UserAgent): pass

store = MongoStore()

store.bulk_insert(log.log(Line, Machin()))
