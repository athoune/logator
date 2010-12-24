#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

class LazyDict(object):
	def __init__(self):
		self.datas = {}
		self._cache = {}
	def __getattr__(self, name):
		if name in self.datas:
			return self.datas[name]
		if name not in self._cache:
			self._cache[name] = self.__getattribute__("get_%s" % name).__call__()
		return self._cache[name]

class InvalidLog(Exception): pass

def log(parser, reader, filter_ = None):
	for line in reader:
		if filter_ == None:
			yield parser.__call__(line)
		else:
			try:
				tmp = filter_.__call__(parser.__call__(line))
			except InvalidLog:
				print "oups"
			if tmp != None: yield tmp

