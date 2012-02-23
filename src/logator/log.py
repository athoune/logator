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

    def __iter__(self):
        for a in self.datas:
            yield a
        for k in dir(self):
            if k[:4] == 'get_':
                yield k[4:]


class AsDict(object):

    def as_dict(self):
        d = self.datas
        for k in dir(self):
            if k[:4] == 'get_':
                d[k[4:]] = self.__getattr__(k[4:])
        return d


class LogLine(LazyDict, AsDict):

    def __init__(self, line):
        LazyDict.__init__(self)
        AsDict.__init__(self)
        self.parse(line)

    def __repr__(self):
        return "<LogLine %s>" % self.datas['url']

    def parse(self, line):
        raise Exception('not implemented')


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

