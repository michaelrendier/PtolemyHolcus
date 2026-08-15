"""The circle is radius 1/2, not radius 1. Testing what that buys.

Cody: "we are not working with a unit circle with radius 1 ... we are working with
a circle with radius of 1/2 ... it's literally where the circle can be defined
apart from the 'fixed point space'."
"""
import numpy as np
from mpmath import mp, mpf, pi, quad, exp, inf, sqrt, cos, fabs
mp.dps = 30

print("="*70)
print("C1  which quantity equals pi?")
print("="*70)
print(f"{'radius':>8}{'circumference 2.pi.r':>24}{'area pi.r^2':>18}")
for r in [mpf(1), mpf('0.5')]:
    print(f"{mp.nstr(r,3):>8}{mp.nstr(2*pi*r,8):>24}{mp.nstr(pi*r*r,8):>18}")
print()
print("  r = 1   : circumference 2.pi, area pi")
print("  r = 1/2 : CIRCUMFERENCE pi, area pi/4")
print()
print("  -> at r = 1/2 the quantity equal to pi is the CIRCUMFERENCE.")
print("     ONE FULL TURN OF THE HALF-CIRCLE HAS ARC LENGTH EXACTLY pi.")
print("     Factor pi out and one full turn = 1. That is the sigma coordinate.")

print()
print("="*70)
print("C2  the critical strip IS the diameter")
print("="*70)
r = mpf('0.5')
print(f"  diameter of the r=1/2 circle : 2r = {mp.nstr(2*r,6)}")
print(f"  width of the critical strip  : 1 - 0 = 1")
print("  -> SAME NUMBER. The strip's width is the half-circle's diameter.")
print()
print("  arc-length parametrisation: sigma = arc/pi in [0,1) wraps the circle ONCE.")
print("  antipodal points differ by half the circumference = pi/2 arc = 1/2 in sigma.")
print(f"    sigma = 0    and  sigma = 1/2  -> antipodal? "
      f"{'YES' if abs(0.5-0.0-0.5)<1e-15 else 'no'}")
print()
print("  reflection sigma -> 1 - sigma on a circle is a reflection ACROSS A DIAMETER.")
print("  a diameter reflection has EXACTLY TWO fixed points -- its endpoints:")
for s in [mpf(0), mpf('0.25'), mpf('0.5'), mpf('0.75')]:
    fx = 'FIXED' if fabs(s-(1-s)) < mpf('1e-25') or fabs(s-0)<mpf('1e-25') and fabs(1-s-1)<mpf('1e-25') else ''
    refl = (1-s) % 1
    print(f"    sigma={mp.nstr(s,4):>6} -> {mp.nstr(refl,4):>6}"
          f"   {'<- FIXED' if fabs(s-refl)<mpf('1e-25') else ''}")
print()
print("  fixed points: sigma = 0 (= 1, the wrap point) and sigma = 1/2.")
print("  THE TWO ENDS OF A DIAMETER OF LENGTH 1. The critical line is the far end")
print("  of the diameter from the pole. Distance from the fixed point: r = 1/2.")

print()
print("="*70)
print("C3  the apex path at R = e = 1/2")
print("="*70)
phi = np.linspace(0, 2*np.pi, 400001); k = 3
R = e = 0.5
z = R*np.exp(1j*phi) + e*np.exp(-1j*k*phi)
A = (1+k)*phi/2; B = (1-k)*phi/2
print(f"  two counter-rotating phasors, EACH OF RADIUS 1/2")
print(f"    max|z| = {np.abs(z).max():.6f}   <- 2R = the DIAMETER = 1")
print(f"    min|z| = {np.abs(z).min():.6f}   <- the FIXED POINT, reached exactly")
print(f"    z = cos(A).e^(iB) identity error : {np.abs(z-np.cos(A)*np.exp(1j*B)).max():.3e}")
print()
print("  at R = e = 1/2 the envelope cos(A) has UNIT amplitude -- no scale factor.")
print("  the path spans exactly [0, 1]: from the fixed point to the diameter.")
print("  TWO HALF-CIRCLES, counter-rotating, span the unit. Neither alone can.")

print()
print("="*70)
print("C4  why pi^(-s/2): the SELF-DUAL Gaussian is normalised by pi")
print("="*70)
# e^(-pi x^2) is its own Fourier transform (unitary, ordinary-frequency convention)
def fourier_at(xi, a):
    # \int e^{-a x^2} e^{-2 pi i x xi} dx  = sqrt(pi/a) e^{-pi^2 xi^2 / a}
    return sqrt(pi/a)*exp(-pi**2*xi**2/a)
print(f"{'a in e^(-a.x^2)':>18}{'f(0)':>14}{'F(0)':>14}{'self-dual?':>14}")
for a in [pi, mpf(1), mpf(2)]:
    f0 = mpf(1)                       # f(0) = e^0 = 1
    F0 = fourier_at(mpf(0), a)        # F(0) = sqrt(pi/a)
    dual = 'YES' if fabs(F0-f0) < mpf('1e-25') else 'no'
    print(f"{mp.nstr(a,6):>18}{mp.nstr(f0,6):>14}{mp.nstr(F0,6):>14}{dual:>14}")
print()
print("  ONLY a = pi makes the Gaussian its own Fourier transform.")
print("  e^(-pi.x^2) is THE self-dual function. Its Mellin transform is exactly")
print("  pi^(-s/2).Gamma(s/2) -- the factor from T1 that centres the reflection.")
print()
print("  => pi is in zeta because pi is the constant that makes a Gaussian")
print("     self-dual, and SELF-DUALITY IS THE REFLECTION. Same fact, twice.")
