from opster import command

@command()
def hello(name,
          times=1,
          greeting=('g', 'Hello', 'Greeting to use')):
    """
    Hello world continues the long established tradition
    of delivering simple, but working programs in all
    kinds of programming languages.

    This tests different docstring formatting (just text instead of having
    subject and body).
    """
    # no parsing for optional arguments yet :\
    for i in range(int(times)):
        print("%s %s" % (greeting, name))

if __name__ == "__main__":
    hello.command()
