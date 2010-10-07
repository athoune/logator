#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime

import regexes
import parser

RE_COMMON = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (\d+)', re.U)
RE_COMBINED = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (.*?) "([^"]*)" "([^"]*)"', re.U)
RE_LIGHTY = re.compile('(.*?) (.*?) - \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (.*?) "([^"]*)" "([^"]*)"', re.U)
RE_OS = re.compile('(.*?) \((.*?)\)', re.U)
RE_MOZILLA = re.compile('.*? \((.*?); U; (.*?);', re.U)

def common(line):
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
def intOrNull(a):
	if a == '-': return None
	return int(a)
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
		'user-agent':userAgent.match(m.group(10))
		}
def lighttpd(line):
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
def os(ua):
	m = RE_OS.match(ua)
	infos = {}
	if m != None:
		args = m.group(2).split('; ')
		if args[1] == 'U':
			infos['os'] = args[0]
			infos['os-version'] = args[2]
	return infos

if __name__ == '__main__':
	import log
	logs = """
141.76.40.242 blog.garambrogne.net - [07/Oct/2010:20:16:05 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 200 83543 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:20:20:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:20:21:27 +0200] "GET /feed/atom HTTP/1.1" 304 0 "-" "Apple-PubSub/65.20"
72.14.199.11 blog.garambrogne.net - [07/Oct/2010:20:24:31 +0200] "GET /index.php?feed/rss2 HTTP/1.1" 304 0 "-" "Feedfetcher-Google; (+http://www.google.com/feedfetcher.html; 5 subscribers; feed-id=12806035431330984702)"
178.79.135.218 blog.garambrogne.net - [07/Oct/2010:20:25:47 +0200] "HEAD / HTTP/1.1" 200 0 "-" "Mozilla/5.0 (compatible; Wasitup monitoring; http://wasitup.com)"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:20:26:49 +0200] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; fr-fr) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:20:26:50 +0200] "GET /themes/garambrogne/js/jquery.mousewheel.min.js HTTP/1.1" 304 0 "http://blog.garambrogne.net/" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; fr-fr) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:20:26:50 +0200] "GET /themes/garambrogne/style.css HTTP/1.1" 304 0 "http://blog.garambrogne.net/" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; fr-fr) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:20:26:50 +0200] "GET /themes/garambrogne/js/pano.js HTTP/1.1" 304 0 "http://blog.garambrogne.net/" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; fr-fr) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
82.227.122.98 blog.garambrogne.net - [07/Oct/2010:20:26:52 +0200] "GET /themes/garambrogne/img/retrolien.png HTTP/1.1" 304 0 "http://blog.garambrogne.net/" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; fr-fr) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5"
"""[1:-1].split("\n")
	for line in log.log(logs, lighttpd):
		print parser.UserAgent(line['user-agent']).pretty()
		print os(line['user-agent'])
