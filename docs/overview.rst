==========
 Overview
==========

Options
=======

Options are defined as keyword arguments to a script's main function::

  from opster import command

  @command(usage='[-l HOST] DIR')
  def main(dirname,
           listen=('l', 'localhost', 'ip to listen on'),
           port=('p', 8000, 'port to listen on'),
           daemonize=('d', False, 'daemonize process'),
           pid_file=('', '', 'name of file to write process ID to')):
      '''help message contained here'''
      pass

  if __name__ == '__main__':
      main.command()


Options contents
----------------

Each option is defined by a keyword argument, whose name is the long option
name (read :ref:`note <renaming-note>`) and whose default value is a 3-tuple
containing the elements:

1. short name
2. default value
3. help string

If a short name renders to False (for example, an empty string), then it's not
used at all.

.. _renaming-note:

If the keyword argument name contains underscores, they are converted to
dashes when generating the long option name since this is the typical
convention for command line applications. If the keyword argument name ends
with an underscore and is a python keyword, the trailing underscore will be
removed.

.. _options-processing:

Options processing
------------------

The default value for each option also determines how any values supplied for
the option should be parsed:

- string: the string is passed as is
- integer: the value is convert to an integer
- boolean/None: ``not default`` is passed and option takes no value
- function: function is called with value and the return value is used
- list: the value is appended to this list
- tuple: value is checked to be present in default value (i.e. tuple behaves
  as a list of choices)
- dictionary: the value is then assumed to be in the format ``key=value`` and
  is then assigned to this dictionary, :ref:`example <definitions-test>`

Note that only the boolean/None case results in an option that does not
require an argument.

Usage
-----

Running the python script above will trigger Opster's command line parsing
facility, using arguments from ``sys.argv``. ``sys.argv[0]`` will be prepended
to the usage string (you can put it in another place using macro ``%name`` in
the usage string).

In the case above simply running the script with no arguments will display
help, since the script has a required positional argument::

  > python example.py
  main: invalid arguments

  example.py [-l HOST] DIR

  help message contained here

  options:

   -l --listen     ip to listen on (default: localhost)
   -p --port       port to listen on (default: 8000)
   -d --daemonize  daemonize process
      --pid-file   name of file to write process ID to
   -h --help       display help

In general, to obtain help you can run the script with ``python example.py
--help`` or ``python example.py -h`` (unless ``-h`` is used as the short name
for another option).

You can parse command line strings programmatically, supplying a list of
arguments to ``.command()`` attribute of the decorated main function::

  main.command('-l 0.0.0.0 /my/dir'.split())

Or you still can use your function in python::

  main('/tmp', listen='0.0.0.0')

In this case no type conversion (which is done during argument parsing) will
be performed.

.. _subcommands:

Subcommands
===========

It's pretty common for a complex application to have a system of subcommands,
and Opster provides a facility for handling them. It's easy to define them::

  from opster import command, dispatch

  @command(usage='[-t]', shortlist=True)
  def simple(test=('t', False, 'just test execution')):
      '''
      Just a simple command to print keys of received arguments.
  
      I assure you! Nothing to see here. ;-)
      '''
      pass

  @command(usage='[-p] [--exit value] ...', name='complex', hide=True)
  def complex_(pass_=('p', False, "don't run the command"),
               exit=('', 100, 'exit with supplied code'),
               name=('n', '', 'optional name'),
               *args):
      '''This is a more complex command intended to do something'''
      pass

  if __name__ == '__main__':
      dispatch()

Your application will always also have the ``help`` command when it uses the
subcommand system.

Usage
-----

Usage is the same as with a single command, except that running without arguments
will display the shortlist of commands::

  > python multicommands.py
  usage: multicommands.py <command> [options]

  commands:

   simple  Just a simple command to print keys of received arguments.

Provided no commands have been marked with ``shortlist=True``, all commands
will be displayed (excluding those that have ``hide=True``). Also, you can run
``python multicommands.py help``, which will show the list of all commands
(still excluding hidden commands).

Using ``help command`` or ``command --help`` will display a help on this
command::

  > python multicommands.py help simple
  multicommands.py simple [-t]

  Just a simple command to print keys of received arguments.
  
      I assure you! Nothing to see here. ;-)

  options:

   -t --test     just test execution
   -h --help     display help

Global options
--------------

In case your application has options that every command should receive they
can be declared in the following format::

  options = [('v', 'verbose', False, 'enable additional output'),
             ('q', 'quiet', False, 'suppress output')]

Which is, obviously ``(shortname, longname, default, help)``.
             
They can then be passed to ``dispatch``::

  if __name__ == '__main__':
      dispatch(globaloptions=options)

Global options must have a different ``longname`` from any options used in a
subcommand. If a subcommand has an option with the same ``shortname`` as a
global option, then the ``shortname`` will be used for the subcommand option
(overriding the option in ``globaloptions``).

Global options can be used before the argument that names the subcommand::

  > python multicommands.py --quiet complex
  write
  warn
  [100]

This is useful since it enables a user to alias a script with something like::

  alias multi='python multicommands.py --quiet'

so that a global option is always enabled.
However, non-global options may not appear before the subcommand argument::

  > python multicommands.py --name=dave complex
  error: option --name not recognized
  
  usage: multicommands.py <command> [options]
  
  commands:
  
   help    Show help for a given help topic or a help overview.
   nodoc   (no help text available)
   simple  Just simple command to print keys of received arguments.

Inner structure
---------------

:ref:`@command <api-command>` and :ref:`@dispatch <api-dispatch>` are actually
aliases for internal :ref:`Dispatcher <api-dispatcher>` class. They assign and
dispatch on a global object ``opster._dispatcher``.

.. _partial-names:

Partial names
=============

Nice property of opster is that there is no need to type any option or
subcommand name completely. You are always free to use only first few letter of
name so opster can identify what are you trying to run.

For example, if we will use application created earlier, it's possible to call
it like this::

  app comp --ex 5

This means we're calling ``complex_``, passing 5 as an argument for option ``exit``.

.. _help-generation:

Help generation
===============

Help is generated automatically and is available by the ``-h/--help`` command
line option or by ``help`` subcommand (if you're using subcommand system).

It is generated from the usage string, the function docstring and the help
strings provided for each option and wrapped to length of 70 characters so it
looks
like::

  > python multicommands.py help complex
  multicommands.py complex: [-p] [--exit value] ...

  This is a more complex command intended to do something

  options:

   -p --pass  don't run the command
      --exit  exit with supplied code (default: 100)
   -n --name  optional name
   -h --help  show help

The default value is displayed here only if it does not evaluate as ``False``.
   
.. _innerhelp:

If you need to display help from inside your application, you can always use
the fact that the help-displaying function is attached to your decorated
function object, i.e.::

  @command()
  def something():
      if some_consequences:
          something.help()

See `an example from the tests`_.

.. _an example from the tests: http://hg.piranha.org.ua/opster/file/default/tests/selfhelp.py

Error messages
==============

Opster provides a mechanism to quit out of script execution returning a
message to the user: simply raise ``command.Error`` at any point. Opster will
catch the error and display its message to the script user. For example::

  from opster import command

  @command()
  def main(algorithm=('a', 'fast', 'algorithm: slow or fast')):
      '''
      script that uses two possible algorithms.
      '''
      if algorithm not in ('short', 'fast'):
          raise command.Error('unrecognised algorithm "{0}"'.format(algorithm))
      pass

  if __name__ == "__main__":
      main.command()

Now we can do::

  > python quit.py --algorithm=quick
  unrecognised algorithm "quick"
