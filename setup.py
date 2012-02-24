#!/usr/bin/env python

from setuptools import setup

# http://pypi.python.org/pypi?%3Aaction=list_classifiers

setup(name='logator',
    version='0.2',
    package_dir={'': 'src'},
    url='http://github.com/athoune/logator',
    #scripts=[],
    description="Log parsing tool",
    long_description="""
Log parsing
===========

Bricks for building your own log parser.
Ready to use parser for apache like logs.
""",
    classifiers=[
         'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: French',
          'Topic :: System :: Logging'
        ],
    license="MIT",
    author="Mathieu Lecarme",
    packages=['logator'],
    keywords= ["log"],
    zip_safe = True,
    install_requires=["pyyaml"],
)
