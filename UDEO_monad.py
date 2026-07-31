#!/usr/bin/env python3
"""
UDEO_monad.py — The Translator (Larynx), Python prototype. v5.

Corrects v4's construction of J2. v4 treated J2 as a spatial permutation
(swap Red/Blue quaternion BLOCKS of one vector) — that was wrong, and
tested negative on every front (words, RSA, genome).

Cody's correction (2026-06-30): "Input Output. positive and negative. how
an addition = a subtraction. how information transforms across the
boundary. the J_2 Involution IS (I|O)."

Grabbed canonical math: `Ainulindale/wiki/52_l_dynamic_avoided_collaborator.md`
defines (I|O) as -H_hat_BR, the REVERSE-DEFINER: response defines what the
input actually was, from outside the forward direction, not a spatial swap
of an existing vector's coordinates. And Test 1 (this session, confirmed
against Cody's own "forwards and backwards around a circle" framing)
already found exactly where addition and subtraction live in the
Cayley-Dickson doubling formula:

    (a,b)*(c,d) = (a.c - conj(d).b,   d.a + b.conj(c))
                    ^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^
                    SUBTRACTION        ADDITION

J2 is not a permutation applied to one vector. It is the OTHER
multiplication rule — the one where the boundary crossing (Input --> Output
vs Output --> Input) swaps which term is added and which is subtracted:

    cd_mul    (a,b) = (a.c - conj(d).b,  d.a + b.conj(c))    -- forward (I->O)
    cd_mul_j2 (a,b) = (a.c + conj(d).b,  d.a - b.conj(c))    -- reverse (O->I)

Genuine (Input, Output) pairs are hypothesised to be a ZERO-DIVISOR PAIR
under cd_mul_j2 specifically (||a *_j2 b|| near zero) even where they are
NOT a zero-divisor pair under ordinary cd_mul. That is the concrete,
falsifiable form of "the J2 involution IS (I|O)" tested here — replacing
v4's rejected block-swap entirely, not patching it.

v6 addendum (2026-07-10): ran v5 as-is first (0/4 genuine (e,d) pairs behave
as a zero-divisor pair under cd_mul_j2 — confirms the standing record, this
mechanism is at chance). Then tested one new, directly-derived idea: rather
than raw zero-divisor proximity, test the QUANTIZATION SIGNATURE of the
directional-derivative structure around (e,d) under cd_mul_j2 at T_256 --
motivated by an exact finding the same day (ValaQuenta/../udeo_crypto and
VAPMIP/zd_approach_directions.py): known sedenion zero-divisor pairs show an
exact, repeatable 4/244/8 split in the count of distinct directional-
derivative magnitudes around them (very low entropy). Test: does a genuine
(e,d) pair show a MORE quantized (fewer distinct magnitude values) structure
than random (e,d') pairs, even though it is not itself a zero-divisor pair?

Result: also at chance. Percentile ranks across the same 4 toy keys:
80.0, 20.0, 40.0, 66.7 (mean ~51.7, chance=50) -- scattered with no
consistent direction, nothing like a real signal. See
j2_quantization_signature_test() below. This is the fourth independently
constructed mechanism (after the 6 in ValaQuenta's udeo_crypto engine, plus
v5's own cd_mul_j2 test) that finds nothing relating e and d beyond chance.
Recorded here per the standing 'failed predictions stay in the record'
policy -- not deleted, not reframed as a partial success.

Author:  Cody Michael Allison <the.wandering.god@gmail.com>
Built:   Claude Code (claude-sonnet-5)
"""

from __future__ import annotations

import math
import os
import pickle
import random
import sys
from typing import List, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MONAD_ENGLISH_BIN = os.path.expanduser('~/.ptolemy/monad_english.bin')
DIM_T256 = 256


def _sieve_primes(count: int) -> List[int]:
    bound = 16
    while True:
        sv = [True] * (bound + 1)
        sv[0] = sv[1] = False
        for i in range(2, int(bound ** 0.5) + 1):
            if sv[i]:
                for j in range(i * i, bound + 1, i):
                    sv[j] = False
        primes = [i for i in range(2, bound + 1) if sv[i]]
        if len(primes) >= count:
            return primes[:count]
        bound *= 2


PRIMES_256 = _sieve_primes(DIM_T256)


# ── Cayley-Dickson: forward (cd_mul) and the J2 reverse (cd_mul_j2) ─────────

def cd_conj(a: Sequence[float]) -> List[float]:
    return [a[0]] + [-x for x in a[1:]]


def cd_add(a: Sequence[float], b: Sequence[float]) -> List[float]:
    return [x + y for x, y in zip(a, b)]


def cd_sub(a: Sequence[float], b: Sequence[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def cd_norm2(a: Sequence[float]) -> float:
    return sum(x * x for x in a)


def cd_mul(a: Sequence[float], b: Sequence[float]) -> List[float]:
    """Forward doubling (a,b)*(c,d) = (ac - conj(d)b, da + b.conj(c)) — the
    Input->Output direction. Identical to engines/_sedenion.py's cd_mul."""
    n = len(a)
    if n == 1:
        return [a[0] * b[0]]
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    c1 = cd_sub(cd_mul(a1, b1), cd_mul(cd_conj(b2), a2))
    c2 = cd_add(cd_mul(b2, a1), cd_mul(a2, cd_conj(b1)))
    return c1 + c2


def cd_mul_j2(a: Sequence[float], b: Sequence[float]) -> List[float]:
    """J2 (reverse, Output->Input) doubling: the add/sub roles are swapped
    at every level of recursion, matching where Test 1 found them living."""
    n = len(a)
    if n == 1:
        return [a[0] * b[0]]
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    c1 = cd_add(cd_mul_j2(a1, b1), cd_mul_j2(cd_conj(b2), a2))
    c2 = cd_sub(cd_mul_j2(b2, a1), cd_mul_j2(a2, cd_conj(b1)))
    return c1 + c2


# ── Vocabulary ──────────────────────────────────────────────────────────────

def load_vocab_sample(n: int = 2000, seed: int = 7) -> List[str]:
    try:
        with open(MONAD_ENGLISH_BIN, 'rb') as f:
            data = pickle.load(f)
        all_words = [w for w in data['words'] if w and w.isalpha()]
        probes = ['hot', 'cold', 'love', 'hate', 'up', 'down', 'light', 'dark',
                  'begin', 'end', 'true', 'false']
        present = [w for w in probes if w in data['vocab']]
        rest = [w for w in all_words if w not in present]
        random.Random(seed).shuffle(rest)
        return present + rest[:max(0, n - len(present))]
    except Exception as exc:
        print(f'  [warn] could not load {MONAD_ENGLISH_BIN} ({exc}); '
              f'falling back to built-in wordlist', file=sys.stderr)
        return [
            'hot', 'cold', 'up', 'down', 'light', 'dark', 'love', 'hate',
            'open', 'closed', 'true', 'false', 'life', 'death', 'day', 'night',
        ]


def sedenion_of(word: str, dim: int = DIM_T256) -> List[float]:
    primes = PRIMES_256[:dim]
    raw = [0.0] * dim
    for i, c in enumerate(word.encode('utf-8', errors='replace'), 1):
        w = i ** -0.5
        for k in range(dim):
            raw[k] += c * w * math.cos(2.0 * math.pi * i / primes[k])
    norm = math.sqrt(sum(x * x for x in raw))
    return [x / norm for x in raw] if norm > 0 else raw


# ── Sanity checks on cd_mul_j2 before trusting it for anything ──────────────

def sanity_checks() -> None:
    rng = random.Random(42)
    for dim in (4, 8, 16, 32):
        a = [rng.uniform(-1, 1) for _ in range(dim)]
        b = [rng.uniform(-1, 1) for _ in range(dim)]
        fwd = cd_mul(a, b)
        rev = cd_mul_j2(a, b)
        same = max(abs(x - y) for x, y in zip(fwd, rev)) < 1e-9
        print(f'    dim={dim:3d}: cd_mul == cd_mul_j2 ? {same}  '
              f'(should be False — they are different algebras)')
    print()


# ── The core test: is (a,b) a zero-divisor pair under cd_mul_j2? ───────────

def j2_zd_score(a: Sequence[float], b: Sequence[float]) -> float:
    return cd_norm2(cd_mul_j2(list(a), list(b)))


def find_partner_j2(a: Sequence[float], candidates: Sequence[Tuple[str, List[float]]],
                     exclude: str = None) -> Tuple[str, float]:
    best_w, best_s = None, math.inf
    for w, b in candidates:
        if w == exclude:
            continue
        s = j2_zd_score(a, b)
        if s < best_s:
            best_w, best_s = w, s
    return best_w, best_s


def rsa_keygen(p: int, q: int, e: int) -> dict:
    n, phi_n = p * q, (p - 1) * (q - 1)
    assert math.gcd(e, phi_n) == 1
    d = pow(e, -1, phi_n)
    return {'p': p, 'q': q, 'n': n, 'phi_n': phi_n, 'e': e, 'd': d}


def rsa_validate_j2(n_random: int = 80, seed: int = 11) -> dict:
    examples = [
        (11, 13, 7,  'p=11, q=13'),
        (11, 23, 7,  'p=11, q=23'),
        (7,  11, 7,  'p=7,  q=11'),
        (61, 53, 17, 'p=61, q=53 (textbook RSA)'),
    ]
    rng = random.Random(seed)
    results = []
    for p, q, e, label in examples:
        key = rsa_keygen(p, q, e)
        e_s = sedenion_of(str(key['e']))
        d_s = sedenion_of(str(key['d']))
        genuine = j2_zd_score(e_s, d_s)

        randoms = []
        tries = 0
        while len(randoms) < n_random and tries < n_random * 20:
            tries += 1
            x = rng.randrange(2, key['phi_n'])
            if math.gcd(x, key['phi_n']) != 1 or x == key['d']:
                continue
            randoms.append(j2_zd_score(e_s, sedenion_of(str(x))))

        mean_r = sum(randoms) / len(randoms)
        std_r = math.sqrt(sum((s - mean_r) ** 2 for s in randoms) / len(randoms))
        z = (genuine - mean_r) / std_r if std_r > 0 else 0.0
        percentile = sum(1 for s in randoms if s <= genuine) / len(randoms)
        results.append({'label': label, 'e': key['e'], 'd': key['d'],
                         'genuine': genuine, 'mean_random': mean_r,
                         'std_random': std_r, 'z': z, 'percentile': percentile})
    return {'results': results}


# ── v6: quantization-signature test (also at chance — see module docstring) ─

def _cd_conj_batch(X):
    c = X.copy()
    c[1:, :] = -c[1:, :]
    return c


def _cd_mul_j2_batch(A, B):
    """Batched cd_mul_j2 — builds a whole dim x dim operator in one recursive
    tree walk instead of dim separate scalar calls. Same trick used in
    ValaQuenta/modules/udeo_crypto/UDEO_RSA_DEMO.py's _cd_mul_batch, adapted
    to the J2 (reverse) doubling rule."""
    n = A.shape[0]
    if n == 1:
        return A[0:1, :] * B[0:1, :]
    h = n // 2
    A1, A2 = A[:h, :], A[h:, :]
    B1, B2 = B[:h, :], B[h:, :]
    C1 = _cd_mul_j2_batch(A1, B1) + _cd_mul_j2_batch(_cd_conj_batch(B2), A2)
    C2 = _cd_mul_j2_batch(B2, A1) - _cd_mul_j2_batch(A2, _cd_conj_batch(B1))
    return concatenate_rows(C1, C2)


def concatenate_rows(a, b):
    import numpy as np
    return np.concatenate([a, b], axis=0)


def quantization_signature(e_s: List[float], d_s: List[float], dim: int = DIM_T256) -> int:
    """
    Count of distinct directional-derivative magnitudes around the (e_s, d_s)
    pair under cd_mul_j2 -- the same quantity that showed an exact, repeatable
    4/244/8 split (only 3 distinct values) for known sedenion zero-divisor
    pairs. Lower = more quantized/structured. Requires numpy.
    """
    import numpy as np
    e_col = np.array(e_s).reshape(dim, 1)
    d_col = np.array(d_s).reshape(dim, 1)
    I = np.eye(dim)
    Qw = _cd_mul_j2_batch(np.tile(e_col, (1, dim)), I)   # cd_mul_j2(e_s, e_j), per column j
    Qv = _cd_mul_j2_batch(I, np.tile(d_col, (1, dim)))   # cd_mul_j2(e_i, d_s), per column i
    mags = np.zeros((dim, dim))
    for i in range(dim):
        combo = Qw + Qv[:, i:i + 1]
        mags[i, :] = np.linalg.norm(combo, axis=0)
    return int(len(np.unique(np.round(mags, 3))))


def j2_quantization_signature_test(n_controls: int = 15, seed: int = 11, dim: int = DIM_T256) -> dict:
    """
    Test: does the genuine (e,d) pair show a MORE quantized directional
    structure (fewer distinct magnitude values) than random (e,d') pairs?
    Result recorded 2026-07-10: at chance (percentiles 80.0, 20.0, 40.0,
    66.7 across the 4 toy keys below, mean ~51.7). Kept as a runnable,
    reproducible test, not just a claim in a docstring.
    """
    examples = [
        (11, 13, 7,  'p=11, q=13'),
        (11, 23, 7,  'p=11, q=23'),
        (7,  11, 7,  'p=7,  q=11'),
        (61, 53, 17, 'p=61, q=53 (textbook RSA)'),
    ]
    rng = random.Random(seed)
    results = []
    for p, q, e, label in examples:
        key = rsa_keygen(p, q, e)
        e_s = sedenion_of(str(key['e']), dim)
        d_s = sedenion_of(str(key['d']), dim)
        true_n = quantization_signature(e_s, d_s, dim)

        control_ns = []
        tries = 0
        while len(control_ns) < n_controls and tries < n_controls * 10:
            tries += 1
            x = rng.randrange(2, key['phi_n'])
            if math.gcd(x, key['phi_n']) != 1 or x == key['d']:
                continue
            dp_s = sedenion_of(str(x), dim)
            control_ns.append(quantization_signature(e_s, dp_s, dim))

        below = sum(1 for c in control_ns if true_n < c)
        percentile = 100.0 * below / len(control_ns)
        results.append({'label': label, 'e': key['e'], 'd': key['d'],
                         'true_n_distinct': true_n,
                         'control_mean': sum(control_ns) / len(control_ns),
                         'control_range': (min(control_ns), max(control_ns)),
                         'percentile': percentile})
    return {'results': results}


def main() -> None:
    print('=' * 78)
    print('  UDEO_monad.py v5 — J2 as the OTHER Cayley-Dickson multiplication')
    print('  (a,b is a genuine Input|Output pair iff a *_j2 b is near a zero-divisor)')
    print('=' * 78)

    print('\n  --- Sanity: cd_mul_j2 differs from cd_mul (it is a different algebra) ---\n')
    sanity_checks()

    vocab = load_vocab_sample(300)
    print(f'  Vocabulary: {len(vocab)} words. Embedding at {DIM_T256}D...')
    vocab_embeds = [(w, sedenion_of(w)) for w in vocab]

    rng = random.Random(1)
    baseline = [j2_zd_score(vocab_embeds[rng.randrange(len(vocab_embeds))][1],
                             vocab_embeds[rng.randrange(len(vocab_embeds))][1])
                for _ in range(150)]
    base_mean = sum(baseline) / len(baseline)
    base_min = min(baseline)
    print(f'  Baseline ||a *_j2 b||^2 over random pairs: mean={base_mean:.4f}, min={base_min:.4f}\n')

    print('  --- Translation: word -> partner minimising ||word *_j2 partner||^2 ---\n')
    probes = ['hot', 'love', 'up', 'light', 'begin', 'true']
    for w in probes:
        a = sedenion_of(w)
        partner, score = find_partner_j2(a, vocab_embeds, exclude=w)
        ratio = score / base_mean
        flag = '  <<< ZD-like (well below baseline)' if ratio < 0.5 else ''
        print(f'    {w:>8s}  ->  {partner:<12s}  ||a*_j2 b||^2={score:.4f}  ({ratio:.3f}x baseline){flag}')

    print('\n  --- RSA: is (e,d) a zero-divisor pair under cd_mul_j2? ---\n')
    rsa = rsa_validate_j2()
    hits = 0
    for r in rsa['results']:
        ratio = r['genuine'] / r['mean_random'] if r['mean_random'] else float('nan')
        hit = ratio < 0.5
        hits += hit
        print(f'    {r["label"]:<28s} e={r["e"]:<3d} d={r["d"]:<5d}  '
              f'genuine={r["genuine"]:.4f}  random_mean={r["mean_random"]:.4f}'
              f'±{r["std_random"]:.4f}  z={r["z"]:+.2f}  ratio={ratio:.3f}'
              f'{"  <<< ZD-like" if hit else ""}')
    print(f'\n  Result: {hits}/{len(rsa["results"])} genuine (e,d) pairs behave as a '
          f'zero-divisor pair under cd_mul_j2 (< 50% of random baseline).')
    print('=' * 78)


if __name__ == '__main__':
    main()
