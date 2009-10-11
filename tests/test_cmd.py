#!/usr/bin/env python

import opster

config_opts=[('c', 'config', 'webshops.ini', 'config file to use')]

@opster.command(config_opts)
def initdb(config):
    """Initialize database"""
    pass

@opster.command(config_opts)
def runserver(listen=('l', 'localhost', 'ip to listen on'),
              port=('p', 5000, 'port to listen on'),
              **opts):
    """Run development server"""
    print locals()

if __name__ == '__main__':
    opster.dispatch()
