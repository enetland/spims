import numpy as np
import scipy as sp
from scipy import fftpack, signal
from PIL import Image

# This is just for debugging, should be removed later
import pdb


def match(pattern_file, source_file):
    validate(pattern_file, source_file)
    print "Pattern: " + pattern_file
    print "Source: " + source_file
    #First, Read in Both pattern and Source images
    pattern = sp.misc.imread(pattern_file, True)
    source = sp.misc.imread(source_file, True)

    # Normalize the two arrays, should be like this:
    # http://stackoverflow.com/questions/5639280/why-numpy-correlate-and-corrcoef-return-different-values-and-how-to-normalize
    # a = (a - mean(a)) / (std(a) * len(a))
    # v = (v - mean(v)) /  std(v)
    normalized_pattern = (pattern - np.mean(pattern)) / (np.std(pattern) * pattern.size)
    normalized_source = (source - np.mean(source)) / np.std(source)

    #Take the fft of both Images, padding the pattern out with 0's to be the same shape as the source
    pattern_fft = fftpack.fft2(normalized_pattern, source.shape)
    source_fft = fftpack.fft2(normalized_source)

    # Perform the correlation in the frequency domain, which just the inverse FFT of the pattern matrix's conjugate *
    # the source matrix
    # http://en.wikipedia.org/wiki/Cross-correlation#Properties
    correlated = fftpack.ifft2(pattern_fft.conjugate() * source_fft)
    
    # Find the Max of the correlated array, and print out the index in the source image
    print np.unravel_index(correlated.argmax(), correlated.shape)
 
    # Can visualize the correlated matrix (For testing)
    #Image.fromarray(correlated).show()


def validate(pattern_file, source_file):
    Image.open(pattern_file).verify()
    Image.open(source_file).verify()
    # Probably need a lot more verification here, ie. Pattern smaller than Source
    # Not really sure how much the PIL verify function does either, the documentation
    # sucks

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
