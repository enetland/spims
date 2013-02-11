import numpy as np
import scipy as sp
from scipy import fftpack, ndimage, signal
from PIL import Image

#MatPlotLib is not installed on the linux machines, used just for testing
#import matplotlib.pyplot as plt
# This is just for debugging, should be removed later
import pdb


def match(pattern_file, source_file):
    pattern = Image.open(pattern_file).convert('L')
    source = Image.open(source_file)
    validate(pattern, source)
    print "Pattern: " + pattern_file
    print "Source: " + source_file

    pattern = sp.misc.imread(pattern_file, False)
    pattern_fft = fftpack.fft2(pattern)
    pdb.set_trace()
    fft_power = np.log(np.abs(fftpack.fftshift(pattern_fft)) ** 2)
    Image.fromarray(fft_power.astype(np.uint8)).show()
    pdb.set_trace() 
    Image.fromarray(np.abs(fftpack.ifft2(pattern_fft)).astype(np.uint8)).show()
    print pattern.shape
    source = sp.misc.imread(source_file)
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
    if options.pattern is None:
        parser.error('Pattern must be provided')
    if options.source is None:
        parser.error('Source must be provided')
    else:
        match(options.pattern, options.source)
