#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
http://www.faqs.org/rfcs/rfc3164.html
"""

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

levels = [
	"emerg",
	"alert",
	"crit",
	"err",
	"warning",
	"notice",
	"info",
	"debug"
]

facilities = [
	"kernel messages",
	"user-level messages",
	"mail system",
	"system daemons",
	"security/authorization messages",
	"messages generated internally by syslogd",
	"line printer subsystem",
	"network news subsystem",
	"UUCP subsystem",
	"clock daemon",
	"security/authorization messages",
	"FTP daemon",
	"NTP subsystem",
	"log audit",
	"log alert",
	"clock daemon",
	"local use 0",
	"local use 1",
	"local use 2",
	"local use 3",
	"local use 4",
	"local use 5",
	"local use 6",
	"local use 7"
]

class SyslogInput(DatagramProtocol):
	"""
	Syslog UDP listener
	"""
	def processLine(self, level, facility, month, day, hour, host, msg):
		"""
		One line of log
		override me !
		"""
		print "\x1b[31m%s\x1b[39;49;00m\x1b[32m@%s\x1b[39;49;00m [\x1b[33m%s\x1b[39;49;00m] %s" % (levels[level], host, facilities[facility], msg)
	def datagramReceived(self, data, (host, port)):
		n = data.find(">")
		a = int(data[1:n])
		level = a & 0b00000111
		facility = (a & 0b01111000) / 8
		(month, day, hour, host, msg) = data[n+1:].split(' ', 4)
		self.processLine(level, facility, month, day, hour, host, msg)

if __name__ == '__main__':
	reactor.listenUDP(514, SyslogInput())
	reactor.run()