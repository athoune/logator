#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime

from logator.reader.syslog import SyslogLine

class PostfixLine(SyslogLine):
	def parse_msg(self, line):
		if line.startswith('postfix'):
			self.datas['type'] = 'postfix'
			self.datas['service'] = line[:line.find('[')].split('/')[1]
		if line.startswith('amavis'):
			self.datas['type'] = 'amavis'
