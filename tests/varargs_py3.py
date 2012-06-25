# varargs_py3.py

from __future__ import print_function

from opster import command

@command()
def main(shop,
         *cheeses,
         music=('m', False, 'provide musical accompaniment')):
    '''Buy cheese'''
    print('shop:', shop)
    print('cheeses:', cheeses)
    print('music:', music)

if __name__ == "__main__":

    print('\nmain():')
    try:
        main()
    except TypeError:
        print('TypeError raised')

    for expr in 'main("a")', 'main("a", "b")', 'main("a", "b", "c")':
        print('\n{0}:'.format(expr))
        eval(expr)

    print('\nmain(music=True):')
    try:
        main(music=True)
    except TypeError:
        print('TypeError raised')

    for expr in ('main("a", music=True)',
                 'main("a", "b", music=True)',
                 'main("a", "b", "c", music=True)'):
        print('\n{0}:'.format(expr))
        eval(expr)
