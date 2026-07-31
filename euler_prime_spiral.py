#!/usr/bin/python3
"""
Euler Spiral Prime / Zeta-Zero Construction
=============================================
Native Space interpretation:
  The Euler (Cornu) spiral's NATIVE coordinate is arc length s -- not
  (x,y), not (r,theta). Curvature kappa(s) = pi*s is linear in s BY
  CONSTRUCTION. The embedding (x,y) = (C(s), S(s)) (Fresnel integrals)
  is the extrinsic/observer view. s is the intrinsic/source view.
  This mirrors the existing Observer/Source split: Observer reads
  (x,y) position: Source reads s directly.

Construction:
  s_n = k * n            for n = 1..N   (integers get uniform arc-length spacing)
  (x_n, y_n) = (C(s_n), S(s_n))         via scipy Fresnel integrals

  Primes highlighted against composites on the same spiral.
  Tangent angle at s_n: phi(s_n) = (pi/2) s_n^2  -- QUADRATIC PHASE.
  This is the same quadratic-phase structure that underlies Gauss sums
  and theta-function modularity (theta(t) = sum e^{-pi n^2 t}), which
  is the transform that produces the zeta functional equation. That
  is the genuine mathematical link between "Euler spiral" and
  "Riemann zeta" -- not decorative, structural: both are built on
  sum/integral of e^{i pi n^2 x} type quadratic phase.

  Second panel: first N_zeros nontrivial zeta zeros (via mpmath,
  computed directly -- not from memory) placed on an Euler spiral by
  INDEX using the same construction, for direct visual comparison.

Confidence: CONJECTURE / exploratory visualization only. No claim of
new theorem. Patterns noted are visual/statistical, not proofs.
"""
import numpy as np
from scipy.special import fresnel
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sympy import primerange
import mpmath as mp

# ---------- 1. Integers + primes on Euler spiral ----------
N = 4000
k = 0.055                      # arc-length step per integer
n_vals = np.arange(1, N + 1)
s_vals = k * n_vals

S_fresnel, C_fresnel = fresnel(s_vals)   # scipy returns (S, C) for
                                          # C(s)=int cos(pi t^2/2)dt, S(s)=int sin(pi t^2/2)dt
x_all, y_all = C_fresnel, S_fresnel

primes = list(primerange(2, N + 1))
prime_set = set(primes)
is_prime = np.array([p in prime_set for p in n_vals])

# ---------- 2. First N_zeros nontrivial zeta zeros, computed directly ----------
N_zeros = 400
mp.mp.dps = 25
zeros = [float(mp.im(mp.zetazero(i))) for i in range(1, N_zeros + 1)]
zeros = np.array(zeros)

n_z = np.arange(1, N_zeros + 1)
s_z = k * n_z * (N / N_zeros)   # rescale index-spacing so the zero-spiral
                                 # covers comparable arc length to the prime spiral
Sz, Cz = fresnel(s_z)
x_z, y_z = Cz, Sz

# radius (from spiral center) modulated by the actual zero height gamma_n,
# normalized -- lets the *value* of each zero (not just its index) leave
# a signature on the spiral via radial displacement
gamma_norm = zeros / zeros.max()
x_z_mod = x_z * (0.6 + 0.4 * gamma_norm)
y_z_mod = y_z * (0.6 + 0.4 * gamma_norm)

# ---------- 3. Plot ----------
fig, axes = plt.subplots(1, 2, figsize=(15, 7.2), facecolor="#050505")

ax = axes[0]
ax.set_facecolor("#050505")
ax.plot(x_all, y_all, color="#2a2a2a", lw=0.6, zorder=1)
ax.scatter(x_all[~is_prime], y_all[~is_prime], s=2, color="#333333", zorder=2)
ax.scatter(x_all[is_prime], y_all[is_prime], s=6, color="#00f2ff", zorder=3, label=f"primes (n<{N})")
ax.set_title("Integers 1..%d on Euler Spiral\n(native coord s = k*n, embedding (C(s),S(s)))" % N,
             color="white", fontsize=10)
ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="upper right", facecolor="#111111", labelcolor="white", fontsize=8)

ax2 = axes[1]
ax2.set_facecolor("#050505")
ax2.plot(x_z, y_z, color="#2a2a2a", lw=0.5, zorder=1)
sc = ax2.scatter(x_z_mod, y_z_mod, s=10, c=gamma_norm, cmap="plasma", zorder=3)
ax2.set_title(f"First {N_zeros} Nontrivial Zeta Zeros on Euler Spiral\n(index n -> s_n, radius modulated by gamma_n)",
              color="white", fontsize=10)
ax2.set_aspect("equal")
ax2.axis("off")
cb = plt.colorbar(sc, ax=ax2, fraction=0.04, pad=0.02)
cb.set_label("gamma_n / gamma_max", color="white")
cb.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="white")

plt.tight_layout()
plt.savefig("/home/claude/euler_prime_spiral.png", dpi=170, facecolor=fig.get_facecolor())
print("saved png")

# ---------- 4. Numerical notes (printed, not asserted as proof) ----------
print(f"N integers plotted: {N}, primes found: {len(primes)}")
print(f"N zeta zeros computed directly via mpmath: {N_zeros}")
print(f"gamma_1..gamma_5 (first 5 zero heights, computed not recalled): {zeros[:5]}")

# quadratic residue banding check (Ulam-spiral-style diagonal test):
# on an Euler spiral the "radial arm" a point falls on is set by s_n mod 2
# (since tangent angle is pi/2 * s_n^2, arms recur roughly every Delta n
# where k^2 * Delta n^2 pattern aliases). Check prime density by arm.
arm = np.floor(s_vals) % 2
for a in [0, 1]:
    mask = (arm == a)
    dens = is_prime[mask].mean()
    print(f"arm {a}: integer count {mask.sum()}, prime density {dens:.4f}")
