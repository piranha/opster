from opster import command

@command()
def main(arg1, arg2, arg3=None, arg4='arg4', *args,
         opt1=('', 'opt1', 'help for --opt1'),
         opt2=('', 'opt2', 'help for --opt2')):
    print(arg1, arg2, arg3, arg4)
    print(args)
    print(opt1, opt2)

main.command()
