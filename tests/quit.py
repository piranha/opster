from opster import command

@command()
def main(algorithm=('a', 'fast', 'algorithm: slow or fast')):
    '''
    script that uses two possible algorithms.
    '''
    if algorithm not in ('short', 'fast'):
        raise command.Error('unrecognised algorithm "{0}"'.format(algorithm))
    pass

if __name__ == "__main__":
    main.command()
