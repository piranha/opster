# better.py

from __future__ import print_function

from opster import command

@command()
def main(arg1, arg2=None):
    '''Display the values of ARG1 and ARG2'''
    print('arg1:', arg1)
    print('arg2:', arg2)

if __name__ == "__main__":
    main.command()
