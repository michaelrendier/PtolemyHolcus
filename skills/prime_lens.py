"""
skills/prime_lens.py — The Prime Lens

Shared optic for Paper's Hands (Housing) and Mind's Eye (MindEye).
Pure functions. No state. No class. No VAPMIP imports.

Both eyes import this. Neither eye IS this.

The Prime Lens focuses any word or concept to a point on σ=½ via
the prime hash → Riemann zero address mapping. The eye decides what
to point it at. The lens does the focusing.

Two strokes. One lens:

* **Intake stroke** (Paper's Hands eye): Prime Lens pointed OUTWARD
  at the token field. Fovea selector finds highest-J_μ token.
  ZD ring defines the perceptual boundary of the object in focus.

* **Power stroke** (Mind's Eye eye): Prime Lens pointed INWARD
  at the meaning gap (G_me_steer). Callosum coupling (e₁₅) maps
  unfilled psi2 channels back to vocabulary via the same optic.

The lens is the same in both strokes. The pointing direction is the eye's.

:constants:
    D_STAR        — ZD proximity threshold (0.24600)
    FOCUS_RATIO   — in-focus threshold: 1/D_STAR ≈ 4.065
    GAP           — Yang-Mills mass gap / apex seal floor
    SIGMA_CRIT    — critical line σ=½ (the focal plane)
    DIM_NAMES     — sedenion dimension labels e₀..e₁₅

:functions:
    riemann_address(word)           — prime hash → γ_n on σ=½
    zero_dim(word)                  — sedenion dimension (0..15)
    j_mu(E, beta, age)              — J_μ pressure score
    in_focus(J_object, J_context)   — fovea threshold: ratio > 1/D_STAR
    zd_ring(dim)                    — ZD-adjacent dimensions (callosum crossings)
    focus_scores(words, E, beta, age) — J_μ per word list
    split_field(words, scores)      — fovea + context + ZD ring

:engine_note:
    Active engine: ptol.c (PtolC/ptol.c). Python skills import this lens
    and pass field data from the C daemon via socket. A C binding
    (prime_lens.h) is planned — same sieve, same table, same constants.
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple

# ── Constants ─────────────────────────────────────────────────────────────────

D_STAR      = 0.24600                    # Fermat ZD proximity threshold
FOCUS_RATIO = 1.0 / D_STAR              # ≈ 4.065 — in-focus fovea threshold
GAP         = 7.073575e-4               # Yang-Mills mass gap; apex seal floor
SIGMA_CRIT  = 0.5                       # critical line — the focal plane

# Sedenion dimension semantic labels e₀..e₁₅
# Lower 𝕆 (e₀–e₇): linguistic / motor field (Paper's Hands)
# Upper 𝕆 (e₈–e₁₅): visual / spatial field (Mind's Eye)
DIM_NAMES: Tuple[str, ...] = (
    'identity',     # e₀  — coupling quality; who the engine is
    'negate',       # e₁  — negation, refusal, boundary
    'bind',         # e₂  — conjunction, connection
    'name',         # e₃  — noun, reference introduction
    'apply',        # e₄  — verb, action, predication
    'abstract',     # e₅  — adjective, qualification
    'branch',       # e₆  — conditional, alternative paths
    'iterate',      # e₇  — time, sequence, repetition
    'recurse',      # e₈  — pronoun, self-reference, stack
    'allocate',     # e₉  — indefinite article; new reference slot
    'query',        # e₁₀ — question, search, open slot
    'deref',        # e₁₁ — auxiliary, dereference, modal
    'compose',      # e₁₂ — conjunction, function composition
    'parallelize',  # e₁₃ — concurrent, simultaneous activation
    'interrupt',    # e₁₄ — affective break, negative signal
    'emit',         # e₁₅ — output, meta, callosum surface
)

# First 50 non-trivial Riemann zeros (imaginary parts, σ=½)
_ZEROS: Tuple[float, ...] = (
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918720, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831778, 65.112544,
    67.079810, 69.546401, 72.067158, 75.704690, 77.144840,
    79.337375, 82.910381, 84.735492, 87.425275, 88.809111,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
    103.725538, 105.446623, 107.168611, 111.029535, 111.874659,
    114.320220, 116.226680, 118.790782, 121.370125, 122.946829,
    124.256819, 127.516683, 129.578704, 131.087688, 133.497737,
    134.756510, 138.116042, 139.736208, 141.123707, 143.111845,
)

# ── Prime sieve (cap = 2¹⁶ = 65536, matches rotary_monad._PRIME_CAP) ─────────

_PRIME_CAP = 1 << 16
_cap        = _PRIME_CAP + 2
_sv         = bytearray([1]) * _cap
_sv[0] = _sv[1] = 0
for _i in range(2, int(_cap ** 0.5) + 1):
    if _sv[_i]:
        _sv[_i * _i :: _i] = bytearray(len(_sv[_i * _i :: _i]))
_prime_pi: List[int] = [0] * _cap
_cnt = 0
for _k in range(_cap):
    if _sv[_k]: _cnt += 1
    _prime_pi[_k] = _cnt
del _i, _k, _cnt, _cap

# ── Prime hash ────────────────────────────────────────────────────────────────

def _horner(w: str) -> int:
    """Horner accumulation over Unicode codepoints. Identical to rotary_monad._horner."""
    v = 0
    for ch in w:
        v = v * 95 + max(0, ord(ch) - 32)
    return abs(v)

def _next_prime(v: int) -> int:
    v = max(2, int(v) % (_PRIME_CAP + 1))
    while v <= _PRIME_CAP + 1:
        if _sv[min(v, _PRIME_CAP + 1)] or v > _PRIME_CAP:
            return v
        v += 1
    return 65537

_zidx_cache: Dict[str, int] = {}

def word_zero_idx(w: str) -> int:
    """
    Prime hash → Riemann zero index.

    Maps any word (any Unicode) to a 1-based index into the Riemann zero
    sequence. Identical result to ``rotary_monad._word_zero_idx``.

    :param w: Input word.
    :returns: 1-based zero index.
    :rtype: int
    """
    if w in _zidx_cache:
        return _zidx_cache[w]
    p   = _next_prime(_horner(w))
    idx = max(1, _prime_pi[min(p, _PRIME_CAP + 1)])
    _zidx_cache[w] = idx
    return idx

# ── Riemann address ───────────────────────────────────────────────────────────

_gamma_cache: Dict[int, float] = {}

def riemann_address(w: str) -> float:
    """
    Focus a word to its address on the critical line σ=½.

    Returns γ_n — the imaginary part of the n-th non-trivial Riemann zero.
    This is the word's spectral address: the point on the focal plane
    the Prime Lens resolves it to.

    :param w: Input word (any Unicode).
    :returns: γ_n on σ=½.
    :rtype: float
    """
    idx = word_zero_idx(w)
    if idx in _gamma_cache:
        return _gamma_cache[idx]
    if idx <= len(_ZEROS):
        g = _ZEROS[idx - 1]
    else:
        n = float(idx)
        g = 2.0 * math.pi * math.e * n / math.log(n / (2.0 * math.pi * math.e))
    _gamma_cache[idx] = g
    return g

def zero_dim(w: str) -> int:
    """
    Which sedenion dimension (0..15) does this word activate?

    ``word_zero_idx(w) % 16`` — maps to one of the 16 prime basis channels
    {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53}.

    :param w: Input word.
    :returns: Sedenion dimension (0..15).
    :rtype: int
    """
    return word_zero_idx(w) % 16

def dim_name(w: str) -> str:
    """
    Human-readable sedenion dimension label for a word.

    :param w: Input word.
    :returns: Dimension name from ``DIM_NAMES``.
    :rtype: str
    """
    return DIM_NAMES[zero_dim(w)]

# ── Sedenion ZD ring ──────────────────────────────────────────────────────────
# Octonion multiplication table (Fano plane convention).
# Identical to rotary_monad._build_oct_table / _build_sed_table.

def _build_oct() -> List[List[Tuple[int, int]]]:
    t = [[(0, 0)] * 8 for _ in range(8)]
    for i in range(8):
        t[0][i] = (1, i);  t[i][0] = (1, i)
    for i in range(1, 8):
        t[i][i] = (-1, 0)
    for i, j, k in [(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]:
        t[i][j]=(+1,k); t[j][k]=(+1,i); t[k][i]=(+1,j)
        t[j][i]=(-1,k); t[k][j]=(-1,i); t[i][k]=(-1,j)
    return t

_OCT = _build_oct()

def _build_sed() -> List[List[Tuple[int, int]]]:
    t = [[(0, 0)] * 16 for _ in range(16)]
    for i in range(16):
        for j in range(16):
            io, jo = (i - 8 if i >= 8 else i), (j - 8 if j >= 8 else j)
            ih, jh = i >= 8, j >= 8
            if not ih and not jh:
                t[i][j] = _OCT[io][jo]
            elif not ih and jh:
                sg, k = _OCT[jo][io];  t[i][j] = (sg, k + 8)
            elif ih and not jh:
                if jo == 0:  t[i][j] = (1, i)
                else:        sg, k = _OCT[io][jo]; t[i][j] = (-sg, k + 8)
            else:
                if jo == 0:  t[i][j] = (-1, io)
                else:        sg, k = _OCT[jo][io]; t[i][j] = (sg, k)
    return t

_SED = _build_sed()

# ZD ring: for dimension d, the dimensions d' whose product e_d × e_d'
# CROSSES the 𝕆-𝕆 boundary — i.e., lands in the OPPOSITE octonion copy.
# Lower 𝕆: e₀–e₇. Upper 𝕆: e₈–e₁₅.
# These are the callosum-crossing neighbors — the perceptual edge of the
# object at d. The fovea sees the object; the ZD ring sees the boundary.
_ZD_RING: List[List[int]] = []
for _d in range(16):
    _lower  = _d < 8
    _ring   = []
    for _dp in range(16):
        if _dp == _d:
            continue
        _, _prod_k = _SED[_d][_dp]
        # Cross-copy: product lands in opposite 𝕆 from d
        if (_prod_k < 8) != _lower:
            _ring.append(_dp)
    _ZD_RING.append(_ring)
del _d, _dp, _lower, _ring, _prod_k

def zd_ring(dim: int) -> List[int]:
    """
    ZD-adjacent sedenion dimensions for ``dim``.

    Returns dimensions d' such that ``e_dim × e_d'`` crosses the 𝕆-𝕆
    boundary — landing in the opposite octonion copy. These are the
    callosum-crossing neighbors: the perceptual edge (ZD ring) that
    defines the boundary of the object at ``dim``.

    In biological vision: the fovea resolves the object; the ZD ring
    is the edge-detection surround — the boundary where the object
    ends and the context field begins.

    :param dim: Sedenion dimension (0..15). Values outside range wrap mod 16.
    :returns: List of ZD-adjacent dimension indices.
    :rtype: List[int]
    """
    return list(_ZD_RING[dim % 16])

def zd_ring_names(dim: int) -> List[str]:
    """
    ZD-adjacent dimension names for ``dim``.

    :param dim: Sedenion dimension (0..15).
    :returns: DIM_NAMES labels of ZD-adjacent dimensions.
    :rtype: List[str]
    """
    return [DIM_NAMES[d] for d in zd_ring(dim)]

# ── J_μ pressure ──────────────────────────────────────────────────────────────

def j_mu(E: float, beta: float, age: float = 1.0) -> float:
    """
    J_μ pressure score for a word: β × E² × age.

    The semantic pressure a word exerts on the field. High J_μ = deep
    field word with strong activation history. Floored at GAP (Yang-Mills
    mass gap) so no word ever has zero pressure — the vacuum is not empty.

    :param E:    Word energy  — ``1 / (1 + log(zero_idx))``, range (0,1].
    :param beta: Field confidence weight (learned from corpus).
    :param age:  Age decay factor (1.0 = fresh; < 1.0 = scavenged). Default 1.0.
    :returns: J_μ ≥ GAP.
    :rtype: float
    """
    return max(GAP, beta * (E ** 2) * age)

def in_focus(J_object: float, J_context: float) -> bool:
    """
    Is this object sharp enough to justify placing the fovea on it?

    Threshold: J_object / J_context > 1/D_STAR ≈ 4.065.

    The ratio 1/D_STAR is not a tuning parameter — D_STAR = 0.24600 is
    derived from the sedenion ZD structure (Fermat proximity). The focus
    threshold inherits from the ZD boundary geometry.

    :param J_object:  J_μ of the candidate fovea token.
    :param J_context: Mean J_μ of the surrounding context field.
    :returns: True if J_object / J_context exceeds the fovea threshold.
    :rtype: bool
    """
    if J_context < GAP:
        return True
    return (J_object / J_context) > FOCUS_RATIO

# ── Field splitting ───────────────────────────────────────────────────────────

def focus_scores(words:     List[str],
                 E_vals:    List[float],
                 beta_vals: List[float],
                 age_vals:  List[float]) -> List[float]:
    """
    Compute J_μ pressure scores for a list of words.

    Caller (Housing or MindEye) provides the field data. The lens
    computes scores; the eye decides what to do with them.

    :param words:     Word strings (same order as field arrays).
    :param E_vals:    Energy per word.
    :param beta_vals: Beta (confidence) per word.
    :param age_vals:  Age decay per word.
    :returns: J_μ score per word (same order).
    :rtype: List[float]
    """
    return [j_mu(E_vals[i], beta_vals[i], age_vals[i])
            for i in range(len(words))]

def split_field(words: List[str], scores: List[float]) -> Dict:
    """
    Split a token field into fovea, context, and ZD ring.

    The highest-J_μ word is the fovea candidate. If it clears the
    ``in_focus`` threshold against the context mean, the fovea is
    confirmed. The ZD ring of the fovea's sedenion dimension is
    extracted as the perceptual boundary layer.

    :param words:  Word strings.
    :param scores: J_μ per word (same order as words).
    :returns: Dict with keys:

        * ``fovea``          — the word in sharp focus (str or None)
        * ``fovea_J``        — its J_μ pressure score
        * ``fovea_dim``      — its sedenion dimension (0..15)
        * ``fovea_dim_name`` — dimension label from DIM_NAMES
        * ``fovea_gamma``    — its Riemann address γ_n on σ=½
        * ``in_focus``       — bool: clears FOCUS_RATIO threshold
        * ``context``        — remaining words (list, ranked by J_μ)
        * ``context_J_mean`` — mean J_μ of context field
        * ``zd_ring_dims``   — ZD-adjacent dimension indices (boundary)
        * ``zd_ring_names``  — ZD-adjacent dimension labels
    :rtype: dict
    """
    if not words:
        return {
            'fovea': None, 'fovea_J': 0.0, 'fovea_dim': 0,
            'fovea_dim_name': DIM_NAMES[0], 'fovea_gamma': _ZEROS[0],
            'in_focus': False, 'context': [], 'context_J_mean': 0.0,
            'zd_ring_dims': [], 'zd_ring_names': [],
        }

    ranked        = sorted(zip(scores, words), reverse=True)
    fovea_J, fovea_w = ranked[0]
    ctx_pairs     = ranked[1:]
    context       = [w for _, w in ctx_pairs]
    ctx_scores    = [s for s, _ in ctx_pairs]
    ctx_mean      = sum(ctx_scores) / len(ctx_scores) if ctx_scores else GAP

    fovea_dim     = zero_dim(fovea_w)
    ring_dims     = zd_ring(fovea_dim)

    return {
        'fovea':          fovea_w,
        'fovea_J':        fovea_J,
        'fovea_dim':      fovea_dim,
        'fovea_dim_name': DIM_NAMES[fovea_dim],
        'fovea_gamma':    riemann_address(fovea_w),
        'in_focus':       in_focus(fovea_J, ctx_mean),
        'context':        context,
        'context_J_mean': ctx_mean,
        'zd_ring_dims':   ring_dims,
        'zd_ring_names':  [DIM_NAMES[d] for d in ring_dims],
    }
