=============
 Finaloption
=============

::

  If that's the Final Option,
  I'm gonna choose it.
                   Die Krupps 

.. toctree::
   :maxdepth: 2

   changelog
   overview
   api

Finaloption is a command line parser, intended to make writing command line
applications easy and painless. It uses built-in Python types (lists,
dictionaries, etc) to define options, which makes configuration clear and
concise. Additionally it contains possibility to handle subcommands (i.e.
``hg commit`` or ``svn update``).

JFYI: name is derived from Die Krupps' song `Final Option`_, featured in
epigraph.

.. _Final Option: http://musi.cx/music/Die_Krupps/III_Odyssey_of_the_Mind/The_Final_Option/

Features
--------

 - parsing arguments from sys.argv or custom strings
 - converting from string to appropriate Python objects
 - generating help message
 - positional and named arguments
 - subcommands support
 - short, clean and concise definitions
 - ability to shorten names of subcommand and long options
