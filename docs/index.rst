=============
 Opster
=============

.. toctree::
   :maxdepth: 2

   changelog
   overview
   api

Opster is a command line parser, intended to make writing command line
applications easy and painless. It uses built-in Python types (lists,
dictionaries, etc) to define options, which makes configuration clear and
concise. Additionally it contains possibility to handle subcommands (i.e.
``hg commit`` or ``svn update``).

Features
--------

 - parsing arguments from sys.argv or custom strings
 - converting from string to appropriate Python objects
 - help message generation
 - positional and named arguments
 - subcommands support
 - short, clean and concise definitions
 - ability to shorten names of subcommand and long options
