import numpy, scipy, os
from PIL import Image


def match(pattern_file, source_file):
    pattern = Image.open(pattern_file)
    source = Image.open(source_file)
    #converting images to greyscale from RGB
    pattern = pattern.convert(mode="L")
    source = source.convert(mode="L")
    
    patternHeight, patternWidth = pattern.size
    sourceHeight, sourceWidth = source.size
    
    print patternHeight, patternWidth
    print sourceHeight, sourceWidth  
    


    validate(pattern, source)
    print "Pattern: " + os.path.basename(pattern_file)
    print "Source: " + os.path.basename(source_file)


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
