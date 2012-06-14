# pos3.py

from __future__ import print_function

from opster import command

@command()
def main(infile,
         outfile,
         pattern='.*',
         exclude=None,
         regex=('r', False, 'Use regular expressions'),
         extended=('e', False, 'Use extended syntax')):
    '''
    Write lines from INFILE to OUTFILE.

    If PATTERN and/or EXCLUDE is given,
    only lines matching PATTERN but not
    matching EXCLUDE will be written
    '''
    print('infile:', infile)
    print('outfile:', outfile)
    print('pattern:', pattern)
    print('exclude:', exclude)

if __name__ == "__main__":
    main.command()
