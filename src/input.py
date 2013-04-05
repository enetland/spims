import sys
import os
import spims


def error(s):
    print s
    exit(1)


def is_valid_arg(arg):
    valid_flag = os.path.isfile(arg) or os.path.isdir(arg)
    if not(valid_flag):
        error('No such file or directory %s' % arg)
    else:
        pass


def get_args():
    debug_flag = False
    patterns = None
    sources = None
    args = enumerate(sys.argv)
    try:
        for i, obj in args:
            if obj == '-p':
                is_valid_arg(sys.argv[i+1])
                patterns = [sys.argv[i+1]]
                args.next()
                continue
            elif obj == '-s':
                is_valid_arg(sys.argv[i+1])
                sources = [sys.argv[i+1]]
                args.next()
                continue
            elif obj == '-pdir' or obj == '--pdir':
                is_valid_arg(sys.argv[i+1])
                pattern_dir = sys.argv[i+1]
                patterns = map(lambda x: pattern_dir + '/' + x, os.listdir(pattern_dir))
                args.next()
                continue
            elif obj == '-sdir' or obj == '--sdir':
                is_valid_arg(sys.argv[i+1])
                source_dir = sys.argv[i+1]
                sources = map(lambda x: source_dir + '/' + x, os.listdir(source_dir))
                args.next()
                continue
            elif obj == '-d':
                debug_flag = True
                continue
    except IndexError:
        error_str = 'Please provide input with one of the following forms:\n' + \
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
