# kwonly.py

from __future__ import print_function

from opster import command

@command()
def main(arg1,
         arg2=(),
         *,    #   <-- separates option definitions
         eggs=('e', False, 'use eggs')):
    '''spam the ham'''
    print('arg1:', arg1)
    print('arg2:', arg2)
    print('eggs:', eggs)

if __name__ == "__main__":
    main.command()
