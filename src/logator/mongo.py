#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import weblog
import log

from pymongo import Connection
from bson.code import Code

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
			try:
				store.insert(line.as_dict())
			except Exception as inst:
				print inst
				print line.as_dict()
	else:
		print store.db.logs.count(), 'documents'
		#print "404 not found :", store.db.logs.find({'code':404}).count()
		#print "User agent :", store.db.logs.distinct('userAgent.family')
		#print "Country :", store.db.logs.distinct('ip2something.country_name')
		map_ = Code("""
			function() {
				emit(this.ip2something.country_name, {size: this.size});
			}
		""")
		reduce_ = Code("""
			function(key, values) {
				var sum = 0;
				var n = 0;
				values.forEach(function(doc) {
					sum += doc.size;
					n += 1;
				});
				return {size: sum, count: n};
			}
		""")
		result = store.db.logs.map_reduce(map_, reduce_) #limit=1000 full_response=True
		print result
		for doc in result.find():
			print doc
		#for doc in store.db.logs.find(limit=20):
			#print doc
			#print doc['url'], doc['size']
		#for log in store.db.logs.find({'code':404}):
		#	print log
