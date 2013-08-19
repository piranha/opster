from opster import command

@command()
def main(arg1, arg2, arg3=None, arg4='arg4',
         opt1=('', 'opt1', 'help for --opt1'),
         *args,
         opt2=('', 'opt2', 'help for --opt2')):
    print(arg1, arg2, arg3, arg4)
    print(args)
    print(opt1, opt2)

if __name__ == '__main__':
    main.command()
