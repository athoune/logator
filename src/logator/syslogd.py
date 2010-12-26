from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class SyslogInput(DatagramProtocol):

      def datagramReceived(self, data):
          print "I have received %r" % data

reactor.listenUDP(514, SyslogInput())
reactor.run()