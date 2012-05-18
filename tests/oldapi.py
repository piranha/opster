#!/usr/bin/env python

import sys

from opster import dispatch


cmd1opts = [('q', 'quiet', False, 'be quiet')]
def cmd1(**opts):
    if not opts['quiet']:
        print('Not being quiet!')

cmd2opts = [('v', 'verbose', False, 'be loud')]
def cmd2(arg, *args, **opts):
    print(arg)
    if opts['verbose']:
        for arg in args:
            print(arg)

cmdtable = {
    'cmd1':(cmd1, cmd1opts, '[-q|--quiet]'),
    'cmd2':(cmd2, cmd2opts, '[ARGS]'),
}

dispatch(sys.argv[1:], cmdtable)
