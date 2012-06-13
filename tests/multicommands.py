#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs

from opster import dispatch, command


# Replace stdio to enforce utf-8 output
writer = codecs.getwriter('utf-8')
sys.stdout = writer(getattr(sys.stdout, 'buffer', sys.stdout))
sys.stderr = writer(getattr(sys.stderr, 'buffer', sys.stderr))


@command(usage='[-t]', shortlist=True)
def simple(ui,
           test=('t', False, 'just test execution')):
    '''
    Just simple command to print keys of received arguments.

    I assure you! Nothing to look here. ;-)
    '''
    ui.write(str(list(locals().keys())))
    ui.write('\n')

@command(usage='[-p] [--exit value] ...', name='complex', hide=True)
def complex_(ui,
             pass_=('p', False, "don't run the command"),
             exit=('', 100, 'exit with supplied code'),
             name=('n', '', 'optional name'),
             *args):
    '''That's more complex command intended to do something

    И самое главное - мы тут немножечко текста не в ascii напишем
    и посмотрим, что будет. :)
    '''
    if pass_:
        return
    # test ui
    ui.write('write\n')
    ui.note('note\n')
    ui.info('info\n')
    ui.warn('warn\n')
    sys.exit(exit)

@command(shortlist=True)
def nodoc():
    pass

def ui_middleware(func):
    def extract_dict(source, *keys):
        dest = {}
        for k in keys:
            dest[k] = source.pop(k, None)
        return dest

    def inner(*args, **kwargs):
        opts = extract_dict(kwargs, 'verbose', 'quiet')
        if func.__name__ == 'help_inner':
            return func(*args, **kwargs)
        ui = UI(**opts)
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
        sys.stdout.flush()

    def warn(self, *messages):
        for m in messages:
            sys.stderr.write(m)
        sys.stderr.flush()

    info = lambda self, *m: not self.quiet and self.write(*m)
    note = lambda self, *m: self.verbose and self.write(*m)


if __name__ == '__main__':
    dispatch(globaloptions=UI.options, middleware=ui_middleware)
