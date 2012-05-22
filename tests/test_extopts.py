# First line of opttypes.py
from __future__ import print_function

import sys
from decimal import Decimal
from fractions import Fraction

from opster import command


@command()
def main(money=('m', Decimal('100.00'), 'amount of money'),
         ratio=('r', Fraction('1/4'), 'input/output ratio')):
    '''Command using extended option types'''
    print('money:', type(money), money)
    print('ratio:', type(ratio), ratio)


if __name__ == '__main__':
    main.command()
