from datetime import datetime

from logator.log import LogLine


class SyslogLine(LogLine):
    def parse(self, line):
        tokens = line.split(' ', 4)
        self.datas['date'] = datetime.strptime('2010 ' + ' '.join(tokens[:3]), '%Y %b %d %H:%M:%S'),
        self.datas['facility'] = tokens[3]
        self.parse_msg(tokens[4])

    def parse_msg(self, msg):
        self.datas['msg'] = msg

    def __repr__(self):
        print self.datas
        return "<SyslogLine %s >" % self.datas['date']
