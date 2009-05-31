# (c) Alexander Solovyov, 2009, under terms of the new BSD License
'''Fancy option parser
'''

import getopt, types

def fancyopts(args, options):
    '''
    >>> opts = [('l', 'listen', 'localhost',
    ...          'ip to listen on (default: localhost)'),
    ...         ('p', 'port', 8000,
    ...          'port to listen on (default: 8000)'),
    ...         ('d', 'daemonize', False,
    ...          'daemonize process'),
    ...         ('', 'pid-file', '',
    ...          'name of file to write process ID to')]
    >>> print fancyopts(['-l', '0.0.0.0', '--pi', 'test', 'all'], opts)
    ({'pid_file': 'test', 'daemonize': False, 'port': 8000, 'listen': '0.0.0.0'}, ['all'])

    '''
    argmap = {}
    state = {}
    shortlist = ''
    namelist = []

    for short, oname, default, comment in options:
        # change name to match Python styling
        name = oname.replace('-', '_')
        argmap['-' + short] = argmap['--' + oname] = name
        state[name] = default

        # it takes a parameter
        if default not in (None, True, False):
            if short: short += ':'
            if oname: oname += '='
        if short:
            shortlist += short
        if name:
            namelist.append(oname)

    opts, args = getopt.gnu_getopt(args, shortlist, namelist)

    # transfer result to state
    for opt, val in opts:
        name = argmap[opt]
        t = type(state[name])
        if t is types.FunctionType:
            state[name] = state[name](val)
        elif t is types.IntType:
            state[name] = int(val)
        elif t is types.StringType:
            state[name] = val
        elif t is types.ListType:
            state[name].append(val)
        elif t in (types.NoneType, types.BooleanType):
            state[name] = not state[name]

    return state, args

if __name__ == '__main__':
    import doctest
    doctest.testmod()
