#!/usr/bin/env python

import sys
from opster import command, dispatch

@command(usage='[-h]')
def cmd():
    pass

if __name__ == "__main__":
    dispatch(sys.argv[1:], scriptname='newname')
