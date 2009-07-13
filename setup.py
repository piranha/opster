#!/usr/bin/env python

import os
from distutils.core import setup
import finaloption

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'finaloption',
    description = 'command line arguments parser',
    long_description = read('README'),
    version = finaloption.__version__,
    author = finaloption.__author__,
    url = 'http://hg.piranha.org.ua/finaloption/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Languge :: Python',
        'Topic :: Software Development',
        ],
    py_modules = ['finaloption'],
    )
