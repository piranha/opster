from opster import command

@command()
def selfhelp(assist=('', False, 'show help')):
    '''Displays ability to show help'''
    if assist:
        selfhelp.help()
    else:
        print 'no help for you!'

if __name__ == '__main__':
    selfhelp()
