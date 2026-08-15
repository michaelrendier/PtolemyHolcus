"""TEST A — affix pass -> morph relation.
   TEST B — e0 share by WordNet degree (the 2026-08-06 primer's prediction).

No hyperindexing. No NLTK (broken here). Reads monad_englishwordnet.bin (PTOL v3)
and raw CMUdict directly.
"""
import struct, re, collections, sys
import numpy as np

BIN  = '/home/rendier/Projects/ThePlace/PTorrent/bin_archive/clean/monad_englishwordnet.bin'
CMU  = ('/home/rendier/Projects/ThePlace/Ptolemy2/technical/sourcebuilds/'
        'sphinx-source/cmusphinx-code/cmudict/cmudict-0.7b')
sys.path.insert(0, '/home/rendier/Projects/ThePlace/VAPMIP')
import phonetic_face as pf

# ── read PTOL v3 ──────────────────────────────────────────────────────────────
def load_ptol(path):
    f = open(path, 'rb')
    magic = f.read(4)
    ver, N, vsz, asz, wc = struct.unpack('<5I', f.read(20))
    thr, = struct.unpack('<d', f.read(8))
    if ver >= 4: f.read(4)
    beta = np.frombuffer(f.read(N*8), dtype='<f8')
    age  = np.frombuffer(f.read(N*4), dtype='<i4')
    words, idxs, Es = [], [], []
    nextra = 0 if ver < 2 else (2 if ver == 2 else 3)
    for _ in range(vsz):
        idx,  = struct.unpack('<I', f.read(4))
        wlen, = struct.unpack('<H', f.read(2))
        E,    = struct.unpack('<d', f.read(8))
        if nextra: f.read(nextra)
        w = f.read(wlen).decode('utf-8', 'replace')
        words.append(w); idxs.append(idx); Es.append(E)
    raw = f.read(asz*16)
    A = np.frombuffer(raw, dtype=np.dtype([('i','<u4'),('j','<u4'),('w','<f8')]))
    f.close()
    return dict(ver=ver, N=N, words=words, idxs=np.array(idxs), E=np.array(Es),
                beta=beta, age=age, A=A)

print("loading monad_englishwordnet.bin ...")
S = load_ptol(BIN)
print(f"  version {S['ver']}   vocab {len(S['words']):,}   edges {len(S['A']):,}")

# ── CMUdict ───────────────────────────────────────────────────────────────────
cmu = {}
for line in open(CMU, encoding='latin-1'):
    if line.startswith(';;;'): continue
    parts = line.split()
    if len(parts) < 2: continue
    w = parts[0].lower()
    if w.endswith(')'): w = w[:w.rindex('(')]
    cmu.setdefault(w, parts[1:])
print(f"  CMUdict entries: {len(cmu):,}")

def phon_vec(w):
    pr = cmu.get(w)
    if not pr: return None
    vs = [np.asarray(pf.phoneme_vector(p), float) for p in pr]
    return np.mean(vs, 0)

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*72)
print("TEST A — affix pass, and the morph relation it produces")
print("="*72)

SUF = ['ations','ation','ingly','ments','ement','ness','less','able','ible',
       'ally','ings','ing','ers','est','ies','ive','ous','ity','ment','ed',
       'es','er','ly','al','s']
PRE = ['under','inter','anti','over','dis','non','pre','mis','sub','un','re',
       'in','im','de','en']

vocab = set(w for w in S['words'] if w.isalpha() and len(w) > 2)
print(f"alphabetic vocab: {len(vocab):,}")

def strip_once(w):
    for s in sorted(SUF, key=len, reverse=True):
        if w.endswith(s) and len(w)-len(s) >= 3:
            return w[:-len(s)], ('SUF', s)
    for p in sorted(PRE, key=len, reverse=True):
        if w.startswith(p) and len(w)-len(p) >= 3:
            return w[len(p):], ('PRE', p)
    return None, None

# an edge is emitted ONLY when the stripped form is itself in the vocabulary
edges, affix_count, chains = [], collections.Counter(), collections.Counter()
for w in vocab:
    cur, depth = w, 0
    while True:
        r, af = strip_once(cur)
        if r is None: break
        if r in vocab:
            edges.append((w, r, af[0], af[1])); affix_count[af] += 1
            cur = r; depth += 1
            if depth >= 3: break
        else:
            break
    if depth: chains[depth] += 1

roots = {r for _, r, _, _ in edges}
derived = {d for d, _, _, _ in edges}
print(f"morph edges emitted (stripped form IS in vocab): {len(edges):,}")
print(f"  distinct derived forms : {len(derived):,}  ({100*len(derived)/len(vocab):.1f}% of vocab)")
print(f"  distinct roots reached : {len(roots):,}")
print(f"  chain-depth histogram  : {dict(sorted(chains.items()))}")
print(f"\n  top affixes by yield:")
for (kind, af), n in affix_count.most_common(12):
    print(f"    {kind} -{af:<7} {n:>6}")
print(f"\n  sample edges:")
for d, r, k, af in sorted(edges)[:8]:
    print(f"    {d:<18} -> {r:<14} ({k} {af})")

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*72)
print("TEST B — e0 share by WordNet degree")
print("PREDICTION (primer 2026-08-06): function words carry systematically")
print("HIGHER e0 share than content words, because they route through the fixed point.")
print("="*72)

deg = np.zeros(S['N'], dtype=np.int64)
np.add.at(deg, S['A']['i'].astype(np.int64), 1)
np.add.at(deg, S['A']['j'].astype(np.int64), 1)
w2i = {w: int(i) for w, i in zip(S['words'], S['idxs'])}

# phonetic 16-vectors; e0 share = |projection on the common mode|
rows, keep = [], []
for w in vocab:
    v = phon_vec(w)
    if v is None or not np.any(v): continue
    rows.append(v); keep.append(w)
V = np.array(rows)
Vn = V / np.linalg.norm(V, axis=1, keepdims=True)
mu = Vn.mean(0); mu /= np.linalg.norm(mu)
e0share = np.abs(Vn @ mu)
print(f"words with both a phonetic vector and a bin entry: {len(keep):,}")

d = np.array([deg[w2i[w]] if w in w2i else 0 for w in keep])
conn, orph = e0share[d > 0], e0share[d == 0]
print(f"\n  WordNet-CONNECTED (content) : n={len(conn):>6}  mean e0 share = {conn.mean():.4f}  sd {conn.std():.4f}")
print(f"  WordNet-ORPHANED  (pathway) : n={len(orph):>6}  mean e0 share = {orph.mean():.4f}  sd {orph.std():.4f}")
gap = orph.mean() - conn.mean()
se  = np.sqrt(conn.var()/len(conn) + orph.var()/len(orph))
print(f"\n  GAP (orphan - connected) = {gap:+.4f}   SE {se:.4f}   t = {gap/se:+.1f}")
print(f"  DIRECTION PREDICTED: positive (orphans higher)")
print(f"  DIRECTION MEASURED : {'POSITIVE - as predicted' if gap>0 else 'NEGATIVE - prediction fails'}")

# the honest control: is this just word length again?
Lc = np.array([len(w) for w in keep])
print(f"\n  CONTROL — mean length: connected {Lc[d>0].mean():.2f}  orphaned {Lc[d==0].mean():.2f}")
r = np.corrcoef(Lc, e0share)[0,1]
print(f"  corr(length, e0 share) = {r:+.4f}")
