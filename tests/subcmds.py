#!/usr/bin/env python

from __future__ import print_function

from opster import Dispatcher

d = Dispatcher()

d2 = Dispatcher()
@d2.command()
def subcmd1(quiet=('q', False, 'quietly')):
    '''Help for subcmd1'''
    if not quiet:
        print('running subcmd1')

@d2.command()
def subcmd2(number):
    '''Help for subcmd2'''
    print('running subcmd2', number)

d3 = Dispatcher()
@d3.command()
def subsubcmd(loud=('l', False, 'loudly')):
    '''Help for subsubcmd'''
    if loud:
        print('running subsubcmd')

d2.add_dispatcher('subcmd3', d3, 'Help for subcmd3')
d.add_dispatcher('cmd', d2, 'Help for cmd')

if __name__ == '__main__':
    d.dispatch()
