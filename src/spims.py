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
            self.histogram = histogram(self.data)

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
    # warnings.simplefilter("ignore", np.ComplexWarning)
    correlated = np.zeros(source.data[:,:,0].shape)
    for i in range(3):
        correlated += match_layer(pattern.data[:,:,i], source.data[:,:,i])
    point = np.unravel_index(correlated.argmax(), correlated.shape)
    if debug:
        print 'location: ' + point.__str__()
        print 'std_dev from mean: ' + ((correlated.max() - correlated.mean()) / correlated.std()).__str__()
        print 'max_value: ' + correlated.max().__str__()
        #show_stretched(correlated)
        #pdb.set_trace()
    if ((correlated.max() - correlated.mean()) / correlated.std()) > 2 and  confirm_match(pattern, source, point):
        return point
    else:
        return False

def confirm_match(pattern, source, point):
    hist_threshold = .25
    hash_threshold = 5
    ss = source_slice(source.data, point[1], point[0], pattern.data.shape[1], pattern.data.shape[0]) 
    
    source_hist = histogram(ss)
    hist_dist = histogram_distance(pattern.histogram, source_hist)    
    
    source_hash = perceptual_hash(ss)
    hash_dist = np.sum(np.abs(pattern.hash - source_hash))
    

    if debug:
        print 'hist_dist: ' + hist_dist.__str__()
        print 'hash_dist: ' + hash_dist.__str__()
        if hist_dist < hist_threshold or hash_dist < hash_threshold:
            Image.fromarray(ss.astype(np.uint8)).show()
            pdb.set_trace()
    return hist_dist < hist_threshold or hash_dist < hash_threshold
    

def match_dirs(patterns, sources, debug_flag):
    global debug
    debug = debug_flag
    for pattern_file in patterns:
        pattern = Img(pattern_file, True)
        for source_file in sources:
            source = Img(source_file)
            match_coords = match_rgb(pattern, source)
            print_result(match_coords, pattern, source)

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

# Raises exceptions for the followiing incorrect inputs:
# Invalid file type, incorrect image format for the pattern or source file 
# and when the pattern file is bigger than the source file  
def validate(pattern, source):
    if check_size(pattern, source):
        raise Exception('Pattern file is larger than source file')
    else: 
        pass
# This method takes any image, resizes it to 8x8, and hashes into a 64 length
# array for comparison. It doesn't work at all.
def perceptual_hash(data):
    im = np.asarray(Image.fromarray(data).resize((8,8), Image.ANTIALIAS).convert('L'))
    result = im > im.mean()
    return result

def source_slice(source, x, y, width, height):
    slice = source[y:y+height,x:x+width,:]
    #Image.fromarray(slice.astype(np.uint8)).show()
    return slice

##Calculate a histogram using 768 buckets, one for each value
def histogram(data):
    histograms = np.zeros(0, np.uint8)
    for i in range(3):
       histograms =  np.append(histograms, np.histogram(data[:,:,i], bins=256, normed=True)[0])
    flat = histograms.ravel()
    return flat

def histogram_distance(h1, h2):
    diff = h1 - h2
    return np.sqrt(np.dot(diff, diff))

def check_size(pattern, source):
    return pattern.width > source.width or \
            pattern.height > source.height

#debugging/visualization

def show_stretched(array):
    Image.fromarray(contrast_stretch(array).astype(np.uint8)).show()

def contrast_stretch(array):
    return (array - array.min()) / (array.max() - array.min()) * 255
