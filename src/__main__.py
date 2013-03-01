import sys
import os
import Image
import pdb

if __name__ == "__main__":
    import spims
    #(options, args) = parser.parse_args()
    #patterns = None
    #sources = None
    debug_flag = False
    patterns = None
    sources = None
    args = enumerate(sys.argv)
    for i, obj in args:
        if obj == '-p':
            if os.path.isfile(sys.argv[i+1]):
                patterns = [sys.argv[i+1]]
                args.next()
                continue
        elif obj == '-s':
            if os.path.isfile(sys.argv[i+1]):
                sources = [sys.argv[i+1]]
                args.next()
                continue
        elif obj == '-pdir':
            if os.path.isdir(sys.argv[i+1]):
                pattern_dir = sys.argv[i+1]
                patterns = map(lambda x: pattern_dir + x, os.listdir(pattern_dir))
                args.next()
                continue
        elif obj == '-sdir':
            if os.path.isdir(sys.argv[i+1]):
                source_dir = sys.argv[i+1]
                sources = map(lambda x: source_dir + x, os.listdir(source_dir))
                args.next()
                continue
        elif obj == '-d':
            debug_flag = True
            continue
        
    if patterns is None:
        print 'Pattern file or Directory must be provided'
        exit(1)
    elif sources is None:
        print 'Source file or Directory must be provided'
        exit(1)
    else:
        spims.match_dirs(patterns, sources, debug_flag)
