.. -*- mode: rst -*-

========
 Opster
========

Opster is a command line options parser, intended to make writing command line
applications easy and painless. It uses built-in Python types (lists,
dictionaries, etc) to define options, which makes configuration clear and
concise. Additionally it contains possibility to handle subcommands (i.e.
``hg commit`` or ``svn update``).


.. note:: Requires at least Python 2.6


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

Running this program will print help message::

  > ./echo.py
  echo.py: invalid arguments
  echo.py [OPTIONS] MESSAGE

  Simple echo program

  options:

   -n --no-newline  don't print a newline
   -h --help        show help

As you can see, here we have defined option to not print newline: keyword
argument name is a long name for option, default value is a 3-tuple, containing
short name for an option (can be empty), default value (on base of which
processing is applied - `see description`_) and a help string.

Underscores in long names of options are converted into dashes.

If you are calling a command with option using long name, you can supply it
partially. In this case it could look like ``./echo.py --no-new``. This is also
true for subcommands: read about them and everything else you'd like to know in
`documentation`_.

.. _documentation: http://opster.readthedocs.org/en/latest/
.. _see description: http://opster.readthedocs.org/en/latest/overview.html#options-processing
