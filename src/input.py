""" Handle argument parsing and assosciated errors. """

import sys
import os
import spims


def error(s):
    """ Print a helpful error string and exit with code 1 """
    print s
    exit(1)


def is_valid_file(arg):
    """ Confirm a file argument is indeed a file. """
    if not(os.path.isfile(arg)):
        error('No such file %s' % arg)


def is_valid_dir(arg):
    """ Confirm a directory argument is indeed a directory. """
    if not(os.path.isdir(arg)):
        error('No such directory %s' % arg)


# TODO: Switch back to optparse method, sanitizing the -pdir and -sdir arguments
# beforehand
def get_args():
    """
    Loop through sys.argv, extracting the desired arguments. Not using optparse
    because it does not support the strange -pdir/-sdir syntax.

    """
    debug_flag = False
    patterns = None
    sources = None
    args = enumerate(sys.argv)
    try:
        for i, obj in args:
            if obj == '-p':
                is_valid_file(sys.argv[i+1])
                patterns = [sys.argv[i+1]]
                args.next()
                continue
            elif obj == '-s':
                is_valid_file(sys.argv[i+1])
                sources = [sys.argv[i+1]]
                args.next()
                continue
            elif obj == '-pdir' or obj == '--pdir':
                is_valid_dir(sys.argv[i+1])
                pdir = sys.argv[i+1]
                patterns = \
                    map(lambda x: pdir + '/' + x, os.listdir(pdir))
                args.next()
                continue
            elif obj == '-sdir' or obj == '--sdir':
                is_valid_dir(sys.argv[i+1])
                sdir = sys.argv[i+1]
                sources = \
                    map(lambda x: sdir + '/' + x, os.listdir(sdir))
                args.next()
                continue
            elif obj == '-d':
                debug_flag = True
                continue
    except IndexError:
        error_str = 'Please provide input with one of the following forms:\n' +\
            '\t./spims -p <pattern_image> -s <source_image>' + \
            '\t./spims -pdir <pattern_image_dir> -s <source_image>' + \
            '\t./spims --pdir <pattern_image_dir> -s <source_image>' + \
            '\t./spims -p <pattern_image> -sdir <source_image_dir>' + \
            '\t./spims -p <pattern_image> --sdir <source_image_dir>' + \
            '\t./spims -pdir <pattern_image_dir> -sdir <source_image_dir>' + \
            '\t./spims --pdir<pattern_image_dir> --sdir <source_image_dir>\n'
        error(error_str)

    if patterns is None:
        error('Pattern file or Directory must be provided')
    elif sources is None:
        print('Source file or Directory must be provided')
    else:
        spims.run(patterns, sources)
