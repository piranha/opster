from opster import command

@command()
def test(arg1,
         b=1,
         opt=('o', False, 'some option'),
         bopt=('', 'bopt', 'another option'),
         *args):
    '''Simple command to test that it won't get multiple values for opt
    '''
    print 'I work!', opt, bopt, arg1, b, args
    assert opt == False
    assert bopt == 'bopt'

if __name__ == '__main__':
    test.command()
