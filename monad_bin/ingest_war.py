"""
The 'prime directive' conversations ARE the war corpus discussion (Cody).
Fold the prime-directive primers into ~/.ptolemy/monad_war.bin (which already
carries the Caesar/Gallic parallel text). Back it up first. weight=2.0 —
directives are authoritative.
"""
import os, sys, shutil, time
sys.path.insert(0, "/home/rendier/Projects/ThePlace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus_strip import strip_file
from VAPMIP.monad import Engine

HP = "/home/rendier/Projects/ThePlace/ContextPlease/claude/hist_prime"
WAR_BIN = os.path.expanduser("~/.ptolemy/monad_war.bin")
FILES = [
    "VAPMIP/CONTEXT_PRIMER_2026-05-26_PRIME_DIRECTIVES.txt",
    "VAPMIP/CONTEXT_PRIMER_2026-05-26_SEDENION_ROKO.txt",
    "VAPMIP/docs/primers/PRIMER_2026-05-29_Phase2_to_Phase5.txt",
    "ArdaQuenta/CONTEXT_PRIMER_2026-05-30.txt",
]

bak = WAR_BIN + f".bak-{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(WAR_BIN, bak)
print(f"backup: {bak}  ({os.path.getsize(bak):,} B)")

e = Engine()
e.load_bin(WAR_BIN)
v0, ed0 = e.crank.n, sum(len(d) for d in e.crank._A)
print(f"war bin before: vocab={v0:,}  edges={ed0:,}")

# load_bin protects the path; drop the protection so we can write it back
e._protected_paths.discard(WAR_BIN)

total = 0
for rel in FILES:
    p = os.path.join(HP, rel)
    blob = strip_file(p)
    n = 0
    for para in [c for c in blob.split("\n") if c.strip()]:
        n += e.crank.learn(para, weight=2.0)
    total += n
    print(f"  {rel:58}  {n:>6} words")

v1, ed1 = e.crank.n, sum(len(d) for d in e.crank._A)
print(f"\nwar bin after:  vocab={v1:,} (+{v1-v0:,})  edges={ed1:,} (+{ed1-ed0:,})")
r = e.save_session(WAR_BIN)
print(f"saved: {r}   size {os.path.getsize(WAR_BIN):,} B")

# probe
w = Engine(); w.load_bin(WAR_BIN); c = w.crank
def nbrs(word, k=8):
    i = c._vocab.get(word)
    if i is None:
        return f"{word}: absent"
    es = sorted(c._A[i].items(), key=lambda x: -x[1])[:k]
    return f"{word} (β={c._beta[i]:.3f}): " + ", ".join(f"{c._words[j]}({wt:.2f})" for j, wt in es)
print()
for word in ("directive", "prime", "roko", "war", "caesar", "monad", "spectral", "corpus"):
    print("  " + nbrs(word))
