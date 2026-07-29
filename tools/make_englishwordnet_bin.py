#!/usr/bin/env python3
"""
make_englishwordnet_bin.py — Build English_WordNet combined bin files.

Combines:
  - holcus_monad_english.bin (pickle, 164,283 words, co-occurrence A-matrix)
  - NLTK WordNet typed semantic edges (hypernym, hyponym, antonym, etc.)

Merge rule: repeats deepen context — max(existing, new). No renormalisation.

Two outputs:
  1. holcus_monad_englishwordnet.bin  — pickle, for ptol_layer.py PSVG operator
  2. monad_englishwordnet.bin         — PTOL C binary v3, for eval_checkpoint / monad.py

The combined bin holds the Unclean Lagrangian from two perspectives:
  - Paper's Hands (co-occurrence): the lived pathway, inside the ripple
  - Mind's Eye (WordNet):  the semantic hierarchy, looking DOWN from outside
"""

import pickle, struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BIN_DIR    = '/media/rendier/0123-4567/PTorrent/bin_archive/clean'
SRC_PICKLE = os.path.join(BIN_DIR, 'holcus_monad_english.bin')
OUT_PICKLE = os.path.join(BIN_DIR, 'holcus_monad_englishwordnet.bin')
OUT_PTOL   = os.path.join(BIN_DIR, 'monad_englishwordnet.bin')

# WordNet edge weights — reflect direction on L_(I|O)
# UP toward O (general/abstract) = higher weight
# DOWN toward I (specific/concrete) = slightly lower
# CROSS | boundary (antonym) = medium
WEIGHTS = {
    'hypernym':                  0.85,  # specific → general = I → O
    'derivationally_related':    0.80,  # same point, different grammatical form
    'similar_to':                0.75,  # near-neighbor step on path
    'hyponym':                   0.70,  # general → specific = O → I
    'also_sees':                 0.68,  # lateral near-step
    'part_holonym':              0.65,  # part → whole (toward I)
    'part_meronym':              0.62,  # whole → part
    'member_meronym':            0.60,  # collection → member
    'antonym':                   0.55,  # crosses | boundary
}

def load_english():
    print(f"Loading {SRC_PICKLE} ...")
    with open(SRC_PICKLE, 'rb') as f:
        state = pickle.load(f)
    n     = state['n']
    vocab = state['vocab']   # word → idx
    words = state['words']   # idx → word
    beta  = state['beta']
    E     = state['E']
    A     = state['A']       # list[n] of dict[j → weight]
    age   = state['age']
    print(f"  words={n:,}  edges={sum(len(d) for d in A):,}  word_count={state['word_count']}")
    return state, n, vocab, words, beta, E, A, age

def add_wordnet_edges(vocab, A):
    from nltk.corpus import wordnet as wn

    added = 0
    deepened = 0
    missing = 0

    def add_edge(src_word, tgt_word, weight):
        nonlocal added, deepened, missing
        src = vocab.get(src_word)
        tgt = vocab.get(tgt_word)
        if src is None or tgt is None:
            missing += 1
            return
        existing = A[src].get(tgt, 0.0)
        if weight > existing:
            if existing > 0.0:
                deepened += 1
            else:
                added += 1
            A[src][tgt] = weight  # max, no renorm

    print("Adding WordNet edges ...")

    for synset in wn.all_synsets():
        lemma_names = [l.name().replace('_', ' ') for l in synset.lemmas()]

        # Synset-level relations
        for relation, rel_name in [
            (synset.hypernyms(),       'hypernym'),
            (synset.hyponyms(),        'hyponym'),
            (synset.part_meronyms(),   'part_meronym'),
            (synset.part_holonyms(),   'part_holonym'),
            (synset.member_meronyms(), 'member_meronym'),
            (synset.also_sees(),       'also_sees'),
            (synset.similar_tos(),     'similar_to'),
        ]:
            w = WEIGHTS[rel_name]
            for tgt_synset in relation:
                tgt_names = [l.name().replace('_', ' ') for l in tgt_synset.lemmas()]
                for src in lemma_names:
                    for tgt in tgt_names:
                        add_edge(src, tgt, w)

        # Lemma-level relations
        for lemma in synset.lemmas():
            src = lemma.name().replace('_', ' ')
            for rel_lemma in lemma.antonyms():
                add_edge(src, rel_lemma.name().replace('_', ' '), WEIGHTS['antonym'])
            for rel_lemma in lemma.derivationally_related_forms():
                add_edge(src, rel_lemma.name().replace('_', ' '), WEIGHTS['derivationally_related'])

    total_new = sum(len(d) for d in A)
    print(f"  WordNet edges added={added:,}  deepened={deepened:,}  missing_vocab={missing:,}")
    print(f"  Total A-matrix edges: {total_new:,}")
    return A

def write_pickle(state, A, path):
    out = dict(state)
    out['A'] = A
    print(f"Writing pickle → {path}")
    with open(path, 'wb') as f:
        pickle.dump(out, f, protocol=4)
    size = os.path.getsize(path)
    print(f"  {size/1024/1024:.1f} MB")

def write_ptol_binary(n, vocab, words, beta, E, A, age, path):
    """Write PTOL C binary v3 (little-endian)."""
    import math

    OMEGA_ZS  = 0.5671432904097838
    VERSION   = 3
    word_count = 0
    threshold  = OMEGA_ZS

    # Build flat edge list
    edges = []
    for ai, nbrs in enumerate(A):
        for aj, aw in nbrs.items():
            edges.append((ai, aj, aw))

    vocab_size = len(vocab)
    A_size     = len(edges)

    print(f"Writing PTOL v{VERSION} binary → {path}")
    print(f"  N={n:,}  vocab={vocab_size:,}  edges={A_size:,}")

    with open(path, 'wb') as f:
        # Header
        f.write(b'PTOL')
        f.write(struct.pack('<I', VERSION))
        f.write(struct.pack('<I', n))
        f.write(struct.pack('<I', vocab_size))
        f.write(struct.pack('<I', A_size))
        f.write(struct.pack('<I', word_count))
        f.write(struct.pack('<d', threshold))

        # Beta array [N × double]
        f.write(struct.pack(f'<{n}d', *beta))

        # Age array [N × int32]
        age_int = [int(a) for a in age]
        f.write(struct.pack(f'<{n}i', *age_int))

        # Vocab entries
        for word, idx in vocab.items():
            e_val = E[idx] if idx < len(E) else 0.0
            encoded = word.encode('utf-8')
            wlen = len(encoded)
            f.write(struct.pack('<I', idx))
            f.write(struct.pack('<H', wlen))
            f.write(struct.pack('<d', e_val))
            f.write(struct.pack('<B', 0))   # home_stratum
            f.write(struct.pack('<B', 0))   # gen_stratum
            f.write(struct.pack('<B', 0))   # prime_stratum (v3)
            f.write(encoded)

        # A-matrix edges
        for ai, aj, aw in edges:
            f.write(struct.pack('<I', ai))
            f.write(struct.pack('<I', aj))
            f.write(struct.pack('<d', aw))

    size = os.path.getsize(path)
    print(f"  {size/1024/1024:.1f} MB")

def main():
    state, n, vocab, words, beta, E, A, age = load_english()

    # Deep-copy A to avoid mutating source state
    A_new = [dict(d) for d in A]

    # Add WordNet edges — repeats deepen context (max), no renorm
    A_new = add_wordnet_edges(vocab, A_new)

    # Write pickle (for ptol_layer.py PSVG operator)
    write_pickle(state, A_new, OUT_PICKLE)

    # Write PTOL C binary (for eval_checkpoint / monad.py)
    write_ptol_binary(n, vocab, words, beta, E, A_new, age, OUT_PTOL)

    print("\nDone.")
    print(f"  PSVG operator: <Englishwordnet>  ←  {OUT_PICKLE}")
    print(f"  C binary:      monad_englishwordnet.bin  ←  {OUT_PTOL}")

if __name__ == '__main__':
    main()
