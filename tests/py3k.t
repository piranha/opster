.. -*- mode: rst -*-

==================
 Opster Py3K tests
==================

This is the opster test suite for tests that are only to be run on python 3.x

.. highlight:: console

Actors cast
-----------

Choose python version::

  $   if [ -z "$PYTHON" ]; then
  >      PYTHON="python"
  >   fi

Add opster to the PYTHONPATH::

  $   if [ -z "$OPSTER_DIR" ]; then
  >      OPSTER_DIR="$TESTDIR/.."
  >   fi
  >   export PYTHONPATH="$OPSTER_DIR"

Define function to make it simpler::

  $ run() {
  >   name=$1
  >   shift
  >   export COVERAGE_FILE=$TESTDIR/coverage.db
  >   if [ -z "$COVERAGE" ]; then
  >      "$PYTHON" "$TESTDIR/$name" "$@"
  >   else
  >      coverage run -a --rcfile="$TESTDIR/../.coveragerc" "$TESTDIR/$name" "$@"
  >   fi
  > }

Keyword-only args
-----------------

Check that opster understand keyword-only args when used without varargs.

  $ run kwonly.py
  kwonly.py: invalid arguments
  
  kwonly.py [OPTIONS] ARG1 [ARG2]
  
  (no help text available)
  
  options:
  
      --opt1  help for --opt1 (default: opt1)
   -h --help  display help

  $ run kwonly.py A
  A None
  opt1

  $ run kwonly.py A B
  A B
  opt1

  $ run kwonly.py A B C
  kwonly.py: invalid arguments
  
  kwonly.py [OPTIONS] ARG1 [ARG2]
  
  (no help text available)
  
  options:
  
      --opt1  help for --opt1 (default: opt1)
   -h --help  display help

  $ run kwonly.py A --opt1=newval
  A None
  newval

  $ run kwonly.py A B --opt1=newval
  A B
  newval

  $ run kwonly.py A B C --opt1=newval
  kwonly.py: invalid arguments
  
  kwonly.py [OPTIONS] ARG1 [ARG2]
  
  (no help text available)
  
  options:
  
      --opt1  help for --opt1 (default: opt1)
   -h --help  display help

Keyword-only args and varargs
-----------------------------

Check that opster understand keyword-only args when used with varargs.

  $ run kwonlyvarargs.py
  kwonlyvarargs.py: invalid arguments
  
  kwonlyvarargs.py [OPTIONS] ARG1 ARG2 [ARG3] [ARG4] [ARGS ...]
  
  (no help text available)
  
  options:
  
      --opt1  help for --opt1 (default: opt1)
      --opt2  help for --opt2 (default: opt2)
   -h --help  display help

  $ run kwonlyvarargs.py A B
  A B None arg4
  ()
  opt1 opt2

  $ run kwonlyvarargs.py A B C D
  A B C D
  ()
  opt1 opt2

  $ run kwonlyvarargs.py A B C D E F
  A B C D
  ('E', 'F')
  opt1 opt2

  $ run kwonlyvarargs.py A B --opt1=newval --opt2=newval2
  A B None arg4
  ()
  newval newval2

  $ run kwonlyvarargs.py A B C D --opt1=newval1 --opt2=newval2
  A B C D
  ()
  newval1 newval2

  $ run kwonlyvarargs.py A B C D E F --opt1=newval1 --opt2=newval2
  A B C D
  ('E', 'F')
  newval1 newval2

Check the `varargs` works when calling ```main``` directly::

  $ run varargs_py3.py
  
  main():
  TypeError raised
  
  main("a"):
  shop: a
  cheeses: ()
  music: False
  
  main("a", "b"):
  shop: a
  cheeses: ('b',)
  music: False
  
  main("a", "b", "c"):
  shop: a
  cheeses: ('b', 'c')
  music: False
  
  main(music=True):
  TypeError raised
  
  main("a", music=True):
  shop: a
  cheeses: ()
  music: True
  
  main("a", "b", music=True):
  shop: a
  cheeses: ('b',)
  music: True
  
  main("a", "b", "c", music=True):
  shop: a
  cheeses: ('b', 'c')
  music: True

