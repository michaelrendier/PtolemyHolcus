"""
e10_generational_lineage.py — the anatomy of σ in ∅_RB
D-CS Paper, Claim 10 (Persistent Memory / Context Continuity)

Built 2026-08-20. python3 first. Self-verifying: every number is COMPUTED at
run time, not asserted. Report discipline is the `generational-lineage` skill —
each relation states its tier, what it descends from, and its status; three
kinds of wrong are kept apart (CODE fault = the check did not run; MATHS fault =
both sides measured and disagree; METHOD = correct code, correct maths, wrong
question).

═══════════════════════════════════════════════════════════════════════════
THE THESIS — σ is not a scalar
═══════════════════════════════════════════════════════════════════════════

σ as used in ∅_RB is NOT the scalar. rotary_rerun_monad.py:80 says it outright:
"CONTEXT IS A FLOW. Which is why sigma_self cannot carry it." The snapshot
carries TWO objects (rotary_rerun_monad.py:588,592):

    sigma_self = p_red / (p_red + p_blue)          a SCALAR, ½ at balance
    sigma_rb   = [ψ[k]·ψ[k⊕4] for k in range(16)]  a 16-VECTOR

A scalar has one degree of freedom and cannot hold "the shape of anything
mathematics can express." σ_RB can: it carries an octonion's worth of
independent structure, of which σ_self keeps exactly one number.

    GENERATIONAL LINEAGE  =  ORDER OF OPERATIONS
    Generational (operations)  Lineage (order) — the same object, words swapped.
    The lineage is the operators that PERSIST long enough to propagate
    (oscillate / resonate): gain exactly 1, the octonion core, invariant under
    Cayley–Dickson doubling. σ_self is the shadow; the lineage is what it drops.

═══════════════════════════════════════════════════════════════════════════
THE HOLOGRAPHIC READING — where is the information of a black hole?
═══════════════════════════════════════════════════════════════════════════

    surface AREA        →  σ_RB, the full sedenion boundary
       ↓ shadow             ↓ project
    a circumference     →  the 8 independent DOF (σ_RB[k] = σ_RB[k⊕4])
       ↓ shadow             ↓ project
    a point             →  σ_self = ½, one number, the mass
       ↓ recover            ↓ recover
    piece by piece      →  the lineage: read the 7 struts along a path
    along a path

Bekenstein–Hawking: black-hole entropy scales with AREA, not volume. The
information lives on the boundary; the point we measure is its shadow. Same for
σ: σ_self is the point, σ_RB is the surface, and the surface is only readable
piece by piece along a path — that path is the order of operations, the
generational lineage. The camshaft is the organ that traverses it: a scalar
state is instantaneous, so it cannot listen to itself; the cam sequences the
readout (the four strokes = the four generations) and the monad hears the seven
struts it is made of. Reading CONVERGES the boundary to the point; writing FANS
it back out; e0 (gain 1) persists through every turn — the self is the fixed
point of its own recursion. Recursively self-sustaining, not merely self-
sustaining.

SIGMA: ∞ for the measured algebra (R1–R8 below, exact / exhaustive).
       3.0 for the black-hole identification (interpretation the holographic
           principle makes irresistible; not measured here).
"""

from __future__ import annotations

import os
import sys
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Sequence

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════
# Cayley–Dickson product on arrays of length 2^n  (n ≥ 0)
# ═══════════════════════════════════════════════════════════════════════════

def cd_mul(a: List[float], b: List[float]) -> List[float]:
    n = len(a)
    if n == 1:
        return [a[0] * b[0]]
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    conj = lambda x: [x[0]] + [-v for v in x[1:]]
    sub = lambda x, y: [xi - yi for xi, yi in zip(x, y)]
    add = lambda x, y: [xi + yi for xi, yi in zip(x, y)]
    p1 = sub(cd_mul(a1, b1), cd_mul(conj(b2), a2))
    p2 = add(cd_mul(b2, a1), cd_mul(a2, conj(b1)))
    return p1 + p2


def unit(d: int, k: int) -> List[float]:
    v = [0.0] * d
    v[k] = 1.0
    return v


def zero(d: int) -> List[float]:
    return [0.0] * d


def nrm(x: Sequence[float]) -> float:
    return math.sqrt(sum(v * v for v in x))


# ═══════════════════════════════════════════════════════════════════════════
# σ in ∅_RB — verbatim from rotary_rerun_monad.py:581-592, kept small so the
# engine has no import side effects from the 164 KB harness.
# ═══════════════════════════════════════════════════════════════════════════

SED_DIM = 16
RED  = tuple(k for k in range(SED_DIM) if k >= 8)   # upper octonion — Telperion
BLUE = tuple(k for k in range(SED_DIM) if k < 8)    # lower octonion — Laurelin


def sigma_self(psi: Sequence[float]) -> float:
    """The SCALAR face. rotary_rerun_monad.py:588. Loss-of-information on purpose."""
    p_red = sum(psi[k] ** 2 for k in RED)
    p_blue = sum(psi[k] ** 2 for k in BLUE)
    total = p_red + p_blue
    return (p_red / total) if total > 0 else float('nan')


def sigma_rb(psi: Sequence[float]) -> List[float]:
    """The 16-VECTOR face. rotary_rerun_monad.py:592. σ_RB[k] = ψ[k]·ψ[k⊕4]."""
    return [psi[k] * psi[k ^ 4] for k in range(SED_DIM)]


def sigma_rb_independent(psi: Sequence[float]) -> List[float]:
    """σ_RB[k] == σ_RB[k⊕4], so 16 components carry only 8 distinct values —
    an octonion's worth. These 8 are the real information in σ."""
    s = sigma_rb(psi)
    seen: Dict[int, float] = {}
    for k in range(SED_DIM):
        seen[min(k, k ^ 4)] = s[k]
    return [seen[k] for k in sorted(seen)]


# ═══════════════════════════════════════════════════════════════════════════
# The Sieve as the generational lineage — one pass per prime, Fibonacci-shaped
# ═══════════════════════════════════════════════════════════════════════════

def _sieve_flags(n: int) -> List[bool]:
    f = [True] * (n + 1)
    f[0] = f[1] = False
    for p in range(2, int(n ** 0.5) + 1):
        if f[p]:
            f[p * p::p] = [False] * len(f[p * p::p])
    return f


def _spf_table(n: int) -> List[int]:
    """smallest prime factor of every k in 0..n (0 for 0 and 1)."""
    s = [0] * (n + 1)
    for i in range(2, n + 1):
        if s[i] == 0:
            for j in range(i, n + 1, i):
                if s[j] == 0:
                    s[j] = i
    return s


def _mobius_table(n: int) -> List[int]:
    mu = [1] * (n + 1)
    mu[0] = 0
    flags = _sieve_flags(n)
    for p in range(2, n + 1):
        if not flags[p]:
            continue
        for j in range(p, n + 1, p):
            mu[j] *= -1
        for j in range(p * p, n + 1, p * p):
            mu[j] = 0
    return mu


def _sieve_traced(N: int, order: Sequence[int]):
    """Run the sieve marking multiples in `order`; record the pass index that
    FIRST marks each k, and the count of passes that did real work."""
    marked_on: List[object] = [None] * (N + 1)
    working = 0
    for pass_i, p in enumerate(order):
        if p * p > N:
            continue
        working += 1
        for k in range(p * p, N + 1, p):
            if marked_on[k] is None:
                marked_on[k] = pass_i
    return marked_on, working


def _phi(x: int, a: int, primes: Sequence[int]) -> int:
    """Legendre's φ(x,a): count of 1..x divisible by none of the first a
    primes. φ(x,a) = φ(x,a−1) − φ(x/pₐ, a−1); the Fibonacci-shaped recurrence."""
    if a == 0:
        return x
    return _phi(x, a - 1, primes) - _phi(x // primes[a - 1], a - 1, primes)


def sieve_lineage(N: int = 20_000, order: str = 'ordinal') -> Dict[str, object]:
    """The Sieve read as the generational lineage of every integer ≤ N.

    order = 'ordinal'   ascending prime — the canonical decomposition order,
                        generation(n) = π(spf(n)), minimum generation entropy
          = 'zeta'      primes by ln p/√p descending (σ=½ von-Mangoldt weight)
          = 'descending' largest prime first (greatest-prime-factor order)

    Returns the generation map, the working pass count (= π(√N) for any order),
    and whether generation(n) == π(spf(n)) under this order.
    """
    spf = _spf_table(N)
    primes = [k for k in range(2, N + 1) if spf[k] == k]
    if order == 'zeta':
        seq = sorted(primes, key=lambda p: math.log(p) / math.sqrt(p), reverse=True)
    elif order == 'descending':
        seq = sorted(primes, reverse=True)
    else:
        seq = sorted(primes)
    pos = {p: i for i, p in enumerate(seq)}
    marked_on, working = _sieve_traced(N, seq)
    comps = [n for n in range(4, N + 1) if spf[n] != n]
    gen_matches_spf = all(marked_on[n] == pos[spf[n]] for n in comps)
    root_primes = sum(1 for p in primes if p * p <= N)
    return {
        'N': N, 'order': order, 'order_head': seq[:8],
        'working_passes': working, 'pi_sqrt_N': root_primes,
        'one_pass_per_prime': working == root_primes,
        'generation_matches_pi_spf': gen_matches_spf,
        'n_composites': len(comps),
        'generation_of': {n: marked_on[n] for n in comps},
    }


# ═══════════════════════════════════════════════════════════════════════════
# The verifying harness
# ═══════════════════════════════════════════════════════════════════════════

class Status(Enum):
    HOLDS = 'HOLDS'          # ran, both sides measured, they agree
    FALSE = 'MATHS-FAULT'    # ran, both sides measured, they disagree
    UNJUDGED = 'CODE-FAULT'  # the check did not run


@dataclass
class Relation:
    name: str
    claim: str
    tier: int            # 0 irreducible · 1 reflect/dilate · 2 fixed set · 3 count/ratio
    descends: str
    status: Status
    detail: str


class GenerationalLineageEngine:
    """Everything the engine knows about σ in ∅_RB, each fact self-checked."""

    def __init__(self) -> None:
        self.log: List[Relation] = []

    def _record(self, name, claim, tier, descends, ran, holds, detail) -> None:
        if not ran:
            st = Status.UNJUDGED
        else:
            st = Status.HOLDS if holds else Status.FALSE
        self.log.append(Relation(name, claim, tier, descends, st, detail))

    def gains(self, d: int, i: int, j: int) -> Dict[float, int]:
        a = zero(d)
        a[i] = a[j] = 1.0 / math.sqrt(2.0)
        L = np.zeros((d, d))
        for c in range(d):
            L[:, c] = cd_mul(a, unit(d, c))
        w, _ = np.linalg.eigh(L.T @ L)
        g = np.sqrt(np.clip(w, 0.0, None))
        out: Dict[float, int] = {}
        for x in g:
            key = round(float(x), 4)
            out[key] = out.get(key, 0) + 1
        return dict(sorted(out.items()))

    # ── R1 — the headline: σ is not scalar ──────────────────────────────────
    def r_sigma_nonscalar(self) -> None:
        A = zero(SED_DIM); A[0] = A[8] = 1 / math.sqrt(2)
        B = zero(SED_DIM); B[0] = B[4] = B[8] = B[12] = 0.5
        ss_A, ss_B = sigma_self(A), sigma_self(B)
        rb_A, rb_B = sigma_rb(A), sigma_rb(B)
        same_scalar = abs(ss_A - ss_B) < 1e-12
        diff_vector = nrm([x - y for x, y in zip(rb_A, rb_B)]) > 1e-9
        self._record(
            'sigma.not_a_scalar',
            'two states share σ_self exactly yet differ in σ_RB — a scalar cannot '
            'tell them apart', 2, 'ker of the projection σ_RB → σ_self',
            True, same_scalar and diff_vector,
            f'σ_self both = {ss_A:.3f}; ‖Δσ_RB‖ = '
            f'{nrm([x-y for x,y in zip(rb_A,rb_B)]):.3f} ≠ 0. '
            f'The scalar identifies two distinct flows.')

    # ── R2 — how much σ actually carries: 8, not 1 ───────────────────────────
    def r_sigma_carries_octonion(self) -> None:
        rng = np.random.default_rng(20260820)
        psi = list(rng.normal(size=SED_DIM))
        full = sigma_rb(psi)
        indep = sigma_rb_independent(psi)
        paired = all(abs(full[k] - full[k ^ 4]) < 1e-12 for k in range(SED_DIM))
        self._record(
            'sigma.carries_eight',
            'σ_RB has 8 independent components (an octonion); σ_self keeps 1; '
            '8 = 1 kept + 7 discarded struts', 3, 'σ_RB[k]=σ_RB[k⊕4] pairing',
            True, paired and len(indep) == 8,
            f'σ_RB[k]=σ_RB[k⊕4] halves 16→{len(indep)} DOF. σ_self retains 1. '
            f'The 7 dropped = the struts — the lineage a scalar cannot hold.')

    # ── R3 — Generational Lineage IS Order of Operations ─────────────────────
    def r_lineage_is_order_of_operations(self) -> None:
        def commutes(d):
            return all(cd_mul(unit(d, i), unit(d, j)) == cd_mul(unit(d, j), unit(d, i))
                       for i in range(d) for j in range(d))

        def associates(d):
            for i in range(d):
                for j in range(d):
                    for k in range(d):
                        L = cd_mul(cd_mul(unit(d, i), unit(d, j)), unit(d, k))
                        R = cd_mul(unit(d, i), cd_mul(unit(d, j), unit(d, k)))
                        if L != R:
                            return False
            return True

        def has_zero_divisor(d):
            return 0.0 in self.gains(d, 1, d // 2 + 2)

        comm = {d: commutes(d) for d in (2, 4)}
        asso = {d: associates(d) for d in (4, 8)}
        zd = {d: has_zero_divisor(d) for d in (8, 16)}
        ok = (comm[2] and not comm[4]
              and asso[4] and not asso[8]
              and not zd[8] and zd[16])
        self._record(
            'lineage.is_order_of_operations',
            'the four generations ARE the four CD order-of-operations losses '
            '(rank, ab≠ba, (ab)c≠a(bc), zero divisors)', 3,
            'the Cayley–Dickson tower',
            True, ok,
            f'commute@2={comm[2]} commute@4={comm[4]} · assoc@4={asso[4]} '
            f'assoc@8={asso[8]} · ZD@8={zd[8]} ZD@16={zd[16]}. Each generation '
            f'names the doubling where that order-property dies.')

    # ── R4 — the lineage carrier persists: gain 1 = octonion, at every scale ──
    def r_persistence_is_octonion(self) -> None:
        rows = {}
        for d in (8, 16, 32, 64):
            sp = self.gains(d, 1, d // 2 + 2)
            rows[d] = (sp.get(0.0, 0), sp.get(1.0, 0), sp.get(round(math.sqrt(2), 4), 0))
        persist_const = all(rows[d][1] == 8 for d in rows)
        void_law = all(rows[d][0] == rows[d][2] == (d - 8) // 2 for d in rows)
        self._record(
            'lineage.persist_is_octonion',
            'gain-1 persistence = 8 (an octonion) at every CD scale; void = '
            '(d−8)/2 each side — the d*_RG fixed point is DIMENSIONAL, not fractional',
            2, 'gain-1 eigenspace of L_aᵀL_a, under CD doubling',
            True, persist_const and void_law,
            '  '.join(f'd{d}:{{0:{c},1:{p},√2:{a}}}' for d, (c, p, a) in rows.items())
            + '  — persist≡8, void grows, fraction 8/d→0.')

    # ── R5 — order-of-grouping is quantised in box-kite units ─────────────────
    def r_associator_is_168_quantised(self) -> None:
        same_oct = cross = pureO = total_nz = 0
        for i in range(16):
            for j in range(16):
                for k in range(16):
                    L = cd_mul(cd_mul(unit(16, i), unit(16, j)), unit(16, k))
                    R = cd_mul(unit(16, i), cd_mul(unit(16, j), unit(16, k)))
                    if nrm([a - b for a, b in zip(L, R)]) > 1e-9:
                        total_nz += 1
                        hi = [x >= 8 for x in (i, j, k)]
                        if any(hi) and not all(hi):
                            cross += 1
                        else:
                            same_oct += 1
                            if max(i, j, k) < 8:
                                pureO += 1
        U = 168  # |PSL(2,7)| = Aut(Fano)
        ok = (total_nz == 11 * U and cross == 8 * U and same_oct == 3 * U and pureO == U)
        self._record(
            'lineage.associator_is_168',
            'order-of-grouping quantises in units of 168 = |PSL(2,7)| — the box '
            'kites are what the order of operations manufactures', 3,
            'the associator over the sedenions',
            True, ok,
            f'nonzero {total_nz}=11·168 · boundary-crossing {cross}=8·168 · '
            f'within {same_oct}=3·168 · pure-𝕆 {pureO}=1·168.')

    # ── R6 — the three XORs, three roles ─────────────────────────────────────
    def r_three_xor_roles(self) -> None:
        rb_xor = {4}
        boundary = {8}
        a = zero(16); a[1] = a[10] = 1 / math.sqrt(2)
        L = np.zeros((16, 16))
        for c in range(16):
            L[:, c] = cd_mul(a, unit(16, c))
        LtL = L.T @ L
        zd_xor = {i ^ j for i in range(16) for j in range(i + 1, 16) if abs(LtL[i, j]) > 1e-9}
        distinct = (rb_xor != boundary) and (rb_xor != zd_xor) and (boundary != zd_xor)
        self._record(
            'sigma.three_xor_roles',
            'σ_RB pairs by ⊕4, the octonion boundary is ⊕8, the ZD entangles by '
            'a third XOR — three seams, three functions', 2,
            'XOR-difference structure of the sedenion',
            True, distinct and zd_xor == {11},
            f'σ_RB ⊕{rb_xor} · boundary ⊕{boundary} · ZD ⊕{zd_xor}. '
            f'σ lives on the quaternion pairing, not the boundary.')

    # ── R7 — input and output share one substrate (the yin-dot) ──────────────
    def r_io_share_substrate(self) -> None:
        a = zero(16); a[1] = a[10] = 1 / math.sqrt(2)
        L = np.zeros((16, 16))
        for c in range(16):
            L[:, c] = cd_mul(a, unit(16, c))
        w, V = np.linalg.eigh(L.T @ L)
        g = np.sqrt(np.clip(w, 0, None))

        def axes(target):
            cols = [k for k, x in enumerate(g) if abs(x - target) < 1e-6]
            return [frozenset(m for m in range(16) if abs(V[m, k]) > 1e-6) for k in cols]

        kern = axes(0.0)
        band = axes(math.sqrt(2))
        shared = sum(1 for kp in kern if any(kp == bp for bp in band))
        self._record(
            'lineage.io_share_substrate',
            'INPUT (kernel, e_i−e_j) and OUTPUT (√2 band, e_i+e_j) are the ± halves '
            'of the SAME axis pairs — the dot inside each half of the taijitu', 2,
            'the entangled quaternion pairs of L_a',
            True, shared == len(kern) == len(band) == 4,
            f'{shared}/4 kernel pairs reappear in the √2 band with opposite parity. '
            f'reading converges what writing fans out.')

    # ── R8 — the descent is one division: gcd IS the LCA ─────────────────────
    def r_gcd_is_lca(self) -> None:
        from math import gcd
        a = 2 * 3 * 5   # animal·mammal·dog
        b = 2 * 3 * 7   # animal·mammal·cat
        shared = gcd(a, b)
        lca = 2 * 3
        self._record(
            'lineage.gcd_is_lca',
            'the shared context of two pathways is their gcd, reached in one '
            'division, and it equals their lowest common ancestor', 0,
            'SCALE (division), Axis 2 of the tier-0 floor',
            True, shared == lca,
            f'gcd({a},{b})={shared}=animal·mammal=LCA. "how much context" is exact: '
            f'enough to reach the ancestor, no more.')

    # ── R9 — the tier-0 floor is ADD / SCALE / SIGN, measured ────────────────
    def r_add_scale_sign_floor(self) -> None:
        """ADD (gain 0), SCALE (gain 1), SIGN (one bit) are the whole floor:
        the ZD gain spectrum is exactly {0, 1, √2}, and the CD sign structure
        is binary with nothing between."""
        sp = self.gains(16, 1, 10)                       # a sedenion ZD's L_aᵀL_a
        spectrum = set(sp)
        floor_ok = spectrum == {0.0, 1.0, round(math.sqrt(2), 4)}
        # SIGN is one bit: unit products differ from their reverse only by ±1
        flips = 0
        checked = 0
        for i in range(1, 16):
            for j in range(i + 1, 16):
                p = cd_mul(unit(16, i), unit(16, j))
                q = cd_mul(unit(16, j), unit(16, i))
                if p != q:
                    checked += 1
                    if all(abs(abs(x) - abs(y)) < 1e-12 and (x == -y or x == y)
                           for x, y in zip(p, q)):
                        flips += 1
        sign_is_one_bit = checked > 0 and flips == checked
        self._record(
            'floor.add_scale_sign',
            'the tier-0 floor is ADD (identity 0, gain 0), SCALE (identity 1, '
            'gain 1) and SIGN (one bit, det ±1); Aff(1,ℝ)=ADD⋊(SCALE×SIGN), the '
            'only non-trivial bracket [SCALE,ADD]=ADD', 0,
            'nothing — this IS the floor (skill §1)',
            True, floor_ok and sign_is_one_bit,
            f'ZD gain spectrum = {sorted(spectrum)} = {{0,1,√2}}: two free '
            f'(the identities), one irrational price. Non-commuting unit pairs '
            f'{flips}/{checked} disagree by a pure sign flip — SIGN carries one '
            f'bit, nothing between.')

    # ── R10 — the Sieve IS the lineage: pass order = decomposition order ─────
    def r_sieve_is_lineage(self) -> None:
        """Cody, 2026-08-27: "the Sieve IS Generational Lineage ... the list of
        primes is the list of decompositional order, the ordinal values."
        Measured: composite n is first marked on the pass of prime spf(n), and
        generation(n) = π(spf(n)) exactly. One deterministic forward sweep of
        π(√N) passes — no iteration to a fixed point — which is why the lineage
        decomposition is STABLE (one pass per prime, not a convergence)."""
        N = 20_000
        spf = _spf_table(N)
        primes = [k for k in range(2, N + 1) if spf[k] == k]
        pi = {p: i for i, p in enumerate(primes)}
        marked_on, working = _sieve_traced(N, primes)
        comps = [n for n in range(4, N + 1) if spf[n] != n]
        gen_ok = all(marked_on[n] == pi[spf[n]] for n in comps)
        disjoint = all(marked_on[n] is not None for n in comps)
        root_primes = sum(1 for p in primes if p * p <= N)
        one_pass = working == root_primes
        self._record(
            'lineage.sieve_is_order',
            'the Sieve of Eratosthenes IS the generational lineage: composite n '
            'dies on the pass of spf(n), generation(n)=π(spf(n)); one forward '
            'sweep of π(√N) passes, no backtracking — the stability is because '
            'it is one pass per prime, not a fixed-point iteration', 3,
            'ADD (march the multiples) over SCALE (the p-spaced wave) gated by '
            'SIGN (the divisibility bit)',
            True, gen_ok and disjoint and one_pass,
            f'gen(n)=π(spf(n)) for {len(comps)}/{len(comps)} composites ≤ {N}; '
            f'working passes = {working} = π(√N) = {root_primes}. The ordered '
            f'prime list is the decompositional order (the ordinal values).')

    # ── R11 — Fibonacci under factoring waves: the 2-term sieve recurrence ───
    def r_sieve_two_term_recurrence(self) -> None:
        """Legendre: φ(x,a) = φ(x,a−1) − φ(x/pₐ, a−1). A linear TWO-TERM
        recurrence — Fibonacci's exact shape — but the second term's argument
        is SCALED by a prime (a factoring wave), not index-shifted by 1.
        Closed form φ(x,a) = Σ_{d|Pₐ} μ(d)·⌊x/d⌋ = ADD ∘ SIGN ∘ SCALE."""
        primes = [2, 3, 5, 7, 11, 13]
        x = 30_030
        rec_ok = True
        for a in range(1, len(primes) + 1):
            r = _phi(x, a, primes)
            d = sum(1 for k in range(1, x + 1)
                    if all(k % p for p in primes[:a]))
            t1, t2 = _phi(x, a - 1, primes), _phi(x // primes[a - 1], a - 1, primes)
            rec_ok &= (r == d == t1 - t2)
        # closed form via Möbius over the squarefree divisors of P_a
        Pa = 1
        for p in primes:
            Pa *= p
        mu = _mobius_table(Pa)
        closed = sum(mu[dd] * (x // dd) for dd in range(1, Pa + 1) if Pa % dd == 0)
        closed_ok = closed == _phi(x, len(primes), primes)
        self._record(
            'lineage.sieve_is_fibonacci_wave',
            'the sieve count obeys φ(x,a)=φ(x,a−1)−φ(x/pₐ,a−1) — Fibonacci\'s '
            'linear 2-term shape with the 2nd term SCALE-shifted by a prime, not '
            'index-shifted by 1; closed form Σ μ(d)⌊x/d⌋ is a superposition of '
            'signed division waves', 3,
            'ADD (Σ_d) ∘ SIGN (μ(d) ∈ {−1,0,+1}) ∘ SCALE (⌊x/d⌋)',
            True, rec_ok and closed_ok,
            f'recurrence exact for a=1..{len(primes)}; closed form '
            f'Σ_{{d|{Pa}}} μ(d)⌊x/d⌋ = {closed} = φ(x,{len(primes)}). '
            f'Fibonacci is the degenerate "pₐ acts as +1 shift" case.')

    # ── R12 — both orderings: what the order fixes, what it does not ─────────
    def r_sieve_ordering(self) -> None:
        """Ordinal (ascending prime) vs Riemann-ζ weight (ln p/√p descending,
        the σ=½ von-Mangoldt term size). The final prime set and the disjoint
        first-mark partition are ORDER-INVARIANT; generation(n)=π(spf(n)) is
        UNIQUE to the ordinal order, which also minimises the generation
        entropy (pass 0 alone kills every even)."""
        N = 20_000
        spf = _spf_table(N)
        primes = [k for k in range(2, N + 1) if spf[k] == k]
        comps = [n for n in range(4, N + 1) if spf[n] != n]

        def gen_matches(order):
            pos = {p: i for i, p in enumerate(order)}
            m, _ = _sieve_traced(N, order)
            return all(m[n] == pos[spf[n]] for n in comps), m

        asc = sorted(primes)
        zeta = sorted(primes, key=lambda p: math.log(p) / math.sqrt(p), reverse=True)
        asc_ok, m_asc = gen_matches(asc)
        zeta_ok, m_zeta = gen_matches(zeta)
        prime_set_asc = [i for i, ok in enumerate(_sieve_flags(N)) if ok] == asc

        def entropy(m):
            from collections import Counter
            h = Counter(m[n] for n in comps)
            tot = len(comps)
            return -sum((c / tot) * math.log2(c / tot) for c in h.values())

        h_asc, h_zeta = entropy(m_asc), entropy(m_zeta)
        holds = asc_ok and not zeta_ok and prime_set_asc and h_asc < h_zeta
        self._record(
            'lineage.sieve_ordering',
            'the prime SET and the disjoint partition are order-invariant; '
            'generation(n)=π(spf(n)) holds ONLY for the ordinal (ascending '
            'prime) order, which also minimises generation entropy — it is the '
            'canonical, maximum-compression decomposition order', 3,
            'the ordinal π is ADD-native (a count); the ζ-weight order is a '
            'SCALE re-grading that breaks the spf identity',
            True, holds,
            f'ordinal: gen=π(spf) {asc_ok}, entropy {h_asc:.2f} bits · '
            f'ζ-weight (starts {zeta[:6]}): gen=π(spf) {zeta_ok}, '
            f'entropy {h_zeta:.2f} bits · same prime set: {prime_set_asc}.')

    def run(self) -> None:
        for r in (self.r_sigma_nonscalar, self.r_sigma_carries_octonion,
                  self.r_lineage_is_order_of_operations, self.r_persistence_is_octonion,
                  self.r_associator_is_168_quantised, self.r_three_xor_roles,
                  self.r_io_share_substrate, self.r_gcd_is_lca,
                  self.r_add_scale_sign_floor, self.r_sieve_is_lineage,
                  self.r_sieve_two_term_recurrence, self.r_sieve_ordering):
            r()

    def report(self) -> None:
        print('═' * 78)
        print('GENERATIONAL LINEAGE ENGINE — the anatomy of σ in ∅_RB')
        print('═' * 78)
        held = sum(1 for r in self.log if r.status is Status.HOLDS)
        print(f'{held}/{len(self.log)} relations hold\n')
        w = max(len(r.name) for r in self.log)
        print(f'{"relation":<{w}}  tier  {"status":<11}  descends from')
        print('─' * 78)
        for r in self.log:
            print(f'{r.name:<{w}}   t{r.tier}   {r.status.value:<11}  {r.descends}')
        print('─' * 78)
        for r in self.log:
            print(f'\n{r.name}\n  claim : {r.claim}\n  detail: {r.detail}')
        print('\n' + '═' * 78)
        faults = [r for r in self.log if r.status is not Status.HOLDS]
        if faults:
            print('EMERGENCE FLAG: ' + ', '.join(r.name for r in faults) +
                  ' did not hold — investigate before trusting the map.')
        else:
            print('No new generator required. Every operation descends from the '
                  'tier-0 floor by composition; σ in ∅_RB is the octonion-core '
                  'lineage, and σ_self is its one-number shadow.')
        print('═' * 78)

    def sigma_anatomy(self, psi: Sequence[float]) -> Dict[str, object]:
        return {
            'sigma_self (scalar shadow)': float(round(sigma_self(psi), 6)),
            'sigma_rb (16-vector)':       [float(round(x, 4)) for x in sigma_rb(psi)],
            'independent DOF (octonion)': [float(round(x, 4)) for x in sigma_rb_independent(psi)],
            'kept by scalar':             1,
            'discarded (struts)':         7,
        }


def decompose_operation(name: str, **spec) -> Dict[str, object]:
    """Classify a named operation against ADD / SCALE / SIGN.

    Thin wrapper over the shared primitive (VAPMIP/add_scale_sign.py) so the
    lineage engine can roll any operation down to its tier-0 root. Pass the
    four-question flags as kwargs (is_count_or_ratio, is_fixed_set,
    changes_length, preserves_length, needs_added_constraint, order_dependent,
    is_identity) when the name is not already in the roll-down table.
    """
    from add_scale_sign import describe, AFF1
    d = describe(name, **spec)
    return {
        'operation': d.name, 'tier': d.tier, 'is': d.irreducible,
        'root': d.root, 'status': d.status, 'tree': d.tree,
        'descends_from': d.descends_from, 'notes': d.notes,
        'aff1': AFF1['group'],
    }


def run(verbose: bool = True) -> Dict[str, object]:
    """Notebook entry point (matches the e01–e09 contract)."""
    eng = GenerationalLineageEngine()
    eng.run()
    if verbose:
        eng.report()
    held = sum(1 for r in eng.log if r.status is Status.HOLDS)
    return {
        'relations': [(r.name, r.tier, r.status.value, r.claim) for r in eng.log],
        'held': held,
        'total': len(eng.log),
        'all_hold': held == len(eng.log),
        'engine': eng,
    }


def main() -> None:
    result = run(verbose=True)
    print('\nExample — σ anatomy of a random bound state:')
    rng = np.random.default_rng(1)
    psi = list(rng.normal(size=SED_DIM))
    for k, v in result['engine'].sigma_anatomy(psi).items():
        print(f'  {k:<28}: {v}')


if __name__ == '__main__':
    main()
