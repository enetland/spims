################################################################################
# SPIMS Match Confirmation Logic
################################################################################
import numpy as np
from PIL import Image


# Run the confirmation logic on a matching point
def confirm_match(pattern, source, point):
    if not is_match_in_bounds(pattern, source, point):
        return False

    ss = source_slice(source.data, point[1], point[0], pattern.data.shape[1], pattern.data.shape[0])
    # If the pattern does not have a hash, compare pixels directly
    if pattern.hash is None:
        pixel_threshold = 1 + (pattern.data.size / 10)
        pixel_dist = pixel_distance(pattern.data, ss)
        return (pixel_dist < pixel_threshold)
    else:
        hash_threshold = 3
        source_hash = perceptual_hash(ss)
        hash_dist = np.sum(np.abs(pattern.hash - source_hash))
        return (hash_dist < hash_threshold)


def is_match_in_bounds(pattern, source, point):
    return (point[1] + pattern.width) <= source.width and \
        (point[0] + pattern.height) <= source.height


# This method will slice out a portion of a source image, for use with the hashing
# and histogram methods
def source_slice(source, x, y, width, height):
    return source[y:y+height, x:x+width, :]


# This method takes any image, resizes it to 8x8, and hashes into a 64 length
# array for comparison. It doesn't work at all.
def perceptual_hash(data):
    im = np.asarray(Image.fromarray(data).resize((8, 8), Image.ANTIALIAS).convert('L'))
    if im.std() < .03:
        return None
    result = im > im.mean()
    return result


# Directly calculate the distance between the pixel values of two images. Trying
# this out for smaller patterns where the hash doesnt make sense
def pixel_distance(i1, i2):
    return np.sqrt(np.sum((i1-i2) ** 2))
