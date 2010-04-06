===================
 Opster usage
===================

Options
-------

Configuration of option parser is a list of tuples::

  opts = [('l', 'listen', 'localhost', 'ip to listen on'),
          ('p', 'port', 8000, 'port to listen on'),
          ('d', 'daemonize', False, 'daemonize process'),
          ('', 'pid-file', '', 'name of file to write process ID to')]

Each tuple is a definition of some option, consisting of 4 elements:

 1. short name
 2. long name (read note_)
 3. default value
 4. help string

If a short name renders to False (for example, empty string), then it's not used
at all. Long name is pretended to be available in any case. Default value also
determines how supplied argument should be parsed:

 - function: return value of function called with a specified value is passed
 - integer: value is convert to integer
 - string: value is passed as is
 - list: value is appended to this list
 - boolean/None: ``not default`` is passed and option takes no argument

Usage is easy like that::

  from opster import command

  @command(options=opts, usage='%name [-l HOST] DIR')
  def main(dirname, **opts):
      '''write some help here'''
      pass

There is alternative declaration, easier for simple cases::

  @command(usage='%name [-l HOST] DIR')
  def main(dirname,
           listen=('l', 'localhost', 'ip to listen on'),
           pid_file=('', '', 'name of file to write process ID to')):
      pass

.. _note:

I think it's easy to understand what's going on here, except that you need to
know that underscores in the long name will be replaced with dashes at the
command line. Of course, reverse process happens: if you have option with a dash
in long name in a definition, it will be replaced with underscore when passed to
function. This is done to comply with standarts of writing both console
interfaces and Python application.

After that you can simply call this function as an entry point to your program::

  if __name__ == '__main__':
      main()

This will run command line parsing facility, using arguments from
``sys.argv``. ``%name`` in usage string will be replaced with ``sys.argv[0]``
(or prepended to usage string if there is no ``%name``), and rest of arguments
will be passed to command line parser. In case if rest is empty, help will be
displayed.

Of course, you can use your function programmatically, supplying list of
arguments to function::

  main(argv='-l 0.0.0.0 /my/dir'.split())

Or, if you need this, you can call this function as usual::

  main('/my/dir', listen='0.0.0.0')

In this case no type conversion (which is done upon arguments parsing) will be
performed.

Subcommands
-----------

It's pretty usual for complex application to have some system of subcommands,
and opster provides facility for handling them. Configuration is simple::

  cmdtable = {
      '^simple':
          (simple,
           [('t', 'test', False, 'just test execution')],
           '[-t] ...'),
      'complex|hard':
          (complex_,
           [('p', 'pass', False, 'don\'t run the command'),
            ('', 'exit', 0, 'exit with supplied code (default: 0)')],
           '[-p] [--exit value] ...')}

Keys in this dictionary are subcommand names. You can add aliases for
subcommands, separating them with the ``|`` sign (of course, there can be few
aliases). Marking command with preceding ``^`` means that this command should
be included in short help, marking with preceding ``~`` means that this command
should be removed from all command listings (more on that later).

Values here are tuples, consisting of 3 elements:

 1. function, which will handle this subcommand
 2. list of options
 3. usage string (used by help generator)

Your application will also always have ``help`` command, when it uses subcommand
system.

You can define your functions for subcommands like this::

    def simple(*args, **opts):
        '''some descriptive text here

        more help, I'd said a lot of help here ;-)
        '''
        pass

Naturally ``args`` is a list, containing all arguments to command, and ``opts``
is a dictionary, containing every option.

After definition of all elements you can call command dispatcher (``cmdtable``
is defined earlier)::

  from opster import dispatch

  if __name__ == '__main__':
      dispatch(cmdtable=cmdtable)

Example usage, calling ``complex_`` with 5 as an argument for ``exit`` option,
shows that command dispatcher will understand partial names of commands and
options::

  app har --ex 5

But if your program is something like program shown earlier, you can use
shortened api::

  @command(usage='[-t] ...', shortlist=True)
  def simple(somearg,
             test=('t', False, 'just test execution')):
      pass

  if __name__ == '__main__':
      dispatch()

Every :ref:`@command <api-command>` stores information about decorated function in
special global command table, which allows to call ``dispatch()`` without
arguments.

Help generation
---------------

Help is generated automatically and is available by the ``-h/--help`` command
line option or by ``help`` subcommand (if you're using subcommand system).

It is generated from usage, function docstring and a list of option help
strings, wrapped to length of 70 characters and looks like that::

  > ./test.py help complex
  test.py complex: [-p] [--exit value] ...

  That's more complex command indented to do something

      Let's try to do that (what?!)

  options:

   -p --pass  don't run the command
      --exit  exit with supplied code (default: 0)
   -h --help  show help


Tips and tricks
---------------

There is one thing which may be obvious: it's easy to have "semi-global"
options. If your subcommands (or scripts) tend to have same options in some
cases - for example, few commands (not every) can receive database credentials -
you can define this options in separate list and then add them to command's own
options, i.e.::

  @command(cmd_opts + dbopts)
  def select(**opts):
      pass
