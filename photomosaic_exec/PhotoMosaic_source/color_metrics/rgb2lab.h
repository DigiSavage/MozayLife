/*
rgb2lab.h

PURPOSE:
    Header for rgb2lab.c — defines the rgb2lab() function for converting RGB to Lab color space.

USAGE:
    Include in any C or Cython code that needs fast color conversion.

MODERNIZATION NOTES:
    - Compatible with C/C++ and Cython.
    - All math and stdio headers included as needed.

Author: (Your Name / MozayLab Project)
*/

#ifndef RGB2LAB_H
#define	RGB2LAB_H

#ifdef	__cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <math.h>

// Converts RGB (R, G, B: 0-255 or 0-1) to Lab (L, a, b: pointers).
void rgb2lab(double R, double G, double B, double *L, double *a, double *b);

#ifdef	__cplusplus
}
#endif

#endif	/* RGB2LAB_H */