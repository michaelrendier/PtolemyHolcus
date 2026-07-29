#!/usr/bin/env python3
"""
lio_monad.py — L_(I|O): the inside-out path of the primes. v1.

Python testbed (Cody's standing rule: Python first, ptol.c only on
significant progress or when C-level testing is actually needed).

Rebuild of the L_(I|O) model, replacing the approach in
translator_monad.py, which failed for a diagnosed reason kept on record
below.

────────────────────────────────────────────────────────────────────────────
WHY THE PREVIOUS ATTEMPT FAILED — and what changed
────────────────────────────────────────────────────────────────────────────
translator_monad.py ran the lens equation on ptol.c's (sigma,theta) tower
and came back BELOW chance (top1=0.000 vs chance 0.091), every cosine
+1.0000. Two causes, both measured, both fixed here rather than papered
over:

1. THE COMMON MODE.  ptol.c's project() decomposes exactly as
       project(text,k,sigma) = cbar * W(n,k,sigma) + D(content)
   where cbar is the mean character code and W depends ONLY on length and
   channel. Measured: content is 2-3% of the signal; cos(actual,common)
   = +0.9998; and for 'zzz' the content term is EXACTLY 0.0 (all chars
   equal the mean). Consequence: cosine is a LENGTH detector.
       |len(a)-len(b)|=0 -> mean|cos| = 0.994
                       =5 -> mean|cos| = 0.868
   Worse, ptol.c then normalises (v[k]=_x[k]/norm), which DIVIDES OUT cbar
   — the only content-carrying scalar — leaving the pure length kernel.

2. NO QUADRATURE PAIR.  ptol.c assigns cos/sin BY SHELL (J_red k=0-3,8-11
   cos; J_blue k=4-7,12-15 sin), so s_rb[k]=v[k]*v[partner] multiplies
   cos-at-p_k by sin-at-a-DIFFERENT-prime (2 with 11, 3 with 13, ...).
   That is not a spin-2 object, so there is nothing for a Kaiser-Squires-
   shaped inversion to act on.

THE FIX, and it is not a tuning knob:

  * engines/e06_two_trees.py already computes BOTH cos and sin at EVERY
    prime — Telperion (symmetric/cosine/standing wave/pi-family) and
    Laurelin (antisymmetric/sine/spiral/phi-family). At each prime that
    gives a genuine quadrature pair, so z_k = T_k + i*L_k is a real
    complex amplitude at ONE frequency. This is the Two Trees engine's
    decomposition, not a new construction.

  * PHASE arg(z_k) is EXACTLY invariant under scaling every character
    code, because cbar multiplies T and L identically and atan2 is a
    ratio. Measured: max|phase(x) - phase(7.3x)| = 4.4e-16. The common
    mode is a SCALE, and phase is scale-free. This removes it without
    subtracting anything and without introducing the zero-vector
    degeneracy that centering does ('zzz' centred -> all zeros).

    Separation, same word list: magnitude mean|cos| = 0.990,
    PHASE mean|cos| = 0.634.

────────────────────────────────────────────────────────────────────────────
FERMAT N-SHAPE, RIEMANN N-HOLES
────────────────────────────────────────────────────────────────────────────
From MonsterFermat.md (Cody's result, TAKEN AS GIVEN here — this file does
NOT re-derive it and must not be read as evidence for it):

  23 rank-24 root systems of equal Coxeter number land on 13 of the 16
  sedenion slots. Three slots cannot be reached by A/D/E arithmetic at
  all. The Monster fills exactly those three. 71 structures cover all 16,
  no gaps, no overlaps. The missing set is named there as {1, 11, 15}.

So the 16 prime channels split:
    N-SHAPE  the 13 Fermat-reachable slots — what the equation permits
    N-HOLES  {1, 11, 15} — unreachable by the regular families

CONFIDENCE: the {1,11,15} identification is CITED, not verified here. I
have not checked the Niemeier-to-sedenion slot assignment. If it is wrong
the hole set is wrong, and every hole-dependent result below is wrong with
it. Flagged, not hidden.

The holes are treated as Phase 22 instructs — ZD loci are PORTALS, where
information is BORN, not endpoints where it dies. They are therefore the
degenerate loci of the transform, and are resolved the way L_(I|O)'s
kaiser_squires_kappa resolves its own k=0 mode: assigned explicitly by a
stated convention, neither allowed to blow up nor silently dropped.

────────────────────────────────────────────────────────────────────────────
PRIME DIRECTIVES
────────────────────────────────────────────────────────────────────────────
#1  Nothing fitted. Primes, sigma, and the (I|O) map are lifted verbatim
    from ptol.c / the inversion engine. Phase invariance is proved, not
    tuned. No thresholds are chosen to make a test pass.
#2  Every probe may fail and its failure is the output. Controls are drawn
    from an INDEPENDENT pool (.clauderc_context_2 records a real
    contaminated-control bug in this codebase: p+2*randint near-duplicates
    manufacturing a signal).

Author: Cody Michael Allison + Claude (Anthropic), 2026-07-28
"""

import cmath
import itertools
import math
import random
import sys
from typing import Dict, List, Sequence, Tuple

# ── Constants, verbatim from ptol.c / e06_two_trees.py ───────────────────────

P16: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
N_SLOTS = 16

# MonsterFermat.md: the three sedenion slots A/D/E arithmetic cannot reach.
# CITED, NOT VERIFIED HERE.
N_HOLES: Tuple[int, int, int] = (1, 11, 15)
N_SHAPE: Tuple[int, ...] = tuple(k for k in range(N_SLOTS) if k not in N_HOLES)

PHI = (1.0 + math.sqrt(5.0)) / 2.0
SIGMA_CRIT = 0.5


# ── The Two Trees — e06_two_trees.py's decomposition, both at every prime ────

def two_trees(text: str, sigma: float = SIGMA_CRIT) -> Tuple[List[float], List[float]]:
    """
    Telperion T (cosine, standing wave, pi-family) and
    Laurelin  L (sine,   spiral,        phi-family)
    computed at EVERY prime — the whole point.

    ptol.c splits these across shells; e06_two_trees.py does not. Taking
    both at each prime is what makes z_k = T_k + i*L_k a genuine
    quadrature pair at a single frequency.
    """
    T = [0.0] * N_SLOTS
    L = [0.0] * N_SLOTS
    for i, c in enumerate(text.encode('utf-8', 'replace'), start=1):
        w = i ** -sigma
        for k in range(N_SLOTS):
            ph = 2.0 * math.pi * i / P16[k]
            T[k] += c * w * math.cos(ph)
            L[k] += c * w * math.sin(ph)
    return T, L


def z_field(text: str, sigma: float = SIGMA_CRIT) -> List[complex]:
    """z_k = T_k + i*L_k — the complex amplitude at prime p_k."""
    T, L = two_trees(text, sigma)
    return [complex(T[k], L[k]) for k in range(N_SLOTS)]


def phase_signature(text: str, sigma: float = SIGMA_CRIT) -> List[float]:
    """
    arg(z_k) for all 16 slots — the common-mode-immune object.

    EXACTLY scale-invariant: multiplying every character code by any m>0
    multiplies T and L identically, and atan2 is a ratio. Proven by
    verify_phase_scale_invariance(), not assumed.
    """
    return [cmath.phase(z) for z in z_field(text, sigma)]


# ── The (I|O) inversion — inside-out ─────────────────────────────────────────

def inversion_io(z: complex) -> complex:
    """
    The (I|O) map from the inversion engine: (r, theta) -> (1/r, theta+pi/2).

    Compression stroke r -> 1/r; the pi/2 is the horizon rotation, which
    the inversion module derives from Hurwitz (exactly 4 normed division
    algebras => the map's order is exactly 4 => one full turn / 4 = pi/2).
    Not an assumed constant.

    r=0 is the Observer — the map's own degenerate point. Returns 0 there
    by stated convention rather than raising: the inside-out image of the
    origin is the point at infinity, which this finite representation
    cannot hold, and silently dropping it would lose a slot.
    """
    r = abs(z)
    if r == 0.0:
        return 0j
    return cmath.rect(1.0 / r, cmath.phase(z) + math.pi / 2.0)


def io_field(text: str, sigma: float = SIGMA_CRIT) -> List[complex]:
    """The inside-out image of the whole prime field."""
    return [inversion_io(z) for z in z_field(text, sigma)]


# ── The path of the primes ───────────────────────────────────────────────────

def prime_path(text: str, sigma: float = SIGMA_CRIT) -> List[int]:
    """
    ptol.c's spiral idx[]: slots ordered by ascending |z_k| — the walk from
    the ZD centre outward to the great-circle rim.

    Phase 22: this is not just a picture, it is the memory trace. Here it
    is the PATH OF THE PRIMES: which prime channel the field passes through
    at each step on its way out of the portal.
    """
    z = z_field(text, sigma)
    return sorted(range(N_SLOTS), key=lambda k: abs(z[k]))


def path_through_holes(text: str, sigma: float = SIGMA_CRIT) -> Dict[str, object]:
    """
    Where do the N-HOLES sit on the outward path?

    Phase 22's correction: a ZD locus is an ORIGIN, not an endpoint —
    "they ARE where things are born". If the holes are portals, they
    should sit EARLY on a centre-outward walk (small |z|, near the
    centre). Late positions would contradict that reading.

    This measures. It does not adjust anything to make the holes land early.
    """
    path = prime_path(text, sigma)
    pos = {h: path.index(h) for h in N_HOLES}
    mean_hole = sum(pos.values()) / len(pos)
    others = [path.index(k) for k in N_SHAPE]
    return {
        'path': path,
        'hole_positions': pos,
        'mean_hole_position': mean_hole,
        'mean_shape_position': sum(others) / len(others),
        'holes_earlier_than_shape': mean_hole < sum(others) / len(others),
        'note': 'portals should sit early (near centre) if Phase 22 is right here.',
    }


# ── N-shape / N-hole split of the signature ──────────────────────────────────

def n_shape_signature(text: str, sigma: float = SIGMA_CRIT) -> List[float]:
    """Phases on the 13 Fermat-reachable slots only."""
    p = phase_signature(text, sigma)
    return [p[k] for k in N_SHAPE]


def n_hole_signature(text: str, sigma: float = SIGMA_CRIT) -> List[float]:
    """Phases on the 3 Monster slots only."""
    p = phase_signature(text, sigma)
    return [p[k] for k in N_HOLES]


# ── Similarity ───────────────────────────────────────────────────────────────

def cos_sim(a: Sequence[float], b: Sequence[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def circular_sim(a: Sequence[float], b: Sequence[float]) -> float:
    """
    Mean cos(delta) between two phase vectors. Phases are ANGLES, so the
    circular measure is the correct one; plain cosine on raw angle values
    treats 0 and 2pi as maximally different. Reported alongside cos_sim so
    the difference is visible rather than assumed.
    """
    if not a:
        return 0.0
    return sum(math.cos(x - y) for x, y in zip(a, b)) / len(a)


# ── Diagnostics. All may fail. Failure is the output. ────────────────────────

def verify_phase_scale_invariance(text: str = "hot", mult: float = 7.3) -> Dict[str, object]:
    """The claim the whole rebuild rests on. If this fails, nothing below holds."""
    def scaled(t, k):
        T = L = 0.0
        for i, c in enumerate(t.encode(), start=1):
            w = i ** -SIGMA_CRIT
            ph = 2.0 * math.pi * i / P16[k]
            T += c * mult * w * math.cos(ph)
            L += c * mult * w * math.sin(ph)
        return complex(T, L)
    a = phase_signature(text)
    b = [cmath.phase(scaled(text, k)) for k in range(N_SLOTS)]
    resid = max(abs(x - y) for x, y in zip(a, b))
    return {'multiplier': mult, 'max_residual': resid,
            'pass': resid < 1e-12,
            'note': 'cbar is a SCALE; arg() is scale-free. Exact, not approximate.'}


def verify_io_order_four() -> Dict[str, object]:
    """
    (I|O) has order 4: r->1/r twice returns r, and theta+pi/2 four times is
    a full turn. Hurwitz forces exactly 4. Checked, not assumed.
    """
    z = complex(0.7, -1.3)
    w = z
    steps = [w]
    for _ in range(4):
        w = inversion_io(w)
        steps.append(w)
    resid = abs(steps[4] - steps[0])
    return {'start': z, 'after_4': steps[4], 'residual': resid,
            'pass': resid < 1e-9}


def common_mode_comparison(words: Sequence[str]) -> Dict[str, object]:
    """
    Magnitude vs phase, on identical inputs. This is the measurement that
    justifies using phase, reported so it can be checked rather than
    trusted.
    """
    out = {}
    for lbl, f in (('magnitude', lambda t: [abs(z) for z in z_field(t)]),
                   ('phase', phase_signature)):
        cs = [abs(cos_sim(f(a), f(b))) for a, b in itertools.combinations(words, 2)]
        out[lbl] = {'mean_abs_cos': sum(cs) / len(cs), 'max_abs_cos': max(cs)}
    return out


def test_translation(pairs: Sequence[Tuple[str, str]],
                     distractors: Sequence[str],
                     signature=phase_signature,
                     sim=circular_sim,
                     seed: int = 20260728) -> Dict[str, object]:
    """
    Does the input's signature rank its paired response above an
    INDEPENDENTLY drawn pool? Reports rank and margin. Does not threshold,
    does not declare success.
    """
    rng = random.Random(seed)
    pool = [d for d in distractors if all(d != a and d != b for a, b in pairs)]
    if len(pool) < 2:
        raise ValueError("distractor pool too small for an independent control")
    rows, hits = [], 0
    for a, b in pairs:
        sa = signature(a)
        s_true = sim(sa, signature(b))
        ctrl = rng.choice(pool)
        scored = sorted(((sim(sa, signature(c)), c) for c in pool + [b]), reverse=True)
        rank = [c for _, c in scored].index(b) + 1
        hits += (rank == 1)
        rows.append({'input': a, 'partner': b, 'sim_partner': s_true,
                     'control': ctrl, 'sim_control': sim(sa, signature(ctrl)),
                     'rank': rank, 'n': len(pool) + 1})
    n = len(rows)
    return {'rows': rows, 'top1': hits / n, 'chance': 1.0 / (len(pool) + 1),
            'mean_margin': sum(r['sim_partner'] - r['sim_control'] for r in rows) / n}


def _main() -> int:
    print("lio_monad.py v1 — L_(I|O): the inside-out path of the primes")
    print("=" * 74)

    print("\n[1] Phase scale-invariance — the claim the rebuild rests on")
    v = verify_phase_scale_invariance()
    print(f"    max residual under x{v['multiplier']} : {v['max_residual']:.3e}   PASS={v['pass']}")

    print("\n[2] (I|O) has order 4 (Hurwitz: exactly 4 normed division algebras)")
    o = verify_io_order_four()
    print(f"    |(I|O)^4(z) - z| = {o['residual']:.3e}   PASS={o['pass']}")

    words = ['hot', 'cold', 'up', 'down', 'light', 'dark',
             'stone', 'river', 'engine', 'copper']
    print("\n[3] Common mode: magnitude vs phase, same inputs")
    cm = common_mode_comparison(words)
    for k, d in cm.items():
        print(f"    {k:10} mean|cos| = {d['mean_abs_cos']:.6f}   max = {d['max_abs_cos']:.6f}")

    print("\n[4] Fermat N-shape / Riemann N-holes")
    print(f"    N_SHAPE (13 reachable) : {N_SHAPE}")
    print(f"    N_HOLES (Monster, 3)   : {N_HOLES}   [CITED from MonsterFermat.md, unverified]")
    for t in ('hot', 'philadelphos'):
        h = path_through_holes(t)
        print(f"    {t:14} path={h['path']}")
        print(f"    {'':14} holes at {h['hole_positions']}  mean {h['mean_hole_position']:.2f} "
              f"vs shape {h['mean_shape_position']:.2f}  earlier={h['holes_earlier_than_shape']}")

    print("\n[5] Translation test — full 16, N-shape only, N-holes only")
    pairs = [("hot", "cold"), ("up", "down"), ("light", "dark"), ("true", "false")]
    distractors = ["stone", "river", "engine", "quiet", "seven", "orbit",
                   "copper", "silent", "harbour", "lantern"]
    for lbl, sigf in (("all 16", phase_signature),
                      ("N-shape", n_shape_signature),
                      ("N-holes", n_hole_signature)):
        r = test_translation(pairs, distractors, signature=sigf)
        ranks = [row['rank'] for row in r['rows']]
        print(f"    {lbl:8} top1={r['top1']:.3f} (chance {r['chance']:.3f})  "
              f"ranks={ranks}  mean margin={r['mean_margin']:+.4f}")

    print("\n    per-pair detail (all 16):")
    for row in test_translation(pairs, distractors)['rows']:
        print(f"      {row['input']:6} -> {row['partner']:6} sim={row['sim_partner']:+.4f}  "
              f"ctrl({row['control']:8})={row['sim_control']:+.4f}  rank={row['rank']}/{row['n']}")
    return 0


if __name__ == '__main__':
    sys.exit(_main())
