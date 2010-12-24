#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name='logator',
      version='0.1',
      package_dir={'': 'src'},
      url='http://github.com/athoune/logator',
      #scripts=[],
      description="Log parsing",
      license="GPL-v3",
      author="Mathieu Lecarme",
      packages=['logator'],
      keywords= ["log"],
      zip_safe = True,
      install_requires=["ip2something"],

      )