#!/usr/bin/env python

import finaloption

config_opts=[('c', 'config', 'webshops.ini', 'config file to use')]


@finaloption.command(config_opts)
def initdb(config):
    """Initialize database"""
    pass


@finaloption.command(options=config_opts + [
    ('h', 'host', 'localhost', 'The host for the application.'),
    ('p', 'port', 5000, 'The port for the server.'),
    ('', 'nolint', False, 'Do not use LintMiddleware')
])
def runserver(**opts):
    """Run development server"""
    print opts


finaloption.dispatch()
