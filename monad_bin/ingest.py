"""
Ingest the stripped primer/TODO prose into a NEW Monad bin —
~/.ptolemy/monad_engineering.bin — leaving the live monad_english.bin
(36 MB) and monad_war.bin untouched. Engineering is its own domain bin,
same as physics / mathematics / python / c.
"""
import os, sys, time
sys.path.insert(0, "/home/rendier/Projects/ThePlace")
from VAPMIP.monad import Engine

HERE = os.path.dirname(os.path.abspath(__file__))
_cands = [os.environ.get("MONAD_CORPUS_ALL"),
          os.path.join(os.path.dirname(HERE), "corpus", "corpus_all.txt"),
          os.path.join(HERE, "corpus_all.txt")]
CORPUS = next(c for c in _cands if c and os.path.exists(c))
OUT = os.path.expanduser("~/.ptolemy/monad_engineering.bin")
WEIGHT = 1.5   # Cody's own detailed engineering descriptions — authoritative

text = open(CORPUS, encoding="utf-8").read()
print(f"corpus: {len(text):,} chars, {len(text.split()):,} whitespace tokens")

e = Engine()
t0 = time.time()
# learn in paragraph chunks so adjacency edges respect sentence order
chunks = [c for c in text.split("\n") if c.strip()]
total = 0
for i, ch in enumerate(chunks):
    total += e.crank.learn(ch, weight=WEIGHT)
    if i % 4000 == 0:
        print(f"  {i:>6}/{len(chunks)} chunks   vocab={e.crank.n:,}   words={total:,}")
dt = time.time() - t0
print(f"\nlearned {total:,} words in {dt:.1f}s")
print(f"vocab (unique addressed words): {e.crank.n:,}")
edges = sum(len(d) for d in e.crank._A)
print(f"A-matrix edges: {edges:,}")
beta = e.crank._beta
print(f"β field: min={min(beta):.4g}  mean={sum(beta)/len(beta):.4g}  "
      f"max={max(beta):.4g}  (>0.5: {sum(1 for b in beta if b>0.5):,} words)")

r = e.save_session(OUT)
print(f"\nsaved: {r}")
print(f"file:  {OUT}  ({os.path.getsize(OUT):,} bytes)")

# ── verify: reload into a fresh Engine, probe ────────────────────────────
print("\n── verify: reload + probe ──")
v = Engine()
v.load_bin(OUT)
print(f"reloaded vocab: {v.crank.n:,}")
for probe in ("monad", "sedenion", "harness", "primer", "ptolemy",
              "engineering", "corpus", "fold", "riemann", "flashlight"):
    hits = v.crank.hear(probe)[:5]
    got = ", ".join(f"{w}({s:.2f})" for _, s, w in hits) if hits else "—"
    print(f"  {probe:14} → {got}")
