#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime
import socket

import regexes
import parser

import ip2something

from logator.log import InvalidLog

RE_COMMON = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (\d+)', re.U)
RE_COMBINED = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (.*?) "([^"]*)" "([^"]*)"', re.U)
RE_LIGHTY = re.compile('(.*?) (.*?) - \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (.*?) "([^"]*)" "([^"]*)"', re.U)
RE_OS = re.compile('(.*?) \((.*?)\)', re.U)
RE_MOZILLA = re.compile('.*? \((.*?); U; (.*?);', re.U)

class LogLine(object):
	def __init__(self, line):
		self.datas = self.parse(line)
		self._cache = {}
	def __getattr__(self, name):
		if name in self.datas:
			return self.datas[name]
		if name not in self._cache:
			self._cache[name] = self.__getattribute__("get_%s" % name).__call__()
		return self._cache[name]
			
	def get_os(self):
		m = RE_OS.match(self.datas['user-agent'])
		infos = {}
		if m != None:
			args = m.group(2).split('; ')
			if len(args) > 1 and args[1] == 'U':
				infos['os'] = args[0]
				if len(args) > 2:
					infos['os-version'] = args[2]
		return infos
	def __repr__(self):
		return "<LogLine %s>" % self.datas['url']
	def as_dict(self):
		d = self.datas
		for k in dir(self):
			if k[:4] == 'get_':
				d[k[4:]] = self.__getattr__(k[4:])
		return d

class UserAgent(object):
	def get_userAgent(self):
		p = parser.UserAgent(self.datas['user-agent'])
		return {
			'family' : p.family,
			'v1' : p.v1,
			'v2' : p.v2,
			'v3' : p.v3
		}

socket.setdefaulttimeout(2)

class HostByName(object):
	def get_hostByName(self):
		try:
			return socket.gethostbyaddr(self.datas['ip'])[0]
		except socket.herror:
			return '?'

ip2 = None
class IP2Something(object):
	def get_ip2something(self):
		global ip2
		if ip2 == None:
			ip2 = ip2something.Index('ip_group_city.csv')
		data = ip2.search(self.datas['ip'])
		data['loc'] = [data['latitude'], data['longitude']]
		del data['latitude']
		del data['longitude']
		return data

def intOrNull(a):
	if a == '-': return None
	return int(a)

class Common(LogLine):
	def parse(self, line):
		m = RE_COMMON.match(line)
		if m == None:
			raise InvalidLog()
		return {
		'ip':     m.group(1),
		'user':   m.group(2),
		'date':   datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
		'command':m.group(4),
		'url':    m.group(5),
		'http':   m.group(6),
		'code':   int(m.group(7)),
		'size':   int(m.group(8))
		}
class Combined(LogLine):
	def parse(self, line):
		m = RE_COMBINED.match(line)
		if m == None:
			raise InvalidLog()
		return {
		'ip':     m.group(1),
		'user':   m.group(2),
		'date':   datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
		'command':m.group(4),
		'url':    m.group(5),
		'http':   m.group(6),
		'code':   int(m.group(7)),
		'size':   intOrNull(m.group(8)),
		'referer':m.group(9),
		'user-agent':m.group(10)
		}
class Lighttpd(LogLine):
	def parse(self, line):
		m = RE_LIGHTY.match(line)
		if m == None:
			raise InvalidLog()
		return {
		'ip':     m.group(1),
		'domain': m.group(2),
		'date':   datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
		'command':m.group(4),
		'url':    m.group(5),
		'http':   m.group(6),
		'code':   int(m.group(7)),
		'size':   intOrNull(m.group(8)),
		'referer':m.group(9),
		'user-agent':m.group(10)
		}


class MetaFilter:
	def __init__(self, filter_):
		self.filters = [filter_]
	def append(self, other):
		self.filters.append(other)
	def __or__(self,other):
		self.append(other)
		return self
	def __call__(self, data):
		for filter_ in self.filters:
			data = filter_.__call__(data)
			if data == None: return None
		return data

class Filter(object):
	def __or__(self, other):
		meta = MetaFilter(self)
		meta.append(other)
		return meta

class Filter_by_attribute(Filter):
	def __init__(self, key, value):
		self.key = key
		self.value = value
	def __call__(self, logline):
		if logline.__getattr__(self.key) in self.value:
			return logline

class Filter_by_code(Filter_by_attribute):
	def __init__(self, codes = [404]):
		self.key = 'code'
		self.value = codes

class Filter_by_error(Filter_by_code):
	def __init__(self):
		Filter_by_code.__init__(self, [403, 404, 500, 501, 502])

class Filter_by_domain(Filter):
	def __init__(self, domain=['net']):
		self.domain = domain
	def __call__(self, logline):
		if logline.hostByName.split('.')[-1] in self.domain:
			return logline
