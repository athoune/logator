Logator
=======

Build your own log parser.


Installing it
-------------

	python setup.py build
	sudo python setup.py install

Using it
--------

Log is handled as an iterable lines object. The basic example is a file.

You build your own parser with multiple heritage. Attributes can be static (from a regex parsing) or dynamic.
Logator handles lazy loading and memoization.

You can use filters.

User Agent parsing is stolen from Google code : http://code.google.com/p/ua-parser/.

	from logator.log import log
	from logator.weblog import Common, UserAgent, HostByName, Filter_by_code, Filter_by_attribute
	
	class Line(Common, UserAgent, HostByName):
		pass
	
	f = open('/var/log/apache2/access.log', 'r')
	for line in log(Line, f, Filter_by_code([200]) | Filter_by_attribute('command', 'HEAD')):
		print line.url, line.userAgent.pretty(), line.os#, line.hostByName

The futur
---------

 - √ Parsing http server log
 - _ Reading stdin
 - _ Filling a mongo database
 - √ IP to country
 - _ Querying
 - _ Nice graph from stored data