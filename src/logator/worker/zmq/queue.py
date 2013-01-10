import zmq
import sys
import time

c = zmq.Context()
s = c.socket(zmq.REP)
#s.bind('tcp://127.0.0.1:10001')
s.bind('ipc:///tmp/logator')

print "waiting for workers"
cpt = 0
chrono = time.time()
for line in sys.stdin:
    msg = s.recv(copy=False)
    s.send(line)
    cpt += 1
    if cpt % 5000 == 0:
        print cpt, 5000 / (time.time() - chrono), "lines/second"
        chrono = time.time()

while True:
    msg = s.recv(copy=False)
    s.send('')
