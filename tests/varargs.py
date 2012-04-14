import pprint
from opster import command


@command()
def varargs_and_underscores(
    test_option=('t', 'test', 'just option with underscore'),
    *args):
    pprint.pprint(locals())


if __name__ == '__main__':
    varargs_and_underscores.command()
