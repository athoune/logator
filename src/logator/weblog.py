#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime
import socket

import regexes
import parser

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
				infos['os-version'] = args[2]
		return infos
	def __repr__(self):
		return "<LogLine %s>" % self.datas['url']

class UserAgent(object):
	def get_userAgent(self):
		return parser.UserAgent(self.datas['user-agent'])

socket.setdefaulttimeout(2)

class HostByName(object):
	def get_hostByName(self):
		try:
			return socket.gethostbyaddr(self.datas['ip'])[0]
		except socket.herror:
			return '?'



def intOrNull(a):
	if a == '-': return None
	return int(a)

class Common(LogLine):
	def parse(self, line):
		m = RE_COMMON.match(line)
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
def combined(line):
	m = RE_COMBINED.match(line)
	if m == None:
		print line
		raise 
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

if __name__ == '__main__':
	import log
	logs = """
82.246.177.240 blog.garambrogne.net - [07/Oct/2010:21:47:19 +0200] "GET /post/2009/08/12/Trac%2C-un-bien-bel-outil HTTP/1.1" 200 19431 "http://blog.garambrogne.net/post/2009/06/29/Palette" "Mozilla/5.0 (X11; U; Linux i686; fr; rv:1.9.2.10) Gecko/20100915 Ubuntu/10.04 (lucid) Firefox/3.6.10"
66.249.65.142 blog.garambrogne.net - [07/Oct/2010:21:48:18 +0200] "GET /public/panoramique/.sous_la_passerelle_t.jpg HTTP/1.1" 200 2391 "-" "Googlebot-Image/1.0"
204.2.152.3 blog.garambrogne.net - [07/Oct/2010:21:48:58 +0200] "HEAD /post/2010/10/06/Rendre-DotClear-plus-joli-avec-php5.3-fpm-et-lighttpd HTTP/1.1" 200 0 "http://bit.ly/b5NByk" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:21:50:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:21:51:43 +0200] "GET /feed/atom HTTP/1.1" 304 0 "-" "Apple-PubSub/65.20"
66.249.65.142 blog.garambrogne.net - [07/Oct/2010:21:52:46 +0200] "GET /public/panoramique/.sous_la_passerelle_m.jpg HTTP/1.1" 200 23380 "-" "Googlebot-Image/1.0"
141.76.40.242 blog.garambrogne.net - [07/Oct/2010:21:53:35 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 200 83543 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4"
207.244.223.77 blog.garambrogne.net - [07/Oct/2010:21:55:42 +0200] "GET /index.php?feed/atom HTTP/1.1" 304 0 "-" "BlogSearch/2 +http://www.icerocket.com/"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:21:55:48 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
66.249.65.142 blog.garambrogne.net - [07/Oct/2010:21:57:14 +0200] "GET /public/panoramique/.Rue_Saint-Julien_spherique_sq.jpg HTTP/1.1" 200 1570 "-" "Googlebot-Image/1.0"
72.14.199.11 blog.garambrogne.net - [07/Oct/2010:22:00:22 +0200] "GET /index.php?feed/atom HTTP/1.1" 304 0 "-" "Feedfetcher-Google; (+http://www.google.com/feedfetcher.html; 1 subscribers; feed-id=15175022000772746345)"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:00:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:05:48 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
67.202.16.206 blog.garambrogne.net - [07/Oct/2010:22:08:30 +0200] "GET /index.php?feed/rss2/comments HTTP/1.1" 304 0 "-" "notifyBot/1.002 (+http://www.notify.me/bot)"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:22:10:41 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 304 0 "-" "Apple-PubSub/65.20"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:10:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
148.244.172.122 blog.garambrogne.net - [07/Oct/2010:22:13:29 +0200] "GET /public/voeux_2009/timbre_2009.jpg HTTP/1.1" 200 100520 "http://picsicio.us/keyword/timbre%202009/" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3"
81.56.60.246 blog.garambrogne.net - [07/Oct/2010:22:15:15 +0200] "GET /images/gnome-dev-ipod.png HTTP/1.1" 200 2496 "http://www.netvibes.com/privatepage/1" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; fr-fr) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:15:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
67.195.115.172 blog.garambrogne.net - [07/Oct/2010:22:15:55 +0200] "GET /robots.txt HTTP/1.0" 404 10232 "-" "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)"
67.195.115.172 blog.garambrogne.net - [07/Oct/2010:22:15:55 +0200] "GET /index.php?tag/python HTTP/1.0" 200 24804 "-" "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)"
67.195.115.172 blog.garambrogne.net - [07/Oct/2010:22:15:58 +0200] "GET /themes/garambrogne/style.css HTTP/1.0" 304 0 "http://blog.garambrogne.net/index.php?tag/python" "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)"
67.195.115.172 blog.garambrogne.net - [07/Oct/2010:22:16:01 +0200] "GET /themes/default/print.css HTTP/1.0" 304 0 "http://blog.garambrogne.net/index.php?tag/python" "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)"
90.8.164.162 blog.garambrogne.net - [07/Oct/2010:22:17:17 +0200] "GET /favicon.ico HTTP/1.1" 404 10252 "-" "Socialite/7157 CFNetwork/454.9.8 Darwin/10.4.0 (i386) (MacBookPro5%2C5)"
72.14.199.11 blog.garambrogne.net - [07/Oct/2010:22:19:50 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 304 0 "-" "Feedfetcher-Google; (+http://www.google.com/feedfetcher.html; 5 subscribers; feed-id=12806035431330984702)"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:20:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:22:21:43 +0200] "GET /feed/atom HTTP/1.1" 304 0 "-" "Apple-PubSub/65.20"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:25:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
141.76.40.242 blog.garambrogne.net - [07/Oct/2010:22:26:06 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 200 83543 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4"
66.249.65.142 blog.garambrogne.net - [07/Oct/2010:22:26:08 +0200] "GET /public/grenouille/ HTTP/1.1" 200 7533 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
67.195.115.172 blog.garambrogne.net - [07/Oct/2010:22:27:38 +0200] "GET /index.php?feed/tag/persisted/atom HTTP/1.0" 200 6153 "-" "Mozilla/5.0 (compatible; Yahoo! Slurp/3.0; http://help.yahoo.com/help/us/ysearch/slurp)"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:30:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
67.202.16.206 blog.garambrogne.net - [07/Oct/2010:22:34:20 +0200] "GET /index.php?feed/rss2/comments HTTP/1.1" 304 0 "-" "notifyBot/1.002 (+http://www.notify.me/bot)"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:35:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:22:40:44 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 304 0 "-" "Apple-PubSub/65.20"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:22:40:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
"""[1:-1].split("\n")

	class Line(Lighttpd, UserAgent, HostByName):
		pass
	
	for line in log.log(Line, logs, Filter_by_code([200]) | Filter_by_attribute('command', 'GET')):
		print line.url, line.userAgent.pretty(), line.os#, line.hostByName
