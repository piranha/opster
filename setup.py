#!/usr/bin/env python

import os
from setuptools import setup
import opster

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def desc():
    info = read('README')
    try:
        return info + '\n\n' + read('docs/changelog.rst')
    except IOError:
        # no docs
        return info

setup(
    name = 'opster',
    description = 'command line parsing speedster',
    long_description = desc(),
    license = 'BSD',
    version = opster.__version__,
    author = opster.__author__,
    author_email = opster.__email__,
    url = 'http://hg.piranha.org.ua/opster/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        ],
    py_modules = ['opster'],
    platforms='any',
    )
