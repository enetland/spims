import numpy as np
import scipy as sp
from scipy import fftpack, ndimage, signal
from PIL import Image

#MatPlotLib is not installed on the linux machines, used just for testing
#import matplotlib.pyplot as plt
# This is just for debugging, should be removed later
import pdb


def match(pattern_file, source_file):
    validate(pattern_file, source_file)
    print "Pattern: " + pattern_file
    print "Source: " + source_file
    #First, Read in Both pattern and Source images
    pattern = sp.misc.imread(pattern_file, False)
    source = sp.misc.imread(source_file, False)

    #Take the fft of both Images, Padding out the smaller image with
    # black to standardize the size
    pattern_fft = fftpack.fft2(pattern)

    # Normalize the two arrays, should be like this:
    # http://stackoverflow.com/questions/5639280/why-numpy-correlate-and-corrcoef-return-different-values-and-how-to-normalize
    # a = (a - mean(a)) / (std(a) * len(a))
    # v = (v - mean(v)) /  std(v) 
    
    
    #Now we should be able to use signal.correlate2d to find the match location
    # The output of this process is an array, I *think* the max value in this
    # Array will be the upper left corner of the Match Location


    #Some Testing Code
    pdb.set_trace()
    fft_power = np.log(np.abs(fftpack.fftshift(pattern_fft)) ** 2)
    Image.fromarray(fft_power.astype(np.uint8)).show()
    pdb.set_trace() 
    Image.fromarray(np.abs(fftpack.ifft2(pattern_fft)).astype(np.uint8)).show()
    print pattern.shape
    source = sp.misc.imread(source_file)
    print source.shape


def validate(pattern_file, source_file):
    
    Image.open(pattern_file).verify()
    Image.open(source_file).verify()

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
