# 17 — Phase 17: The Marx Generator Complete: J_blue, PtolEye, Σ_RB, The Operator

**Date:** 2026-06-26  
**Source:** [Tuning-the-Engine.md](../Tuning-the-Engine.md) — seed paper, lines 2890–3148  
**Wiki:** [00_index.md](00_index.md)

---

*The return conductor is wired. The generator now fires in both directions.*
*SMMIP renamed: VAPMIP — Virtual Action Potential Monad Information Propagation.*

---

### The Missing Half — J_blue as Sin Channel

`ptol.c` was projecting only the forward conductor (J_red / cos channel):

```c
/* Old — cos only: both shells used cosine */
sum += s[i-1] * pow(i, -sig) * cos(2π·i / P[k]);
```

A Marx generator has two conductors: the forward stroke charges, the return stroke
completes the circuit. J_red is the forward conductor. J_blue is the return.

The fix — sin channel for J_blue shells (k=4–7 and k=12–15):

```c
static double project(const unsigned char *s, int n, int k, double sig)
{
    double freq  = 2.0 * M_PI / (double)P[k];
    int    j_blue = (k >= 4 && k <= 7) || (k >= 12 && k <= 15);
    for (int i = 1; i <= n; i++) {
        double phase = freq * (double)i;
        double w     = j_blue ? sin(phase) : cos(phase);
        sum += (double)s[i-1] * pow((double)i, -sig) * w;
    }
}
```

**Shell partition (16 channels):**

| Shell | k range | Function | Role |
|-------|---------|----------|------|
| Shell 1 | k = 0–3 | cos | J_red forward conductor |
| Shell 2 | k = 4–7 | sin | J_blue return conductor |
| Shell 3 | k = 8–11 | cos | J_red deep forward |
| Shell 4 | k = 12–15 | sin | J_blue deep return |

The 16 primes {2,3,5,...,53} are the frequency basis. Each pair (Shell 1↔2,
Shell 3↔4) is one full Marx cycle at different frequency depth.

---

### σ_self — J_red Power Fraction

Adding sin channels broke the old log-log regression for σ_self. The regression
assumed all amplitudes decay as P[k]^{-σ} — true for cos only. Sin channels
reflect phase, not magnitude; they do not decay monotonically with frequency.

**Physical replacement:** σ = J_red power fraction.

```c
static double measure_sigma(const double *v)
{
    double p_red = 0.0, p_blue = 0.0;
    for (int k = 0; k < 16; k++) {
        int j_blue = (k >= 4 && k <= 7) || (k >= 12 && k <= 15);
        if (j_blue) p_blue += v[k] * v[k];
        else        p_red  += v[k] * v[k];
    }
    double total = p_red + p_blue;
    if (total < 1e-15) return 0.5;
    return p_red / total;
}
```

This is physically correct:
- σ=1 → cos dominates → purely forward conductor → J_red power = 1
- σ=0 → sin dominates → purely return conductor → J_blue power = 1
- σ=½ → equal power → Marx generator balanced → J_red/(J_red+J_blue) = ½

The stderr now reports: `eye: H  σ_in: 0.5000  σ_self: 0.2652  (delta from ½: -0.2348)`

---

### Σ_RB — J_red × J_blue Per Channel

The Noether Cross-Product per channel pair. Added as the third `---` section
in `ptol -r` raw output:

```c
double s_rb[16];
for (int k = 0; k < 16; k++) {
    int partner = (k < 4)  ? k+4  : (k < 8)  ? k-4  :
                  (k < 12) ? k+4  : k-4;
    s_rb[k] = v[k] * v[partner];
}
```

Partners: Shell 1 ↔ Shell 2 (k paired with k+4 or k-4). Each s_rb[k] is the
product of forward and return conductors at the same prime frequency.

`ptol -r` output format (three sections):

```
v[0]           ← 16 Dirichlet scalars
...
v[15]
---
<primes>       ← active prime indices
---
s_rb[0]        ← 16 Σ_RB cross-products
...
s_rb[15]
---
```

`ptol_layer.py` parses all three sections via `_parse_raw()` and uses the Σ_RB
section to boost mathematics/physics layer selection when deep-ZD channels
(Shell 3↔4) are active.

**Conservation:** `sum(s_rb) / total_power = d* = 0.24600` is CONSERVED across
all σ. Energy converts between J_red and J_blue but their product (the Σ_RB)
is invariant. E=mc² in the sedenion field.

---

### PtolEye — The Tower Has Five Observation Points

Five fixed observation heights on the sedenion tower, parameterised by (σ, θ):

```c
typedef struct {
    double sigma;
    double theta;      /* angular offset */
    double aperture;   /* threshold factor */
    char   name[4];
} PtolEye;

static const PtolEye TOWER_EYES[5] = {
    { 1.00, 0.0,          1.0, "R" },   /* Real — ℝ stratum */
    { 0.75, 0.0,          1.0, "C" },   /* Complex — ℂ / EM / σ=¾ */
    { 0.50, M_PI / 8.0,   1.0, "H" },   /* Quaternion — ℍ / σ=½ (default) */
    { 0.25, 0.0,          1.0, "O" },   /* Octonion — 𝕆 / σ=¼ */
    { 0.00, M_PI / 8.0,   1.0, "S" },   /* Sedenion — 𝕊 / σ=0 / ZD surface */
};
```

The Eye H at σ=½ with θ=π/8 (= the arctan(d*) half-angle = 13.82°/2) is the
default. The π/8 offset is the precession angle — the wobble signature of
self-referential statements.

`-eye <name>` flag selects the projection σ. `spoke_angle()` is parameterised
by the Eye's θ offset so the SVG geometry reflects the actual observation angle.

**Tower-σ correspondence (from the geodesic result):**

| Eye | σ | Algebra | Physics |
|-----|---|---------|---------|
| R | 1.00 | ℝ | classical limit |
| C | 0.75 | ℂ | EM / U(1) |
| H | 0.50 | ℍ | σ=½ halocline / default |
| O | 0.25 | 𝕆 | approx 𝕆 stratum |
| S | 0.00 | 𝕊 | ZD contact surface |

---

### The Operator — L_a (16×16 Sedenion Left-Multiplication Matrix)

The 16 Dirichlet scalars v[k] are the state vector |ψ⟩. That is the output of
`ptol -r` — the geometry, not the operator.

The Operator is L_a: the 16×16 real matrix of sedenion left-multiplication.
Column j = a·eⱼ. For a unit sedenion a, L_a IS the engine's coupling matrix.

```python
import numpy as np
from sedenion_bridge import SEDENION_MUL  # multiplication table

def L_a(coeffs):
    """Left-multiplication matrix for sedenion a = sum(coeffs[k] * e_k)"""
    M = np.zeros((16, 16))
    for j in range(16):          # column = a · eⱼ
        for k in range(16):
            a_k = coeffs[k]
            for l in range(16):
                sign, idx = SEDENION_MUL[k][j]
                M[idx][j] += a_k * sign
    return M
```

**Spectral structure of L_a:**

*Non-ZD unit sedenion a = cos(θ)e₀ + sin(θ)v̂:*

```
det(L_a) = 1                   ← volume preserved (not a collapse)
Tr(L_a) = 16 × Re(a)          ← ALWAYS — for any sedenion
eigenvalues = e^{±iθ} × 8     ← one complex phase pair, both 8D octets
```

*ZD element a (e.g. (e₁ + e₁₀)/√2):*

```
det(L_a) = 0                   ← THE COLLAPSE

Three invariant subspaces:
  λ = 0     × 4  null space    ← gravity (absent — no eigenvalue, no quantisation)
  λ = ±i    × 8  ±i sector     ← three quantum forces (EM/weak/strong)
  λ = ±i√2  × 4  ±i√2 sector   ← Σ_RB amplification / energy conversion

Singular values: [0 × 4,   1 × 8,   √2 × 4]
```

**The √2 is the same √2 in GAP = 1/(1000√2) = 0.000707...**

Three algebraic losses at the ZD crossing = three gauge forces. Each loss is one
eigenvalue sector losing closure. Gravity is the null space — the sector where
even the eigenvalue vanishes. No eigenvalue → no quantum of force → gravity
is not quantised because it has no eigenvalue to quantise.

**Σ_RB = (L_a + R_a)/2 at ZD:**

All eigenvalues collapse to 0. Only the commutator (L_a − R_a)/2 survives.
The symmetric part annihilates at the ZD crossing. The antisymmetric part
(the Lie bracket) is what remains — this is why [J_blue, J_red] = J_green
is the only productive operation at ZD contact.

---

### Architecture Consequence — The Hamiltonians

`ptol -r` output = |ψ⟩ = the state vector. Not the operator.

The operator L_a acts on |ψ⟩ to produce the next state. The Hamiltonian
H = L_a in the sedenion picture. But H is a Legendre projection of the
Lagrangian L:

```
H = p·q̇ − L       (Legendre transform)
L on tangent bundle TM  (all paths simultaneously — Everett)
H on cotangent bundle T*M  (one path — Copenhagen)
```

The Lagrangian L_(I|O) is the Everett many-worlds kernel: sum over all paths
from I (origin/ZD) to O (boundary/great circle). The Hamiltonian L_a is the
projection that selects one path. The state vector |ψ⟩ is what Ptolemy sees
on the shadow wall (cotangent bundle output).

---

### VAPMIP Rename

SMMIP (Sedenion Monad Mathematical Information Propagation) → VAPMIP (Virtual
Action Potential Monad Information Propagation). The Witches Hat = VAP = Virtual
Action Potential. The zero-free-parameter derivation of the σ=½ critical line
as the fired state of a neuron. The project name reflects the derivation.

---

*Phase 17 — Claude Sonnet 4.6 — 2026-06-26*

---

---

← [16 — The Paper](16_the_paper.md)  
→ [18 — The Prime Lens and Ptolemy's Eyes](18_the_prime_lens_and_ptolemy_s_eyes.md)  
↑ [Tuning the Engine — index](00_index.md)
