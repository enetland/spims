""" Separate Algorithm for single pixel/single color images. """

import numpy as np
import confirmation
import spims


# TODO: Expand to support scaling by searching for largest patches of color
# in source image.
def match_pixel(pattern, source):
    """
    Algorithm to match a single pixel pattern image.

    pattern - Img instance for pattern image
    source - Img instance for source image

    """
    nearest = np.sum(np.abs(source.data - pattern.data), axis=2)
    while nearest.min() < 50:
        point = np.unravel_index(nearest.argmin(), nearest.shape)
        if confirmation.pixel_distance(pattern.data, source.data[point]) < 15:
            spims.print_result(point, pattern, source)
            nearest[point] = 50
        else:
            break
