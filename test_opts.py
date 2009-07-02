#!/usr/bin/env python

import sys

from fancycmd import optionize

opts = [('l', 'listen', 'localhost', 'ip to listen on'),
        ('p', 'port', 8000, 'port to listen on'),
        ('d', 'daemonize', False, 'daemonize process'),
        ('', 'pid-file', '', 'name of file to write process ID to')]

@optionize(opts, usage='%prog [-l HOST] DIR')
def main(dirname, **opts):
    '''This is some command

    It looks very similar to some serve command
    '''
    print opts.get('pid_file')

if __name__ == '__main__':
    main()
