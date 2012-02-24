Logator
=======

Build your own log parser.


Installing it
-------------

	python setup.py build
	sudo python setup.py install

Using it
--------

You need a **source**. Something wich iterate log line. The simplest way is STDIN and files, but you can also use syslogd protocol or more complex source.

For reading loglines, you need a **reader**. Reader is basically a regex with simple string manipulations. You can add dynamic getter for castly query (ip to country for example).
Dynamic attributes are lazy loaded and memoized.

Query is done with **filter**, wich can be piped.

Result can be return as dict wich can be easily serialized if you wont to index it or storing it.

```python
from logator.log import log
from logator.weblog import Common, UserAgent, HostByName, Filter_by_code, Filter_by_attribute
#The filter
filtr = Filter_by_code(200) | Filter_by_attribute('command', 'GET')
#The source
logs = open('/var/log/apache2/access.log', 'r')
#Lighttpd is the reader with two dynamic attributes reader : UserAgent, HostByName
for line in filtr.filter(logs, Lighttpd, UserAgent, HostByName):
    print line.as_dict()
```

User Agent parsing is stolen from Google code : http://code.google.com/p/ua-parser/.


The future
----------

 - √ Filter
 - √ Dynamic attributes
 - √ Parsing http server log
 - _ Parsing mail log (postfix + amavis)
 - _ Reading stdin
 - _ Reading syslog protocol
 - _ Reading "à la" tail -f
 - _ Filling a mongo database
 - √ IP to country
 - _ Querying
 - _ Nice graph from stored data

Licence
-------

MIT, 2012 © Mathieu Lecarme
