#include "deltaE2000.h"
//#include <stdio.h>
#include <math.h> // Needed for sqrt, pow, atan2, sin, cos, fabs, exp

#ifndef PI
#define PI 3.14159265358979323846
#endif

/* Compute deltaE2000 metric */

double deltaE2000(double Lstd, double astd, double bstd,
                  double Lsample, double asample, double bsample,
                  double kL, double kC, double kH) {

    double kl = kL;
    double kc = kC;
    double kh = kH;
    double Cabstd = sqrt(astd * astd + bstd * bstd);
    double Cabsample = sqrt(asample * asample + bsample * bsample);

    double Cabarithmean = (Cabstd + Cabsample) / 2.0;

    double G = 0.5 * (1.0 - sqrt(pow(Cabarithmean, 7.0) / (pow(Cabarithmean, 7.0) + pow(25.0, 7.0))));

    double apstd = (1.0 + G) * astd; // aprime in paper
    double apsample = (1.0 + G) * asample; // aprime in paper
    double Cpsample = sqrt(apsample * apsample + bsample * bsample);

    double Cpstd = sqrt(apstd * apstd + bstd * bstd);
    // Compute product of chromas
    double Cpprod = Cpsample * Cpstd;

    // Ensure hue is between 0 and 2pi
    double hpstd = atan2(bstd, apstd);
    if (hpstd < 0) hpstd += 2.0 * PI;  // rollover ones that come -ve

    double hpsample = atan2(bsample, apsample);
    if (hpsample < 0) hpsample += 2.0 * PI;
    if ((fabs(apsample) + fabs(bsample)) == 0.0) hpsample = 0.0;

    double dL = Lsample - Lstd;
    double dC = Cpsample - Cpstd;

    // Computation of hue difference
    double dhp = (hpsample - hpstd);
    if (dhp > PI)  dhp -= 2.0 * PI;
    if (dhp < -PI) dhp += 2.0 * PI;

    // set chroma difference to zero if the product of chromas is zero
    if (Cpprod == 0.0) dhp = 0.0;

    // Note that the defining equations actually need
    // signed Hue and chroma differences which is different
    // from prior color difference formulae

    double dH = 2.0 * sqrt(Cpprod) * sin(dhp / 2.0);
    //%dH2 = 4*Cpprod.*(sin(dhp/2)).^2;

    // weighting functions
    double Lp = (Lsample + Lstd) / 2.0;
    double Cp = (Cpstd + Cpsample) / 2.0;

    // Average Hue Computation
    // This is equivalent to that in the paper but simpler programmatically.
    // Note average hue is computed in radians and converted to degrees only
    // where needed
    double hp = (hpstd + hpsample) / 2.0;
    // Identify positions for which abs hue diff exceeds 180 degrees
    if (fabs(hpstd - hpsample)  > PI ) hp -= PI;
    // rollover ones that come -ve
    if (hp < 0) hp += 2.0 * PI;

    // Check if one of the chroma values is zero, in which case set
    // mean hue to the sum which is equivalent to other value
    if (Cpprod == 0.0) hp = hpsample + hpstd;

    double Lpm502 = (Lp - 50.0) * (Lp - 50.0);
    double Sl = 1.0 + 0.015 * Lpm502 / sqrt(20.0 + Lpm502);
    double Sc = 1.0 + 0.045 * Cp;
    double T = 1.0 - 0.17 * cos(hp - PI / 6.0) + 0.24 * cos(2.0 * hp)
        + 0.32 * cos(3.0 * hp + PI / 30.0) - 0.20 * cos(4.0 * hp - 63.0 * PI / 180.0);
    double Sh = 1.0 + 0.015 * Cp * T;
    double delthetarad = (30.0 * PI / 180.0) * exp(-pow(((180.0 / PI * hp - 275.0)/ 25.0), 2.0));
    double Rc = 2.0 * sqrt(pow(Cp, 7.0) / (pow(Cp, 7.0) + pow(25.0, 7.0)));
    double RT= -sin(2.0 * delthetarad) * Rc;

    double klSl = kl * Sl;
    double kcSc = kc * Sc;
    double khSh = kh * Sh;

    // The CIE 00 color difference
    double de00 = sqrt(pow((dL / klSl), 2.0) + pow((dC / kcSc), 2.0)
        + pow((dH / khSh), 2.0) + RT * (dC / kcSc) * (dH / khSh));

    return de00;
} // end deltaE2000

/*
int main(int argc, const char * argv[])
{
  double L1 = 65.9520;
  double a1 = -16.9007;
  double b1 = 50.7476;
  double L2 = 69.5527;
  double a2 = -15.4632;
  double b2 = 32.1215;
  // Converts the first color from RGB to LAB
  double de00 = deltaE2000(L1, a1, b1, L2, a2, b2, 1, 1, 1);
  printf("de00 = %f\n", de00);
}
*/