"""
Confirm matches found through cross-correlation algorithm or direct pixel search
Using perceptual hashing and pixel distance

"""
import numpy as np
from PIL import Image

HASH_THRESHOLD = 3


def confirm_match(pattern, source, point):
    """
    Run appropriate confirmation step on the supposed match point.

    pattern - Img instance for pattern
    source - Img instance for source
    point - match point to be confirmed

    """
    # Check if match would be outisde bounds of source image.
    if not is_match_in_bounds(pattern, source, point):
        return False

    ss = source_slice(source, point, pattern.data.shape)
    # If the pattern does not have a hash, compare pixels directly
    if pattern.hash is None:
        pixel_threshold = 1 + (pattern.data.size / 10)
        pixel_dist = pixel_distance(pattern.data, ss)
        return (pixel_dist < pixel_threshold)
    else:
        source_hash = perceptual_hash(ss)
        hash_dist = np.sum(np.abs(pattern.hash - source_hash))
        return (hash_dist < HASH_THRESHOLD)


def is_match_in_bounds(pattern, source, point):
    """ Confirm that match would fall within source bounds """
    return (point[1] + pattern.width) <= source.width and \
        (point[0] + pattern.height) <= source.height


def source_slice(source, point, shape):
    """
    Slice out a portion of the source image matching the pattern shape at the
    match location.

    source - Img instance for source
    point - tuple (y, x) for matching point
    shape - tuple (y, x) for shape of matching pattern

    """
    x = point[1]
    y = point[0]
    width = shape[1]
    height = shape[0]
    return source.data[y:y+height, x:x+width, :]


def perceptual_hash(data):
    """
    Perform perceptual hash on an image. Algorithm resizes the image to 8x8
    greyscale image, and outputs an 8x8 boolean array representing whether
    a given pixel is above the mean.

    Skips the hash if the std deviation is so low it will not be useful.

    data - ndarray representing image to be hashed
    """
    im = Image.fromarray(data).resize((8, 8), Image.ANTIALIAS).convert('L')
    array = np.asarray(im)
    if array.std() < .03:
        return None
    return array > array.mean()


# Directly calculate the distance between the pixel values of two images. Trying
# this out for smaller patterns where the hash doesnt make sense
def pixel_distance(ndimage_1, ndimage_2):
    """
    Direct pixel distance calculation, uses sum of squared difference betweeen
    rgb values to check if images are similar. Does not hold up will to
    compression/conversion artifacts.

    Passed arrays must be the same size, or this will blow up.

    ndimage_1 - ndarray of first image data
    ndimage_2 - ndarray of second image data
    """
    return np.sqrt(np.sum((ndimage_1 - ndimage_2) ** 2))
