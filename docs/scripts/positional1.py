#!/usr/bin/env python

import sys

def main(arg1, arg2=None):
    '''Script that prints out its arguments'''
    print 'arg1:', arg1
    print 'arg2:', arg2

if __name__ == "__main__":
    main(*sys.argv[1:])
