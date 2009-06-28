# (c) Alexander Solovyov, 2009, under terms of the new BSD License
'''Fancy command line arguments parser
'''

import sys, traceback, getopt, types, textwrap
from itertools import imap

__all__ = ['fancyopts', 'dispatch']

# --------
# Public interface
# --------

def fancyopts(cmd, options, usage):
    def inner(args):
        if not args:
            help_cmd(cmd, usage, options)
        else:
            opts, args = parse(args, options)
            cmd(*args, **opts)
    return inner

def dispatch(args, cmdtable, globalopts=None):
    '''Dispatch command arguments based on subcommands.

     - ``args``: sys.argv[1:]
     - ``cmdtable``: dict of commands in next format::

     {'name': (function, options, usage)}

     - ``globalopts``: list of options which are applied to all
       commands, if not supplied will contain ``--help`` option

    where:

     - ``name`` is the name used on command-line. Can containt
       aliases (separate them with '|') or pointer to the fact
       that this command should be displayed in short help (start
       name with '^')
     - ``function`` is the actual callable
     - ``options`` is options list in fancyopts format
     - ``usage`` is the short string of usage
    '''

    ui = UI()
    if not globalopts:
        globalopts = [
            ('h', 'help', False, 'display help'),
            # is not used yet
            ('', 'traceback', False, 'display full traceback on error')]

    cmdtable['help'] = (help_(cmdtable, globalopts), [], '[TOPIC]')

    try:
        return _dispatch(ui, args, cmdtable, globalopts + UI.options)
    except Abort, e:
        ui.warn('abort: %s\n' % e)
    except UnknownCommand, e:
        ui.warn("unknown command: '%s'\n" % e)
    except AmbiguousCommand, e:
        ui.warn("command '%s' is ambiguous:\n    %s\n" %
                (e.args[0], ' '.join(e.args[1])))
    except ParseError, e:
        ui.warn('%s: %s\n' % (e.args[0], e.args[1]))
        cmdtable['help'][0](ui, e.args[0])
    except KeyboardInterrupt:
        ui.warn('interrupted!\n')
    except SystemExit:
        raise
    except:
        ui.warn('unknown exception encountered')
        raise

    return -1


# --------
# Help
# --------

def help_(cmdtable, globalopts):
    def inner(ui, name=None):
        '''Show help for a given help topic or a help overview

        With no arguments, print a list of commands with short help messages.

        Given a command name, print help for that command.
        '''
        def helplist():
            hlp = {}
            # determine if any command is marked for shortlist
            shortlist = (name == 'shortlist' and
                         any(imap(lambda x: x.startswith('^'), cmdtable)))

            for cmd, info in cmdtable.items():
                if shortlist and not cmd.startswith('^'):
                    continue # short help contains only marked commands
                cmd = cmd.lstrip('^')
                doc = info[0].__doc__ or '(no help text available)'
                hlp[cmd] = doc.splitlines()[0].rstrip()

            hlplist = sorted(hlp)
            maxlen = max(map(len, hlplist))
            for cmd in hlplist:
                doc = hlp[cmd]
                if ui.verbose:
                    ui.write(' %s:\n     %s\n' % (cmd.replace('|', ', '), doc))
                else:
                    ui.write(' %-*s  %s\n' % (maxlen, cmd.split('|', 1)[0],
                                              doc))

        if not cmdtable:
            return ui.warn('No commands specified!\n')

        if not name or name == 'shortlist':
            return helplist()

        aliases, (cmd, options, usage) = findcmd(name, cmdtable)
        return help_cmd(cmd, aliases[0]  + ' ' + usage, options)
    return inner

def help_cmd(func, usage, options):
    '''show help for given command

    >>> def test(*args, **opts):
    ...     """that's a test command
    ...
    ...        you can do nothing with this command"""
    ...     pass
    >>> opts = [('l', 'listen', 'localhost',
    ...          'ip to listen on'),
    ...         ('p', 'port', 8000,
    ...          'port to listen on'),
    ...         ('d', 'daemonize', False,
    ...          'daemonize process'),
    ...         ('', 'pid-file', '',
    ...          'name of file to write process ID to')]
    >>> help_cmd(test, 'test [-l HOST] [NAME]', opts)
    test [-l HOST] [NAME]
    <BLANKLINE>
    that's a test command
    <BLANKLINE>
           you can do nothing with this command
    <BLANKLINE>
    options:
    <BLANKLINE>
     -l --listen     ip to listen on (default: localhost)
     -p --port       port to listen on (default: 8000)
     -d --daemonize  daemonize process
        --pid-file   name of file to write process ID to
    <BLANKLINE>
    '''
    print '%s\n' % usage
    doc = func.__doc__
    if not doc:
        doc = '(no help text available)'
    print '%s\n' % doc.strip()
    if options:
        print ''.join(help_options(options))

def help_options(options):
    yield 'options:\n\n'
    output = []
    for short, name, default, desc in options:
        default = default and ' (default: %s)' % default or ''
        output.append(('%2s%s' % (short and '-%s' % short,
                                  name and ' --%s' % name),
                       '%s%s' % (desc, default)))

    opts_len = max([len(first) for first, second in output if second] or [0])
    for first, second in output:
        if second:
            # wrap description at 70 chars
            second = textwrap.wrap(second, width=(70 - opts_len - 3))
            pad = '\n' + ' ' * (opts_len + 3)
            yield ' %-*s  %s\n' % (opts_len, first, pad.join(second))
        else:
            yield '%s\n' % first


# --------
# Options parsing
# --------

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
    argmap, defmap, state = {}, {}, {}
    shortlist, namelist = '', []

    for short, name, default, comment in options:
        # change name to match Python styling
        pyname = name.replace('-', '_')
        argmap['-' + short] = argmap['--' + name] = pyname
        defmap[pyname] = default

        # copy defaults to state
        if isinstance(default, list):
            state[pyname] = default[:]
        elif hasattr(default, '__call__'):
            state[pyname] = None
        else:
            state[pyname] = default

        # getopt wants indication that it takes a parameter
        if not (default is None or default is True or default is False):
            if short: short += ':'
            if name: name += '='
        if short:
            shortlist += short
        if name:
            namelist.append(name)

    opts, args = getopt.gnu_getopt(args, shortlist, namelist)

    # transfer result to state
    for opt, val in opts:
        name = argmap[opt]
        t = type(defmap[name])
        if t is types.FunctionType:
            state[name] = defmap[name](val)
        elif t is types.IntType:
            state[name] = int(val)
        elif t is types.StringType:
            state[name] = val
        elif t is types.ListType:
            state[name].append(val)
        elif t in (types.NoneType, types.BooleanType):
            state[name] = not defmap[name]

    return state, args


# --------
# Subcommand system
# --------

def _dispatch(ui, args, cmdtable, globalopts):
    cmd, func, args, options, globaloptions = cmdparse(args, cmdtable,
                                                       globalopts)

    ui.verbose = globaloptions['verbose']
    # see UI.__init__ for explanation
    ui.quiet = (not ui.verbose and globaloptions['quiet'])

    if globaloptions['help']:
        return cmdtable['help'][0](ui, cmd)
    elif not cmd:
        return cmdtable['help'][0](ui, 'shortlist')

    try:
        return func(ui, *args, **options)
    except TypeError:
        if len(traceback.extract_tb(sys.exc_info()[2])) == 1:
            raise ParseError(cmd, "invalid arguments")
        raise

def cmdparse(args, cmdtable, globalopts):
    # command is the first non-option
    cmd = None
    for arg in args:
        if not arg.startswith('-'):
            cmd = arg
            break

    if cmd:
        args.pop(args.index(cmd))

        aliases, info = findcmd(cmd, cmdtable)
        cmd = aliases[0]
        possibleopts = list(info[1])
    else:
        possibleopts = []

    possibleopts.extend(globalopts)

    try:
        options, args = parse(args, possibleopts)
    except getopt.GetoptError, e:
        raise ParseError(cmd, e)

    globaloptions = {}
    for o in globalopts:
        name = o[1]
        globaloptions[name] = options.pop(name)

    return (cmd, cmd and info[0] or None, args, options, globaloptions)

def findpossible(cmd, table):
    """
    Return cmd -> (aliases, command table entry)
    for each matching command.
    """
    choice = {}
    for e in table.keys():
        aliases = e.lstrip("^").split("|")
        found = None
        if cmd in aliases:
            found = cmd
        else:
            for a in aliases:
                if a.startswith(cmd):
                    found = a
                    break
        if found is not None:
            choice[found] = (aliases, table[e])

    return choice

def findcmd(cmd, table):
    """Return (aliases, command table entry) for command string."""
    choice = findpossible(cmd, table)

    if cmd in choice:
        return choice[cmd]

    if len(choice) > 1:
        clist = choice.keys()
        clist.sort()
        raise AmbiguousCommand(cmd, clist)

    if choice:
        return choice.values()[0]

    raise UnknownCommand(cmd)


# --------
# UI and exceptions
# --------

class UI(object):
    '''User interface helper.

    Intended to ease handling of quiet/verbose output and more.

    You have three methods to handle program messages output:

      - ``UI.status`` is printed by default, but hidden with quiet option
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

    status = lambda self, *m: not self.quiet and self.write(*m)
    note = lambda self, *m: self.verbose and self.write(*m)

# Command exceptions
class CommandException(Exception):
    'Base class for command exceptions'

class Abort(CommandException):
    'Raised if an error in command occured'

class AmbiguousCommand(CommandException):
    'Raised if command is ambiguous'

class UnknownCommand(CommandException):
    'Raised if command is unknown'

class ParseError(CommandException):
    'Raised on error in command line parsing'

class SignatureError(CommandException):
    'Raised if function signature does not correspond to arguments'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
