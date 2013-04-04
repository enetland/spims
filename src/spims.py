import numpy as np
from scipy import fftpack
from PIL import Image
import os
import imghdr
import pdb
import confirmation
import match

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
            self.hash = confirmation.perceptual_hash(self.data)

    def open(self):
        fname = self.full_name
        img = Image.open(fname)
        if not (imghdr.what(fname) == 'png'
                or imghdr.what(fname) == 'gif'
                or imghdr.what(fname) == 'jpeg'):
            print "Invalid file given: %s" % fname
            exit(1)
        else:
            return img

    @staticmethod
    def match(pattern, source):
        matches = []
        if pattern.data.shape == (1, 1, 3):
            matches = match_pixel(pattern, source)
        else:
            matches = match.fft_match_layers(pattern, source)
        return matches


###############################################################################
# Single Pixel Algorithm
###############################################################################
def match_pixel(pattern, source):
    nearest = np.sum(np.abs(source.data - pattern.data), axis=2)
    while nearest.min() < 50:
        point = np.unravel_index(nearest.argmin(), nearest.shape)
        if confirmation.pixel_distance(pattern.data, source.data[point]) < 15:
            print_result(point, pattern, source)
            nearest[point] = 50
        else:
            break


###############################################################################
# Utils
###############################################################################
def print_result(match_coords, pattern, source):
    x = match_coords[1]
    y = match_coords[0]
    print "%s matches %s at %dx%d+%d+%d" % (pattern.name,
          source.name, pattern.width, pattern.height, x, y)


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
