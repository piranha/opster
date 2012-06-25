.. -*- mode: rst -*-

==============
 Opster tests
==============

This is a test suite for opster library. Just read it to get some idea of how it
works.

.. highlight:: console

Actors cast
-----------

Choose python version::

  $   if [ -z "$PYTHON" ]; then
  >      PYTHON="python"
  >   fi

Add opster to the PYTHONPATH::

  $   if [ -z "$OPSTER_DIR" ]; then
  >      OPSTER_DIR="$TESTDIR/.."
  >   fi
  >   export PYTHONPATH="$OPSTER_DIR"

Define function to make it simpler::

  $ run() {
  >   name=$1
  >   shift
  >   export COVERAGE_FILE=$TESTDIR/coverage.db
  >   if [ -z "$COVERAGE" ]; then
  >      "$PYTHON" "$TESTDIR/$name" "$@"
  >   else
  >      coverage run -a --rcfile="$TESTDIR/../.coveragerc" "$TESTDIR/$name" "$@"
  >   fi
  > }

Main characters:

* `multicommands.py <http://hg.piranha.org.ua/opster/file/tip/tests/multicommands.py>`_
* `test_opts.py <http://hg.piranha.org.ua/opster/file/tip/tests/test_opts.py>`_


Action
------

Check if usage is working::

  $ run multicommands.py
  usage: multicommands.py <command> [options]
  
  commands:
  
   nodoc   (no help text available)
   simple  Just simple command to print keys of received arguments.


Ok, then let's run it::

  $ run multicommands.py simple
  ['test', 'ui']

.. _multihelp1:

Yeah, nice one, but we know that command ``complex`` is just hidden there. Let's
check it out::

  $ run multicommands.py help complex
  multicommands.py complex [-p] [--exit value] ...
  
  That's more complex command intended to do something
  
      \xd0\x98 \xd1\x81\xd0\xb0\xd0\xbc\xd0\xbe\xd0\xb5 \xd0\xb3\xd0\xbb\xd0\xb0\xd0\xb2\xd0\xbd\xd0\xbe\xd0\xb5 - \xd0\xbc\xd1\x8b \xd1\x82\xd1\x83\xd1\x82 \xd0\xbd\xd0\xb5\xd0\xbc\xd0\xbd\xd0\xbe\xd0\xb6\xd0\xb5\xd1\x87\xd0\xba\xd0\xbe \xd1\x82\xd0\xb5\xd0\xba\xd1\x81\xd1\x82\xd0\xb0 \xd0\xbd\xd0\xb5 \xd0\xb2 ascii \xd0\xbd\xd0\xb0\xd0\xbf\xd0\xb8\xd1\x88\xd0\xb5\xd0\xbc (esc)
      \xd0\xb8 \xd0\xbf\xd0\xbe\xd1\x81\xd0\xbc\xd0\xbe\xd1\x82\xd1\x80\xd0\xb8\xd0\xbc, \xd1\x87\xd1\x82\xd0\xbe \xd0\xb1\xd1\x83\xd0\xb4\xd0\xb5\xd1\x82. :) (esc)
  
  options:
  
   -p --pass     don't run the command
      --exit     exit with supplied code (default: 100)
   -n --name     optional name
   -v --verbose  enable additional output
   -q --quiet    suppress output
   -h --help     display help

Check if integer errors correctly::

  $ run multicommands.py complex --exit q
  error: invalid option value 'q' for option 'exit'
  
  multicommands.py complex [-p] [--exit value] ...
  
  That's more complex command intended to do something
  
      \xd0\x98 \xd1\x81\xd0\xb0\xd0\xbc\xd0\xbe\xd0\xb5 \xd0\xb3\xd0\xbb\xd0\xb0\xd0\xb2\xd0\xbd\xd0\xbe\xd0\xb5 - \xd0\xbc\xd1\x8b \xd1\x82\xd1\x83\xd1\x82 \xd0\xbd\xd0\xb5\xd0\xbc\xd0\xbd\xd0\xbe\xd0\xb6\xd0\xb5\xd1\x87\xd0\xba\xd0\xbe \xd1\x82\xd0\xb5\xd0\xba\xd1\x81\xd1\x82\xd0\xb0 \xd0\xbd\xd0\xb5 \xd0\xb2 ascii \xd0\xbd\xd0\xb0\xd0\xbf\xd0\xb8\xd1\x88\xd0\xb5\xd0\xbc (esc)
      \xd0\xb8 \xd0\xbf\xd0\xbe\xd1\x81\xd0\xbc\xd0\xbe\xd1\x82\xd1\x80\xd0\xb8\xd0\xbc, \xd1\x87\xd1\x82\xd0\xbe \xd0\xb1\xd1\x83\xd0\xb4\xd0\xb5\xd1\x82. :) (esc)
  
  options:
  
   -p --pass     don't run the command
      --exit     exit with supplied code (default: 100)
   -n --name     optional name
   -v --verbose  enable additional output
   -q --quiet    suppress output
   -h --help     display help

Opster can parse non-global options after the command argument::

  $ run multicommands.py complex --name dave
  write
  info
  warn
  [100]

We also get the right command when using --opt=value syntax::

  $ run multicommands.py complex --name=dave
  write
  info
  warn
  [100]

Global options can appear before the command argument.

  $ run multicommands.py --quiet complex
  write
  warn
  [100]

However, non-global options before the command argument are not allowed::

  $ run multicommands.py --name=dave complex
  error: option --name not recognized
  
  usage: multicommands.py <command> [options]
  
  commands:
  
   help    Show help for a given help topic or a help overview.
   nodoc   (no help text available)
   simple  Just simple command to print keys of received arguments.

regardless of which syntax you use::

  $ run multicommands.py --name dave complex
  error: option --name not recognized
  
  usage: multicommands.py <command> [options]
  
  commands:
  
   help    Show help for a given help topic or a help overview.
   nodoc   (no help text available)
   simple  Just simple command to print keys of received arguments.

Opster won't accidentally run the simple command because you tried to pass
simple as an argument to the --name option::

  $ run multicommands.py --name simple complex
  error: option --name not recognized
  
  usage: multicommands.py <command> [options]
  
  commands:
  
   help    Show help for a given help topic or a help overview.
   nodoc   (no help text available)
   simple  Just simple command to print keys of received arguments.

We also have completion::

  $ run multicommands.py _completion
  # opster bash completion start
  _opster_completion()
  {
      COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \
                     COMP_CWORD=$COMP_CWORD \
                     OPSTER_AUTO_COMPLETE=1 $1 ) )
  }
  complete -o default -F _opster_completion multicommands.py
  # opster bash completion end


Now we're going to test if a script with a single command will work (not
everyone needs subcommands, you know)::

  $ run test_opts.py
  test_opts.py: invalid arguments
  
  test_opts.py [-l HOST] DIR
  
  Command with option declaration as keyword arguments
  
  options:
  
   -l --listen       ip to listen on (default: localhost)
   -p --port         port to listen on (default: 8000)
   -d --daemonize    daemonize process
      --pid-file     name of file to write process ID to
   -D --definitions  just some definitions
   -t --test         testing help for a function (default: test)
   -h --help         display help


Yeah, I've got it, I should supply some arguments::

  $ run test_opts.py -d -p 5656 --listen anywhere right-here
  {'daemonize': True,
   'definitions': {},
   'dirname': 'right-here',
   'listen': 'anywhere',
   'pid_file': '',
   'port': 5656,
   'test': 'test'}

.. _definitions-test:

Now let's test our definitions::

  $ run test_opts.py -D a=b so-what?
  {'daemonize': False,
   'definitions': {'a': 'b'},
   'dirname': 'so-what?',
   'listen': 'localhost',
   'pid_file': '',
   'port': 8000,
   'test': 'test'}

As long as only the last option has a parameter We can combine short options
into one argument::

  $ run test_opts.py -dDa=b so-what?
  {'daemonize': True,
   'definitions': {'a': 'b'},
   'dirname': 'so-what?',
   'listen': 'localhost',
   'pid_file': '',
   'port': 8000,
   'test': 'test'}

The parameter can be in a separate argument::

  $ run test_opts.py -dD a=b so-what?
  {'daemonize': True,
   'definitions': {'a': 'b'},
   'dirname': 'so-what?',
   'listen': 'localhost',
   'pid_file': '',
   'port': 8000,
   'test': 'test'}

  $ run test_opts.py -D can-i-haz fail?
  error: wrong definition: 'can-i-haz' (should be in format KEY=VALUE)
  
  test_opts.py [-l HOST] DIR
  
  Command with option declaration as keyword arguments
  
  options:
  
   -l --listen       ip to listen on (default: localhost)
   -p --port         port to listen on (default: 8000)
   -d --daemonize    daemonize process
      --pid-file     name of file to write process ID to
   -D --definitions  just some definitions
   -t --test         testing help for a function (default: test)
   -h --help         display help


Should we check passing some invalid arguments? I think so::

  $ run test_opts.py --wrong-option
  error: option --wrong-option not recognized
  
  test_opts.py [-l HOST] DIR
  
  Command with option declaration as keyword arguments
  
  options:
  
   -l --listen       ip to listen on (default: localhost)
   -p --port         port to listen on (default: 8000)
   -d --daemonize    daemonize process
      --pid-file     name of file to write process ID to
   -D --definitions  just some definitions
   -t --test         testing help for a function (default: test)
   -h --help         display help


Lets try some extended option types::

  $ run test_extopts.py -h
  test_extopts.py [OPTIONS]
  
  Command using extended option types
  
  options:
  
   -m --money  amount of money (default: 100.00)
   -r --ratio  input/output ratio (default: 1/4)
   -h --help   display help

  $ run test_extopts.py
  money: <class 'decimal.Decimal'> 100.00
  ratio: <class 'fractions.Fraction'> 1/4

  $ run test_extopts.py --money=-.12 --ratio='5/6'
  money: <class 'decimal.Decimal'> -0.12
  ratio: <class 'fractions.Fraction'> 5/6

Another things should be checked: calling help display from the function
itself::

  $ run selfhelp.py --assist
  selfhelp [OPTIONS]
  
  Displays ability to show help
  
  options:
  
      --assist  show help
   -h --help    display help


.. _multihelp2:

Are we getting nicely stripped body when not following subject/body convention
of writing commands?

::

  $ run hello.py --help
  hello.py [OPTIONS] NAME [TIMES]
  
  Hello world continues the long established tradition
  of delivering simple, but working programs in all
  kinds of programming languages.
  
  This tests different docstring formatting (just text instead of having
  subject and body).
  
  options:
  
   -g --greeting  Greeting to use (default: Hello)
   -h --help      display help


There is no problems with having required and optional arguments at the same
time::

  $ run hello.py stranger
  Hello stranger
  $ run hello.py stranger 2 -g 'Good bye'
  Good bye stranger
  Good bye stranger
  $ run hello.py stranger -g 'Good bye' 2
  Good bye stranger
  Good bye stranger


And there is no problems handling unicode data::

  $ OPSTER_ARG_ENCODING=utf-8 run hello.py кросавчег -g Привет
  \xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82 \xd0\xba\xd1\x80\xd0\xbe\xd1\x81\xd0\xb0\xd0\xb2\xd1\x87\xd0\xb5\xd0\xb3 (esc)


.. _multivalues:

There is no problems with ``TypeError: function() got multiple values for
keyword argument 'option'``::

  $ run multivalueserr.py some arguments hehe
  I work! False bopt some arguments ('hehe',)

Opster can give helpful error messages if arguments are invalid::

  $ run quit.py --help
  quit.py [OPTIONS]
  
  script that uses different algorithms and numbers of cpus
  
  options:
  
   -a --algo1  algorithm: slow or fast (default: fast)
   -A --algo2  algorithm: slow or fast (default: slow)
   -n --ncpus  number of cpus to use (default: 1)
   -h --help   display help

Scripts can exit with a user-defined error message at any time by raising
``command.Error``::

  $ run quit.py --algo1=quick
  unrecognised algorithm "quick"

Or arguments can be rejected because they are not in a tuple::

  $ run quit.py --algo2=quick
  error: unrecognised value: 'quick' (should be one of slow, fast)
  
  quit.py [OPTIONS]
  
  script that uses different algorithms and numbers of cpus
  
  options:
  
   -a --algo1  algorithm: slow or fast (default: fast)
   -A --algo2  algorithm: slow or fast (default: slow)
   -n --ncpus  number of cpus to use (default: 1)
   -h --help   display help

  $ run quit.py --ncpus=-1
  error: unrecognised value: '-1' (should be one of 1, 2, 3, 4)
  
  quit.py [OPTIONS]
  
  script that uses different algorithms and numbers of cpus
  
  options:
  
   -a --algo1  algorithm: slow or fast (default: fast)
   -A --algo2  algorithm: slow or fast (default: slow)
   -n --ncpus  number of cpus to use (default: 1)
   -h --help   display help

Just check that the tuple options work when there's no error::

  $ run quit.py --algo1=fast --algo2=slow --ncpus=3
  algo1: fast
  algo2: slow
  ncpus: 3


That's all for today; see you next time!

.. _varargs:

There is no problems with handling variable argumentrs and underscores::

  $ run varargs.py --test-option test1 var1 var2
  {'args': ('var1', 'var2'), 'test_option': 'test1'}
  $ run varargs.py var1 var2
  {'args': ('var1', 'var2'), 'test_option': 'test'}

We should check that we can still run opster scripts written using the old
API::

  $ run oldapi.py help
  usage: oldapi.py <command> [options]
  
  commands:
  
   cmd1  (no help text available)
   cmd2  (no help text available)
   help  Show help for a given help topic or a help overview.
  $ run oldapi.py cmd1
  Not being quiet!
  $ run oldapi.py cmd2 --verbose 1 2 3
  1
  2
  3

We can have an option that uses the '-h' short name (although we use it as a
short name for '--help'::

  $ run ls.py --help
  ls [-h]
  
  (no help text available)
  
  options:
  
   -h --human  Pretty print filesizes
      --nohelp1
   -n --nohelp2
      --help   display help

Let's just check that the scriptname argument ``scriptname='ls'`` works as
expected for the error messages::

  $ run ls.py invalid
  ls: invalid arguments
  
  ls [-h]
  
  (no help text available)
  
  options:
  
   -h --human  Pretty print filesizes
      --nohelp1
   -n --nohelp2
      --help   display help

  $ run ls.py --invalid
  error: option --invalid not recognized
  
  ls [-h]
  
  (no help text available)
  
  options:
  
   -h --human  Pretty print filesizes
      --nohelp1
   -n --nohelp2
      --help   display help


We can also supply the ``scriptname`` argument to ``dispatch``::

  $ run scriptname.py
  usage: newname <command> [options]
  
  commands:
  
   cmd   (no help text available)
   help  Show help for a given help topic or a help overview.

  $ run scriptname.py help
  usage: newname <command> [options]
  
  commands:
  
   cmd   (no help text available)
   help  Show help for a given help topic or a help overview.

  $ run scriptname.py help cmd
  newname cmd [-h]
  
  (no help text available)
  
  options:
  
   -h --help  display help

  $ run scriptname.py cmd --help
  newname cmd [-h]
  
  (no help text available)
  
  options:
  
   -h --help  display help

  $ run scriptname.py cmd invalid
  cmd: invalid arguments
  
  newname cmd [-h]
  
  (no help text available)
  
  options:
  
   -h --help  display help

  $ run scriptname.py cmd --invalid
  error: option --invalid not recognized
  
  newname cmd [-h]
  
  (no help text available)
  
  options:
  
   -h --help  display help

It is possible to nest a dispatcher as a command within another dispatcher so
that we can have subsubcommands.

::

  $ run subcmds.py
  usage: subcmds.py <command> [options]
  
  commands:
  
   cmd   Help for cmd
   cmd2  (no help text available)
   help  Show help for a given help topic or a help overview.

  $ run subcmds.py help cmd
  usage: subcmds.py cmd <command> [options]
  
  commands:
  
   subcmd1  Help for subcmd1
   subcmd2  Help for subcmd2
   subcmd3  Help for subcmd3

  $ run subcmds.py cmd --help
  usage: subcmds.py cmd <command> [options]
  
  commands:
  
   help     Show help for a given help topic or a help overview.
   subcmd1  Help for subcmd1
   subcmd2  Help for subcmd2
   subcmd3  Help for subcmd3

  $ run subcmds.py cmd2 --help
  subcmds.py cmd2 [OPTIONS]
  
  (no help text available)
  
  options:
  
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd2 --showhelp
  Showing the help:
  subcmds.py cmd2 [OPTIONS]
  
  (no help text available)
  
  options:
  
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd subcmd1 --help
  subcmds.py cmd subcmd1 [OPTIONS]
  
  Help for subcmd1
  
  options:
  
   -q --quiet     quietly
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py help cmd subcmd1
  subcmds.py cmd subcmd1 [OPTIONS]
  
  Help for subcmd1
  
  options:
  
   -q --quiet     quietly
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd subcmd1
  running subcmd1

  $ run subcmds.py cmd subcmd1 --quiet

  $ run subcmds.py cmd subcmd1 --showhelp
  running subcmd1
  Showing the help:
  subcmds.py cmd subcmd1 [OPTIONS]
  
  Help for subcmd1
  
  options:
  
   -q --quiet     quietly
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd subcmd2
  subcmd2: invalid arguments
  
  subcmds.py cmd subcmd2 NUMBER
  
  Help for subcmd2
  
  options:
  
   -h --help  display help

  $ run subcmds.py cmd subcmd2 5
  running subcmd2 5

  $ run subcmds.py help cmd subcmd3
  usage: subcmds.py cmd subcmd3 <command> [options]
  
  commands:
  
   subsubcmd  Help for subsubcmd

  $ run subcmds.py help cmd subcmd3 --help
  subcmds.py help [TOPIC]
  
  Show help for a given help topic or a help overview.
  
          With no arguments, print a list of commands with short help messages.
  
          Given a command name, print help for that command.
  
  options:
  
   -h --help  display help

  $ run subcmds.py help cmd subcmd3 subsubcmd
  subcmds.py cmd subcmd3 subsubcmd [OPTIONS]
  
  Help for subsubcmd
  
  options:
  
   -l --loud      loudly
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd subcmd3 subsubcmd --help
  subcmds.py cmd subcmd3 subsubcmd [OPTIONS]
  
  Help for subsubcmd
  
  options:
  
   -l --loud      loudly
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd subcmd3 subsubcmd --showhelp
  Showing the help:
  subcmds.py cmd subcmd3 subsubcmd [OPTIONS]
  
  Help for subsubcmd
  
  options:
  
   -l --loud      loudly
   -h --showhelp  Print the help message
      --help      display help

  $ run subcmds.py cmd subcmd3 subsubcmd

  $ run subcmds.py cmd subcmd3 subsubcmd -l
  running subsubcmd

Check the `varargs` works when calling ```main``` directly::

  $ run varargs_py2.py
  
  main():
  TypeError raised
  
  main("a"):
  shop: a
  cheeses: ()
  music: False
  
  main("a", "b"):
  shop: a
  cheeses: ('b',)
  music: False
  
  main("a", "b", "c"):
  shop: a
  cheeses: ('b', 'c')
  music: False
  
  main(music=True):
  TypeError raised
  
  main("a", music=True):
  shop: a
  cheeses: ()
  music: True
  
  main("a", "b", music=True):
  shop: a
  cheeses: ('b',)
  music: True
  
  main("a", "b", "c", music=True):
  shop: a
  cheeses: ('b', 'c')
  music: True
