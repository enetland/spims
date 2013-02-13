import numpy as np
import scipy as sp
from scipy import fftpack, signal
from PIL import Image
import os
import imghdr

# This is just for debugging, should be removed later
import pdb


def match(pattern_file, source_file):
    
    validate(pattern_file, source_file)
    pattern = Image.open(pattern_file)
    patternWidth, patternHeight = pattern.size
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
    coords = np.unravel_index(correlated.argmax(), correlated.shape) 
    # Find the Max of the correlated array, and print out the index in the source image
    print os.path.basename(pattern_file) + " matches " + os.path.basename(source_file) + " at " + str(patternWidth) +\
           "x" + str(patternHeight) + "+" + str(coords[1]) + "+" + str(coords[0])
    # Can visualize the correlated matrix (For testing)
    #Image.fromarray(correlated).show()


def validate(pattern_file, source_file):
    if not Image.open(pattern_file).verify() and Image.open(source_file).verify():
        raise Exception('Not a valid file!')
    elif not check_format(pattern_file):
        raise Exception('Pattern file is incorrect format')
    elif not check_format(source_file):
        raise Exception('Source file is incorrect format')
    elif check_size(pattern_file, source_file):
        raise Exception('Pattern file is larger than source file')
    else: 
        pass 
    # Probably need a lot more verification here, ie. Pattern smaller than Source
    # Not really sure how much the PIL verify function does either, the documentation
    # sucks


def check_format(img_file):
    return imghdr.what(img_file) == 'png' or imghdr.what(img_file) == 'gif' or imghdr.what(img_file) == 'jpeg'

def check_size(pattern_file, source_file):
    pattern = Image.open(pattern_file)
    source = Image.open(source_file)
    return pattern.size > source.size


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
