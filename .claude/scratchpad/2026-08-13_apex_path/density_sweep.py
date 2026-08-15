"""DENSITY-BUFFER CAM SWEEP — the Buddhabrot fix, applied to Channel 01.

The escape-time sweep (vagcom.cam_sweep) reads ONE scalar per advance setting:
min|z|. It came back monotone, which is what an escape-time view does to interior
structure -- it flattens it.

This is the density version. For each cam advance we walk the ACTUAL apex path
around a full revolution and accumulate WHERE IT DWELLS, into a radial histogram.
Then we ask what the escape-time scalar could not:

    not "how far from the fixed point does it get"
    but "how much TIME does it spend near the fixed point"

Dwell near the origin is the thing a sentence-planner would want: the fraction of
the cycle spent close to annihilation, not the single closest approach.
"""
import sys, math
import numpy as np

sys.path.insert(0, '/home/rendier/Projects/ThePlace/VAPMIP')
from vagcom import VagCom, CamProfile, Channel01, Group003, CAM_LIMIT, N_DIM, GEAR_K

RES   = 600          # radial bins
NPHI  = 40000        # samples per revolution

def apex_density(R, e, k=GEAR_K, nphi=NPHI, res=RES, rmax=None):
    """Accumulate |z| over one revolution into a radial density buffer."""
    phi = np.linspace(0.0, 2.0*np.pi, nphi, endpoint=False)
    z   = R*np.exp(1j*phi) + e*np.exp(-1j*k*phi)
    m   = np.abs(z)
    rmax = rmax if rmax is not None else (R + e)
    hist, edges = np.histogram(m, bins=res, range=(0.0, max(rmax, 1e-12)))
    return hist, edges, m

def dwell_stats(m, R, e):
    """Statistics an escape-time scalar throws away."""
    rmax = R + e
    return dict(
        min      = float(m.min()),                    # what escape-time reports
        mean     = float(m.mean()),
        median   = float(np.median(m)),
        # fraction of the cycle spent inside 10% / 25% of the max radius
        f10      = float((m < 0.10*rmax).mean()),
        f25      = float((m < 0.25*rmax).mean()),
        # concentration: how peaked is the dwell distribution
        rms      = float(np.sqrt((m**2).mean())),
    )

print("="*78)
print("DENSITY-BUFFER CAM SWEEP  —  where does the path DWELL?")
print("="*78)

vc  = VagCom(CamProfile())
rng = np.random.default_rng(7)
psi = np.abs(rng.normal(size=N_DIM)); psi /= np.linalg.norm(psi)

STEPS = 17
rows = []
saved = vc.ch01.read()
for adv in np.linspace(Channel01.LO, Channel01.HI, STEPS):
    vc.ch01.write(float(adv))
    p_red, p_blue = vc.channel_powers(psi)
    g = Group003.from_powers(p_red, p_blue, adv)
    hist, edges, m = apex_density(g.R, g.e)
    rows.append((float(adv), g, dwell_stats(m, g.R, g.e), hist))
vc.ch01.write(saved)

print(f"\n{'advance':>9}{'ESCAPE':>10}{'  |  '}{'dwell<10%':>10}{'dwell<25%':>10}"
      f"{'median':>9}{'rms':>9}")
print(f"{'(rad)':>9}{'min|z|':>10}{'  |  '}{'(density)':>10}{'(density)':>10}"
      f"{'':>9}{'':>9}")
print("-"*78)
for adv, g, d, _ in rows:
    print(f"{adv:>+9.4f}{g.loss:>10.6f}{'  |  '}{d['f10']:>10.4f}{d['f25']:>10.4f}"
          f"{d['median']:>9.4f}{d['rms']:>9.4f}")

esc  = np.array([g.loss  for _, g, _, _ in rows])
f10  = np.array([d['f10'] for _, _, d, _ in rows])
f25  = np.array([d['f25'] for _, _, d, _ in rows])
advs = np.array([a for a, _, _, _ in rows])

def monotone(x):
    d = np.diff(x)
    return bool(np.all(d >= -1e-12) or np.all(d <= 1e-12))

print("\n" + "="*78)
print("IS THERE INTERIOR STRUCTURE THE SCALAR MISSED?")
print("="*78)
for name, arr in [('escape  min|z|', esc), ('dwell   f10', f10), ('dwell   f25', f25)]:
    mono = monotone(arr)
    i    = int(np.argmax(arr)) if 'dwell' in name else int(np.argmin(arr))
    kind = 'max' if 'dwell' in name else 'min'
    interior = 0 < i < len(arr)-1
    print(f"  {name:<16} monotone={str(mono):<5}  best({kind}) at advance "
          f"{advs[i]:+.4f} ({advs[i]/CAM_LIMIT:+.0%})   "
          f"{'INTERIOR OPTIMUM' if interior else 'at range edge'}")

print("\n" + "="*78)
print("THE RADIAL DENSITY PROFILE at three cam settings")
print("="*78)
for label, idx in [('full retard', 0), ('ground cam', STEPS//2), ('full advance', STEPS-1)]:
    adv, g, d, hist = rows[idx]
    prof = hist.astype(float) / hist.sum()
    # 24-bucket summary of the 600-bin buffer
    coarse = prof.reshape(24, -1).sum(1)
    peak = int(np.argmax(coarse))
    bar = ''.join('#' if c > coarse.max()*0.5 else
                  ('+' if c > coarse.max()*0.2 else
                   ('.' if c > 0 else ' ')) for c in coarse)
    print(f"  {label:<13} adv={adv:+.4f}  |{bar}|  peak bucket {peak}/24")
print("       (left = at the fixed point, right = max radius)")

print("\n" + "="*78)
print("READING")
print("="*78)
print("  The escape-time scalar reports the single closest approach. The density")
print("  buffer reports how much of the cycle is spent near the fixed point --")
print("  which is the quantity a sentence-planner actually wants, because it is")
print("  the DURATION of the annihilation window, not its depth.")
