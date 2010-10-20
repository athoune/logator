#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import weblog
import log

from pymongo import Connection


class MongoStore(object):
	def __init__(self):
		connection = Connection()
		self.db = connection.test_log
	def insert(self, line):
		self.db.logs.insert(line)

if __name__ == '__main__':
	import sys
	
	store = MongoStore()

	if len(sys.argv) == 1:
		class Line(weblog.Lighttpd, weblog.IP2Something, weblog.UserAgent): pass
		cpt = 0
		for line in log.log(Line, sys.stdin):
			cpt +=1
			if cpt % 5000 == 0:
				print cpt
			store.insert(line.as_dict())
	else:
		print "404 not found :", store.db.logs.find({'code':404}).count()
		print "User agent :", store.db.logs.distinct('userAgent.family')
		print "Country :", store.db.logs.distinct('ip2something.country_name')
		#for log in store.db.logs.find({'code':404}):
		#	print log
