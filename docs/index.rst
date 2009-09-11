=============
 Opster
=============

.. toctree::
   :maxdepth: 1

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

What's nice
-----------

 - Opster is a `single file`_, which means that you can easily include it with
   your application
 - When you've decorated function as command, you can continue to use it as
   usual Python function.
 - It's easy to switch between usual command line options parser and
   subcommands.

Read more in `overview`_.


.. _single file: http://hg.piranha.org.ua/opster/file/tip/opster.py
.. _overview: overview
