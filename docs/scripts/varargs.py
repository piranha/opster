# varargs.py

from __future__ import print_function

from opster import command

@command()
def main(shop,
         *cheeses,
         music=('m', False, 'provide musical accompaniment')):
    '''Buy cheese'''
    print('shop:', shop)
    print('cheeses:', cheeses)

if __name__ == "__main__":
    main.command()
