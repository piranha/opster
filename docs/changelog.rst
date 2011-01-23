Changelog
---------

2.0 (2010.01.23)
~~~~~~~~~~~~~~~~

 - fix help display when there is no __doc__ declared for function
 - ``dict`` type `handling`_
 - ``.help()`` attribute for every function, printing help on call

.. _handling: http://hg.piranha.org.ua/opster/docs/overview.html#options-processing

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
