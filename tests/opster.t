.. -*- mode: rst -*-

==============
 Opster tests
==============

This is a test suite for opster library. Just read it to get some idea of how it
works.

.. highlight:: console

Actors cast
-----------

Define function to make it simpler::

  $ run() {
  >   name=$1
  >   shift
  >   export PYTHONPATH=$TESTDIR/../
  >   export COVERAGE_FILE=$TESTDIR/coverage.db
  >   if [ -z "$COVERAGE" ]; then
  >      python "$TESTDIR/$name" "$@"
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


Another things should be checked: calling help display from the function
itself::

  $ run selfhelp.py --assist
  selfhelp.py [OPTIONS]
  
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


.. _multivalues:

There is no problems with ``TypeError: function() got multiple values for
keyword argument 'option'``::

  $ run multivalueserr.py some arguments hehe
  I work! False bopt some arguments ('hehe',)

Scripts can exit with an error message at any time by raising
``command.Error``::

  $ run quit.py --algorithm=quick
  unrecognised algorithm "quick"

That's all for today; see you next time!

.. _varargs:

There is no problems with handling variable argumentrs and underscores::

  $ run varargs.py --test-option test1 var1 var2
  {'args': ('var1', 'var2'), 'test_option': 'test1'}
  $ run varargs.py var1 var2
  {'args': ('var1', 'var2'), 'test_option': 'test'}
