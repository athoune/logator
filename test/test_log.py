import sys
import os.path
import unittest

sys.path.insert(0, os.path.abspath('../src/'))

from logator.log import LazyDict

class DummyDict(LazyDict):
	hop = 41
	def get_foo(self):
		self.hop += 1
		return self.hop

class LazyDictTest(unittest.TestCase):
	def test_get(self):
		d = DummyDict()
		self.assertEqual(42, d.foo)
		#dynamic but cached
		self.assertEqual(42, d.foo)

if __name__ == '__main__':
    unittest.main()