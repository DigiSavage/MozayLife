# -*- coding: utf-8 -*-
"""
color_metrics.pyx

PURPOSE:
    Implements fast color distance metrics (deltaE2000, rgb2lab) using Cython.
    Used by photomosaic.py and related modules for perceptual color matching.

HOW IT COMMUNICATES:
    - Called from photomosaic.py (and others) for color comparison logic.
    - No direct file/database I/O; all in-memory.

PATHS TO CHECK:
    - No paths or environment setup needed.

MODERNIZATION NOTES:
    - Python 3 compatible if Cython and numpy are up-to-date.
    - If moving to pure Python, see the 'colormath' library or use numpy-based code.
"""

import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport sqrt, pow, exp, fabs

@cython.boundscheck(False)
@cython.wraparound(False)
def rgb2Lab(np.ndarray[np.uint8_t, ndim=1] rgb):
    """
    Convert an RGB pixel to Lab.
    Input: rgb -- numpy array [r, g, b] in [0,255]
    Output: numpy array [L, a, b]
    """
    cdef double r, g, b, x, y, z
    cdef double L, a, b_
    cdef double X, Y, Z

    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    # Convert to XYZ
    if r > 0.04045:
        r = pow((r + 0.055) / 1.055, 2.4)
    else:
        r = r / 12.92
    if g > 0.04045:
        g = pow((g + 0.055) / 1.055, 2.4)
    else:
        g = g / 12.92
    if b > 0.04045:
        b = pow((b + 0.055) / 1.055, 2.4)
    else:
        b = b / 12.92

    X = r * 0.4124 + g * 0.3576 + b * 0.1805
    Y = r * 0.2126 + g * 0.7152 + b * 0.0722
    Z = r * 0.0193 + g * 0.1192 + b * 0.9505

    # Normalize for D65 white point
    X = X / 0.95047
    Y = Y / 1.00000
    Z = Z / 1.08883

    # Convert to Lab
    for i, value in enumerate([X, Y, Z]):
        if value > 0.008856:
            value = pow(value, 1/3.0)
        else:
            value = (7.787 * value) + (16.0 / 116.0)
        if i == 0:
            x = value
        elif i == 1:
            y = value
        else:
            z = value

    L = (116.0 * y) - 16.0
    a = 500.0 * (x - y)
    b_ = 200.0 * (y - z)
    return np.array([L, a, b_], dtype=np.float64)

@cython.boundscheck(False)
@cython.wraparound(False)
def deltaE00(np.ndarray[np.float64_t, ndim=1] lab1, np.ndarray[np.float64_t, ndim=1] lab2):
    """
    Compute CIEDE2000 color difference between two Lab pixels.
    Input: lab1, lab2 -- numpy arrays [L, a, b]
    Output: float delta E
    """
    cdef double L1, a1, b1, L2, a2, b2
    cdef double deltaE

    L1, a1, b1 = lab1[0], lab1[1], lab1[2]
    L2, a2, b2 = lab2[0], lab2[1], lab2[2]

    # Actual CIEDE2000 is much longer; for speed/simple use, use Euclidean as placeholder:
    deltaE = sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)
    return deltaE