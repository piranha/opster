# (c) Alexander Solovyov, 2009-2011, under terms of the new BSD License
'''Command line arguments parser
'''

import sys, traceback, getopt, types, textwrap, inspect, os, copy
from itertools import imap

__all__ = ['command', 'dispatch']
__version__ = '2.2'
__author__ = 'Alexander Solovyov'
__email__ = 'piranha@piranha.org.ua'

try:
    import locale
    ENCODING = locale.getpreferredencoding()
    if not ENCODING or ENCODING == 'mac-roman' or 'ascii' in ENCODING.lower():
        ENCODING = 'UTF-8'
except locale.Error:
    ENCODING = 'UTF-8'

def write(text, out=None):
    '''Write output to a given stream (stdout by default)'''
    out = out or sys.stdout
    if isinstance(text, unicode):
        return out.write(text.encode(ENCODING))
    out.write(text)

def err(text):
    '''Write output to stderr'''
    write(text, out=sys.stderr)

CMDTABLE = {}

# --------
# Public interface
# --------

def command(options=None, usage=None, name=None, shortlist=False, hide=False):
    '''Decorator to mark function to be used for command line processing.

    All arguments are optional:

     - ``options``: options in format described later. If not supplied,
       will be determined from function.
     - ``usage``: usage string for function, replaces ``%name`` with name
       of program or subcommand. In case if it's subcommand and ``%name``
       is not present, usage is prepended by ``name``
     - ``name``: used for multiple subcommands. Defaults to wrapped
       function name
     - ``shortlist``: if command should be included in shortlist. Used
       only with multiple subcommands
     - ``hide``: if command should be hidden from help listing. Used only
       with multiple subcommands, overrides ``shortlist``

    Options should be a list of 4-tuples in format::

      (shortname, longname, default, help)

    Where:

     - ``shortname`` is a single letter which can be used then as an option
       specifier on command line (like ``-a``). Will be not used if contains
       falsy value (empty string, for example)
     - ``longname`` - main identificator of an option, can be used as on a
       command line with double dashes (like ``--longname``)
     - ``default`` value for an option, type of it determines how option will be
       processed
     - ``help`` string displayed as a help for an option when asked to
    '''
    def wrapper(func):
        try:
            options_ = list(guess_options(func))
        except TypeError:
            options_ = []
        try:
            options_ = options_ + list(options)
        except TypeError:
            pass

        name_ = name or func.__name__.replace('_', '-')
        if usage is None:
            usage_ = guess_usage(func, options_)
        else:
            usage_ = usage
        prefix = hide and '~' or (shortlist and '^' or '')
        CMDTABLE[prefix + name_] = (func, options_, usage_)

        def help_func(name=None):
            return help_cmd(func, replace_name(usage_, sysname()), options_)
        func.help = help_func

        @wraps(func)
        def inner(*args, **opts):
            # look if we need to add 'help' option
            try:
                (True for option in reversed(options_)
                 if option[1] == 'help').next()
            except StopIteration:
                options_.append(('h', 'help', False, 'show help'))

            argv = opts.pop('argv', sys.argv[1:])
            if opts.pop('help', False):
                return func.help()

            if args or opts:
                # no catcher here because this is call from Python
                return call_cmd_regular(func, options_)(*args, **opts)

            try:
                opts, args = catcher(lambda: parse(argv, options_), func.help)
            except Abort:
                return -1

            if opts.pop('help', False):
                return func.help()

            try:
                return catcher(lambda: call_cmd(name_, func)(*args, **opts),
                               func.help)
            except Abort:
                return -1

        return inner
    return wrapper


def dispatch(args=None, cmdtable=None, globaloptions=None,
             middleware=lambda x: x):
    '''Dispatch command arguments based on subcommands.

    - ``args``: list of arguments, default: ``sys.argv[1:]``
    - ``cmdtable``: dict of commands in format described below.
      If not supplied, will use functions decorated with ``@command``.
    - ``globaloptions``: list of options which are applied to all
      commands, will contain ``--help`` option at least.
    - ``middleware``: global decorator for all commands.

    cmdtable format description::

      {'name': (function, options, usage)}

    - ``name`` is the name used on command-line. Can contain aliases
      (separate them with ``|``), pointer to a fact that this command
      should be displayed in short help (start name with ``^``), or to
      a fact that this command should be hidden (start name with ``~``)
    - ``function`` is the actual callable
    - ``options`` is options list in format described in docs
    - ``usage`` is the short string of usage
    '''
    args = args or sys.argv[1:]
    cmdtable = cmdtable or CMDTABLE

    globaloptions = globaloptions or []
    globaloptions.append(('h', 'help', False, 'display help'))

    cmdtable['help'] = (help_(cmdtable, globaloptions), [], '[TOPIC]')
    help_func = cmdtable['help'][0]

    autocomplete(cmdtable, args, middleware)

    try:
        name, func, args, kwargs = catcher(
            lambda: _dispatch(args, cmdtable, globaloptions),
            help_func)
    except Abort:
        return -1

    if name == '_completion':       # skip middleware
        worker = lambda: call_cmd(name, func)(*args, **kwargs)
    else:
        mwfunc = middleware(func)
        depth = func == mwfunc and 1 or 2
        worker = lambda: call_cmd(name, mwfunc, depth=depth)(*args, **kwargs)

    try:
        return catcher(worker, help_func)
    except Abort:
        return -1

# --------
# Help
# --------

def help_(cmdtable, globalopts):
    '''Help generator for a command table
    '''
    def help_inner(name=None):
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
                if cmd.startswith('~'):
                    continue  # do not display hidden commands
                if shortlist and not cmd.startswith('^'):
                    continue  # short help contains only marked commands
                cmd = cmd.lstrip('^~')
                doc = pretty_doc_string(info[0])
                hlp[cmd] = doc.strip().splitlines()[0].rstrip()

            hlplist = sorted(hlp)
            maxlen = max(map(len, hlplist))

            write('usage: %s <command> [options]\n' % sysname())
            write('\ncommands:\n\n')
            for cmd in hlplist:
                doc = hlp[cmd]
                write(' %-*s  %s\n' % (maxlen, cmd.split('|', 1)[0], doc))

        if not cmdtable:
            return err('No commands specified!\n')

        if not name or name == 'shortlist':
            return helplist()

        aliases, (cmd, options, usage) = findcmd(name, cmdtable)
        return help_cmd(cmd,
                        replace_name(usage, sysname() + ' ' + aliases[0]),
                        options + globalopts)
    return help_inner

def help_cmd(func, usage, options):
    '''show help for given command

    - ``func``: function to generate help for (``func.__doc__`` is taken)
    - ``usage``: usage string
    - ``options``: options in usual format

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
    '''
    write(usage + '\n')
    doc = pretty_doc_string(func)
    write('\n' + doc.strip() + '\n\n')
    if options:
        write(''.join(help_options(options)))

def help_options(options):
    '''Generator for help on options
    '''
    yield 'options:\n\n'
    output = []
    for o in options:
        short, name, default, desc = o[:4]
        if hasattr(default, '__call__'):
            default = default(None)
        default = default and ' (default: %s)' % default or ''
        output.append(('%2s%s' % (short and '-%s' % short,
                                  name and ' --%s' % name),
                       '%s%s' % (desc, default)))

    opts_len = max([len(first) for first, second in output if second] or [0])
    for first, second in output:
        if second:
            # wrap description at 78 chars
            second = textwrap.wrap(second, width=(78 - opts_len - 3))
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
    shortlist, namelist, funlist = '', [], []

    for o in options:
        # might have the fifth completer element
        short, name, default, comment = o[:4]
        if short and len(short) != 1:
            raise OpsterError(
                'Short option should be only a single character: %s' % short)
        if not name:
            raise OpsterError(
                'Long name should be defined for every option')
        # change name to match Python styling
        pyname = name.replace('-', '_')
        argmap['-' + short] = argmap['--' + name] = pyname
        defmap[pyname] = default

        # copy defaults to state
        if isinstance(default, (list, dict)):
            state[pyname] = copy.copy(default)
        elif hasattr(default, '__call__'):
            funlist.append(pyname)
            state[pyname] = None
        else:
            state[pyname] = default

        # getopt wants indication that it takes a parameter
        if not (default is None or default is True or default is False):
            if short:
                short += ':'
            if name:
                name += '='
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
            del funlist[funlist.index(name)]
            state[name] = defmap[name](val)
        elif t is list:
            state[name].append(val)
        elif t is dict:
            try:
                k, v = val.split('=')
            except ValueError:
                raise ParseError(name, "wrong definition: '%s' "
                                 "(should be in format KEY=VALUE)" % val)
            state[name][k] = v
        elif t in (types.NoneType, types.BooleanType):
            state[name] = not defmap[name]
        else:
            state[name] = t(val)

    for name in funlist:
        state[name] = defmap[name](None)

    return state, args


# --------
# Subcommand system
# --------

def _dispatch(args, cmdtable, globalopts):
    '''Dispatch arguments list by a command table
    '''
    cmd, func, args, options = cmdparse(args, cmdtable, globalopts)

    if options.pop('help', False):
        return 'help', cmdtable['help'][0], [cmd], {}
    elif not cmd:
        return 'help', cmdtable['help'][0], ['shortlist'], {}

    return cmd, func, args, options

def cmdparse(args, cmdtable, globalopts):
    '''Parse arguments list to find a command, options and arguments
    '''
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

    options, args = parse(args, possibleopts)
    return cmd, cmd and info[0] or None, args, options

def aliases_(cmdtable_key):
    '''Get aliases from a command table key'''
    return cmdtable_key.lstrip("^~").split("|")

def findpossible(cmd, table):
    """
    Return cmd -> (aliases, command table entry)
    for each matching command.
    """
    choice = {}
    for e in table.keys():
        aliases = aliases_(e)
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
# Helpers
# --------

def guess_options(func):
    '''Get options definitions from function

    They should be declared in a following way:

    def func(longname=(shortname, default, help)):
        pass

    See docstring of ``command()`` for description of those variables.
    '''
    args, _, _, defaults = inspect.getargspec(func)
    for name, option in zip(args[-len(defaults):], defaults):
        try:
            sname, default, hlp = option[:3]
            completer = option[3] if len(option) > 3 else None
            yield (sname, name.replace('_', '-'), default, hlp, completer)
        except TypeError:
            pass

def guess_usage(func, options):
    '''Get usage definition for a function
    '''
    usage = '%name '
    if options:
        usage += '[OPTIONS] '
    args, varargs = inspect.getargspec(func)[:2]
    argnum = len(args) - len(options)
    if argnum > 0:
        usage += args[0].upper()
        if argnum > 1:
            usage += 'S'
    elif varargs:
        usage += '[%s]' % varargs.upper()
    return usage

def catcher(target, help_func):
    '''Catches all exceptions and prints human-readable information on them
    '''
    try:
        return target()
    except UnknownCommand, e:
        err("unknown command: '%s'\n" % e)
        raise Abort()
    except AmbiguousCommand, e:
        err("command '%s' is ambiguous:\n    %s\n" %
            (e.args[0], ' '.join(e.args[1])))
        raise Abort()
    except ParseError, e:
        err('%s: %s\n\n' % (e.args[0], e.args[1].strip()))
        help_func(e.args[0])
        raise Abort()
    except getopt.GetoptError, e:
        err('error: %s\n\n' % e)
        help_func()
        raise Abort()
    except OpsterError, e:
        err('%s\n' % e)
        raise Abort()

def call_cmd(name, func, depth=1):
    '''Wrapper for command call, catching situation with insufficient arguments

    ``depth`` is necessary when there is a middleware in setup
    '''
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            if len(traceback.extract_tb(sys.exc_info()[2])) == depth:
                raise ParseError(name, "invalid arguments")
            raise
    return inner

def call_cmd_regular(func, opts):
    '''Wrapper for command for handling function calls from Python
    '''
    def inner(*args, **kwargs):
        funcargs, _, varkw, defaults = inspect.getargspec(func)
        if len(args) > len(funcargs):
            raise TypeError('You have supplied more positional arguments'
                            ' than applicable')

        funckwargs = dict((lname.replace('-', '_'), default)
                          for _, lname, default, _ in opts)
        if 'help' not in (defaults or ()) and not varkw:
            funckwargs.pop('help', None)
        funckwargs.update(kwargs)
        return func(*args, **funckwargs)
    return inner

def replace_name(usage, name):
    '''Replace name placeholder with a command name'''
    if '%name' in usage:
        return usage.replace('%name', name, 1)
    return name + ' ' + usage

def sysname():
    '''Returns name of executing file'''
    name = sys.argv[0]
    if name.startswith('/'):
        return name.rsplit('/', 1)[1]
    elif name.startswith('./'):
        return name[2:]
    return name

def pretty_doc_string(item):
    "Doc string with adjusted indentation level of the 2nd line and beyond."
    raw_doc = item.__doc__ or '(no help text available)'
    lines = raw_doc.strip().splitlines()
    if len(lines) <= 1:
        return raw_doc
    indent = len(lines[1]) - len(lines[1].lstrip())
    return '\n'.join([lines[0]] + map(lambda l: l[indent:], lines[1:]))

try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        '''functools.wraps replacement for Python 2.4
        '''
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner

# --------
# Autocomplete system
# --------

# Borrowed from PIP
def autocomplete(cmdtable, args, middleware):
    """Command and option completion.

    Enable by sourcing one of the completion shell scripts (bash or zsh).
    """

    # Don't complete if user hasn't sourced bash_completion file.
    if 'OPSTER_AUTO_COMPLETE' not in os.environ:
        return
    cwords = os.environ['COMP_WORDS'].split()[1:]
    cword = int(os.environ['COMP_CWORD'])

    try:
        current = cwords[cword - 1]
    except IndexError:
        current = ''

    commands = []
    for k in cmdtable.keys():
        commands += aliases_(k)

    # command
    if cword == 1:
        print ' '.join(filter(lambda x: x.startswith(current), commands))

    # command options
    elif cwords[0] in commands:
        idx = -2 if current else -1
        options = []
        aliases, (cmd, opts, usage) = findcmd(cwords[0], cmdtable)

        for o in opts:
            short, long, default, help = o[:4]
            completer = o[4] if len(o) > 4 else None
            short, long = '-%s' % short, '--%s' % long
            options += [short, long]

            if cwords[idx] in (short, long) and completer:
                args = middleware(completer)(current)
                print ' '.join(args),

        print ' '.join((o for o in options if o.startswith(current)))

    sys.exit(1)

COMPLETIONS = {
    'bash':
        """
# opster bash completion start
_opster_completion()
{
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   OPSTER_AUTO_COMPLETE=1 $1 ) )
}
complete -o default -F _opster_completion %s
# opster bash completion end
""",
    'zsh':
            """
# opster zsh completion start
function _opster_completion {
  local words cword
  read -Ac words
  read -cn cword
  reply=( $( COMP_WORDS="$words[*]" \\
             COMP_CWORD=$(( cword-1 )) \\
             OPSTER_AUTO_COMPLETE=1 $words[1] ) )
}
compctl -K _opster_completion %s
# opster zsh completion end
"""
    }

@command(name='_completion', hide=True)
def completion(type=('t', 'bash', 'Completion type (bash or zsh)'),
               # kwargs will catch every global option, which we get
               # anyway, because middleware is skipped
               **kwargs):
    """Outputs completion script for bash or zsh."""

    prog_name = os.path.split(sys.argv[0])[1]
    print COMPLETIONS[type].strip() % prog_name

# --------
# Exceptions
# --------

# Command exceptions
class OpsterError(Exception):
    'Base opster exception'

class AmbiguousCommand(OpsterError):
    'Raised if command is ambiguous'

class UnknownCommand(OpsterError):
    'Raised if command is unknown'

class ParseError(OpsterError):
    'Raised on error in command line parsing'

class Abort(OpsterError):
    'Processing error, abort execution'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
