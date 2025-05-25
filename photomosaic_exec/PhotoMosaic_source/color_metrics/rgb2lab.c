/*
rgb2lab.c

PURPOSE:
    Convert RGB color values to CIELab color space (D65 white point).
    Used by photomosaic engine for color matching.

HOW IT WORKS:
    - Accepts R, G, B as input (range 0–255 or 0–1.0, auto-scaled).
    - Writes Lab values to provided double pointers.

MODERNIZATION NOTES:
    - This code is portable and works as-is for C, Cython, and Python extension modules.
    - See rgb2lab.h for function signature and cross-language linkage.

Author: (Your Name / MozayLab Project)
*/

#include "rgb2lab.h"
#include <math.h>

void rgb2lab(double R, double G, double B, double *L, double *a, double *b) {
    if (R > 1.0 || G > 1.0 || B > 1.0) {
        R /= 255.0;
        G /= 255.0;
        B /= 255.0;
    }
    // Set a threshold
    double T = 0.008856;

    double x = R * 0.412453 + G * 0.357580 + B * 0.180423;
    double y = R * 0.212671 + G * 0.715160 + B * 0.072169;
    double z = R * 0.019334 + G * 0.119193 + B * 0.950227;

    // xyz to lab
    x /= 0.950456;
    y /= 1.0;
    z /= 1.088754;

    int xT = (x > T) ? 1 : 0;
    int yT = (y > T) ? 1 : 0;
    int zT = (z > T) ? 1 : 0;

    double fX = xT * pow(x, 1.0/3.0) + (!xT) * (7.787 * x + 16.0/116.0);
    double fY = yT * pow(y, 1.0/3.0) + (!yT) * (7.787 * y + 16.0/116.0);
    double fZ = zT * pow(z, 1.0/3.0) + (!zT) * (7.787 * z + 16.0/116.0);

    *L = yT * (116.0 * pow(y, 1.0/3.0) - 16.0) + (!yT) * (903.3 * y);
    *a = 500.0 * (fX - fY);
    *b = 200.0 * (fY - fZ);
}