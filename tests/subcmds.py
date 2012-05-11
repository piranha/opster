#!/usr/bin/env python

from __future__ import print_function

from opster import Dispatcher

d = Dispatcher()

@d.command()
def cmd2(showhelp=('s', False, 'Print the help message')):
    if showhelp:
        print('Showing the help:')
        cmd2.help()

d2 = Dispatcher()
@d2.command()
def subcmd1(quiet=('q', False, 'quietly'),
            showhelp=('s', False, 'Print the help message')):
    '''Help for subcmd1'''
    if not quiet:
        print('running subcmd1')
    if showhelp:
        print('Showing the help:')
        subcmd1.help()

@d2.command()
def subcmd2(number):
    '''Help for subcmd2'''
    print('running subcmd2', number)

d3 = Dispatcher()
@d3.command()
def subsubcmd(loud=('l', False, 'loudly'),
              showhelp=('s', False, 'Print the help message')):
    '''Help for subsubcmd'''
    if loud:
        print('running subsubcmd')
    if showhelp:
        print('Showing the help:')
        subsubcmd.help()

d2.add_dispatcher('subcmd3', d3, 'Help for subcmd3')
d.add_dispatcher('cmd', d2, 'Help for cmd')

if __name__ == '__main__':
    d.dispatch()
