# pos4.py

from __future__ import print_function

from opster import command

@command()
def main(arg1,
         arg2=(),
         *,    #   <-- separates option definitions
         option=('o', False, 'an arbitrary option')):
    '''Do important things'''
    print('arg1:', arg1)
    print('arg2:', arg2)
    print('option:', option)

if __name__ == "__main__":
    main.command()
