# (c) Alexander Solovyov, 2009, under terms of the new BSD License
'''Fancy option parser
'''

import getopt, types, textwrap

def fancyopts(cmd, args, options):
    if not args:
        help_(cmd, options)
    else:
        opts, args = parse(args, options)
        cmd(*args, **opts)

def help_(cmd, options):
    '''show help for given command

    >>> def test(*args, **opts):
    ...     """test [-l HOST] [NAME]"""
    >>> opts = [('l', 'listen', 'localhost',
    ...          'ip to listen on'),
    ...         ('p', 'port', 8000,
    ...          'port to listen on'),
    ...         ('d', 'daemonize', False,
    ...          'daemonize process'),
    ...         ('', 'pid-file', '',
    ...          'name of file to write process ID to')]
    >>> help_(test, opts)
    test [-l HOST] [NAME]
    <BLANKLINE>
    options:
    <BLANKLINE>
     -l --listen     ip to listen on (default: localhost)
    <BLANKLINE>
     -p --port       port to listen on (default: 8000)
    <BLANKLINE>
     -d --daemonize  daemonize process
    <BLANKLINE>
        --pid-file   name of file to write process ID to
    <BLANKLINE>
    '''
    doc = cmd.__doc__
    if not doc:
        doc = '(no help text available)'
    print '%s\n' % doc.strip()
    print '\n'.join(help_options(options))


def help_options(options):
    yield 'options:\n'
    output = []
    for short, name, default, desc in options:
        default = default and ' (default: %s)' % default or ''
        output.append(('%2s%s' % (short and '-%s' % short,
                                  name and ' --%s' % name),
                       '%s%s' % (desc, default)))

    opts_len = max([len(f) for f, s in output if s] or [0])
    for first, second in output:
        if second:
            # wrap description at 70 chars
            second = textwrap.wrap(second, width=70 - opts_len - 3)
            pad = '\n' + ' ' * (opts_len + 3)
            yield ' %-*s  %s\n' % (opts_len, first, pad.join(second))
        else:
            yield '%s\n' % first


def parse(args, options):
    '''
    >>> opts = [('l', 'listen', 'localhost',
    ...          'ip to listen on'),
    ...         ('p', 'port', 8000,
    ...          'port to listen on'),
    ...         ('d', 'daemonize', False,
    ...          'daemonize process'),
    ...         ('', 'pid-file', '',
    ...          'name of file to write process ID to')]
    >>> print parse(['-l', '0.0.0.0', '--pi', 'test', 'all'], opts)
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

        # getopt wants indication that it takes a parameter
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
