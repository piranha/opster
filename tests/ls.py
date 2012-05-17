#!/usr/bin/env python

import sys
from opster import command

@command(usage='[-h]')
def main(human=('h', False, 'Pretty print filesizes'),
         nohelp1=('', False, ''),
         nohelp2=('n', False, '')):
    if human:
        print('26k')
    else:
        print('26037')

if __name__ == "__main__":
    main.command(sys.argv[1:], scriptname='ls')
