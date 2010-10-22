import zmq
import sys

import mongo
import weblog
import log

c = zmq.Context()
s = c.socket(zmq.REP)
s.bind('tcp://127.0.0.1:10001')

class Line(weblog.Lighttpd, weblog.IP2Something, weblog.UserAgent): pass

l = iter(sys.stdin)

print "waiting for workers"
cpt = 0
while True:
	cpt += 1
	if cpt % 5000 == 0:
		print cpt
	msg = s.recv(copy=False)
	try:
		s.send(l.next())
	except StopIteration:
		s.send('')
		break

