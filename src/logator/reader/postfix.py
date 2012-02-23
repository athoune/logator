#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime

from logator.reader.syslog import SyslogLine

class PostfixLine(SyslogLine):
    def parse_msg(self, line):
        tokens = line.split(': ', 1)
        if tokens[0].startswith('postfix'):
            self.datas['type'] = 'postfix'
            self.datas['service'] = line[:line.find('[')].split('/')[1]
            if tokens[1].startswith('NOQUEUE: reject: '):
                self.datas['action'] = 'reject'
        if tokens[0].startswith('amavis'):
            self.datas['type'] = 'amavis'
            if tokens[1].find('Blocked SPAM') != -1:
                self.datas['action'] = 'blocked spam'
                print tokens[1].split(', ')
