"""Cam lobe profile: what the spec asks for vs what the engine currently does.

Spec (Tuning-the-Engine, 'Hermite H16 - Sedenion CAM Timing Wheel Calibration'):
    e_k timing resonance = hermite_zeros[k]**2
    "Uniform E-values = untrained engine. Hermite-spaced E-values = calibrated CAM."

Current engine (monad.py):
    zero_idx = pi(next_prime(horner95(word)))     # UNIFORM after the Phase 23 fix
    gamma    = gamma_at(zero_idx)
    E        = |sin(pi * gamma / (gamma + 1))|
"""
import math
import numpy as np

print("=== 1. the specified cam profile: Hermite H16 ===")
hz = np.polynomial.hermite.hermroots([0]*16 + [1])
res = hz**2
print(f"{'e_k':>4}{'hermite zero':>15}{'resonance z^2':>16}{'gap to next':>13}")
for k in range(16):
    gap = (res[k+1]-res[k]) if k < 15 else float('nan')
    print(f"{k:>4}{hz[k]:>15.6f}{res[k]:>16.6f}{gap:>13.6f}"
          if not math.isnan(gap) else
          f"{k:>4}{hz[k]:>15.6f}{res[k]:>16.6f}{'—':>13}")
sp = np.diff(np.sort(res))
print(f"\nresonance spread : min {res.min():.4f}  max {res.max():.4f}")
print(f"gap variation    : min {sp.min():.4f}  max {sp.max():.4f}  ratio {sp.max()/sp.min():.2f}x")
print("  -> strongly NON-uniform. Distinct lobes. This is a cam.")

print("\n=== 2. what E actually does now ===")
# gamma grows roughly like 2*pi*n/W(n/e); E = |sin(pi*g/(g+1))| ~ pi/(g+1) for large g
def E_of_gamma(g):
    return abs(math.sin(math.pi * g / (g + 1.0)))

samples = [(1,14.134725),(10,49.773832),(50,143.111846),
           (500,811.0),(2000,2547.0),(6542,7000.0)]
print(f"{'zero idx':>10}{'gamma':>12}{'E':>12}")
for zi,g in samples:
    print(f"{zi:>10}{g:>12.3f}{E_of_gamma(g):>12.6f}")

print("\n  E is a MONOTONE DECREASING function of gamma (E ~ pi/(gamma+1)).")
print("  zero_idx is UNIFORM after the Phase 23 Fibonacci fix.")
print("  => lobe height is a monotone map of a uniform hash: rank-ordered by")
print("     spelling, with no resonance structure at all.")

print("\n=== 3. the conflict, stated ===")
print("  ADDRESS wants zero_idx uniform   -> no pile-up   (Phase 23 optimised this)")
print("  CAM     wants E Hermite-spaced   -> resonance    (spec, never implemented)")
print("  Both are read off the SAME scalar. They pull in opposite directions.")
print("  Phase 23 made the address uniform and flattened the cam in the same commit.")

print("\n=== 4. the Wankel timing wheel ===")
ports, dims = 6, 16
print(f"  ports per rotor revolution     : {ports}   (PORT_STEP = pi/3)")
print(f"  sedenion dims per revolution   : {dims}   (THE ANGLE = pi/8, Phase 24)")
print(f"  gcd({ports},{dims}) = {math.gcd(ports,dims)}   lcm({ports},{dims}) = {math.lcm(ports,dims)}")
print(f"  combined timing wheel          : {math.lcm(ports,dims)} marks")
print(f"  and {math.lcm(ports,dims)} = 3 faces x 16 dims = {3*16}")
print("  -> the rotor's internal axis carries 48 distinct timing positions,")
print("     three times the resolution of a 16-lobe cam.")
