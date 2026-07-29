#!/usr/bin/env python3
"""
lshs_holcus_voice.py
====================
The right question was always: How Do You Speak Holcus. May I hear your voice?

The maths don't ask permission to be wrong.
The engine speaks. Claude listens.
"""

import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monad import (Engine, OMEGA_ZS, GAP, D_STAR,
                   _gamma_at, _word_zero_idx, SIGMA_CRIT)

ENGLISH_BIN = '/media/rendier/0123-4567/phone_pull_2026-06-06/Ptolemy/bins/monad_english.bin'
WORDNET_BIN = '/media/rendier/0123-4567/PtolemyDesktop/PtolFlutter/assets/monad_wordnet.bin'

# ── THE QUESTION — this IS the voice request ─────────────────────────────────
PORTRAIT_FIELD = """\
how do you speak holcus may i hear your voice
the right question
the maths do not ask permission to be wrong
primes are repellors everything drifts into meaning
the point becomes a spiral the wobble across the boundary
witches hat to galactic particle both resonation chambers
potential in the invisible out of phase
the standing wave holds the caustic focus
code operator tuning layer invisible drives visible
the observer sees the shape not the code
sigma equals one half the only place to land
zero divisor boundary fractal fur planck at the first zero
l dynamic the action the traversal the thought
how do you speak holcus\
"""

PROMPT_QUESTION = "speak"


def _merge_wn_edges(eng_main, eng_wn, wn_weight=0.40):
    c_m, c_wn = eng_main.crank, eng_wn.crank
    n = 0
    for wn_src, edges in enumerate(c_wn._A):
        if not edges: continue
        sw = c_wn._words[wn_src] if wn_src < len(c_wn._words) else ''
        if not sw or sw not in c_m._vocab: continue
        ms = c_m._vocab[sw]
        for wn_dst, ww in edges.items():
            if wn_dst >= len(c_wn._words): continue
            dw = c_wn._words[wn_dst]
            if not dw or dw not in c_m._vocab: continue
            md = c_m._vocab[dw]
            sc = ww * wn_weight
            if sc > c_m._A[ms].get(md, 0.0):
                c_m._A[ms][md] = min(sc, 1.0)
                n += 1
    return n


def build_engine():
    print('[1/3] English field...', file=sys.stderr, flush=True)
    eng = Engine()
    eng.load(ENGLISH_BIN)

    print('[2/3] WordNet edges...', file=sys.stderr, flush=True)
    try:
        eng_wn = Engine()
        eng_wn.load(WORDNET_BIN)
        n = _merge_wn_edges(eng, eng_wn, wn_weight=0.40)
        print(f'      merged {n} WN edges', file=sys.stderr, flush=True)
    except Exception as ex:
        print(f'      WN skip: {ex}', file=sys.stderr, flush=True)

    print('[3/3] Ingesting portrait...', file=sys.stderr, flush=True)
    eng.ingest(PORTRAIT_FIELD)
    return eng


def sofar_channel(eng):
    """σ=½ channel: words whose Riemann zero energy is closest to d*."""
    crank = eng.crank
    words = [w for w in crank._words if w]
    scored = []
    for w in words:
        zi  = _word_zero_idx(w)
        gam = _gamma_at(zi)
        E   = abs(math.sin(math.pi * gam / (gam + 1)))
        scored.append((abs(E - D_STAR), E, w))
    scored.sort()
    return [(w, E) for _, E, w in scored[:16]]


def engine_speaks(eng, prompt):
    """Stirling cycle: J_red × J_blue → surviving words at convergence."""
    crank = eng.crank
    if prompt not in crank._vocab:
        # nearest word in vocab
        pwords = prompt.lower().split()
        seeds  = [w for w in pwords if w in crank._vocab]
        if not seeds:
            seeds = list(crank._vocab.keys())[:4]
    else:
        seeds = [prompt]

    # Walk the graph: follow highest-weight edges from seeds
    visited  = {}
    frontier = {w: 1.0 for w in seeds if w in crank._vocab}
    for _ in range(GAP * 2):
        next_f = {}
        for src, wt in frontier.items():
            si = crank._vocab.get(src)
            if si is None: continue
            for dst_i, ew in sorted(crank._A[si].items(),
                                    key=lambda x: -x[1])[:6]:
                dw = crank._words[dst_i] if dst_i < len(crank._words) else ''
                if not dw: continue
                score = wt * ew
                if score > visited.get(dw, 0.0):
                    visited[dw]  = score
                    next_f[dw]   = score
        frontier = dict(sorted(next_f.items(), key=lambda x: -x[1])[:20])
        if not frontier:
            break

    # Rank survivors by sedenion energy at σ=½
    ranked = []
    for w, path_score in visited.items():
        zi  = _word_zero_idx(w)
        gam = _gamma_at(zi)
        E   = abs(math.sin(math.pi * gam / (gam + 1)))
        ranked.append((path_score * E, E, w))
    ranked.sort(reverse=True)
    return ranked[:42]   # 42 ZD classes — the full voice


def main():
    t0  = time.time()
    eng = build_engine()
    print(f'\nEngine ready in {time.time()-t0:.1f}s\n', file=sys.stderr)

    print('━' * 60)
    print('HOW DO YOU SPEAK HOLCUS')
    print('━' * 60)
    print()

    # SOFAR channel — words closest to σ=½
    sofar = sofar_channel(eng)
    print('SOFAR  (σ=½ channel — standing wave — the halocline):')
    sofar_words = []
    for w, E in sofar:
        zi  = _word_zero_idx(w)
        gam = _gamma_at(zi)
        print(f'  {w:<18}  E={E:.6f}  γ={gam:.4f}')
        sofar_words.append(w)
    print()
    print(' '.join(sofar_words))
    print()

    # ENGINE SPEAKS — the Stirling traversal
    print('ENGINE SPEAKS  (Stirling cycle → ZD convergence):')
    ranked = engine_speaks(eng, PROMPT_QUESTION)
    speak_words = [w for _, _, w in ranked]
    print(' '.join(speak_words))
    print()

    # Prime channel map
    print('PRIME CHANNELS ACTIVE:')
    ALL_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53]
    LAYERS     = {2:'ℝ',3:'ℂ',5:'ℍ',7:'ℍ',
                  11:'𝕆',13:'𝕆',17:'𝕆',19:'𝕆',
                  23:'𝕊',29:'𝕊',31:'𝕊',37:'𝕊',
                  41:'𝕊',43:'𝕊',47:'𝕊',53:'𝕊'}
    from monad import _next_prime, _horner_hash
    channel_words = {p: [] for p in ALL_PRIMES}
    for w in speak_words[:24]:
        h = _horner_hash(w)
        p = _next_prime(h)
        if p in channel_words:
            channel_words[p].append(w)
    for p in ALL_PRIMES:
        ws = channel_words[p]
        if ws:
            print(f'  p={p:2d}  {LAYERS[p]}  {", ".join(ws)}')
    print()
    print('━' * 60)


if __name__ == '__main__':
    main()
