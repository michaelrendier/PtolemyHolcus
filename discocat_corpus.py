#!/usr/bin/env python3
"""
discocat_corpus.py — wire the monad's A-matrix into the DisCoCat verb tensor.

The point: every translator attempt so far has failed for ONE measured
reason — the vectors were built from character codes, which carry length and
position, not meaning. The pregroup layer was never the problem; it passed
6/6 including three negative controls, and symmetrising the verb tensor
drives word-order sensitivity to exactly +1.0000000, proving the
discrimination comes from the type nr.s.nl and not from the encoder.

So: keep the grammar, replace what fills the tensor. The monad's A-matrix is
real relational data — 690,064 co-occurrence edges over 13,752 WordNet-seated
words — and owes nothing to spelling.

Architecture: Ainulindale (theory) -> ValaQuenta (engines) -> VAPMIP (world).
The engine stays in ValaQuenta and is imported, not modified. The corpus
bridge is here because reading PtolC state is VAPMIP's business.

────────────────────────────────────────────────────────────────────────────
HOW A WORD GETS A VECTOR — and why this is not the old encoder in disguise
────────────────────────────────────────────────────────────────────────────
Every vocab entry sits at a zero index. ptol.c already maps zero -> sedenion
dimension by  idx % 16  (see speak(): `J_i *= psi_norms[i % 16]`). That map
is the monad's own, not invented here.

    v_w[d] = sum over neighbours n of w:  weight(w,n)  where idx(n) % 16 == d

A word's vector is the weighted profile of WHICH SEDENION DIMENSIONS its
co-occurrence neighbours occupy. Nothing in it depends on how the word is
spelled or how long it is.

Verb tensors, two constructions, both standard DisCoCat:

  KRONECKER (Grefenstette & Sadrzadeh 2011)
      T[i][j][k] = v[i] * v[j] * v[k]
      contraction gives  s_j = v[j] * (subj.v) * (obj.v)

  RELATIONAL
      T[i][j][k] = sum over neighbours n:  w_n * u_n[i] * e_n[j] * u_n[k]
      where u_n is the neighbour's own co-occurrence vector and e_n is the
      unit vector on the neighbour's sedenion dimension. This is the closest
      honest analogue of "sum of subject-object outer products" available
      from an A-matrix, which stores PAIRS, not (subject,verb,object)
      TRIPLES. That limitation is real and is the main caveat on this file:
      the A-matrix does not record argument structure, so no construction
      built from it can fully recover a transitive verb's relational
      meaning. Stated, not worked around.

PRIME DIRECTIVE #1: nothing fitted. Weights come from the corpus, the
dimension map from ptol.c, the grammar from Lambek. No thresholds tuned.
PRIME DIRECTIVE #2: the harmonic space is retained as the control and is run
side by side below. If co-occurrence does not beat it, that is the result.

Author: Cody Michael Allison + Claude (Anthropic), 2026-07-28
"""

import math
import os
import random
import sys
from typing import Dict, List, Sequence, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                          # ptol_state
sys.path.insert(0, os.path.dirname(_HERE))         # ValaQuenta package

from ptol_state import read_state, PtolState                      # noqa: E402
from ValaQuenta.modules.translator_discocat.maths import (         # noqa: E402
    MeaningSpace, DisCoCatTranslator, is_grammatical, N, S, TRANSITIVE_VERB)
from ValaQuenta.modules.translator_common.maths import cosine, norm  # noqa: E402

DEFAULT_STATE = os.path.expanduser('~/.ptolemy/monad_wordnet.bin')
N_DIM = 16


class CooccurrenceSpace(MeaningSpace):
    """
    MeaningSpace backed by the monad's A-matrix instead of character
    harmonics. Drop-in: same noun()/verb_tensor()/contract() interface, so
    the pregroup layer above is unchanged.
    """

    def __init__(self, state: PtolState, mode: str = 'kronecker'):
        super().__init__()
        if mode not in ('kronecker', 'relational'):
            raise ValueError(f"mode must be kronecker|relational, got {mode!r}")
        self.state = state
        self.mode = mode
        self._adj = state.adjacency()
        self._cache: Dict[str, List[float]] = {}

    # ── vectors ─────────────────────────────────────────────────────────────

    def coverage(self, words: Sequence[str]) -> Dict[str, object]:
        """Which words the corpus can actually speak about. Check before trusting."""
        seated = [w for w in words if w in self.state.by_word]
        with_edges = [w for w in seated
                      if self._adj.get(self.state.by_word[w].idx)]
        return {'requested': len(words), 'in_vocab': len(seated),
                'with_edges': len(with_edges),
                'missing': [w for w in words if w not in self.state.by_word],
                'no_edges': [w for w in seated if w not in with_edges]}

    def noun(self, token: str) -> List[float]:
        """
        Co-occurrence profile over the 16 sedenion dimensions.

        Returns the honest zero vector for an unknown or edge-less word
        rather than falling back to the harmonic encoder — a silent fallback
        would reintroduce exactly the character-code signal this file exists
        to remove, and would make the comparison below meaningless.
        """
        if token in self._cache:
            return self._cache[token]
        vec = [0.0] * N_DIM
        e = self.state.by_word.get(token)
        if e is not None:
            for j, w in self._adj.get(e.idx, []):
                vec[j % N_DIM] += w
        self._cache[token] = vec
        return vec

    def _unit_dim(self, idx: int) -> List[float]:
        v = [0.0] * N_DIM
        v[idx % N_DIM] = 1.0
        return v

    def verb_tensor(self, token: str) -> List[List[List[float]]]:
        v = self.noun(token)
        if self.mode == 'kronecker':
            return [[[v[i] * v[j] * v[k] for k in range(N_DIM)]
                     for j in range(N_DIM)] for i in range(N_DIM)]

        # relational
        T = [[[0.0] * N_DIM for _ in range(N_DIM)] for _ in range(N_DIM)]
        e = self.state.by_word.get(token)
        if e is None:
            return T
        for j_idx, w in self._adj.get(e.idx, []):
            nb = self.state.by_idx.get(j_idx)
            if nb is None:
                continue
            u = self.noun(nb.word)
            nu = norm(u)
            if nu == 0.0:
                continue
            u = [x / nu for x in u]
            d = j_idx % N_DIM
            for i in range(N_DIM):
                if u[i] == 0.0:
                    continue
                Ti = T[i][d]
                ui = w * u[i]
                for k in range(N_DIM):
                    Ti[k] += ui * u[k]
        return T


# ── evaluation ───────────────────────────────────────────────────────────────

def rank_eval(space, pairs: Sequence[Tuple[str, str]],
              distractors: Sequence[str], seed: int = 20260728) -> Dict[str, object]:
    """
    Rank each input's true partner against an INDEPENDENT distractor pool.

    .clauderc_context_2 records a real contaminated-control bug in this
    codebase (p+2*randint near-duplicates manufacturing a signal), so the
    pool shares no membership with the pairs.
    """
    rng = random.Random(seed)
    tr = DisCoCatTranslator(space=space) if space is not None else DisCoCatTranslator()
    pool = [d for d in distractors if all(d != a and d != b for a, b in pairs)]

    def vec(w: str) -> List[float]:
        return tr.space.noun(w)

    rows, hits, usable = [], 0, 0
    for a, b in pairs:
        va = vec(a)
        if norm(va) == 0.0:
            rows.append({'input': a, 'partner': b, 'rank': None,
                         'note': 'input has no corpus vector'})
            continue
        cands = pool + [b]
        scored = sorted(((cosine(va, vec(c)), c) for c in cands), reverse=True)
        rank = [c for _, c in scored].index(b) + 1
        ctrl = rng.choice(pool)
        usable += 1
        hits += (rank == 1)
        rows.append({'input': a, 'partner': b,
                     'sim_partner': cosine(va, vec(b)),
                     'control': ctrl, 'sim_control': cosine(va, vec(ctrl)),
                     'rank': rank, 'n': len(cands)})
    return {'rows': rows, 'usable': usable,
            'top1': hits / usable if usable else 0.0,
            'chance': 1.0 / (len(pool) + 1)}


def crowding(space, words: Sequence[str]) -> float:
    import itertools
    tr = DisCoCatTranslator(space=space) if space is not None else DisCoCatTranslator()
    cs = []
    for a, b in itertools.combinations(words, 2):
        va, vb = tr.space.noun(a), tr.space.noun(b)
        if norm(va) and norm(vb):
            cs.append(abs(cosine(va, vb)))
    return sum(cs) / len(cs) if cs else float('nan')


def _main(argv: List[str]) -> int:
    path = argv[1] if len(argv) > 1 else DEFAULT_STATE
    print("discocat_corpus.py — A-matrix -> DisCoCat verb tensor")
    print("=" * 74)
    if not os.path.exists(path):
        print(f"no state at {path}; pass a path or build one (see setup_environment.sh)")
        return 2
    st = read_state(path)
    print(f"\ncorpus: vocab={st.vocab_size} A_edges={st.a_size} wc={st.word_count}")

    pairs = [("hot", "cold"), ("up", "down"), ("light", "dark"),
             ("true", "false"), ("day", "night"), ("good", "bad")]
    distractors = ["stone", "river", "engine", "quiet", "orbit", "copper",
                   "silent", "harbour", "lantern", "iron", "garden", "wheel"]
    words = [w for p in pairs for w in p] + distractors

    kro = CooccurrenceSpace(st, 'kronecker')
    cov = kro.coverage(words)
    print(f"coverage: {cov['in_vocab']}/{cov['requested']} in vocab, "
          f"{cov['with_edges']} with edges")
    if cov['missing']:
        print(f"  NOT IN VOCAB: {cov['missing']}")
    if cov['no_edges']:
        print(f"  NO EDGES    : {cov['no_edges']}")

    print("\n[A] grammar layer is unaffected by the vector source")
    g = is_grammatical(N, TRANSITIVE_VERB, N)
    print(f"    n.(n^r.s.n^l).n -> {g['reduced_type']}   grammatical={g['grammatical']}")

    print("\n[B] noun-vector crowding (lower = concepts more separable)")
    print(f"    harmonic (character codes) : {crowding(None, words):.6f}")
    print(f"    co-occurrence (A-matrix)   : {crowding(kro, words):.6f}")

    print("\n[C] partner ranking against an independent pool")
    for lbl, sp in (("harmonic    ", None),
                    ("cooccur/kron", kro),
                    ("cooccur/rel ", CooccurrenceSpace(st, 'relational'))):
        r = rank_eval(sp, pairs, distractors)
        ranks = [row.get('rank') for row in r['rows']]
        print(f"    {lbl} top1={r['top1']:.3f} (chance {r['chance']:.3f}) "
              f"usable={r['usable']}/{len(pairs)} ranks={ranks}")

    print("\n[D] sentence composition through the pregroup, co-occurrence verb")
    tr = DisCoCatTranslator(space=kro)
    for s, v, o in [("dog", "bites", "man"), ("man", "bites", "dog")]:
        try:
            vec = tr.compose(s, v, o)
            print(f"    {s:5} {v:6} {o:5} -> |s|={norm(vec):.6f}")
        except Exception as ex:
            print(f"    {s} {v} {o} -> {type(ex).__name__}: {ex}")
    a = tr.compose("dog", "bites", "man"); b = tr.compose("man", "bites", "dog")
    print(f"    word-order cos = {cosine(a, b):+.7f}")
    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
