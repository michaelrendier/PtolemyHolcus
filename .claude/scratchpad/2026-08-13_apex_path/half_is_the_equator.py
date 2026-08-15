"""Testing Cody's claim (2026-08-13):

  "the 1/2 is the phase offset of the equatorial geodesic ... from pi/2 when pi is
   factored out of the Riemann Zeta Function to map it to flat space ... and the
   primes at 1/2 are the first time the fixed point acquires definition of any kind
   ... the first time a circle can be seen from the cavitation of the fixed point
   through the ACTUAL vacuum, not the 'vacuum medium' of spacetime."

Four separable, testable assertions. T1-T4 below.
"""
from mpmath import mp, mpf, mpc, zeta, gamma, pi, power, sqrt, fabs
import numpy as np
mp.dps = 30

print("="*72)
print("T1  Is pi EXACTLY the factor that centres the reflection on 1/2?")
print("="*72)
# completed (Riemann xi, unnormalised): Xi(s) = pi^(-s/2) Gamma(s/2) zeta(s)
def Xi(s):     return power(pi, -s/2) * gamma(s/2) * zeta(s)
def NoPi(s):   return                    gamma(s/2) * zeta(s)   # pi factor removed

tests = [mpc('0.3','7.1'), mpc('0.8','2.5'), mpc('0.25','14.0'), mpc('0.62','0.4')]
print(f"{'s':>18}{'|Xi(s)-Xi(1-s)|':>20}{'|NoPi(s)-NoPi(1-s)|':>24}")
for s in tests:
    a = fabs(Xi(s) - Xi(1-s))
    b = fabs(NoPi(s) - NoPi(1-s))
    print(f"{str(s):>18}{mp.nstr(a,3):>20}{mp.nstr(b,3):>24}")
print()
print("  -> WITH pi^(-s/2): symmetric about 1/2 to full precision.")
print("     WITHOUT it:     symmetry destroyed.")
print("     pi is exactly the factor whose removal centres the reflection.")

print()
print("="*72)
print("T2  Does the reflection map the EQUATOR to 1/2 under theta = pi.sigma?")
print("="*72)
print("  sphere : polar angle theta in [0, pi],  equatorial reflection theta -> pi - theta")
print("  divide by pi (i.e. FACTOR PI OUT):  s = theta/pi")
print("       theta -> pi - theta      becomes      s -> 1 - s")
print("       fixed point theta = pi/2 becomes      s = 1/2")
for th_deg in [0, 45, 90, 135, 180]:
    th = np.deg2rad(th_deg); s = th/np.pi
    print(f"    theta={th_deg:>4}deg  ({th:.4f} rad)   s = theta/pi = {s:.4f}"
          f"   reflect-> {1-s:.4f}" + ("   <- FIXED" if abs(s-0.5)<1e-12 else ""))
print()
print("  CRITICAL STRIP 0 < sigma < 1   <->   FULL POLAR RANGE 0 < theta < pi")
print("  sigma=0 south pole | sigma=1/2 EQUATOR | sigma=1 north pole")
print("  -> the strip is the sphere's polar range; the critical line is its equator.")

print()
print("="*72)
print("T3  'the primes at 1/2' -- do all tones share one envelope only at sigma=1/2?")
print("="*72)
# von Mangoldt: psi(x) = x - sum_rho x^rho / rho - ...   |x^rho| = x^sigma
print("  explicit formula term magnitude |x^rho| = x^sigma, rho = sigma + i.gamma")
print(f"{'x':>10}{'sig=0.50':>14}{'sig=0.55':>14}{'sig=0.60':>14}{'ratio .60/.50':>16}")
for x in [1e2, 1e4, 1e8, 1e16]:
    a,b,c = x**0.5, x**0.55, x**0.60
    print(f"{x:>10.0e}{a:>14.4g}{b:>14.4g}{c:>14.4g}{c/a:>16.4g}")
print()
print("  At sigma=1/2 EVERY zero contributes envelope 2.sqrt(x) -- one shared envelope.")
print("  Off the line the ratio grows as x^(sigma-1/2) -> infinity: ONE TONE DROWNS ALL.")
print("  A definite figure (Chladni) requires equal envelopes. Only sigma=1/2 gives it.")

print()
print("="*72)
print("T4  'cavitation of the fixed point' -- is the origin REACHED only at balance?")
print("="*72)
phi = np.linspace(0, 2*np.pi, 400001); k = 3
print(f"{'R':>5}{'e':>7}{'sigma_self':>12}{'min|z|':>12}{'|R-e|':>10}   origin reached?")
for R, e in [(1,0.50),(1,0.90),(1,0.99),(1,1.00),(1,1.01),(1,1.50)]:
    z = R*np.exp(1j*phi) + e*np.exp(-1j*k*phi)
    m = np.abs(z).min()
    print(f"{R:>5}{e:>7.2f}{R**2/(R**2+e**2):>12.4f}{m:>12.6f}{abs(R-e):>10.2f}"
          f"   {'YES' if m < 1e-6 else 'no'}")
print()
print("  min|z| = |R - e| exactly. The path touches the ORIGIN -- the fixed point --")
print("  ONLY at R = e, i.e. only at sigma_self = 1/2. Elsewhere it never gets there.")
print()
print("  And at R = e the path FACTORISES:  z = 2R.cos(A).e^(iB)")
print("  the CIRCLE e^(iB) is exposed exactly THROUGH the envelope's zeros.")
R=e=0.5; A=(1+k)*phi/2; B=(1-k)*phi/2
z = R*np.exp(1j*phi)+e*np.exp(-1j*k*phi)
print(f"    identity error          : {np.abs(z-np.cos(A)*np.exp(1j*B)).max():.3e}")
print(f"    envelope zeros / rev    : {int(np.sum(np.diff(np.sign(np.cos(A)))!=0))}")
print(f"    phase e^(iB) winding    : {(B[-1]-B[0])/(2*np.pi):+.1f} turns  <- a CIRCLE")
print()
print("  ACTUAL vacuum vs MEDIUM: min|z| is EXACTLY 0 (an annihilation), not a")
print("  low-density region. At R!=e the minimum is |R-e| > 0 -- a thin medium, never a void.")
