import numpy as np
from scipy import fftpack
from PIL import Image
import os
import imghdr
import pdb
import confirmation

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
            matches = fft_match_layers(pattern, source)
        return matches


###############################################################################
# FFT Algorithm
###############################################################################

# Loop through the RGB channels of the pattern and source, match each layer
# Loop through the correlation until either a match is not found or the max
# value becomes 0
def fft_match_layers(pattern, source):
    correlated = np.zeros(source.data[:, :, 0].shape)
    for i in range(3):
        correlated += fft_match_layer(pattern.data[:, :, i], source.data[:, :, i])
    matches = []
    while correlated.max() > 0:
        point = np.unravel_index(correlated.argmax(), correlated.shape)
        if confirmation.confirm_match(pattern, source, point):
            print_result(point, pattern, source)
            correlated = blackout(correlated, point, pattern)
            matches.append(point)
        else:
            break
    return matches


# Run a (simplified) normalized fft correlation over a single channel
# of the pattern and source
def fft_match_layer(pattern_layer, source_layer):
  # http://bit.ly/WsRveH
    if pattern_layer.std() == 0:
        normalized_pattern = pattern_layer
    else:
        normalized_pattern = ((pattern_layer - np.mean(pattern_layer)) /
                              (np.std(pattern_layer) * pattern_layer.size))
    if source_layer.std() == 0:
        normalized_source = source_layer
    else:
        normalized_source = ((source_layer - np.mean(source_layer)) /
                             np.std(source_layer))

    #Take the fft of both Images, padding the pattern out with 0's
    # to be the same shape as the source
    pattern_fft = fftpack.fft2(normalized_pattern, source_layer.shape)
    source_fft = fftpack.fft2(normalized_source)

    # Perform the correlation in the frequency domain, which just the
    # inverse FFT of the pattern matrix's conjugate * the source matrix
    # http://en.wikipedia.org/wiki/Cross-correlation#Properties
    return fftpack.ifft2(pattern_fft.conjugate() * source_fft)


# Blacks out part of the correlation map to eliminate peaks, finding multiple
# matches
def blackout(correlated, point, pattern):
    width = pattern.data.shape[1] / 2
    height = pattern.data.shape[0] / 2

    # This section basically makes sure we don't go beyond the bounds of the
    # correlation map
    y = point[0] - height / 2
    y = y if (y > 0) else 0

    x = point[1] - width / 2
    x = x if (x > 0) else 0

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
