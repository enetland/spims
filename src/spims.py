import numpy as np
import scipy as sp
from scipy import fftpack, signal
from PIL import Image
import os
import imghdr
import warnings
import pdb

debug = False

class Img:
    def __init__(self, file_name, hash=False):
        self.full_name = file_name
        self.name = os.path.basename(file_name)
        image = self.open()
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.data = np.asarray(image)
        self.height, self.width, self.depth = self.data.shape
        if hash:
            self.hash = perceptual_hash(self.data)
            #self.histogram = histogram(self.data)

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

###############################################################################
# Main Logic
###############################################################################

# Loop through the passed arrays of patterns and sources, matching each pair
def match_dirs(patterns, sources, debug_flag):
    global debug
    debug = debug_flag
    for pattern_file in patterns:
        pattern = Img(pattern_file, True)
        for source_file in sources:
            source = Img(source_file)
            match_rgb(pattern, source)

# Loop through the RGB channels of the pattern and source, match each layer
# takes the highest values from the fft correlation, and validates the match
# using a hash algorithm
def match_rgb(pattern, source):
    correlated = np.zeros(source.data[:,:,0].shape)
    for i in range(3):
        correlated += match_layer(pattern.data[:,:,i], source.data[:,:,i])
    if debug:
        pass
        #show_stretched(correlated)
        #pdb.set_trace()

    while((correlated.max() - correlated.mean() / correlated.std()) > 2):
        point = np.unravel_index(correlated.argmax(), correlated.shape)
        if confirm_match(pattern, source, point):
            print_result(point, pattern, source)
            correlated = blackout(correlated, point, pattern)
        else:
            break

# Run a (simplified) normalized fft correlation over a single channel
# of the pattern and source
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

# Run the confirmation logic on a matching point
def confirm_match(pattern, source, point):
    #hist_threshold = .15
    hash_threshold = 3
    ss = source_slice(source.data, point[1], point[0], pattern.data.shape[1], pattern.data.shape[0]) 
    
    #source_hist = histogram(ss)
    #hist_dist = histogram_distance(pattern.histogram, source_hist)    
    
    source_hash = perceptual_hash(ss)
    hash_dist = np.sum(np.abs(pattern.hash - source_hash))
    
    if debug:
        #print 'hist_dist: ' + hist_dist.__str__()
        print 'hash_dist: ' + hash_dist.__str__()
        if hash_dist < hash_threshold:
            Image.fromarray(ss.astype(np.uint8)).show()
        pdb.set_trace()

    return  hash_dist < hash_threshold

# If the coordinates returned by match are beyond the bounds of the
# source image, a match was NOT found.
def is_match(pattern, source, match_coords):
    return (match_coords[1] + pattern.width) <= source.width and \
            (match_coords[0] + pattern.height) <= source.height

# Prints the coordinates of the matching images as well as the pattern 
# and source image file names
def print_result(match_coords, pattern, source):
    if match_coords and is_match(pattern, source, match_coords):
        x = match_coords[1]
        y = match_coords[0]
        print "%s matches %s at %dx%d+%d+%d" % (pattern.name,
                source.name, pattern.width, pattern.height, x, y)
        # Can visualize the correlated matrix (For testing)
        # Image.fromarray(correlated).show()

# Blacks out part of the correlation map to eliminate peaks, finding multiple
# matches
def blackout(correlated, point, pattern):
    width = pattern.data.shape[1] / 2
    height = pattern.data.shape[0] / 2
    
    y = point[0] - height / 2
    y = y if y > 0 else 0
    
    x = point[1] - width / 2
    x =  x if x > 0 else 0

    y2 = point[0] + height / 2
    y2 = y2 if y2 < correlated.shape[0] else correlated.shape[0]

    x2 = point[1] + width / 2
    x2 = x2 if x2 < correlated.shape[1] else correlated.shape[1]
    
    correlated[y:y2, x:x2] *= np.zeros((y2-y, x2-x))
    return correlated

# Raises exceptions for the followiing incorrect inputs:
# Invalid file type, incorrect image format for the pattern or source file 
# and when the pattern file is bigger than the source file  
def validate(pattern, source):
    if check_size(pattern, source):
        raise Exception('Pattern file is larger than source file')

###############################################################################
# Validation Logic
##############################################################################

# This method will slice out a portion of a source image, for use with the hashing
# and histogram methods
def source_slice(source, x, y, width, height):
    slice = source[y:y+height,x:x+width,:]
    #Image.fromarray(slice.astype(np.uint8)).show()
    return slice

# This method takes any image, resizes it to 8x8, and hashes into a 64 length
# array for comparison. It doesn't work at all.
def perceptual_hash(data):
    im = np.asarray(Image.fromarray(data).resize((8,8), Image.ANTIALIAS).convert('L'))
    result = im > im.mean()
    return result

# Calculates a color histogram, using 256 buckets for each RGB channel
def histogram(data):
    histograms = np.zeros(0, np.uint8)
    for i in range(3):
       histograms =  np.append(histograms, np.histogram(data[:,:,i], bins=256, normed=True)[0])
    flat = histograms.ravel()
    return flat

# Given two histograms, calculates a difference between them.
# This is a very stupid version of the distance calculation, doesn't work very well.
# With a better distance calculation this could potentially be much more useful.
def histogram_distance(h1, h2):
    diff = h1 - h2
    return np.sqrt(np.dot(diff, diff))

# Simply confirms that the pattern is smaller in both dimensions than 
# the source image
def check_size(pattern, source):
    return pattern.width > source.width or \
            pattern.height > source.height

###############################################################################
# Debugging and Visualization
###############################################################################

# Open a contrast stretched version of the passed array (only really useful for
# the correlation plot
def show_stretched(array):
    Image.fromarray(contrast_stretch(array).astype(np.uint8)).show()

# Stretches the pixel values of the correlation plot to full 0-256, scaling
# each pixel appropriately
def contrast_stretch(array):
    return (array - array.min()) / (array.max() - array.min()) * 255
