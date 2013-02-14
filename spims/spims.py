import numpy as np
import scipy as sp
from scipy import fftpack, signal
from PIL import Image
import os
import imghdr

# This is just for debugging, should be removed later
import pdb

class Img:
    def __init__(self, file_name):
        self.full_name = file_name
        self.name = os.path.basename(file_name)
        self.image = Image.open(file_name)
        if self.image.mode != 'RGB':
            self.image = self.image.convert('RGB')
	self.data = np.asarray(self.image)
        self.height, self.width, self.depth = self.data.shape

    def is_valid_format(self):
        return imghdr.what(self.full_name) == 'png' \
                or imghdr.what(self.full_name) == 'gif' \
                or imghdr.what(self.full_name) == 'jpeg'

def match_rgb(pattern, source):
    correlated = np.zeros(source.data[:,:,0].shape)
    for i in range(2):
        correlated += match_layer(pattern.data[:,:,i], source.data[:,:,i])
    return np.unravel_index(correlated.argmax(), correlated.shape)

def match_layer(pattern_layer, source_layer):
    # Normalize the two arrays, should be like this:
    # http://stackoverflow.com/questions/5639280/why-numpy-correlate-and-corrcoef-return-different-values-and-how-to-normalize
    # a = (a - mean(a)) / (std(a) * len(a))
    # v = (v - mean(v)) /  std(v)
    normalized_pattern = (pattern_layer - np.mean(pattern_layer)) / (np.std(pattern_layer) * pattern_layer.size)
    normalized_source = (source_layer - np.mean(source_layer)) / np.std(source_layer)

    #Take the fft of both Images, padding the pattern out with 0's
    # to be the same shape as the source
    pattern_fft = fftpack.fft2(normalized_pattern, source_layer.shape)
    source_fft = fftpack.fft2(normalized_source)

    # Perform the correlation in the frequency domain, which just the
    # inverse FFT of the pattern matrix's conjugate * the source matrix
    # http://en.wikipedia.org/wiki/Cross-correlation#Properties
    return fftpack.ifft2(pattern_fft.conjugate() * source_fft) 
 
# If the coordinates returned by match are beyond the bounds of the
# source image, a match was NOT found.
def is_match(pattern, source, x, y):
    return (x + pattern.width) <= source.width and \
            (y + pattern.height) <= source.height

# Prints the coordinates of the matching images as well as the pattern 
# and source image file names
def print_result(match_coords, pattern, source):
    x = match_coords[1]
    y = match_coords[0]
    if is_match(pattern, source, x, y):
        print "%s matches %s at %dx%d+%d+%d" % (pattern.name,
                source.name, pattern.width, pattern.height, x, y)
        # Can visualize the correlated matrix (For testing)
        # Image.fromarray(correlated).show()

# Raises exceptions for the followiing incorrect inputs:
# Invalid file type, incorrect image format for the pattern or source file 
# and when the pattern file is bigger than the source file  
def validate(pattern, source):
    if not Image.open(pattern.full_name).verify() and Image.open(source.full_name).verify():
        raise Exception('Not a valid file!')
    elif not pattern.is_valid_format():
        raise Exception('Pattern file is incorrect format')
    elif not pattern.is_valid_format():
        raise Exception('Source file is incorrect format')
    elif check_size(pattern, source):
        raise Exception('Pattern file is larger than source file')
    else: 
        pass 

def check_size(pattern, source):
    return pattern.width > source.width or \
            pattern.height > source.height

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
        pattern = Img(options.pattern)
        source = Img(options.source)
        match_coords = match_rgb(pattern, source)
        print_result(match_coords, pattern, source)
