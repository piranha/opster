#!/usr/bin/env python

import sys
from decimal import Decimal as D
from opster import command

@command(usage='[-h]')
def main(human=('h', False, 'Pretty print filesizes'),
         filesize=('f', D('26037'), 'size to print'),
         nohelp1=('', False, ''),
         nohelp2=('n', False, '')):
    print(type(filesize))
    if human:
        print(str(filesize // 1024) + 'k')
    else:
        print(filesize)

if __name__ == "__main__":
    main.command(sys.argv[1:], scriptname='ls')
