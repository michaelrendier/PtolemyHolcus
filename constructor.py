#!/usr/bin/env python3
"""
constructor.py — the methodological piece, not another data organ.

Two independent Smith-chart folds acting as SIMULTANEOUS constraints on
word construction, not sequential filters:

  ring1 (contextual axis) — RADICAL DISTANCE (context_hash_v2) between the
    seed's combined support set and each candidate's: the log-mass of the
    relations that fire for exactly one of them, computed as
    log(a) + log(b) - 2 log(gcd(a,b)) on the squarefree codes whose prime
    factors ARE which relations fire. Measured 2026-08-27
    (spectral-vs-residual-hash, Tests A/B): of the 19 WordNet relations only
    hyponyms carries information in its COUNT (branching depth — the
    omega-vs-Omega split); the other 18 carry it only in PRESENCE. So the
    18 are a squarefree radical (presence), hyponyms is the one Omega
    channel added as a depth-gap term. Plus a small, FAKED "setting" term
    (_fake_setting): the seed's dominant supersense frame — content-side
    and small; a real situational/deictic model is future work, stubbed
    here like the first-sense WSD stub next to it.

  ring2 (INFORMATION-SCALE axis) — how a candidate word's information
    scale sits relative to a TARGET output scale, where the target is
    derived from the seed's OWN input scale by a conjugate relation.
    Measured 2026-08-27 (spectral-vs-residual-hash, the sum test): adding
    words to a combined shape drives its tail index up and its kurtosis
    toward 1 (alpha 4.4 -> 8.6 over n=1..15) — i.e. more words = more
    RELATIONAL, lower information density per word ("narrative / long
    winded"); few words = the anomaly intact, incompressible detail per
    word ("dissertational / myopic focus"). Detail and relation are a
    CONJUGATE pair (Fourier-dual, an uncertainty relation): sharp in
    meaning-space <=> diffuse in relational-space. So the useful default
    is output_scale = 1 - input_scale (a terse dense seed -> a narrative
    response that unpacks it; a rambling seed -> a dissertational response
    that distills it). `register` in [0,1] tunes this: 0 = full conjugate,
    1 = matched register. A candidate's own info scale is 0.5*(syllable
    length, phonetic — the ORIGIN, corr ~ -0.04 with context) + 0.5*
    context_hash_v2.gamma_radial (the 'everything fires once' fold, which
    already carries both relational breadth and hyponym depth). Input and
    output scale ride the SAME fold, so they sit on one axis. 0 =
    dissertational, 1 = narrative.

    NOT independently validated against real dialogue the way the
    Flesch-Kincaid formula is — the conjugate default is a hypothesis
    about useful register, like Z0=(0.5,0.5) is a reasonable-but-unchecked
    anchor choice.

Folding ring1 + i*ring2 against Z0 and reading |Gamma| is still a real
two-constraint score — the constraints are genuinely independent (context
"what to say" vs information scale "how densely") — geometry is field
(context) + origin (phonetic, folded into the scale term), not two
symmetric rings.

Honest scope for this test flight: SELECTION only. This does not yet
assemble a grammatical sentence (inflection via monad_grammar.bin,
ordering as a real dependency DAG) — that is explicitly the next,
larger step. What's here: given a seed sentence (and optionally an
explicit register or syllable target), rank real candidate words by how
well they satisfy BOTH constraints at once.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sentence_context import build_sentence_context, neighborhood_corpus
from wordnet_boxkite import context_vector, RELATION_METHODS
from tools.make_phonetic_bin import read_bin as read_phonetic_bin, syllable_count
from ValaQuenta.modules.scale.maths import mobius_fold
from context_hash_v2 import (
    code_omega, code_depth_exponent, gamma_radial,
    omega_of_indices, log_code_of, radical_distance, fold_log_code, LN_P_HYP,
)

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


_HYPONYMS_IDX = RELATION_METHODS.index('hyponyms')


def useful_context_vector(vec):
    """The 'useful' slice of a 19-D context_vector: PRESENCE (0/1) for the
    18 relations whose supersense information sits entirely in whether they
    fire, and the raw COUNT for hyponyms — the one relation (measured
    2026-08-27, spectral-vs-residual-hash Tests A/B) whose branching DEPTH
    carries extra information. omega vs Omega: 18 relations are omega-type
    (presence), hyponyms is Omega-type (multiplicity)."""
    return [vec[i] if i == _HYPONYMS_IDX else (1 if vec[i] > 0 else 0)
            for i in range(len(vec))]


def _useful_root(leaves):
    """Componentwise sum of the leaves' useful_context_vectors — the seed's
    own combined useful context (PW3 additivity, same law as root_vector,
    applied to the useful slice)."""
    acc = [0] * len(RELATION_METHODS)
    for leaf in leaves:
        for i, v in enumerate(useful_context_vector(leaf['vector'])):
            acc[i] += v
    return acc


def _fake_setting(leaves):
    """FAKED situational 'setting': the seed's dominant supersense frame as
    a normalised {lexname: weight} map. Content-side (it comes from the
    specific input words, not the fixed relation machinery) and small. A
    real deictic / discourse-situation model is future work — this is a
    stub sitting next to the first-sense WSD stub."""
    from collections import Counter
    c = Counter(leaf['synset'].lexname() for leaf in leaves)
    total = sum(c.values()) or 1
    return {k: n / total for k, n in c.items()}


def _setting_gap(setting, synset):
    """0.0 if the candidate's supersense IS the seed's whole frame, rising
    toward 1.0 as it falls outside it."""
    return 1.0 - setting.get(synset.lexname(), 0.0)


def _squash(n, mid):
    """A count -> [0,1], n/(n+mid): ~0 for n<<mid, 0.5 at n=mid, ->1 for
    n>>mid. Used to put word-counts and syllable-counts on a common
    bounded axis without a hard cap."""
    return n / (n + mid) if n > 0 else 0.0


def _seed_parts(u_root):
    """(present relation indices, hyponym depth) for the seed's combined
    useful context — the shape context_hash_v2 needs to fold a whole seed
    the same way it folds one synset."""
    present = [i for i in range(len(RELATION_METHODS))
               if i != _HYPONYMS_IDX and u_root[i] > 0]
    return present, u_root[_HYPONYMS_IDX]


def _input_scale(leaves, u_root):
    """The seed's own information scale in [0,1]. 0 = dissertational /
    myopic focus (few words, context concentrated — anomaly intact); 1 =
    narrative / long winded (many words, context spread). Uses the same
    'everything fires once' fold as the candidates (fold_log_code), so
    input and output scale sit on ONE axis."""
    present, hyp = _seed_parts(u_root)
    ctx = (fold_log_code(log_code_of(present, hyp)) + 1.0) / 2.0
    breadth = _squash(len(leaves), mid=6.0)
    return 0.5 * ctx + 0.5 * breadth


def construct(seed_text: str, target_syllables: float = None, Z0: complex = None,
             top_k: int = 8, pool_cap: int = 5, setting_weight: float = 3.0,
             register: float = 0.0, echo: int = 0,
             basin_k: int = 40, topic: str = None):
    """Rank real candidate words by BOTH constraints at once: useful
    contextual distance from the seed's combined context (ring1), and how
    a candidate's information scale sits vs a TARGET output scale (ring2).

    The output scale is derived from the seed's own INPUT scale
    (_input_scale) by a conjugate relation:
        output_scale = (1 - register) * (1 - input_scale)
                     +       register  *      input_scale
    register=0 -> full conjugate (terse seed -> narrative reply, and vice
    versa); register=1 -> matched register. If `target_syllables` is given
    it overrides: output_scale = 1 - squash(target_syllables), i.e. a short
    explicit target asks for narrative-scale words.

    Words with no cmudict coverage are skipped, not faked.

    CAUGHT ON THE FIRST RUN, not hidden: feeding a raw contextual sum
    (18 presence bits + the hyponyms count + the setting term) and a raw
    scale gap into one fold against a fixed, unvalidated Z0 let the context
    axis swamp the scale axis -- two different targets produced the
    IDENTICAL ranking. Fixed by min-max normalising both axes to [0,1]
    within the pool retrieved for THIS query before folding against
    Z0=(0.5,0.5)."""
    sbk = build_sentence_context(seed_text)
    if not sbk.leaves:
        return {'error': 'no resolvable words in seed', 'seed': seed_text}

    pool = neighborhood_corpus(sbk.leaves, max_per_relation=pool_cap,
                               basin_k=basin_k, basin_topic=topic)

    # ring1: RADICAL DISTANCE (context_hash_v2) between the seed's support
    # set and each candidate's -- the log-mass of the relations that fire
    # for exactly one of them -- plus the one Omega channel (hyponym-depth
    # gap) and the small faked 'setting' term.
    #
    # `pool` is the leaves' combined neighborhood under set-UNION (the
    # SUPPORT -- which synsets); `seed_omega` is that same neighborhood as
    # a squarefree code whose prime factors ARE which relations fire. Same
    # fold, two semirings -- which is why context-building and semantic
    # neighborhood sit next to each other here, not as two organs.
    u_root = _useful_root(sbk.leaves)
    setting = _fake_setting(sbk.leaves)
    seed_present, seed_hyp = _seed_parts(u_root)
    seed_omega = omega_of_indices(seed_present)

    def _ring1(s):
        rd = radical_distance(seed_omega, code_omega(s))
        hd = abs(seed_hyp - code_depth_exponent(s)) * LN_P_HYP
        return rd + hd + setting_weight * _setting_gap(setting, s)

    ranked = sorted(((_ring1(s), s) for s in pool),
                    key=lambda t: t[0])[:top_k * 4]  # over-fetch; phonetic gaps drop some

    # ring2: relate the seed's INPUT scale to a TARGET OUTPUT scale by the
    # conjugate (narrative <=> dissertational) relation, then score each
    # candidate by how close its own info scale sits to that target.
    in_scale = _input_scale(sbk.leaves, u_root)
    if target_syllables is not None:
        out_scale = 1.0 - _squash(target_syllables, mid=2.5)
    else:
        out_scale = (1.0 - register) * (1.0 - in_scale) + register * in_scale

    raw = []
    seen_words = set()
    for semantic_dist, synset in ranked:
        # context-side info scale from context_hash_v2's 'everything fires
        # once' fold: gamma_radial in (-1,1), <0 dissertational, >0 narrative.
        ctx_scale = (gamma_radial(synset) + 1.0) / 2.0
        for lemma in synset.lemma_names():
            word = lemma.replace('_', ' ')
            if word.lower() in seen_words:
                continue
            comp = phonetic_complexity(word)
            if comp is None:
                continue
            seen_words.add(word.lower())
            syll_term = 1.0 - _squash(comp, mid=2.5)     # short -> narrative
            cand_scale = 0.5 * syll_term + 0.5 * ctx_scale
            ring2 = abs(cand_scale - out_scale)
            raw.append({'word': word, 'synset': synset.name(),
                        'semantic_dist': semantic_dist, 'syllables': comp,
                        'cand_info_scale': cand_scale, 'ring2_scale_gap': ring2})

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
        'register': register,
        'input_scale': in_scale, 'output_scale': out_scale,
        # echo LINEAGE of this content through the monad. A loop driver
        # feeding this output back as the next seed passes echo+1; the
        # monad hears its own output via monad_english_io.hear(text, echo),
        # which is a NO-OP once echo >= ECHO_CAP (=5) -- feedback broken.
        # Anything from outside (user turn, fetched page) is echo 0.
        'echo': echo,
        'skipped_no_wordnet': sbk.skipped,
        'n_pool': len(pool), 'n_scored': len(results),
        'top': results[:top_k],
    }


if __name__ == '__main__':
    # (seed, kwargs, label) — the conjugate default vs matched register,
    # and the explicit-syllable override.
    tests = [
        ("explain the equation",
         {}, "terse seed -> conjugate wants NARRATIVE"),
        ("explain the equation",
         {'register': 1.0}, "terse seed -> matched register wants dissertational"),
        ("the meandering old river wound slowly past the quiet sleepy village "
         "while the children wandered along the muddy bank looking for frogs",
         {}, "rambling seed -> conjugate wants DISSERTATIONAL"),
        ("explain the mathematical structure of the equation",
         {'target_syllables': 2.0}, "explicit syllable target overrides"),
    ]
    for seed, kw, label in tests:
        print(f"\n=== {label} ===\n  seed={seed!r}  kwargs={kw}")
        r = construct(seed, **kw)
        if 'error' in r:
            print("  ERROR:", r['error'])
            continue
        print(f"  input_scale={r['input_scale']:.2f}  output_scale={r['output_scale']:.2f}"
              f"  (register={r['register']})  pool={r['n_pool']} scored={r['n_scored']}")
        for w in r['top']:
            print(f"    {w['word']:<18} syll={w['syllables']} "
                  f"cand_scale={w['cand_info_scale']:.2f}  "
                  f"ctx({w['norm_semantic']:.2f}) scale_gap({w['norm_scale_gap']:.2f})  "
                  f"|Gamma|={w['abs_gamma']:.4f}  <- {w['synset']}")
