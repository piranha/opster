#!/usr/bin/env python

import sys

from fancycmd import dispatch


def simple(ui, *args, **opts):
    '''Just simple command to do nothing.

    I assure you! Nothing to look here. ;-)
    '''
    print opts

def complex_(ui, *args, **opts):
    '''That's more complex command indented to do something

    Let's try to do that (damn, but what?!)
    '''
    if opts.get('pass'):
        return
    # test ui
    ui.write('what the?!\n')
    ui.warn('this is stderr\n')
    ui.status('this would be invisible in quiet mode\n')
    ui.note('this would be visible only in verbose mode\n')
    ui.write('%s, %s\n' % (args, opts))
    if opts.get('exit'):
        sys.exit(opts['exit'])

cmdtable = {
    '^simple':
        (simple,
         [('t', 'test', False, 'just test execution')],
         '[-t] ...'),
    'complex|hard':
        (complex_,
         [('p', 'pass', False, 'don\'t run the command'),
          ('', 'exit', 0, 'exit with supplied code (default: 0)')],
         '[-p] [--exit value] ...')}

if __name__ == '__main__':
    dispatch(sys.argv[1:], cmdtable)
