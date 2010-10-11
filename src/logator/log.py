#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

def log(parser, reader, filter_ = None):
	for line in reader:
		if filter_ == None:
			yield parser.__call__(line)
		else:
			tmp = filter_.__call__(parser.__call__(line))
			if tmp != None:
				yield tmp
