# basic.py

from __future__ import print_function

import sys

def main(arg1, arg2=None):
    '''Print the values of arg1 and arg2'''
    print('arg1:', arg1)
    print('arg2:', arg2)

if __name__ == "__main__":
    main(*sys.argv[1:])
