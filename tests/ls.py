#!/usr/bin/env python

import sys
from opster import command

@command(usage='[-h]')
def main(human=('h', False, 'Pretty print filesizes')):
    if human:
        print('26k')
    else:
        print('26037')

if __name__ == "__main__":
    main.command(sys.argv[1:])
