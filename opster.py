# (c) Alexander Solovyov, 2009-2011, under terms of the new BSD License
'''Command line arguments parser
'''

import sys, traceback, getopt, types, textwrap, inspect, os, re, keyword, codecs
from itertools import imap
from functools import wraps
from collections import namedtuple, Callable
from contextlib import contextmanager


__all__ = ['Dispatcher', 'command', 'dispatch']
__version__ = '4.2'
__author__ = 'Alexander Solovyov'
__email__ = 'alexander@solovyov.net'


def write(text, out=None):
    '''Write output to a given stream (stdout by default).'''
    out = out or sys.stdout
    try:
        print >> out, text
    # Needed on Python 2.x if text is str/bytes containing non-ascii
    # characters and sys.stdout is replaced by a writer from the codecs
    # module. text will be decoded as ascii giving the decode error.
    except UnicodeDecodeError:
        print >> out, text.decode('utf-8')
    # Get the order of stdout/stderr correct on Windows. AFAICT this is only
    # needed for the test environment but it's harmless otherwise.
    out.flush()


def err(text):
    '''Write output to stderr.'''
    write(text, out=sys.stderr)


# encoding to use when decoding command line arguments
FSE_ENCODING = sys.getfilesystemencoding()
ARG_ENCODING = os.environ.get('OPSTER_ARG_ENCODING', FSE_ENCODING)


def decodearg(arg, arg_encoding=ARG_ENCODING):
    '''Decode an argument from sys.argv'''
    # python 2.x: have bytes, convert to unicode with given encoding
    if sys.version_info < (3, 0):
        return arg.decode(arg_encoding)

    # python 3.x: have unicode
    # arg has already been decoded with FSE_ENCODING
    # In the default case we just return the arg as it is
    if arg_encoding == FSE_ENCODING:
        return arg

    # Need to encode and redecode as arg_encoding
    if os.name == 'posix':
        # On posix the argument was decoded using surrogate escape
        arg = arg.encode(FSE_ENCODING, 'surrogateescape')
    else:
        # On windows the 'mbcs' codec has no surrogate escape handler
        arg = arg.encode(FSE_ENCODING)
    return arg.decode(arg_encoding)


class Dispatcher(object):
    '''Central object for command dispatching system.

    - ``cmdtable``: dict of commands. Will be populated with functions,
      decorated with ``Dispatcher.command``.
    - ``globaloptions``: list of options which are applied to all
      commands, will contain ``--help`` option at least.
    - ``middleware``: global decorator for all commands.
    '''

    def __init__(self, cmdtable=None, globaloptions=None, middleware=None):
        self._cmdtable = CmdTable(cmdtable or {})
        self._globaloptions = [Option(o) for o in (globaloptions or [])]
        self.middleware = middleware

    @property
    def globaloptions(self):
        opts = self._globaloptions[:]
        if not any(o.name == 'help' for o in opts):
            opts.append(Option(('h', 'help', False, 'display help')))
        return opts

    @property
    def cmdtable(self):
        return self._cmdtable.copy()

    def command(self, options=None, usage=None, name=None, shortlist=False,
                hide=False, aliases=()):
        '''Decorator to mark function to be used as command for CLI.

        Usage::

          from opster import command, dispatch

          @command()
          def run(argument,
                  optionalargument=None,
                  option=('o', 'default', 'help for option'),
                  no_short_name=('', False, 'help for this option')):
              print argument, optionalargument, option, no_short_name

          if __name__ == '__main__':
              run.command()

          # or, if you want to have multiple subcommands:
          if __name__ == '__main__':
              dispatch()

        Optional arguments:
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
         - ``aliases``: list of aliases for command

        If defined, options should be a list of 4-tuples in format::

          (shortname, longname, default, help)

        Where:

         - ``shortname`` is a single letter which can be used then as an option
           specifier on command line (like ``-a``). Will be not used if contains
           falsy value (empty string, for example)
         - ``longname`` - main identificator of an option, can be used as on a
           command line with double dashes (like ``--longname``)
         - ``default`` value for an option, type of it determines how option
           will be processed
         - ``help`` string displayed as a help for an option when asked to
        '''
        def wrapper(func):
            try:
                options_ = [Option(o) for o in (options or guess_options(func))]
            except TypeError:
                options_ = []

            cmdname = name or name_from_python(func.__name__)
            scriptname_ = name or sysname()
            if usage is None:
                usage_ = guess_usage(func, options_)
            else:
                usage_ = usage
            prefix = hide and '~' or (shortlist and '^' or '')
            cmdname = prefix + cmdname
            if aliases:
                cmdname = cmdname + '|' + '|'.join(aliases)
            self._cmdtable[cmdname] = (func, options_, usage_)

            def help_func(scriptname=None):
                scriptname = scriptname or sysname()
                return help_cmd(func, usage_, options_, aliases, scriptname)

            def command(argv=None, scriptname=None):
                scriptname = scriptname or sysname()
                merge_globalopts(self.globaloptions, options_)

                if argv is None:
                    argv = sys.argv[1:]

                try:
                    with exchandle(func.help, scriptname):
                        args, opts = process(argv, options_)

                    if opts.pop('help', False):
                        return func.help(scriptname)

                    with exchandle(func.help, scriptname):
                        with help_workaround(func, scriptname):
                            return call_cmd(scriptname, func, options_)(*args, **opts)

                except ErrorHandled:
                    return -1

            func.usage = usage_
            func.help = help_func
            func.command = command
            func.opts = options_
            func.orig = func
            func.scriptname = scriptname_

            @wraps(func)
            def inner(*args, **opts):
                return call_cmd_regular(func, options_)(*args, **opts)

            # Store this for help_workaround
            func._inner = inner

            return inner

        return wrapper

    def nest(self, name, dispatcher, help, hide=False, shortlist=False):
        '''Add another dispatcher as a subcommand.'''
        dispatcher.__doc__ = help
        prefix = hide and '~' or (shortlist and '^' or '')
        self._cmdtable[prefix + name] = dispatcher, [], None

    def dispatch(self, args=None, scriptname=None):
        '''Dispatch command line arguments using subcommands.

        - ``args``: list of arguments, default: ``sys.argv[1:]``
        '''
        if args is None:
            args = sys.argv[1:]
        scriptname = scriptname or sysname()

        # Add help function to the table
        cmdtable = self.cmdtable
        help_func = help_(cmdtable, self.globaloptions, scriptname)
        cmdtable['help'] = help_func, [], '[TOPIC]'

        autocomplete(cmdtable, args, self.middleware)

        try:
            with exchandle(help_func):
                cmd, func, args, options = cmdparse(args, cmdtable,
                                                    self.globaloptions)

            if isinstance(func, Dispatcher):
                return func.dispatch(args, scriptname=scriptname + ' ' + cmd)

            with exchandle(help_func, cmd):
                args, opts = process(args, options)

            if not cmd:
                cmd, func, args, opts = ('help', help_func, ['shortlist'], {})
            if opts.pop('help', False):
                cmd, func, args, opts = ('help', help_func, [cmd], {})

            mw = cmd != '_completion' and self.middleware or None
            with exchandle(help_func, cmd):
                with help_workaround(func, cmd, help_func):
                    return call_cmd(cmd, func, options, mw)(*args, **opts)

        except ErrorHandled:
            return -1


_dispatcher = None


def command(options=None, usage=None, name=None, shortlist=False, hide=False,
            aliases=()):
    global _dispatcher
    if not _dispatcher:
        _dispatcher = Dispatcher()
    return _dispatcher.command(options=options, usage=usage, name=name,
                               shortlist=shortlist, hide=hide, aliases=aliases)
command.__doc__ = Dispatcher.command.__doc__


def dispatch(args=None, cmdtable=None, globaloptions=None, middleware=None,
             scriptname=None):
    global _dispatcher
    if not _dispatcher:
        _dispatcher = Dispatcher(cmdtable, globaloptions, middleware)
    else:
        if cmdtable:
            _dispatcher._cmdtable = CmdTable(cmdtable)
        if globaloptions:
            _dispatcher._globaloptions = [Option(o) for o in globaloptions]
        if middleware:
            _dispatcher.middleware = middleware
    return _dispatcher.dispatch(args, scriptname)
dispatch.__doc__ = Dispatcher.dispatch.__doc__


# --------
# Help
# --------

def help_(cmdtable, globalopts, scriptname):
    '''Help generator for a command table.
    '''
    def help_inner(name=None, *args, **opts):
        '''Show help for a given help topic or a help overview.

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

            write('usage: %s <command> [options]' % scriptname)
            write('\ncommands:\n')
            for cmd in hlplist:
                doc = hlp[cmd]
                write(' %-*s  %s' % (maxlen, cmd.split('|', 1)[0], doc))

        if not cmdtable:
            return err('No commands specified!')

        if not name or name == 'shortlist':
            return helplist()

        aliases, (cmd, options, usage) = findcmd(name, cmdtable)

        if isinstance(cmd, Dispatcher):
            recurse = help_(cmd.cmdtable, globalopts, scriptname + ' ' + name)
            return recurse(*args, **opts)

        options = list(options)
        merge_globalopts(globalopts, options)

        return help_cmd(cmd, usage, options, aliases[1:],
                        scriptname + ' ' + aliases[0])

    return help_inner


def help_cmd(func, usage, options, aliases, scriptname=None):
    '''Show help for given command.

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
    >>> help_cmd(test, '%name [-l HOST] [NAME]', opts, (), 'test')
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
    options = [Option(o) for o in options]  # only for doctest
    usage = replace_name(usage, scriptname)
    write(usage)
    if aliases:
        write('\naliases: ' + ', '.join(aliases))
    doc = pretty_doc_string(func)
    write('\n' + doc.strip() + '\n')
    for line in help_options(options):
        write(line)


def help_options(options):
    '''Generator for help on options.
    '''
    yield 'options:\n'
    output = []
    for o in options:
        default = o.default_value()
        default = default and ' (default: %s)' % default or ''
        output.append(('%2s%s' % (o.short and '-%s' % o.short,
                                  o.name and ' --%s' % o.name),
                       '%s%s' % (o.helpmsg, default)))

    opts_len = max([len(first) for first, second in output if second] or [0])
    for first, second in output:
        if second:
            # wrap description at 78 chars
            second = textwrap.wrap(second, width=(78 - opts_len - 3))
            pad = '\n' + ' ' * (opts_len + 3)
            yield ' %-*s  %s' % (opts_len, first, pad.join(second))
        else:
            yield ' %s' % first


# --------
# Options process
# --------

def merge_globalopts(globalopts, opts):
    '''Merge the global options with the subcommand options'''
    for o in globalopts:
        # Don't include global option if long name matches
        if any((x.name == o.name for x in opts)):
            continue
        # Don't use global option short name if already used
        if any((x.short and x.short == o.short for x in opts)):
            o = o._replace(short='')
        opts.append(o)

# Factory for creating _Option instances. Intended to be the entry point to
# the *Option classes here.
def Option(opt):
    '''Create Option instance from tuple of option data.'''
    if isinstance(opt, BaseOption):
        return opt

    # Extract and validate contents of tuple
    short, name, default, helpmsg = opt[:4]
    completer = opt[4] if len(opt) > 4 else None
    if short and len(short) != 1:
        raise OpsterError(
            'Short option should be only a single character: %s' % short)
    if not name:
        raise OpsterError(
            'Long name should be defined for every option')
    pyname = name_to_python(name)

    args = pyname, name, short, default, helpmsg, completer

    # Find matching _Option subclass and return instance
    # nb. the order of testing matters
    for Type in (BoolOption, ListOption, DictOption, FuncOption,
                 TupleOption, UnicodeOption, LiteralOption):
        if Type.matches(default):
            return Type(*args)
    raise OpsterError('Cannot figure out type for option %s' % name)

def CmdTable(cmdtable):
    '''Factory to convert option tuples in a cmdtable'''
    newtable = {}
    for name, (func, opts, usage) in cmdtable.items():
        newtable[name] = (func, [Option(o) for o in opts], usage)
    return newtable

# Superclass for all option classes
class BaseOption(namedtuple('Option', (
            'pyname', 'name', 'short', 'default', 'helpmsg', 'completer'))):
    has_parameter = True
    type = None

    def __repr__(self):
        return (super(BaseOption, self).__repr__()
                .replace('Option', self.__class__.__name__, 1))

    @classmethod
    def matches(cls, default):
        '''Returns True if this is appropriate Option for the default value.'''
        return isinstance(default, cls.type)

    def default_state(self):
        '''Generate initial state value from provided default value.'''
        return self.default

    def update_state(self, state, new):
        '''Update state after encountering an option on the command line.'''
        return new

    def convert(self, final):
        '''Generate the resulting python value from the final state.'''
        return final

    def default_value(self):
        '''Shortcut to obtain the default value when option arg not provided.'''
        return self.convert(self.default_state())


class LiteralOption(BaseOption):
    '''Literal option type (including string, int, float, etc.)'''
    type = object

    def convert(self, final):
        '''Generate the resulting python value from the final state.'''
        if final is self.default:
            return final
        else:
            return type(self.default)(final)


class UnicodeOption(BaseOption):
    '''Handle unicode values, decoding input'''
    type = unicode

    def convert(self, final):
        return decodearg(final)


class BoolOption(BaseOption):
    '''Boolean option type.'''
    has_parameter = False
    type = (bool, types.NoneType)

    def convert(self, final):
        return bool(final)

    def update_state(self, state, new):
        return not self.default


class ListOption(BaseOption):
    '''List option type.'''
    type = list

    def default_state(self):
        return list(self.default)

    def update_state(self, state, new):
        state.append(new)
        return state


class DictOption(BaseOption):
    '''Dict option type.'''
    type = dict

    def default_state(self):
        return dict(self.default)

    def update_state(self, state, new):
        try:
            k, v = new.split('=')
        except ValueError:
            msg = "wrong definition: %r (should be in format KEY=VALUE)"
            raise getopt.GetoptError(msg % new)
        state[k] = v
        return state


class TupleOption(BaseOption):
    '''Tuple option type.'''
    type = tuple

    def __init__(self, *args, **kwargs):
        self._option = Option(('', '_', self.default[0], ''))

    def default_state(self):
        return self._option.default

    def update_state(self, state, new):
        return self._option.update_state(state, new)

    def convert(self, final):
        finalval = self._option.convert(final)
        if finalval not in self.default:
            msg = "unrecognised value: %r (should be one of %s)"
            msg = msg % (final, ', '.join(str(v) for v in self.default))
            raise getopt.GetoptError(msg)
        return finalval


class FuncOption(BaseOption):
    '''Function option type.'''
    type = Callable

    def default_state(self):
        return None

    def convert(self, final):
        return self.default(final)


def process(args, options):
    '''
    >>> opts = [('l', 'listen', 'localhost',
    ...          'ip to listen on'),
    ...         ('p', 'port', 8000,
    ...          'port to listen on'),
    ...         ('d', 'daemonize', False,
    ...          'daemonize process'),
    ...         ('', 'pid-file', '',
    ...          'name of file to write process ID to')]
    >>> x = process(['-l', '0.0.0.0', '--pi', 'test', 'all'], opts)
    >>> x == (['all'], {'pid_file': 'test', 'daemonize': False, 'port': 8000, 'listen': '0.0.0.0'})
    True
    '''
    options = [Option(o) for o in options]  # only for doctest

    # Parse arguments and options
    args, opts = getopts(args, options)

    # Default values
    state = dict((o.pyname, o.default_state()) for o in options)

    # Update for each option on the command line
    for o, val in opts:
        state[o.pyname] = o.update_state(state[o.pyname], val)

    # Convert to required type
    for o in options:
        try:
            state[o.pyname] = o.convert(state[o.pyname])
        except ValueError:
            raise getopt.GetoptError('invalid option value %r for option %r'
                % (state[o.pyname], o.name))

    return args, state


def getopts(args, options, preparse=False):
    '''Parse args and options from raw args.

    If preparse is True, option processing stops at first non-option.
    '''
    argmap = {}
    shortlist, namelist = '', []
    for o in options:
        argmap['-' + o.short] = argmap['--' + o.name] = o

        # getopt wants indication that it takes a parameter
        short, name = o.short, o.name
        if o.has_parameter:
            if short:
                short += ':'
            name += '='
        if short:
            shortlist += short
        namelist.append(name)

    # gnu_getopt will stop at first non-option argument
    if preparse:
        shortlist = '+' + shortlist

    # getopt.gnu_getopt allows options after the first non-option
    opts, args = getopt.gnu_getopt(args, shortlist, namelist)

    # map the option argument names back to their Option instances
    opts = [(argmap[opt], val) for opt, val in opts]

    return args, opts

# --------
# Subcommand system
# --------

def cmdparse(args, cmdtable, globalopts):
    '''Parse arguments list to find a command, options and arguments.
    '''
    # pre-parse arguments here using global options to find command name,
    # which is first non-option entry
    args_new, opts = getopts(args, globalopts, preparse=True)

    args = list(args)
    if args_new:
        cmdarg = args_new[0]
        args.remove(cmdarg)
        aliases, info = findcmd(cmdarg, cmdtable)
        cmd = aliases[0]
        possibleopts = list(info[1])
        merge_globalopts(globalopts, possibleopts)
        return cmd, info[0] or None, args, possibleopts
    else:
        return None, None, args, globalopts


def aliases_(cmdtable_key):
    '''Get aliases from a command table key.'''
    return cmdtable_key.lstrip("^~").split("|")


def findpossible(cmd, table):
    '''Return cmd -> (aliases, command table entry) for each matching command.
    '''
    pattern = '.*?'.join(list(cmd))
    choice = {}
    for e in table.keys():
        aliases = aliases_(e)
        found = None
        if cmd in aliases:
            found = cmd
        else:
            for a in aliases:
                if re.search(pattern, a):
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

    Or, if you are using Python 3.x, you can declare them as keyword-only:

    def func(*, longname=(shortname, default, help)):
        pass

    See docstring of ``command()`` for description of those variables.
    '''
    try:
        args, _, _, defaults = inspect.getargspec(func)
        options = guess_options_py2(args, defaults)
    except ValueError: # has keyword-only arguments
        spec = inspect.getfullargspec(func)
        options = guess_options_py3(spec)
    for name, option in options:
        if isinstance(option, tuple):
            yield (option[0], name_from_python(name)) + option[1:]


def guess_options_py2(args, defaults):
    for name, option in zip(args[-len(defaults):], defaults):
        yield name, option

def guess_options_py3(spec):
    '''Get options definitions from spec with keyword-only arguments
    '''
    if spec.args and spec.defaults:
        for o in guess_options_py2(spec.args, spec.defaults):
            yield o
    for name in spec.kwonlyargs:
        option = spec.kwonlydefaults[name]
        yield name, option


def guess_usage(func, options):
    '''Get usage definition for a function
    '''
    usage = ['%name']
    if options:
        usage.append('[OPTIONS]')
    try:
        arginfo = inspect.getargspec(func)
    except ValueError: # keyword-only args
        arginfo = inspect.getfullargspec(func)
    optnames = [o.name for o in options]
    nonoptional = len(arginfo.args) - len(arginfo.defaults or ())

    for i, arg in enumerate(arginfo.args):
        if name_from_python(arg) not in optnames:
            usage.append((i > nonoptional - 1 and '[%s]' or '%s')
                         % arg.upper())

    if arginfo.varargs:
        usage.append('[%s ...]' % arginfo.varargs.upper())
    return ' '.join(usage)


@contextmanager
def help_workaround(func, scriptname, help_func=None):
    '''Context manager to temporarily replace func.help'''
    # Retrieve inner if function is command wrapped
    func = getattr(func, '_inner', func)

    # Ignore function that was not command wrapped
    if not hasattr(func, 'help'):
        yield
        return

    # Wrap the with block with a replaced help function
    help = func.help
    help_func = help_func or help
    try:
        func.help = lambda: help_func(scriptname)
        yield
    finally:
        func.help = help


@contextmanager
def exchandle(help_func, cmd=None):
    '''Context manager to turn internal exceptions into printed help messages.

    Handles internal opster exceptions by printing help and raising
    ErrorHandled. Other exceptions are propagated.
    '''
    try:
        yield  # execute the block in the 'with' statement
        return
    except UnknownCommand as e:
        err("unknown command: '%s'" % e)
    except AmbiguousCommand as e:
        err("command '%s' is ambiguous:\n    %s" %
            (e.args[0], ' '.join(e.args[1])))
    except ParseError as e:
        err('%s: %s\n' % (e.args[0], e.args[1].strip()))
        help_func(cmd)
    except getopt.GetoptError as e:
        err('error: %s\n' % e)
        help_func(cmd)
    except OpsterError as e:
        err('%s' % e)
    # abort if a handled exception was raised
    raise ErrorHandled()


def call_cmd(name, func, opts, middleware=None):
    '''Wrapper for command call, catching situation with insufficient arguments.
    '''
    # depth is necessary when there is a middleware in setup
    try:
        arginfo = inspect.getargspec(func)
    except ValueError:
        arginfo = inspect.getfullargspec(func)
    if middleware:
        tocall = middleware(func)
        depth = 2
    else:
        tocall = func
        depth = 1

    def inner(*args, **kwargs):
        # NOTE: this is not very nice, but it fixes problem with
        # TypeError: func() got multiple values for 'argument'
        # Would be nice to find better way
        prepend = []
        start = None
        if arginfo.varargs and len(args) > (len(arginfo.args) - len(kwargs)):
            for o in opts:
                if o.pyname in arginfo.args:
                    if start is None:
                        start = arginfo.args.index(o.pyname)
                    prepend.append(o.pyname)
            if start is not None:  # do we have to prepend anything
                args = (args[:start] +
                        tuple(kwargs.pop(x) for x in prepend) +
                        args[start:])

        try:
            return tocall(*args, **kwargs)
        except TypeError:
            if len(traceback.extract_tb(sys.exc_info()[2])) == depth:
                raise ParseError(name, "invalid arguments")
            raise
    return inner


def call_cmd_regular(func, opts):
    '''Wrapper for command for handling function calls from Python.
    '''
    # This would raise an error if there were any keyword-only arguments
    try:
        arginfo = inspect.getargspec(func)
    except ValueError:
        return call_cmd_regular_py3k(func, opts)

    def inner(*args, **kwargs):
        # Map from argument names to Option instances
        opt_args = dict((o.pyname, o) for o in opts)

        # Pull any recognised args out of kwargs and splice them with the
        # positional arguments to give a flat positional arg list
        remaining = list(args)
        args = []
        defaults_offset = len(arginfo.args) - len(arginfo.defaults or [])
        for n, argname in enumerate(arginfo.args):
            # Option arguments MUST be given as keyword arguments
            if argname in opt_args:
                if argname in kwargs:
                    argval = kwargs.pop(argname)
                else:
                    argval = opt_args[argname].default_value()
            # Take a positional argument
            elif remaining:
                argval = remaining.pop(0)
            # Find the default value of the positional argument
            elif n >= defaults_offset:
                argval = arginfo.defaults[n - defaults_offset]
            else:
                raise TypeError('Not enough positional arguments')
            # Accumulate the args in order
            args.append(argval)

        # Combine the remaining positional arguments that go to varargs
        args = args + remaining

        # kwargs is any keyword arguments that were not recognised as options
        return func(*args, **kwargs)

    return inner

def call_cmd_regular_py3k(func, opts):
    '''call_cmd_regular for functions with keyword only arguments'''
    spec = inspect.getfullargspec(func)

    def inner(*args, **kwargs):

        # Replace the option arguments with their default values
        for o in opts:
            if o.pyname not in kwargs:
                kwargs[o.pyname] = o.default_value()

        return func(*args, **kwargs)

    return inner

def replace_name(usage, name):
    '''Replace name placeholder with a command name.'''
    if '%name' in usage:
        return usage.replace('%name', name, 1)
    return name + ' ' + usage


def sysname():
    '''Returns name of executing file.'''
    return os.path.basename(sys.argv[0])


def pretty_doc_string(item):
    '''Doc string with adjusted indentation level of the 2nd line and beyond.'''
    raw_doc = item.__doc__ or '(no help text available)'
    lines = raw_doc.strip().splitlines()
    if len(lines) <= 1:
        return raw_doc
    indent = len(lines[1]) - len(lines[1].lstrip())
    return '\n'.join([lines[0]] + map(lambda l: l[indent:], lines[1:]))


def name_from_python(name):
    if name.endswith('_') and keyword.iskeyword(name[:-1]):
        name = name[:-1]
    return name.replace('_', '-')


def name_to_python(name):
    name = name.replace('-', '_')
    if keyword.iskeyword(name):
        return name + '_'
    return name


# --------
# Autocomplete system
# --------

# Borrowed from PIP
def autocomplete(cmdtable, args, middleware):
    '''Command and option completion.

    Enable by sourcing one of the completion shell scripts (bash or zsh).
    '''

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
            short = '-%s' % o.short
            name = '--%s' % o.name
            options += [short, name]

            completer = o.completer
            if cwords[idx] in (short, name) and completer:
                if middleware:
                    completer = middleware(completer)
                args = completer(current)
                print ' '.join(args),

        print ' '.join((o for o in options if o.startswith(current)))

    sys.exit(1)


COMPLETIONS = {
    'bash':
        '''
# opster bash completion start
_opster_completion()
{
    COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   OPSTER_AUTO_COMPLETE=1 $1 ) )
}
complete -o default -F _opster_completion %s
# opster bash completion end
''',
    'zsh':
            '''
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
'''
    }


@command(name='_completion', hide=True)
def completion(type=('t', 'bash', 'Completion type (bash or zsh)'),
               # kwargs will catch every global option, which we get
               # anyway, because middleware is skipped
               **kwargs):
    '''Outputs completion script for bash or zsh.'''

    prog_name = os.path.split(sys.argv[0])[1]
    print COMPLETIONS[type].strip() % prog_name


# --------
# Exceptions
# --------

class OpsterError(Exception):
    'Base opster exception'


class AmbiguousCommand(OpsterError):
    'Raised if command is ambiguous'


class UnknownCommand(OpsterError):
    'Raised if command is unknown'


class ParseError(OpsterError):
    'Raised on error in command line parsing'


class QuitError(OpsterError):
    'Raised to exit script with a message to the user'


class ErrorHandled(OpsterError):
    'Raised to signal that opster is aborting the command'


# API to expose QuitError for opster users
command.Error = QuitError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
