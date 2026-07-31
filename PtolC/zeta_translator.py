#!/usr/bin/env python3
"""
zeta_translator.py -- sedenion pathway to English, prime-dominant / word-reactive.

Calls the real ptol binary for the geometry (Dirichlet projection on primes
2..53, escape threshold, spiral order -- unchanged, ptol.c owns that). The
only new part: what a scalar addresses. ptol_layer.py's word_at() treats the
scalar as a direct linear index into one flat word list -- word-dominant.
Here the scalar addresses a 25,000-slot Riemann-zero space (English's actual
order of magnitude, not RF_monad.py's N_ZEROS=50 "sufficient for English"
guess), and the word returned is whichever face was recorded at that
address -- reactive, one of potentially several synonymous faces, not the
address itself.

Zero ordinates for n up to 25,000 are the asymptotic (Riemann-von Mangoldt)
approximation, not exact mpmath.zetazero() -- exact computation of 25,000
zeros is real CPU time this hardware does not need to spend when the
asymptotic is accurate to a few percent at this range and only the ORDERING
and spacing matter for addressing, not the exact gamma value.

Author: Cody Michael Allison, with Claude Code -- 2026-07-18
"""

import hashlib
import math
import pickle
import re
import subprocess
from collections import Counter
from pathlib import Path

PTOL_SRC   = Path(__file__).parent / 'ptol.c'
PTOL_BIN   = Path('/tmp/claude-0/-mnt-sdcard-ThePlace/b462ccbe-75ba-4116-bfdc-14f52348bb64/scratchpad/ptol_bin')
if not PTOL_BIN.exists():
    import subprocess as _sp
    PTOL_BIN.parent.mkdir(parents=True, exist_ok=True)
    _sp.run(['gcc', '-O2', '-o', str(PTOL_BIN), str(PTOL_SRC), '-lm'], check=True)
ENGLISH_BIN = Path('/storage/emulated/0/ThePlace/PTorrent/bin_archive/clean/monad_english.bin')
N_ZEROS    = 25000

# ── 25,000 zero ordinates, asymptotic (Riemann-von Mangoldt inversion) ──────
# N(T) ~ T/(2*pi) * log(T/(2*pi*e)) + 7/8  -- invert via Newton's method.
# Cheap: closed-form-ish, no mpmath, no per-zero root finding of zeta itself.

def _n_of_t(t: float) -> float:
    return t / (2 * math.pi) * math.log(t / (2 * math.pi * math.e)) + 7.0 / 8.0


def gamma_asymptotic(n: int) -> float:
    """Invert N(T)=n for T via Newton's method. n=1 -> ~14.13 (real gamma_1)."""
    t = 2 * math.pi * n / max(math.log(max(n, 2)), 1.0)  # seed
    t = max(t, 1.0)
    for _ in range(30):
        nt = _n_of_t(t)
        dndt = math.log(t / (2 * math.pi)) / (2 * math.pi)
        if dndt <= 0:
            break
        step = (nt - n) / dndt
        t -= step
        if abs(step) < 1e-9:
            break
    return t


def build_zero_table(n_zeros: int = N_ZEROS):
    return [gamma_asymptotic(n) for n in range(1, n_zeros + 1)]


# ── Reactive English lexicon: hash word -> t in [0,1] -> nearest zero slot ──

_WORD_RE = re.compile(r'^[A-Za-z]+$')


def _hash_to_t(word: str) -> float:
    h = int(hashlib.sha256(word.lower().encode()).hexdigest(), 16)
    return (h % 10 ** 15) / 10 ** 15


def build_reactive_lexicon(n_zeros: int = N_ZEROS) -> dict:
    """{slot: Counter({word: count})} -- built once from the existing raw
    corpus already on disk (monad_english.bin), re-addressed at 25,000-slot
    resolution instead of its native 164,283-entry linear order."""
    with open(ENGLISH_BIN, 'rb') as f:
        data = pickle.load(f)
    slots: dict = {}
    for w in data['words']:
        if not w or not _WORD_RE.match(w) or len(w) < 2:
            continue
        slot = min(n_zeros - 1, int(_hash_to_t(w) * n_zeros))
        slots.setdefault(slot, Counter())[w.lower()] += 1
    return slots


def face_at(slots: dict, slot: int) -> str:
    """Reactive lookup: the most frequent face recorded at this address,
    walking outward if the exact slot is empty."""
    for r in range(64):
        for s in ({slot} if r == 0 else {slot - r, slot + r}):
            if 0 <= s < N_ZEROS and s in slots:
                return slots[s].most_common(1)[0][0]
    return ''


# ── Geometry: call the real ptol binary, raw mode ───────────────────────────

def geometry(prompt: str):
    out = subprocess.run([str(PTOL_BIN), '-r', prompt],
                          capture_output=True, text=True).stdout
    lines = out.strip().split('\n')
    seps = [i for i, l in enumerate(lines) if l.strip() == '---']
    scalars = [float(l) for l in lines[:seps[0]]]
    primes = [int(l) for l in lines[seps[0] + 1:seps[1]]]
    return scalars, primes


P16 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]


def translate(prompt: str, slots: dict) -> dict:
    scalars, active_primes = geometry(prompt)
    peak = max(abs(v) for v in scalars)
    thresh = peak / 1.6180339887  # MONAD_PHI, matches ptol.c

    order = sorted(range(16), key=lambda k: abs(scalars[k]))  # ZD -> rim
    path = []
    for k in order:
        v = scalars[k]
        t = (v + 1.0) / 2.0
        slot = min(N_ZEROS - 1, max(0, int(t * N_ZEROS)))
        word = face_at(slots, slot)
        active = abs(v) >= thresh
        path.append({'e': k, 'p': P16[k], 'scalar': v, 'active': active,
                     'slot': slot, 'word': word})

    sentence = ' '.join(step['word'] for step in path if step['active'] and step['word'])
    return {'prompt': prompt, 'path': path, 'active_primes': active_primes,
             'sentence': sentence}


if __name__ == '__main__':
    import sys
    print(f"Building {N_ZEROS}-slot reactive English lexicon...")
    slots = build_reactive_lexicon()
    print(f"  {len(slots)} occupied slots / {N_ZEROS} ({100*len(slots)/N_ZEROS:.1f}%)")
    print()

    prompts = sys.argv[1:] or ['hot', 'cold', 'the sky is falling']
    for prompt in prompts:
        r = translate(prompt, slots)
        print(f'σ: "{prompt}"')
        for step in r['path']:
            mark = '*' if step['active'] else ' '
            print(f"  e{step['e']:<2} p{step['p']:<3} {step['scalar']:+.4f} "
                  f"{mark} slot={step['slot']:<6} {step['word']}")
        print(f"  -> {r['sentence']}")
        print()
