==========
 Overview
==========

Options
=======

Options are defined as keyword arguments on a function::

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

Each option is a keyword argument, whose name is a long name (read :ref:`note
<renaming-note>`) and default value is a 3-tuple:

1. short name
2. default value
3. help string

If a short name renders to False (for example, empty string), then it's not used
at all.

.. _renaming-note:

If you have a long name with underscores, they are converted to dashes, which is
common standard for command line applications. If long name ends with
underscore and is a python keyword, this underscore is stripped.

.. _options-processing:

Options processing
------------------

Default value also determines how supplied argument should be parsed:

- string: value is passed as is
- integer: value is convert to integer
- boolean/None: ``not default`` is passed and option takes no value
- function: function is called with value and return value is used
- list: value is appended to this list
- dictionary: value is then assumed being in format ``key=value`` and is
  then assigned to this dictionary, :ref:`example <definitions-test>`

Note that only boolean/None case generates option, which doesn't want any
argument.

Usage
-----

Running this file with python will trigger command line parsing facility, using
arguments from ``sys.argv``. ``sys.argv[0]`` will be prepended to usage string
(you can put it in another place using macro ``%name`` in usage string).

In our current case just calling this file with python will display help, since
there is required argument::

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

You can parse command line strings programmatically, supplying list of
arguments to ``.command()`` property::

  main.command('-l 0.0.0.0 /my/dir'.split())

Or you still can use your function in python::

  main('/tmp', listen='0.0.0.0')

In this case no type conversion (which is done upon arguments parsing) will be
performed.

.. _subcommands:

Subcommands
===========

It's pretty usual for complex application to have some system of subcommands,
and opster provides facility for handling them. It's easy to define them::

  from opster import command, dispatch

  @command(usage='[-t]', shortlist=True)
  def simple(test=('t', False, 'just test execution')):
      '''
      Just simple command to print keys of received arguments.
  
      I assure you! Nothing to look here. ;-)
      '''
      pass

  @command(usage='[-p] [--exit value] ...', name='complex', hide=True)
  def complex_(pass_=('p', False, "don't run the command"),
               exit=('', 100, 'exit with supplied code'),
               name=('n', '', 'optional name'),
               *args):
      '''That's more complex command intended to do something'''
      pass

  if __name__ == '__main__':
      dispatch()

Your application will also always have ``help`` command when it uses subcommand
system.

Usage
-----

Usage is the same as with single command, except that running without arguments
will display you shortlist of commands::

  > python multicommands.py
  usage: multicommands.py <command> [options]

  commands:

   simple  Just simple command to print keys of received arguments.

In case you haven't marked any commands with ``shortlist=True``, all commands
will be displayed (excluding those, which have ``hide=True``). Also, you can run
``python multicommands.py help``, which will show list of all commands (still
excluding hidden commands).

Using ``help command`` or ``command --help`` will display a help on this
command::

  > python multicommands.py help simple
  multicommands.py simple [-t]

  Just simple command to print keys of received arguments.
  
      I assure you! Nothing to look here. ;-)

  options:

   -t --test     just test execution
   -h --help     display help

Global options
--------------

In case your application has options, which every command should receive, you
can declare them in following format::

  options = [('v', 'verbose', False, 'enable additional output'),
             ('q', 'quiet', False, 'suppress output')]

Which is, obviously ``(shortname, longname, default, help)``.
             
And pass them to ``dispatch``::

  if __name__ == '__main__':
      dispatch(globaloptions=options)


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

It is generated from usage, function docstring and a list of option help
strings, wrapped to length of 70 characters and looks like that::

  > python multicommands.py help complex
  multicommands.py complex: [-p] [--exit value] ...

  That's more complex command indented to do something

  options:

   -p --pass  don't run the command
      --exit  exit with supplied code (default: 100)
   -n --name  optional name
   -h --help  show help

Default value is displayed here only if it's not rendered to ``False``.
   
.. _innerhelp:

If you need to display help from inside your application, you can always use the
fact that help-displaying function is attached to your function object, i.e.::

  @command()
  def something():
      if some_consequences:
          something.help()

See `example from tests`_.

.. _example from tests: http://hg.piranha.org.ua/opster/file/default/tests/selfhelp.py
