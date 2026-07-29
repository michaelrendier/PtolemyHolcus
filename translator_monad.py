#!/usr/bin/env python3
"""
translator_monad.py — The Translator via L_(I|O) on the (sigma,theta) tower. v1.

Python testbed. Per Cody's standing instruction: Python first, ptol.c only
after significant progress or when C-level testing is actually needed.

Lineage: sibling of UDEO_monad.py (the Translator testbed, v1-v5, all
negative/inconclusive on the semantic side and currently blocked pending
whether the exact UDEO mechanism exists anywhere). This is NOT a v6 of that
line — it does not reconstruct the cryptovulnerability math from a verbal
description, which is the documented root cause of v1-v5's failures. It
tests a different, independently-motivated question.

────────────────────────────────────────────────────────────────────────────
THE QUESTION
────────────────────────────────────────────────────────────────────────────
L_(I|O) was tested as "the path of the primes". Its GR content is the lens
equation used as a REVERSE-DEFINER:

    beta = theta - alpha(theta)

"from where you OBSERVE it, recover where it ACTUALLY IS." That is exactly
Ainulindale/wiki/52's definition of (I|O) as the reverse-definer — the
response defines what the input actually was — and it is the subtraction in
UDEO v5's "how an addition = a subtraction ... the J_2 Involution IS (I|O)".

Can that run inside 0_RB (the Null Operator, formerly H_hat_RB) as it
exists in PtolC/ptol.c?

Direct port fails, and the reasons are recorded rather than worked around:
  - Kaiser-Squires is irreducibly 2D; 0_RB is 16 scalars.
  - s_rb pairs cos-at-p_k with sin-at-p_{k+4} -- DIFFERENT primes every
    time (2 with 11, 3 with 13, ...). Not a spin-2 quadrature pair, so
    there is no shear field to invert.
  - ptol.c's "J_red x J_blue = d* = 0.24600 conserved at ALL sigma"
    (lines 13 and 111) is FALSE, already measured. There is no conserved
    scalar to act as the Poisson source.

What DOES exist in ptol.c is a genuine plane: TOWER_EYES, the (sigma,theta)
observation points. sigma = 1 - k/4 down R->C->H->O->S, theta at pi/8
offsets. That plane is already in the code; it is not invented here to make
the machinery apply. This file runs L_(I|O) on THAT plane.

────────────────────────────────────────────────────────────────────────────
PRIME DIRECTIVE COMPLIANCE
────────────────────────────────────────────────────────────────────────────
#1  No fitted parameters. No thresholds tuned to make a test pass. The
    primes, the tower sigmas, and the spoke angles are all lifted verbatim
    from ptol.c. The Poisson solve is exact, not iterative-to-tolerance.
#2  Every diagnostic below is allowed to fail and its failure is the
    output. test_d_star_invariant() is EXPECTED to report False -- that is
    ptol.c's own comment being wrong, and it stays wrong here rather than
    being quietly omitted.

KNOWN LIMITATION, STATED UP FRONT: the tower has only 5 sigma levels. Five
radial points is very thin for a Poisson solve. Phase 22's resolution
finding (resolution = dimension count) applies directly. If results come
back flat, under-resolution in sigma is the first hypothesis, and it is
CHEAPLY TESTABLE here via --sigma-levels (see tower_field).

Author: Cody Michael Allison + Claude (Anthropic), 2026-07-28
"""

import cmath
import math
import random
import sys
from typing import Dict, List, Sequence, Tuple

# ── Constants lifted verbatim from PtolC/ptol.c ──────────────────────────────

# ptol.c: static const int P[16]
PRIMES: List[int] = [2, 3, 5, 7, 11, 13, 17, 19,
                     23, 29, 31, 37, 41, 43, 47, 53]
N_SPOKES = 16

# ptol.c: TOWER_EYES — sigma = 1 - k/4, theta offset in radians
TOWER_EYES: List[Tuple[float, float, str]] = [
    (1.00, 0.0,           "R"),   # enumerable
    (0.75, 0.0,           "C"),   # relational (U(1), EM)
    (0.50, math.pi / 8.0, "H"),   # critical line, J_blue fires
    (0.25, 0.0,           "O"),   # octonion
    (0.00, math.pi / 8.0, "S"),   # sedenion, ZD boundary
]

MONAD_PHI = (1.0 + math.sqrt(5.0)) / 2.0


def is_j_blue(k: int) -> bool:
    """ptol.c: J_blue shells are k=4-7 and k=12-15 (the sin channels)."""
    return (4 <= k <= 7) or (12 <= k <= 15)


def spoke_angle(k: int, theta: float) -> float:
    """ptol.c: 2*pi*k/16 - pi/2 + theta."""
    return 2.0 * math.pi * k / N_SPOKES - math.pi / 2.0 + theta


# ── Dirichlet projection — ptol.c's project(), unchanged ─────────────────────

def project(text: str, k: int, sigma: float) -> float:
    """
    ptol.c project(): x_k = sum_i c_i * i^(-sigma) * w(2*pi*i/p_k)
    where w = sin for J_blue shells, cos for J_red shells.
    """
    freq = 2.0 * math.pi / PRIMES[k]
    blue = is_j_blue(k)
    total = 0.0
    for i, ch in enumerate(text.encode('utf-8', 'replace'), start=1):
        phase = freq * i
        total += ch * (i ** -sigma) * (math.sin(phase) if blue else math.cos(phase))
    return total


def measure_sigma(v: Sequence[float]) -> float:
    """ptol.c measure_sigma(): sigma_self = P_red / (P_red + P_blue)."""
    p_red = sum(v[k] * v[k] for k in range(N_SPOKES) if not is_j_blue(k))
    p_blue = sum(v[k] * v[k] for k in range(N_SPOKES) if is_j_blue(k))
    total = p_red + p_blue
    return p_red / total if total > 0.0 else 0.0


# ── 0_RB — the Null Operator, with its degeneracy made EXPLICIT ──────────────

def rb_partner(k: int) -> int:
    """ptol.c: Shell1<->Shell2 (k<->k+4), Shell3<->Shell4 (k<->k+4)."""
    return k + 4 if k < 4 else (k - 4 if k < 8 else (k + 4 if k < 12 else k - 4))


def sigma_rb_full(v: Sequence[float]) -> List[float]:
    """ptol.c's s_rb[16] exactly as written — all 16 entries."""
    return [v[k] * v[rb_partner(k)] for k in range(N_SPOKES)]


def sigma_rb(v: Sequence[float]) -> List[float]:
    """
    0_RB with the degeneracy claimed: only 8 of the 16 entries are
    independent.

    rb_partner is an involution and the product is commutative, so
    s_rb[k] == s_rb[partner(k)] IDENTICALLY for every k. ptol.c computes
    all 16 and says nothing about it; this is the free 2x reduction that
    .clauderc_context_2 records as unclaimed.

    This is the L_(I|O) degenerate-point discipline applied: name the
    structurally-undetermined component, resolve it by a STATED convention
    (keep the lower index of each pair), and say why -- rather than
    computing a redundant half or silently dropping it.
    """
    return [v[k] * v[rb_partner(k)] for k in range(N_SPOKES) if k < rb_partner(k)]


# ── The (sigma, theta) tower plane ───────────────────────────────────────────

def tower_field(text: str, sigma_levels: Sequence[float] = None,
                thetas: Sequence[float] = None) -> List[List[float]]:
    """
    Sample the input across the (sigma, theta) plane -> field[i][k].

    Default is ptol.c's own 5 TOWER_EYES x 16 spokes. sigma_levels is
    exposed ONLY so the Phase 22 under-resolution hypothesis can be tested
    directly (see resolution_probe). It is not a tuning knob: the default
    is the tower as ptol.c defines it, and results are reported at that
    default.
    """
    if sigma_levels is None:
        sigma_levels = [e[0] for e in TOWER_EYES]
        thetas = [e[1] for e in TOWER_EYES]
    if thetas is None:
        thetas = [0.0] * len(sigma_levels)
    return [[project(text, k, s) for k in range(N_SPOKES)]
            for s, _t in zip(sigma_levels, thetas)]


def convergence(field: List[List[float]]) -> List[List[float]]:
    """
    kappa — the Poisson source. Built from 0_RB at each tower level, since
    0_RB is what the question is about.

    Each row is normalised by its own L2 norm before the RB product, exactly
    as ptol.c does (v[k] = _x[k]/norm) before computing s_rb. That is a
    reproduction of existing behaviour, not a rescaling introduced here.
    """
    out = []
    for row in field:
        norm = math.sqrt(sum(x * x for x in row))
        v = [x / norm for x in row] if norm > 0.0 else [0.0] * N_SPOKES
        out.append(sigma_rb_full(v))
    return out


# ── Poisson solve on the plane — exact, no iteration, no tolerance ───────────

def _dft(row: Sequence[float]) -> List[complex]:
    n = len(row)
    return [sum(row[j] * cmath.exp(-2j * math.pi * m * j / n) for j in range(n))
            for m in range(n)]


def _idft(spec: Sequence[complex]) -> List[float]:
    n = len(spec)
    return [(sum(spec[m] * cmath.exp(2j * math.pi * m * j / n)
                 for m in range(n)) / n).real for j in range(n)]


def lensing_potential(kappa: List[List[float]]) -> List[List[float]]:
    """
    Solve  d2(psi)/dsigma2 + d2(psi)/dtheta2 = 2*kappa  on the tower plane.

    theta is periodic (16 spokes close the circle) so it is handled by exact
    DFT: d2/dtheta2 -> -(2*sin(pi*m/N)/dtheta)^2, the discrete second-
    difference symbol (NOT the continuum -m^2 -- the grid is 16 points and
    the discrete symbol is the correct one for it).

    sigma is NOT periodic. Neumann (zero-flux) ends: the tower does not
    continue past R (sigma=1) or S (sigma=0).

    *** THE DEGENERATE MODE — the L_(I|O) boundary-crossing template ***
    For m=0 with Neumann ends the operator is singular: psi is determined
    only up to an additive constant, exactly as the mean convergence is not
    observable from shear alone in Kaiser-Squires. Following
    kaiser_squires_kappa's own convention, that mode is assigned explicitly:

        psi[m=0] := 0

    Assigned by stated convention, not allowed to blow up, not silently
    dropped. This IS the transferable piece of L_(I|O).
    """
    n_sig = len(kappa)
    if n_sig < 3:
        raise ValueError("Poisson solve needs >= 3 sigma levels; got "
                         f"{n_sig}. Fewer cannot form a second difference.")
    dtheta = 2.0 * math.pi / N_SPOKES
    dsigma = 1.0 / (n_sig - 1)

    spec = [_dft(row) for row in kappa]
    psi_spec: List[List[complex]] = [[0j] * N_SPOKES for _ in range(n_sig)]

    for m in range(N_SPOKES):
        # discrete second-difference symbol for a 16-point periodic grid
        lam = -(2.0 * math.sin(math.pi * m / N_SPOKES) / dtheta) ** 2
        rhs = [2.0 * spec[i][m] for i in range(n_sig)]

        if m == 0:
            psi_spec_col = [0j] * n_sig      # the degenerate mode — see above
        else:
            # tridiagonal in sigma with Neumann ends, solved by elimination
            a = [0.0] * n_sig; b = [0.0] * n_sig; c = [0.0] * n_sig
            h2 = dsigma * dsigma
            for i in range(n_sig):
                if i == 0:
                    b[i] = -2.0 / h2 + lam; c[i] = 2.0 / h2
                elif i == n_sig - 1:
                    a[i] = 2.0 / h2; b[i] = -2.0 / h2 + lam
                else:
                    a[i] = 1.0 / h2; b[i] = -2.0 / h2 + lam; c[i] = 1.0 / h2
            cp = [0j] * n_sig; dp = [0j] * n_sig
            cp[0] = c[0] / b[0]; dp[0] = rhs[0] / b[0]
            for i in range(1, n_sig):
                den = b[i] - a[i] * cp[i - 1]
                cp[i] = c[i] / den if i < n_sig - 1 else 0j
                dp[i] = (rhs[i] - a[i] * dp[i - 1]) / den
            psi_spec_col = [0j] * n_sig
            psi_spec_col[-1] = dp[-1]
            for i in range(n_sig - 2, -1, -1):
                psi_spec_col[i] = dp[i] - cp[i] * psi_spec_col[i + 1]

        for i in range(n_sig):
            psi_spec[i][m] = psi_spec_col[i]

    return [_idft(psi_spec[i]) for i in range(n_sig)]


def deflection(psi: List[List[float]]) -> List[List[float]]:
    """alpha_theta = d(psi)/d(theta), central difference, periodic in theta."""
    dtheta = 2.0 * math.pi / N_SPOKES
    out = []
    for row in psi:
        out.append([(row[(k + 1) % N_SPOKES] - row[(k - 1) % N_SPOKES])
                    / (2.0 * dtheta) for k in range(N_SPOKES)])
    return out


# ── The reverse-definer:  beta = theta - alpha ───────────────────────────────

def reverse_define(text: str, level: int = 2) -> Dict[str, object]:
    """
    Run L_(I|O) on the tower plane and return the reverse-defined source
    angles beta for the observed spokes theta.

    level defaults to 2 = the H eye (sigma=1/2, the critical line) because
    that is where ptol.c says J_blue fires. Not a tuned choice; it is the
    tower's own distinguished level.
    """
    field = tower_field(text)
    kappa = convergence(field)
    psi = lensing_potential(kappa)
    alpha = deflection(psi)
    theta = [spoke_angle(k, TOWER_EYES[level][1]) for k in range(N_SPOKES)]
    beta = [theta[k] - alpha[level][k] for k in range(N_SPOKES)]
    return {
        'text': text,
        'level': TOWER_EYES[level][2],
        'sigma': TOWER_EYES[level][0],
        'sigma_self': measure_sigma(field[level]),
        'theta': theta,
        'alpha': alpha[level],
        'beta': beta,
        'rb_independent': sigma_rb([x / (math.sqrt(sum(y * y for y in field[level])) or 1.0)
                                    for x in field[level]]),
    }


def beta_signature(text: str, level: int = 2) -> List[float]:
    """The reverse-defined source angles alone — the comparable object."""
    return reverse_define(text, level)['beta']


def route_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """
    Cosine between two beta signatures. Cosine only — no learned readout,
    no threshold, nothing fitted.
    """
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


# ── Diagnostics. All may fail. Failure is the output. ────────────────────────

def verify_rb_degeneracy() -> Dict[str, object]:
    """s_rb[k] == s_rb[partner(k)] identically, so only 8 of 16 are free."""
    v = [project("degeneracy probe", k, 0.5) for k in range(N_SPOKES)]
    full = sigma_rb_full(v)
    bad = [k for k in range(N_SPOKES)
           if abs(full[k] - full[rb_partner(k)]) > 1e-12]
    return {
        'involution': all(rb_partner(rb_partner(k)) == k for k in range(N_SPOKES)),
        'mismatched_pairs': bad,
        'full_entries': len(full),
        'independent_entries': len(sigma_rb(v)),
        'reduction': f"{len(full)} -> {len(sigma_rb(v))} (2x)",
        'pass': not bad and len(sigma_rb(v)) == 8,
    }


def test_d_star_invariant(texts: Sequence[str] = None) -> Dict[str, object]:
    """
    ptol.c lines 13 and 111 claim: J_red x J_blue = d* = 0.24600, conserved
    at ALL sigma.

    This test EXPECTS TO FAIL. The claim was measured false in the
    2026-07-21/22 session and is still uncorrected in ptol.c. It is
    reproduced here so the falsity travels with the code instead of living
    only in a context file.
    """
    if texts is None:
        texts = ["the quick brown fox", "hot", "philadelphos speaks", "zero divisor"]
    D_STAR = 0.24600
    obs = []
    for t in texts:
        for sig in (0.1, 0.25, 0.5, 1.0, 2.0):
            v = [project(t, k, sig) for k in range(N_SPOKES)]
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            obs.extend(sigma_rb([x / norm for x in v]))
    return {
        'claim': 'J_red x J_blue = d* = 0.24600 conserved at all sigma',
        'observed_min': min(obs), 'observed_max': max(obs),
        'd_star': D_STAR,
        'any_within_1pct': any(abs(o - D_STAR) < 0.0025 for o in obs),
        'claim_holds': False if not any(abs(o - D_STAR) < 0.0025 for o in obs) else None,
        'note': 'ptol.c lines 13/111 are aspirational, not derived. Still uncorrected there.',
    }


def test_reverse_definition(pairs: Sequence[Tuple[str, str]],
                            distractors: Sequence[str],
                            seed: int = 20260728) -> Dict[str, object]:
    """
    Does the reverse-definer relate an input to its paired response more
    than to an INDEPENDENTLY DRAWN control?

    Control construction matters here. .clauderc_context_2 records a real
    baseline-contamination bug in this codebase where the "random" control
    was a near-duplicate of the item under test (p+2*randint), which
    manufactured a signal. Controls here are drawn from a distractor pool
    that shares no membership with the pairs.

    Reports the margin. Does not threshold it, does not declare success.
    """
    rng = random.Random(seed)
    pool = [d for d in distractors
            if all(d != a and d != b for a, b in pairs)]
    if len(pool) < 2:
        raise ValueError("distractor pool too small for an independent control")

    rows = []
    hits = 0
    for a, b in pairs:
        sa, sb = beta_signature(a), beta_signature(b)
        s_true = route_similarity(sa, sb)
        ctrl = rng.choice(pool)
        s_ctrl = route_similarity(sa, beta_signature(ctrl))
        # rank the true partner against the whole independent pool
        scored = sorted(((route_similarity(sa, beta_signature(c)), c)
                         for c in pool + [b]), reverse=True)
        rank = [c for _, c in scored].index(b) + 1
        if rank == 1:
            hits += 1
        rows.append({'input': a, 'partner': b, 'sim_partner': s_true,
                     'control': ctrl, 'sim_control': s_ctrl,
                     'margin': s_true - s_ctrl, 'rank_of_partner': rank,
                     'n_candidates': len(pool) + 1})
    n = len(rows)
    return {
        'rows': rows,
        'top1': hits / n if n else 0.0,
        'chance': 1.0 / (len(pool) + 1),
        'mean_margin': sum(r['margin'] for r in rows) / n if n else 0.0,
        'note': 'top1 at or below chance means the reverse-definer carries no '
                'semantic relation here. That is a result, not a bug.',
    }


def resolution_probe(text_a: str, text_b: str,
                     levels: Sequence[int] = (5, 9, 17, 33)) -> Dict[str, object]:
    """
    Phase 22's standing hypothesis, made cheap to test: if a result is flat,
    is it under-resolution?

    Re-runs the reverse-definer with more sigma levels (uniform on [0,1];
    the 5-level tower is the ptol.c default and stays the reported result).
    If similarity is unchanged as levels grow, under-resolution in sigma is
    REJECTED for this construction and the cause lies elsewhere.
    """
    out = []
    for n in levels:
        sig = [1.0 - i / (n - 1) for i in range(n)]
        def beta_at(t: str) -> List[float]:
            f = tower_field(t, sigma_levels=sig)
            psi = lensing_potential(convergence(f))
            al = deflection(psi)
            mid = n // 2
            th = [spoke_angle(k, math.pi / 8.0) for k in range(N_SPOKES)]
            return [th[k] - al[mid][k] for k in range(N_SPOKES)]
        out.append({'sigma_levels': n,
                    'cos': route_similarity(beta_at(text_a), beta_at(text_b))})
    return {'pair': (text_a, text_b), 'sweep': out,
            'note': 'flat across levels => under-resolution in sigma is not the cause.'}


# ── Main ─────────────────────────────────────────────────────────────────────

def _main() -> int:
    print("translator_monad.py v1 — L_(I|O) reverse-definer on the (sigma,theta) tower")
    print("=" * 74)

    print("\n[1] 0_RB degeneracy — claiming the 2x ptol.c leaves on the table")
    d = verify_rb_degeneracy()
    print(f"    partner is an involution : {d['involution']}")
    print(f"    mismatched pairs         : {d['mismatched_pairs']}")
    print(f"    entries                  : {d['reduction']}")
    print(f"    PASS                     : {d['pass']}")

    print("\n[2] ptol.c's d* invariant claim — EXPECTED TO FAIL, kept on purpose")
    t = test_d_star_invariant()
    print(f"    claim    : {t['claim']}")
    print(f"    observed : [{t['observed_min']:+.6f}, {t['observed_max']:+.6f}]  vs d*={t['d_star']}")
    print(f"    holds    : {t['claim_holds']}")

    print("\n[3] Reverse-definer on the H eye (sigma=1/2)")
    r = reverse_define("the quick brown fox")
    print(f"    level={r['level']} sigma={r['sigma']}  sigma_self={r['sigma_self']:.6f}")
    print(f"    alpha[0:4] = {[round(x, 6) for x in r['alpha'][:4]]}")
    print(f"    beta [0:4] = {[round(x, 6) for x in r['beta'][:4]]}")
    print(f"    0_RB independent entries: {len(r['rb_independent'])}")

    print("\n[4] Does it translate? (antonym/associate pairs, independent controls)")
    pairs = [("hot", "cold"), ("up", "down"), ("light", "dark"), ("true", "false")]
    distractors = ["stone", "river", "engine", "quiet", "seven", "orbit",
                   "copper", "silent", "harbour", "lantern"]
    tr = test_reverse_definition(pairs, distractors)
    for row in tr['rows']:
        print(f"    {row['input']:6} -> {row['partner']:6} "
              f"sim={row['sim_partner']:+.4f}  ctrl({row['control']:8})={row['sim_control']:+.4f}"
              f"  margin={row['margin']:+.4f}  rank={row['rank_of_partner']}/{row['n_candidates']}")
    print(f"    top1={tr['top1']:.3f}  chance={tr['chance']:.3f}  "
          f"mean margin={tr['mean_margin']:+.4f}")
    print(f"    {tr['note']}")

    print("\n[5] Phase 22 resolution hypothesis — is flatness under-resolution?")
    rp = resolution_probe("hot", "cold")
    for s in rp['sweep']:
        print(f"    sigma_levels={s['sigma_levels']:3}  cos(hot,cold)={s['cos']:+.6f}")
    print(f"    {rp['note']}")

    return 0


if __name__ == '__main__':
    sys.exit(_main())
