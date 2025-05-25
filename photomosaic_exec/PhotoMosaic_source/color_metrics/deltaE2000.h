#ifndef DELTA_E_2000_H
#define DELTA_E_2000_H

#ifdef __cplusplus
extern "C" {
#endif

#include <math.h>

#ifndef PI
    #ifdef M_PI
        #define PI M_PI
    #else
        #define PI 3.14159265358979323846
    #endif
#endif

double deltaE2000(double Lstd, double astd, double bstd,
                  double Lsample, double asample, double bsample,
                  double kL, double kC, double kH);

#ifdef __cplusplus
}
#endif

#endif /* DELTA_E_2000_H */