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

	class Line(weblog.Lighttpd): pass

	store = MongoStore()
	cpt = 0
	for line in log.log(Line, sys.stdin):
		cpt +=1
		if cpt % 5000 == 0:
			print cpt
		store.insert(line.as_dict())
