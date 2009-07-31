#!/usr/bin/env python

import sys

from finaloption import dispatch, command


@command(usage='[-t]', shortlist=True)
def simple(test=('t', False, 'just test execution')):
    '''Just simple command to do nothing.

    I assure you! Nothing to look here. ;-)
    '''
    print locals()

cplx_opts = [('p', 'pass', False, 'don\'t run the command'),
             ('', 'exit', 0, 'exit with supplied code (default: 0)')]

@command(cplx_opts, usage='[-p] [--exit value] ...', name='complex', hide=True)
def complex_(*args, **opts):
    '''That's more complex command indented to do something

    Let's try to do that (what?!)
    '''
    if opts.get('pass'):
        return
    # test ui
    if opts.get('exit'):
        sys.exit(opts['exit'])

if __name__ == '__main__':
    dispatch()
