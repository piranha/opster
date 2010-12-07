This is a test suite for opster library. Just read it to get some idea of how it
works.

Define some help functions::

  $ function run() { name=$1; shift; python "$TESTDIR/$name" "$@"; }

Check if usage is working::

  $ run multicommands.py
  usage: multicommands.py <command> [options]
  
  commands:
  
   simple  Just simple command to print keys of received arguments.



Ok, then let's run it::

  $ run multicommands.py simple
  ['test', 'ui']

Yeah, nice one, but we know that command ``complex`` is just hidden there. Let's
check it out::

  $ run multicommands.py help complex
  multicommands.py complex [-p] [--exit value] ...
  
  That's more complex command intended to do something
  
      И самое главное - мы тут немножечко текста не в ascii напишем
      и посмотрим, что будет. :)
  
  options:
  
   -p --pass     don't run the command
      --exit     exit with supplied code (default: 0)
   -n --name     optional name
   -v --verbose  enable additional output
   -q --quiet    suppress output
   -h --help     display help


We also have completion::

  $ run multicommands.py _completion
  # opster bash completion start
  _opster_completion()
  {
      COMPREPLY=( $( COMP_WORDS="${COMP_WORDS[*]}" \
                     COMP_CWORD=$COMP_CWORD \
                     OPSTER_AUTO_COMPLETE=1 $1 ) )
  }
  complete -o default -F _opster_completion multicommands.py
  # opster bash completion end


Now we're going to test if a script with a single command will work (not
everyone needs subcommands, you know)::

  $ run test_opts.py
  another: invalid arguments
  test_opts.py [-l HOST] DIR
  
  Command with option declaration as keyword arguments
  
  options:
  
   -l --listen     ip to listen on (default: localhost)
   -p --port       port to listen on (default: 8000)
   -d --daemonize  daemonize process
      --pid-file   name of file to write process ID to
   -t --test       testing help for a function (default: test)
   -h --help       show help


Yeah, I've got it, I should supply some argument::

  $ run test_opts.py right-here
  {'daemonize': False,
   'dirname': 'right-here',
   'listen': 'localhost',
   'pid_file': '',
   'port': 8000,
   'test': 'test'}


Should we check passing some invalid arguments? I think so::

  $ run test_opts.py --wrong-option
  error: option --wrong-option not recognized
  
  test_opts.py [-l HOST] DIR
  
  Command with option declaration as keyword arguments
  
  options:
  
   -l --listen     ip to listen on (default: localhost)
   -p --port       port to listen on (default: 8000)
   -d --daemonize  daemonize process
      --pid-file   name of file to write process ID to
   -t --test       testing help for a function (default: test)
   -h --help       show help


That's all for today; see you next time!
