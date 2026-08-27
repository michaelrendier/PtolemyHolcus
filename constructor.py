#!/usr/bin/env python3
"""
constructor.py — the methodological piece, not another data organ.

Two orthogonal Smith-chart folds acting as SIMULTANEOUS constraints on
word selection, not sequential filters:

  ring1 (semantic/contextual axis) — distance from the sentence's own
    root_vector (the box-kite, already built, Phase 31) to a candidate
    word's context_vector. Smaller = more relationally on-topic.

  ring2 (scale axis) — a candidate word's phonetic complexity (syllable
    count, from monad_phonetic.bin, built 2026-08-27) versus a target
    complexity. Smaller |difference| = better scale fit.

The two axes are genuinely orthogonal in the sense that matters: nothing
about being semantically close to the topic says anything about syllable
count, and nothing about syllable count says anything about topical
relevance — so folding them together as one complex Z = ring1 + i*ring2
and reading |Gamma| is a real two-constraint score, not one signal
dressed up as two.

Honest scope for this test flight: SELECTION only. This does not yet
assemble a grammatical sentence (inflection via monad_grammar.bin,
ordering as a real dependency DAG) — that is explicitly the next,
larger step. What's here: given a seed sentence and a target syllable
complexity, rank real candidate words by how well they satisfy BOTH
constraints at once.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sentence_context import build_sentence_context, neighborhood_corpus, nearest_synsets
from wordnet_boxkite import context_vector
from tools.make_phonetic_bin import read_bin as read_phonetic_bin, syllable_count
from ValaQuenta.modules.scale.maths import mobius_fold

PHONETIC_BIN = os.path.join(os.path.dirname(__file__), 'PtolC', 'monad_phonetic.bin')

_phon_cache = None


def _load_phonetic():
    global _phon_cache
    if _phon_cache is None:
        _, _phon_cache = read_phonetic_bin(PHONETIC_BIN)
    return _phon_cache


def phonetic_complexity(word: str):
    """Syllable count of a word's first cmudict pronunciation, or None if
    the word isn't covered — an honest gap, not padded with a guess."""
    phon = _load_phonetic()
    prons = phon.get(word.lower())
    if not prons:
        return None
    return syllable_count(prons[0])


def construct(seed_text: str, target_syllables: float, Z0: complex = None,
             top_k: int = 8, pool_cap: int = 5):
    """Rank real candidate words by BOTH constraints at once: semantic
    distance from the seed's own root_vector (ring1), and how far a
    candidate's real syllable count sits from target_syllables (ring2).
    Words with no cmudict coverage are skipped, not faked.

    CAUGHT ON THE FIRST RUN, not hidden: feeding raw semantic_dist
    (typically 11-17, a sum across 19 compress_count dimensions) and raw
    ring2 (typically 0-3, a syllable-count gap) into one fold against a
    fixed, unvalidated Z0 let the semantic axis swamp the scale axis
    completely -- two different target_syllables values produced the
    IDENTICAL word ranking. Fixed by min-max normalising both axes to
    [0,1] within the candidate pool actually retrieved for THIS query,
    before folding against a fixed, symmetric Z0=(0.5,0.5) -- this makes
    the two axes comparably weighted regardless of their raw units,
    without hand-picking a magic constant."""
    sbk = build_sentence_context(seed_text)
    if not sbk.leaves:
        return {'error': 'no resolvable words in seed', 'seed': seed_text}

    pool = neighborhood_corpus(sbk.leaves, max_per_relation=pool_cap)
    ranked = nearest_synsets(sbk.root_vector, pool, top_k=top_k * 4)  # over-fetch, phonetic gaps will drop some

    raw = []
    seen_words = set()
    for semantic_dist, synset in ranked:
        for lemma in synset.lemma_names():
            word = lemma.replace('_', ' ')
            if word.lower() in seen_words:
                continue
            comp = phonetic_complexity(word)
            if comp is None:
                continue
            seen_words.add(word.lower())
            ring2 = abs(comp - target_syllables)
            raw.append({'word': word, 'synset': synset.name(),
                        'semantic_dist': semantic_dist, 'syllables': comp,
                        'ring2_scale_gap': ring2})

    if not raw:
        return {'error': 'no candidates with phonetic coverage', 'seed': seed_text}

    sd_vals = [r['semantic_dist'] for r in raw]
    r2_vals = [r['ring2_scale_gap'] for r in raw]
    sd_lo, sd_hi = min(sd_vals), max(sd_vals)
    r2_lo, r2_hi = min(r2_vals), max(r2_vals)
    sd_span = (sd_hi - sd_lo) or 1.0
    r2_span = (r2_hi - r2_lo) or 1.0

    if Z0 is None:
        Z0 = complex(0.5, 0.5)  # centre of the normalised unit square

    results = []
    for r in raw:
        norm_sd = (r['semantic_dist'] - sd_lo) / sd_span
        norm_r2 = (r['ring2_scale_gap'] - r2_lo) / r2_span
        Z = complex(norm_sd, norm_r2)
        G = mobius_fold(Z, Z0)
        results.append({**r, 'norm_semantic': norm_sd, 'norm_scale_gap': norm_r2,
                        'abs_gamma': abs(G)})

    results.sort(key=lambda r: r['abs_gamma'])
    return {
        'seed': seed_text, 'target_syllables': target_syllables, 'Z0': Z0,
        'skipped_no_wordnet': sbk.skipped,
        'n_pool': len(pool), 'n_scored': len(results),
        'top': results[:top_k],
    }


if __name__ == '__main__':
    tests = [
        ("the dog ran quickly through the park", 1.0, "brief/simple target"),
        ("the dog ran quickly through the park", 4.0, "verbose/complex target"),
        ("explain the mathematical structure of the equation", 2.0, "moderate target"),
    ]
    for seed, target, label in tests:
        print(f"\n=== {label}: seed={seed!r} target_syllables={target} ===")
        r = construct(seed, target)
        if 'error' in r:
            print("  ERROR:", r['error'])
            continue
        print(f"  pool={r['n_pool']} scored={r['n_scored']} skipped(no wordnet)={r['skipped_no_wordnet']}")
        for w in r['top']:
            print(f"    {w['word']:<20} syll={w['syllables']}  "
                  f"sem_dist={w['semantic_dist']:>3}({w['norm_semantic']:.2f})  "
                  f"scale_gap={w['ring2_scale_gap']:.1f}({w['norm_scale_gap']:.2f})  "
                  f"|Gamma|={w['abs_gamma']:.4f}   <- {w['synset']}")
