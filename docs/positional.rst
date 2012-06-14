.. -*- mode: rst -*-

======================
 Positional Arguments
======================

.. hidden::

  $    # Allow opster directory to be overridden
  >    if [ -z "$OPSTER_DIR" ]; then
  >      OPSTER_DIR="$TESTDIR/.."
  >    fi
  >    # Add current dev version of opster to PYTHONPATH
  >    export PYTHONPATH="$OPSTER_DIR"
  >    # Change into the docs/scripts directory to run the tests
  >    cd "${OPSTER_DIR}/docs/scripts"

Introduction
============

Before considering how Opster handles positional arguments it is instructive
to look at a simple example of a script that does not use opster. The simplest
way to construct a script that receives some positional command line arguments
looks something like ``pos1.py``:

.. literalinclude:: scripts/pos1.py

This script will correctly receive its command line arguments if given valid
arguments:

.. code-block:: bash

  $ python pos1.py one
  arg1: one
  arg2: None

  $ python pos1.py one two
  arg1: one
  arg2: two

However ``pos1.py`` is not so nice to the user when given incorrect output:

.. code-block:: bash

  $ python pos1.py
  Traceback (most recent call last):
    File "pos1.py", line 13, in <module>
      main(*sys.argv[1:])
  TypeError: main() takes at least 1 argument (0 given)
  [1]

  $ python pos1.py one two three
  Traceback (most recent call last):
    File "pos1.py", line 13, in <module>
      main(*sys.argv[1:])
  TypeError: main() takes at most 2 arguments (3 given)
  [1]

So we can improve on this
