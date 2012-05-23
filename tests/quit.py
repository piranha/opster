from __future__ import print_function
from opster import command

NMAX = 4
ALGOS = ('slow', 'fast')

@command()
def main(algo1=('a', 'fast', 'algorithm: slow or fast'),
         algo2=('A', ALGOS, 'algorithm: slow or fast'),
         ncpus=('n', tuple(range(1, NMAX+1)), 'number of cpus to use')):
    '''
    script that uses different algorithms and numbers of cpus
    '''
    if algo1 not in ALGOS:
        raise command.Error('unrecognised algorithm "{0}"'.format(algo1))
    print('algo1:', algo1)
    print('algo2:', algo2)
    print('ncpus:', ncpus)

if __name__ == "__main__":
    main.command()
