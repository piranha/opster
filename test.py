#!/usr/bin/env python

import sys

from opster import dispatch, command


@command(usage='[-t]', shortlist=True)
def simple(ui,
           test=('t', False, 'just test execution')):
    '''Just simple command to do nothing.

    I assure you! Nothing to look here. ;-)
    '''
    ui.write(str(locals()))
    ui.write('\n')

cplx_opts = [('p', 'pass', False, 'don\'t run the command'),
             ('', 'exit', 0, 'exit with supplied code (default: 0)'),
             ('n', 'name', '', 'optional name')]

@command(cplx_opts, usage='[-p] [--exit value] ...', name='complex', hide=True)
def complex_(ui, *args, **opts):
    '''That's more complex command indented to do something

    Let's try to do that (what?!)
    '''
    if opts.get('pass'):
        return
    # test ui
    ui.write('write\n')
    ui.note('note\n')
    ui.info('info\n')
    ui.warn('warn\n')
    if opts.get('exit'):
        sys.exit(opts['exit'])

def ui_middleware(func):
    if func.__name__ == 'help_inner':
        return func
    def extract_dict(source, *keys):
        dest = {}
        for k in keys:
            dest[k] = source.pop(k, None)
        return dest

    def inner(*args, **kwargs):
        ui = UI(**extract_dict(kwargs, 'verbose', 'quiet'))
        return func(ui, *args, **kwargs)
    return inner

class UI(object):
    '''User interface helper.

    Intended to ease handling of quiet/verbose output and more.

    You have three methods to handle program messages output:

      - ``UI.info`` is printed by default, but hidden with quiet option
      - ``UI.note`` is printed only if output is verbose
      - ``UI.write`` is printed in any case

    Additionally there is ``UI.warn`` method, which prints to stderr.
    '''

    options = [('v', 'verbose', False, 'enable additional output'),
               ('q', 'quiet', False, 'suppress output')]

    def __init__(self, verbose=False, quiet=False):
        self.verbose = verbose
        # disabling quiet in favor of verbose is more safe
        self.quiet = (not verbose and quiet)

    def write(self, *messages):
        for m in messages:
            sys.stdout.write(m)

    def warn(self, *messages):
        for m in messages:
            sys.stderr.write(m)

    info = lambda self, *m: not self.quiet and self.write(*m)
    note = lambda self, *m: self.verbose and self.write(*m)


if __name__ == '__main__':
    dispatch(globaloptions=UI.options, middleware=ui_middleware)
