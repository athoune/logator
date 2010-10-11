#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

def log(parser, reader, filter = {}):
	for line in reader:
		yield parser.__call__(line)