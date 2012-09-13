import opster

# arginfo.defaults will be None for this function
@opster.command()
def hello():
    print('hello')

hello()
