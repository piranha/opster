import sys
from opster import command

# This could seem to be a little involved, but keep in mind that those little
# movements here are done to support both python 2.x and 3.x
unicode = unicode if sys.version_info < (3, 0) else str
out = getattr(sys.stdout, 'buffer', sys.stdout)

@command()
def hello(name,
          times=1,
          greeting=('g', unicode('Hello'), 'Greeting to use')):
    """
    Hello world continues the long established tradition
    of delivering simple, but working programs in all
    kinds of programming languages.

    This tests different docstring formatting (just text instead of having
    subject and body).
    """
    if hasattr(name, 'decode'):
        name = name.decode('utf-8')
    # no parsing for optional arguments yet :\
    for i in range(int(times)):
        out.write((unicode("%s %s\n") % (greeting, name)).encode('utf-8'))

if __name__ == "__main__":
    hello.command()
