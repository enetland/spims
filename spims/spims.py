import numpy, scipy
from PIL import Image


def match(pattern_file, source_file):
    pattern = Image.open(pattern_file)
    source = Image.open(source_file)
    validate(pattern, source)
    print "Pattern: " + pattern_file
    print "Source: " + source_file

    pattern = scipy.misc.imread(pattern_file)
    print pattern.shape
    source = scipy.misc.imread(source_file)
    print source.shape


def validate(pattern, source):
    pattern.verify()
    source.verify()

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p", "--pattern", dest="pattern", help="Image to search for.", metavar="PATTERN_FILE")
    parser.add_option("-s", "--source", dest="source", help="Image to search for", metavar="SOURCE_FILE")

    (options, args) = parser.parse_args()
    match(options.pattern, options.source)
