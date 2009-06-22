import sys, traceback, getopt
from itertools import imap

from fancyopts import parse, cmd_help

def help_(ui, cmdtable, globalopts, name=None):
    def helplist():
        hlp = {}
        # determine if there any command marked for shortlist
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
                ui.write(' %-*s  %s\n' % (maxlen, cmd.split('|', 1)[0], doc))

    if not cmdtable:
        return ui.warn('No commands specified!\n')

    if not name or name == 'shortlist':
        return helplist()

    cmd, options, usage = cmdtable[name]
    return cmd_help(cmd, name + ': ' + usage, options)


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
            ('', 'traceback', False, 'display full traceback on error')]

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
        help_(ui, cmdtable, globalopts, e.args[0])
    except KeyboardInterrupt:
        ui.warn('interrupted!\n')
    except:
        ui.warn('unknown exception encountered')
        raise

    return -1

def _dispatch(ui, args, cmdtable, globalopts):
    cmd, func, args, options, globaloptions = cmdparse(args, cmdtable,
                                                       globalopts)

    ui.verbose = globaloptions['verbose']
    ui.quiet = globaloptions['quiet']

    if globaloptions['help']:
        pass # help
    elif not cmd:
        return help_(ui, cmdtable, globalopts, 'shortlist')

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
        possibleargs = list(info[1])
    else:
        possibleargs = []

    possibleargs.extend(globalopts)

    try:
        options, args = parse(args, possibleargs)
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
        self.quiet = quiet

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

