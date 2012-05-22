from opster import command

@command()
def hello(name,
          times=1,
          greeting=('g', u'Hello', 'Greeting to use')):
    """
    Hello world continues the long established tradition
    of delivering simple, but working programs in all
    kinds of programming languages.

    This tests different docstring formatting (just text instead of having
    subject and body).
    """
    if isinstance(name, str):
        name = name.decode('utf-8')
    # no parsing for optional arguments yet :\
    for i in range(int(times)):
        print((u"%s %s" % (greeting, name)).encode('utf-8'))

if __name__ == "__main__":
    hello.command()
