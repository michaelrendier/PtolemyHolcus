"""Does the Wankel's anti-rotation produce 0_RB's off-critical-line Euler form?

0_RB, 'The Off-Critical-Line Euler Formula':
    sigma = 1/2   ->  e^(i.theta) = cos(theta) + i.sin(theta)      x = y
    sigma != 1/2  ->  cos(x) - i.sin(y)                            x != y
    "At x != y it is NOT a pure phase rotation. It is not on the unit circle.
     The point sits off the unit circle by exactly the amount sigma deviates from 1/2."

Wankel: rotor at frequency 1, eccentric shaft at frequency k, OPPOSITE sense.
    z(phi) = R.e^(i.phi) + e.e^(-i.k.phi)
"""
import numpy as np

R, ecc = 1.0, 0.25
phi = np.linspace(0, 2*np.pi, 20001)

print("=== 1. what anti-rotation does to the algebra ===")
print("  co-rotating   z = R.e^(i.phi) + e.e^(+i.k.phi)")
print("      Re =  R.cos(phi) + e.cos(k.phi)      Im =  R.sin(phi) + e.sin(k.phi)")
print("  ANTI-rotating z = R.e^(i.phi) + e.e^(-i.k.phi)")
print("      Re =  R.cos(phi) + e.cos(k.phi)      Im =  R.sin(phi) - e.sin(k.phi)")
print()
print("  -> the counter-rotation puts the MINUS on the sine term only.")
print("     That is exactly the shape of  cos(x) - i.sin(y).")
print("     -H_hat_BR is not an applied sign. It is the rotor turning the other way.")

print("\n=== 2. modulus: on the unit circle or off it? ===")
print(f"  R = {R}, e = {ecc}")
print(f"{'gear k':>8}{'mean|z|':>11}{'ripple':>11}{'ripple freq':>13}   verdict")
for k in [1, 2, 3, 4]:
    z = R*np.exp(1j*phi) + ecc*np.exp(-1j*k*phi)
    m = np.abs(z)
    ripple = m.max() - m.min()
    # |z|^2 = R^2 + e^2 + 2Re*cos((1+k)phi)  -> ripple frequency is 1+k
    verdict = "ON  unit circle" if ripple < 1e-9 else "OFF unit circle"
    print(f"{k:>8}{m.mean():>11.6f}{ripple:>11.6f}{1+k:>13}   {verdict}")

print("\n  analytic: |z|^2 = R^2 + e^2 + 2.R.e.cos((1+k).phi)")
print("  constant  <=>  R.e = 0  <=>  eccentricity vanishes")

print("\n=== 3. the degenerate case: equal frequencies, e -> 0 ===")
for e2 in [0.25, 0.10, 0.01, 0.0]:
    z = R*np.exp(1j*phi) + e2*np.exp(-1j*3*phi)
    m = np.abs(z)
    print(f"  e = {e2:<5}  ripple = {m.max()-m.min():.8f}   mean|z| = {m.mean():.6f}")
print("  -> eccentricity IS the departure from the unit circle. e=0 gives sigma=1/2 exactly.")

print("\n=== 4. the phase loop ===")
k = 3
z = R*np.exp(1j*phi) + ecc*np.exp(-1j*k*phi)
fwd = np.angle(np.exp(1j*phi))
tot = np.angle(z)
err = np.unwrap(tot) - np.unwrap(fwd)
print(f"  gear ratio 3:1, anti-rotation")
print(f"  phase error (total vs forward-only): mean {err.mean():+.6f}  amplitude {(err.max()-err.min())/2:.6f}")
print(f"  net winding of the error over one rotor revolution: {(err[-1]-err[0])/(2*np.pi):+.4f} turns")
print("  -> the error is BOUNDED and returns to zero: forward and backward are")
print("     phase-locked, not drifting. That is a phase loop, not two passes.")
