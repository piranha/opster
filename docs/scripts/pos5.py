# pos5.py

from __future__ import print_function

from opster import command

@command()
def main(pattern,
         *files,
         option=('o', False, 'an arbitrary option')):
    '''Do important things'''
    print('pattern:', pattern)
    print('files:', files)

if __name__ == "__main__":
    main.command()
