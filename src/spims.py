import numpy as np
import scipy as sp
from scipy import fftpack, signal
from PIL import Image
import os
import imghdr
import warnings
import pdb

debug = False

###############################################################################
# Image Class
# Handles loading image files and all error checking
# Stores relavant information about the image file. 
# TODO: Should make separate pattern subclass for the hash method, rather than
#       the current boolean flag
#       Might also want to normalize and run FFT here, need separate source
#       Subclass as well
###############################################################################
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
        pattern = Img(pattern_file, hash=True)
        for source_file in sources:
            source = Img(source_file)
            if pattern.data.shape == (1,1,3):
                match_pixel(pattern, source)
            else:
                match_rgb(pattern, source)
                
###############################################################################
# FFT Algorithm
###############################################################################              

# Loop through the RGB channels of the pattern and source, match each layer
# Loop through the correlation until either a match is not found or the max
# value becomes 0
def match_rgb(pattern, source):
    correlated = np.zeros(source.data[:,:,0].shape)
    for i in range(3):
        correlated += match_layer(pattern.data[:,:,i], source.data[:,:,i])
    if debug:
        pass
        #show_stretched(correlated)
        #pdb.set_trace()
    while correlated.max() > 0:
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
    if pattern_layer.std() == 0:
        normalized_pattern = pattern_layer
    else:
        normalized_pattern = (pattern_layer - np.mean(pattern_layer)) / (np.std(pattern_layer) * pattern_layer.size)
    if source_layer.std() == 0:
        normalized_source = source_layer
    else:
        normalized_source = (source_layer - np.mean(source_layer)) / np.std(source_layer)

    #Take the fft of both Images, padding the pattern out with 0's
    # to be the same shape as the source
    pattern_fft = fftpack.fft2(normalized_pattern, source_layer.shape)
    source_fft = fftpack.fft2(normalized_source)

    # Perform the correlation in the frequency domain, which just the
    # inverse FFT of the pattern matrix's conjugate * the source matrix
    # http://en.wikipedia.org/wiki/Cross-correlation#Properties
    return fftpack.ifft2(pattern_fft.conjugate() * source_fft) 

###############################################################################
# Single Pixel Algorithm
###############################################################################
def match_pixel(pattern, source):
    nearest =  np.sum(np.abs(source.data-pattern.data), axis=2)
    while nearest.min() < 50:
        point = np.unravel_index(nearest.argmin(), nearest.shape)
        if pixel_distance(pattern.data, source.data[point]) < 15:
            print_result(point, pattern, source)
            nearest[point] = 50
        else:
            break

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
    
    # This section basically makes sure we don't go beyond the bounds of the
    # correlation map 
    y = point[0] - height / 2
    y = y if y > 0 else 0
    
    x = point[1] - width / 2
    x =  x if x > 0 else 0

    y2 = point[0] + height / 2
    y2 = y2 if y2 < correlated.shape[0] else correlated.shape[0]

    x2 = point[1] + width / 2
    x2 = x2 if x2 < correlated.shape[1] else correlated.shape[1]
    
    if y2 == y:
        y2 = y + 1
    if x2 == x:
        x2 = x + 1
    # Zero out the correct part of the correlation map
    correlated[y:y2, x:x2] *= np.zeros((y2-y, x2-x))
    return correlated
    

###############################################################################
# Validation Logic
##############################################################################

# Run the confirmation logic on a matching point
def confirm_match(pattern, source, point):
    ss = source_slice(source.data, point[1], point[0], pattern.data.shape[1], pattern.data.shape[0]) 
    if debug:
        pass
        #Image.fromarray(ss.astype(np.uint8)).show()
        #pdb.set_trace()
    # If the pattern does not have a hash, compare pixels directly
    if pattern.hash is None:
        pixel_threshold = 1 + (pattern.data.size / 10)
        pixel_dist = pixel_distance(pattern.data, ss)    
        return pixel_dist < pixel_threshold
    else:
        hash_threshold = 3
        source_hash = perceptual_hash(ss)
        hash_dist = np.sum(np.abs(pattern.hash - source_hash))
        return  hash_dist < hash_threshold

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
    if im.std() < .03:
        return None
    result = im > im.mean()
    return result

# Directly calculate the distance between the pixel values of two images. Trying
# this out for smaller patterns where the hash doesnt make sense
def pixel_distance(i1, i2):
    return np.sqrt(np.sum((i1-i2) ** 2))

# Simply confirms that the pattern is smaller in both dimensions than 
# the source image
def check_size(pattern, source):
    return pattern.width > source.width or \
            pattern.height > source.height
            
# Exits with code 1 for the followiing incorrect inputs:
# Invalid file type, incorrect image format for the pattern or source file 
# and when the pattern file is bigger than the source file  
def validate(pattern, source):
    if check_size(pattern, source):
        print 'Pattern file is larger than source file'
        exit(1)

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
