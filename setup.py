#!/usr/bin/env python

import sys, os, re

from distutils.core import setup

# Use 2to3 build conversion if required
if sys.version_info >= (3, 0):
    from distutils.command.build_py import build_py_2to3 as build_py
else:
    from distutils.command.build_py import build_py

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def desc():
    info = read('README.rst')
    try:
        return info + '\n\n' + read('docs/changelog.rst')
    except IOError:
        # no docs
        return info

# grep opster.py since python 3.x cannot import it before using 2to3
opster_text = read('opster.py')
def grep_opsterpy(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, opster_text)
    return strval

setup(
    name='opster',
    description='command line parsing speedster',
    long_description=desc(),
    license='BSD',
    version = grep_opsterpy('__version__'),
    author = grep_opsterpy('__author__'),
    author_email = grep_opsterpy('__email__'),
    url='http://github.com/piranha/opster/',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        ],
    py_modules=['opster'],
    platforms='any',
    cmdclass={'build_py':build_py}
    )
