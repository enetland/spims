###############################################################################
# Single Pixel Algorithm
###############################################################################
import numpy as np
import confirmation
import spims


def match_pixel(pattern, source):
    nearest = np.sum(np.abs(source.data - pattern.data), axis=2)
    while nearest.min() < 50:
        point = np.unravel_index(nearest.argmin(), nearest.shape)
        if confirmation.pixel_distance(pattern.data, source.data[point]) < 15:
            spims.print_result(point, pattern, source)
            nearest[point] = 50
        else:
            break
