#!/usr/bin/env python

import sys

from opster import command

opts = [('l', 'listen', 'localhost', 'ip to listen on'),
        ('p', 'port', 8000, 'port to listen on'),
        ('d', 'daemonize', False, 'daemonize process'),
        ('', 'pid-file', '', 'name of file to write process ID to')]

@command(opts, usage='[-l HOST] DIR')
def main(dirname, **opts):
    '''This is some command

    It looks very similar to some serve command
    '''
    print opts

@command(usage='[-l HOST] DIR')
def another(dirname,
            listen=('l', 'localhost', 'ip to listen on'),
            port=('p', 8000, 'port to listen on'),
            daemonize=('d', False, 'daemonize process'),
            pid_file=('', '', 'name of file to write process ID to')):
    '''Command with option declaration as keyword arguments

    Otherwise it's the same as previous command
    '''
    print locals()

if __name__ == '__main__':
    #main()
    another()
