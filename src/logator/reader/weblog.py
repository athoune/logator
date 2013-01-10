#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime
import socket

import user_agent_parser

from logator.log import InvalidLog, LogLine
from logator.filter import Filter, Filter_by_attribute

RE_COMMON = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (\d+)', re.U)
RE_COMBINED = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (.*?) "([^"]*)" "([^"]*)"', re.U)
RE_LIGHTY = re.compile('(.*?) (.*?) - \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (.*?) "([^"]*)" "([^"]*)"', re.U)
RE_OS = re.compile('(.*?) \((.*?)\)', re.U)
RE_MOZILLA = re.compile('.*? \((.*?); U; (.*?);', re.U)


class WebLine(LogLine):

    def get_os(self):
        m = RE_OS.match(self.datas['user-agent'])
        infos = {}
        if m is not None:
            args = m.group(2).split('; ')
            if len(args) > 1 and args[1] == 'U':
                infos['os'] = args[0]
                if len(args) > 2:
                    infos['os-version'] = args[2]
        return infos

    def __repr__(self):
        return "<LogLine >"


class UserAgent(object):

    def get_userAgent(self):
        p = user_agent_parser.ParseUserAgent(self.datas['user-agent'])
        return {
            'family': p['family'],
            'v1': p['v1'],
            'v2': p['v2'],
            'v3': p['v3']
        }


socket.setdefaulttimeout(2)


class HostByName(object):

    def get_hostByName(self):
        try:
            return socket.gethostbyaddr(self.datas['ip'])[0]
        except socket.herror:
            return '?'


def intOrNull(a):
    if a == '-':
        return None
    return int(a)


class Common(WebLine):

    def parse(self, line):
        m = RE_COMMON.match(line)
        if m is None:
            raise InvalidLog()
        self.datas = {
            'ip':      m.group(1),
            'user':    m.group(2),
            'date':    datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
            'command': m.group(4),
            'url':     m.group(5),
            'http':    m.group(6),
            'code':    int(m.group(7)),
            'size':    int(m.group(8))
        }


class Combined(WebLine):

    def parse(self, line):
        m = RE_COMBINED.match(line)
        if m is None:
            raise InvalidLog()
        self.datas = {
            'ip':         m.group(1),
            'user':       m.group(2),
            'date':       datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
            'command':    m.group(4),
            'url':        m.group(5),
            'http':       m.group(6),
            'code':       int(m.group(7)),
            'size':       intOrNull(m.group(8)),
            'referer':    m.group(9),
            'user-agent': m.group(10)
        }


class Lighttpd(WebLine):

    def parse(self, line):
        m = RE_LIGHTY.match(line)
        if m is None:
            raise InvalidLog()
        self.datas = {
            'ip':     m.group(1),
            'domain': m.group(2),
            'date':   datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
            'command': m.group(4),
            'url':    m.group(5),
            'http':   m.group(6),
            'code':   int(m.group(7)),
            'size':   intOrNull(m.group(8)),
            'referer': m.group(9),
            'user-agent': m.group(10)
        }


class Filter_by_code(Filter_by_attribute):

    def __init__(self, *codes):
        self.key = 'code'
        self.value = codes


class Filter_by_error(Filter_by_code):

    def __init__(self):
        Filter_by_code.__init__(self, 403, 404, 500, 501, 502)


class Filter_by_domain(Filter):

    def __init__(self, *domain):
        self.domain = domain

    def __call__(self, logline):
        if logline.hostByName.split('.')[-1] in self.domain:
            return logline
