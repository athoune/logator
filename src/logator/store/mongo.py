#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import time

import weblog
import log

from pymongo import Connection
from bson.code import Code

class MongoStore(object):
    def __init__(self):
        connection = Connection()
        self.db = connection.test_log
    def insert(self, line):
        try:
            self.db.logs.insert(line)
        except Exception as inst:
            print inst
            print line
    def bulk_insert(self, lines):
        cpt = 0
        buff = []
        for line in lines:
            cpt += 1
            if cpt % 5000 == 0:
                print cpt
            if line != None:
                buff.append(line.as_dict())
            if cpt % 500 == 0:
                self.insert(buff)
                buff = []
        if len(buff) > 0:
            self.insert(buff)

if __name__ == '__main__':
    import sys

    store = MongoStore()

    if len(sys.argv) == 1:
        class Line(weblog.Lighttpd, weblog.IP2Something, weblog.UserAgent): pass
        store.bulk_insert(log.log(Line, sys.stdin))
    else:
        store.db.logs.ensure_index('code')
        print store.db.logs.count(), 'documents'
        print "codes :"
        chrono = time.time()
        for code in store.db.logs.distinct('code'):
            print "\t", code, ' :', store.db.logs.find({'code':code}).count()
        print time.time() - chrono, 's'
        #chrono = time.time()
        map_ = Code('function() { emit(this.code, {cpt:1}); }')
        reduce_ = Code('''
            function(key, values) {
                var sum = 0;
                values.forEach(function(doc){
                    sum += 1;
                });
                return {cpt:sum};
            }
        ''')
        #result = store.db.logs.map_reduce(map_, reduce_) #limit=1000 full_response=True
        #for doc in result.find():
        #    print doc
        #print time.time() - chrono, 's'
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
        #result = store.db.logs.map_reduce(map_, reduce_) #limit=1000 full_response=True
        #for doc in result.find():
        #    print doc
        #for doc in store.db.logs.find(limit=20):
            #print doc
            #print doc['url'], doc['size']
        #for log in store.db.logs.find({'code':404}):
        #    print log
