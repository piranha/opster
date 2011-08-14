========
 Opster
========

Opster is a command line parser, intended to make writing command line
applications easy and painless. It uses built-in Python types (lists,
dictionaries, etc) to define options, which makes configuration clear and
concise. Additionally it contains possibility to handle subcommands (i.e.
``hg commit`` or ``svn update``).

* Page on PyPI: http://pypi.python.org/pypi/opster/
* Repository: http://hg.piranha.org.ua/opster/
* Requires at least Python 2.6

Features
--------

- parsing arguments from ``sys.argv`` or custom strings
- :ref:`converting <options-processing>` from string to appropriate Python
  objects
- :ref:`help message <help-generation>` generation
- positional and named arguments (i.e. arguments and options)
- :ref:`subcommands <subcommands>` support
- short, clean and concise definitions
- :ref:`ability to shorten <partial-names>` names of subcommand and long options

Quick example
-------------

That's an example of an option definition::

  import sys
  from opster import command

  @command()
  def main(message,
           no_newline=('n', False, "don't print a newline")):
      '''Simple echo program'''
      sys.stdout.write(message)
      if not no_newline:
          sys.stdout.write('\n')

  if __name__ == '__main__':
      main.command()

Running this program will print the help::

  > ./echo.py
  echo.py: invalid arguments
  echo.py [OPTIONS] MESSAGE

  Simple echo program

  options:

   -n --no-newline  don't print a newline
   -h --help        display help

As you can see, here we have defined option to not print newline: keyword
argument name is a long name for option, default value is a 3-tuple, containing
short name for an option (can be empty), default value (on base of which
processing is applied - :ref:`see description <options-processing>`) and a help
string.

Underscores in long names of options are converted into dashes.

If you are calling a command with option using long name, you can supply it
partially. In this case it could look like ``./echo.py --no-new``. This is also
true for subcommands: read about them and everything else you'd like to know
further in documentation.

What's nice
-----------

- Opster is a `single file`_, which means that you can easily include it in
  your application
- When you've decorated function as command, you can continue to use it as
  usual Python function.
- It's easy to switch between usual command line options parser and
  subcommands.
- No need to type complete name of option or subcommand: :ref:`just type
  <partial-names>` unique start sequence.

Read more in :doc:`overview`.

More documentation
------------------

.. toctree::
   :maxdepth: 1

   changelog
   overview
   api
   tests

.. _single file: http://hg.piranha.org.ua/opster/file/tip/opster.py
