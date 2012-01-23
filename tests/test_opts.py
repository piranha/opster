import pprint
from opster import command

@command(usage='[-l HOST] DIR')
def another(dirname,
            listen=('l', 'localhost', 'ip to listen on'),
            port=('p', 8000, 'port to listen on'),
            daemonize=('d', False, 'daemonize process'),
            pid_file=('', '', 'name of file to write process ID to'),
            definitions=('D', {}, 'just some definitions'),
            test=('t', lambda x: x or 'test', 'testing help for a function')):
    '''Command with option declaration as keyword arguments
    '''
    pprint.pprint(locals())

@command()
def varargs_and_underscores(test_option=('t', 'test', 'just option with underscore'), *args):
    pprint.pprint(locals())

if __name__ == '__main__':
    varargs_and_underscores.command('-t test vararg1 vararg2'.split())
    varargs_and_underscores.command('vararg1 vararg2'.split())
    another.command()
