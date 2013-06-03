Changelog
---------

4.0 (2013.06.03)
~~~~~~~~~~~~~~~~

 - Infinitely `nested subcommands`_.
 - Tuple options (one of given enumerated values).
 - A lot of fixes.

Most of changes were done by `Oscar Benjamin`_.

.. _nested subcommands: http://opster.readthedocs.org/en/latest/overview.html#nested-subcommands

3.7 (2012.05.03)
~~~~~~~~~~~~~~~~

 - Fixed name in usage on Windows.
 - Improved and documented preparsing of global options when using subcommands (GH-25).

3.6 (2012.04.23)
~~~~~~~~~~~~~~~~

 - Now commands can have ``-h`` option (GH-2).
 - Better Windows compatibility (GH-18, GH-20).
 - Refactored internal options representation with easier introspectability
   (GH-19).
 - Tests support Python 3 (GH-21).

Thanks for this release are going to `Oscar Benjamin`_, every point in this
release is his work.

.. _Oscar Benjamin: https://github.com/oscarbenjamin
 

3.5 (2012.03.25)
~~~~~~~~~~~~~~~~

 - Added `command.Error`_ to facilitate easy exits from scripts (GH-12).
 - Fixed opster.t output.

.. _command.Error: http://opster.readthedocs.org/en/latest/overview.html#error-messages

3.4 (2012.01.24)
~~~~~~~~~~~~~~~~

 - Fix for installation issue (MANIFEST.in wasn't included).
 - Fix for pep8.py complaints (most of them).
 - Fix for script name when calling as a command (and not a dispatcher) (GH-4).
 - Fix for some 2to3 issues (GH-5).
 - Fixed bug with empty arguments for ``opster.command`` (GH-6).
 - opster.t is now able to run under ``dash``.
 - More output encodings supported (GH-7).
 - Coverage support for cram tests (GH-8).
 - Fixed combination of varargs and option name with underscore (GH-10).

3.3 (2011.09.04)
~~~~~~~~~~~~~~~~

 - Multicommands: ability to specify `global options`_ before specifying name of
   command

.. _global options: http://opster.readthedocs.org/en/latest/overview.html#global-options

3.2 (2011.08.27)
~~~~~~~~~~~~~~~~

 - `Fix`_ for ``TypeError: func() got multiple values for 'argument'``

.. _Fix: http://opster.readthedocs.org/en/latest/tests.html#multivalues

3.1 (2011.08.27)
~~~~~~~~~~~~~~~~

 - Better `aliases`_ support.
 - Fixes for options and usage discovery.
 - Fix for error handling of dictionary options in multicommands.
 - Fix for help not working when global options are defined.

.. _aliases: http://readthedocs.org/docs/opster/en/latest/api.html#opster.command

3.0 (2011.08.14)
~~~~~~~~~~~~~~~~

 - **Backward incompatible** Single commands now don't attempt to parse.
   arguments if you call them. `Use`_ ``function.command()`` attribute (much like
   earlier ``function.help()``) to parse arguments now.
 - Switch to Python 2.6.
 - Ability to have few subcommand `dispatchers`_ in a single runtime (no single
   global ``CMDTABLE`` dictionary anymore).

.. _Use: http://opster.readthedocs.org/en/latest/#quick-example
.. _dispatchers: http://opster.readthedocs.org/en/latest/api.html#opster.Dispatcher

2.2 (2011.03.23)
~~~~~~~~~~~~~~~~

 - adjust indentation level in multiline docstrings (compare `1`_ and `2`_)
 - small fix for internal getopt exception handling

.. _1: http://opster.readthedocs.org/en/latest/tests.html#multihelp1
.. _2: http://opster.readthedocs.org/en/latest/tests.html#multihelp2


2.1 (2011.01.23)
~~~~~~~~~~~~~~~~

 - fix help display in case middleware returns original function

2.0 (2011.01.23)
~~~~~~~~~~~~~~~~

 - fix help display when there is no __doc__ declared for function
 - ``dict`` type `handling`_
 - ``.help()`` attribute for every function, printing help on call

.. _handling: http://opster.readthedocs.org/en/latest/overview.html#options-processing

1.2 (2010.12.29)
~~~~~~~~~~~~~~~~

 - fix option display for a list of subcommands if docstring starts with a blank
   line

1.1 (2010.12.07)
~~~~~~~~~~~~~~~~

 - _completion was failing to work when global options were supplied to command
   dispatcher

1.0 (2010.12.06)
~~~~~~~~~~~~~~~~

 - when middleware was used and command called without arguments, instead of
   help, traceback was displayed

0.9.13 (2010.11.18)
~~~~~~~~~~~~~~~~~~~

 - fixed exception handling (cleanup previous fix, actually)
 - display only name of application, without full path

0.9.12 (2010.11.02)
~~~~~~~~~~~~~~~~~~~

 - fixed trouble with non-ascii characters in docstrings

0.9.11 (2010.09.19)
~~~~~~~~~~~~~~~~~~~

 - fixed exceptions handling
 - autocompletion improvements (skips middleware, ability of options completion)

0.9.10 (2010.04.10)
~~~~~~~~~~~~~~~~~~~

 - if default value of an option is a fuction, always call it (None is passed in
   case when option is not supplied)
 - always call a function if it's default argument for an option
 - some cleanup with better support for python 3
 - initial support for autocompletion (borrowed from PIP)

0.9 - 0.9.9 (since 2009.07.13)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ancient history ;-)
