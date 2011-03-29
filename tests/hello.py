from opster import command

@command(usage="%name [options]")
def hello(name=('n', 'world', 'your name')):
    """
    Hello world continues the long established tradition
    of delivering simple, but working programs in all
    kinds of programming languages.
    """
    print "Hello %s" % name

if __name__ == "__main__":
    hello()

