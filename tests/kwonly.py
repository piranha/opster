from opster import command

@command()
def main(arg1, arg2=None, *,
         opt1=('', 'opt1', 'help for --opt1')):
    print(arg1, arg2)
    print(opt1)

main.command()
