# varargs_py2.py

from __future__ import print_function

from opster import command

@command()
def main(shop,
         music=('m', False, 'provide musical accompaniment'),
         *cheeses):
    '''Buy cheese'''
    print('shop:', shop)
    print('cheeses:', cheeses)

if __name__ == "__main__":
    main.command()
