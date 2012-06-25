========
 Opster
========

Opster is a command line parser, intended to make writing command line
applications easy and painless. It uses built-in Python types (lists,
dictionaries, etc) to define options, which makes configuration clear and
concise. Additionally, Opster supports parsing arguments for an application
that uses subcommands (i.e. ``hg commit`` or ``svn update``).

* Page on PyPI: http://pypi.python.org/pypi/opster/
* Repository: http://hg.piranha.org.ua/opster/
* Requires at least Python 2.6

More documentation
------------------

.. toctree::
   :maxdepth: 1

   changelog
   overview
   positional
   api
   Opster tests (examples here!) <tests>

Features
--------

- parsing of arguments from ``sys.argv`` or custom strings
- :ref:`conversion <options-processing>` from strings to the appropriate
  Python objects
- :ref:`help message <help-generation>` generation
- positional and named arguments (i.e. arguments and options)
- :ref:`subcommands <subcommands>` support
- short, clean and concise definitions
- :ref:`ability to shorten <partial-names>` names of both subcommands and long
  options

Quick example
-------------

Here's an example of a program that defines a single option::

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

Running the program above will print the help message:::

  > ./echo.py
  echo.py: invalid arguments
  echo.py [OPTIONS] MESSAGE

  Simple echo program

  options:

   -n --no-newline  don't print a newline
   -h --help        display help

As you can see, here we have defined an option to not print newlines: the
keyword argument is used as the long name for the option and its default value
is a 3-tuple, containing short name for an option (can be empty), default
value (whose type determines what conversion is applied - 
:ref:`see description <options-processing>`) and a help string for the option.

Any underscores in the keyword argument name are converted into dashes in the
long option name.

When a command is called using the long name for an option, the option need
not be fully entered. In the case above this could look like ``./echo.py
--no-new``. This is also true for subcommands: read about them and everything
else you'd like to know further on in the documentation.

Nice points
-----------

- Opster is a `single file`_, which means that you can easily include it in
  your application
- When you've decorated a function with ``command``, you can continue to use
  it as an ordinary Python function.
- It's easy to switch between a simple command line application and one that
  uses subcommands.
- There's no need to type the complete name of an option or subcommand:
  :ref:`just type <partial-names>` as many letters as are needed to
  distinguish it from the others.

Read more in :doc:`overview`.

.. _single file: http://hg.piranha.org.ua/opster/file/tip/opster.py
