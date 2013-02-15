import numpy as np
import scipy as sp
from scipy import fftpack, signal
from PIL import Image
import os
import imghdr
import warnings
import pdb


class Img:
    def __init__(self, file_name):
        self.full_name = file_name
        self.name = os.path.basename(file_name)
        self.image = self.open()
        if self.image.mode != 'RGB':
            self.image = self.image.convert('RGB')
        self.data = np.asarray(self.image)
        self.height, self.width, self.depth = self.data.shape

    def open(self):
        try:
            fname = self.full_name
            img = Image.open(fname)
            if not (imghdr.what(fname) == 'png'
                    or imghdr.what(fname) == 'gif'
                    or imghdr.what(fname) == 'jpeg'):
                print "Invalid file given: %s" % fname
                exit(1)
            else:
                return img
        except IOError:
            print "No such file or directory: %s" % fname
            exit(1)

def match_rgb(pattern, source):
    # Ignore's ComplexWarning when casting complex values to
    # real values, which effectivly discards the imaginary part
    warnings.simplefilter("ignore", np.ComplexWarning)
    correlated = np.zeros(source.data[:,:,0].shape)
    for i in range(2):
        correlated += match_layer(pattern.data[:,:,i], source.data[:,:,i])
    return np.unravel_index(correlated.argmax(), correlated.shape)

def match_layer(pattern_layer, source_layer):
    # Normalize the two arrays, should be like this:
    # a = (a - mean(a)) / (std(a) * len(a))
    # v = (v - mean(v)) /  std(v)
    # Source: http://bit.ly/WsRveH
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
    if check_size(pattern, source):
        raise Exception('Pattern file is larger than source file')
    else: 
        pass 

def check_size(pattern, source):
    return pattern.width > source.width or \
            pattern.height > source.height

