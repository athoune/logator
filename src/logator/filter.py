from logator.log import InvalidLog

"""
Filters can be piped, and called, it returns None or a Logline.

"""


class Filter(object):

    def __or__(self, other):
        meta = MetaFilter(self)
        meta.append(other)
        return meta

    def filter(self, iterable, *parser):
        c = type('Line', parser, {})
        for line in iterable:
            try:
                tmp = self.__call__(c(line))
                if tmp != None:
                    yield tmp
            except InvalidLog:
                pass


class MetaFilter(Filter):

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


class Filter_by_attribute(Filter):

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __call__(self, logline):
        if logline.__getattr__(self.key) in self.value:
            return logline
        return None
