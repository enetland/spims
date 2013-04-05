""" Define Img class, handle main matching loop and printing of matches """

import numpy as np
from PIL import Image
import os
import imghdr
import confirmation
import match
import single_match

debug = False


class Img:
    """
    Img Class handles image file validation and storage of all relavant image
    information.

    full_name - Image file path
    name - Image file name
    data - NumPy ndarray with RGB data
    height - Image height
    width - Image width
    hash - Perceptual hash of image where appropriate

    """
    def __init__(self, file_name, hash=False):
        self.full_name = file_name
        self.name = os.path.basename(file_name)
        image = self.open()
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.data = np.asarray(image)
        self.height, self.width, _ = self.data.shape
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


def run(patterns, sources):
    """
    Main matching loop. Loops over passed pattern and source arrays, creating
    an instance of the Img class for each and running the match code.

    patterns - List of pattern file locations
    sources - List of source file locations

    """
    for pattern_file in patterns:
        pattern = Img(pattern_file, True)
        for source_file in sources:
            source = Img(source_file)
            do_match(pattern, source)


def do_match(pattern, source):
    """
    Match two images. Performs the appropriate match algorithm, and prints the
    resulting matches.

    pattern - Img instance for pattern image
    source - Img instance for source image

    """

    if pattern.data.shape == (1, 1, 3):
        single_match.match_pixel(pattern, source)
    else:
        match.correlate_rgb(pattern, source)


###############################################################################
# Utils
###############################################################################
def print_result(match_coords, pattern, source):
    """
    Match printing function, prints output in format:
    '<file1> matches <file2> at <m1>x<n1>+<x>+<y>'.

    match_coords - tuple representing coordinates of pattern in source (y, x)
    pattern - Img instance for pattern image
    source - Img instance for source image

    """
    x = match_coords[1]
    y = match_coords[0]
    print "%s matches %s at %dx%d+%d+%d" % (pattern.name,
          source.name, pattern.width, pattern.height, x, y)


# TODO: remove this method once scaling is implemented
def check_size(pattern, source):
    """
    Validates that pattern image is smaller than source image in both dimensions

    pattern - Img instance for pattern image
    source - Img instance for source image

    """
    return pattern.width > source.width or \
        pattern.height > source.height

###############################################################################
# Debugging and Visualization
###############################################################################


def show_stretched(array):
    """ Utility function to show stretched correlation plots for debugging """
    show_image(contrast_stretch(array))


def show_image(array):
    """ Utility function to display an image array, used for debugging. """
    Image.fromarray(array.astype(np.uint8)).show()


def contrast_stretch(array):
    """
    Stretches the pixel values of the correlation plot to full 0-256, scaling
    each pixel appropriately

    """
    return (array - array.min()) / (array.max() - array.min()) * 255
