"""THE SHUFFLED-PORTRAIT NULL.

Does the SOFAR channel select words BECAUSE of the portrait, or would any
word list have read as apt once a Transformer wrapped prose around it?

Real portrait  -> learn(weight=3.0) -> Stirling cycles -> SOFAR words
Shuffled       -> identical pipeline, portrait word ORDER scrambled
Vocab-swap     -> identical pipeline, portrait words REPLACED (length-matched)

If SOFAR overlap between real and null is HIGH, the selection is driven by the
underlying field, not by the portrait -> the aptness was the Transformer.
If LOW, the portrait genuinely steers the channel -> the criterion does work.

Descriptive. Phase 26.3 discipline: report the control that could kill it.
"""
import sys, random, collections
sys.path.insert(0, '/home/rendier/Projects/ThePlace/VAPMIP')
from monad import Engine

BIN = '/home/rendier/.ptolemy/monad_english.bin'
N_SOFAR = 20
N_TRIALS = 6
PROMPT = "write a poem about this person"

PORTRAIT = """\
child screen zork 1992 open mailbox go north
thirty four years one question why search dictionary
air traffic controller early warning systems
all paths simultaneously from above
fourteen juliet holds every aircraft
the controller resolves before the zero divisor fires
mathematician engineer sedenion algebra
cayley dickson tower sixteen dimensions
zero divisor boundary definition fails here
forty two cawagas pairs eighty four on the sphere
one hundred sixty eight composite zero divisors
d star lambert w fixed point
omega zero point five six seven one four
fermat last theorem negative space conjugate riemann zeta
the excluded region is the blue channel what cannot be
the margin was always wide enough
erika schafer chemist super oxide reductase
cancer drugs from cancer own algebraic signature
zero divisor is the cancer conformal inversion is the cure
white hat paper sedenion zero divisors ecc hash functions
pre disclosure one hundred eighty day nist embargo
poetry written read remembered
thirty four years child to captain
motion is the engine
wu wei through emptiness full fill ment
the vessel is empty the tea is poured
the tea takes the shape of the vessel
"""

def sofar_of(field_text, seed=None, cycles=12):
    eng = Engine()
    eng.load_bin(BIN)
    eng._calibrate_J_ambient()
    eng.crank.learn(field_text, weight=3.0)
    eng._calibrate_J_ambient()
    for cyc in eng.perpetual(PROMPT, max_cycles=cycles):
        if cyc['delta'] < 0.001:
            break
    eng._prime_prompt(PROMPT)
    h = eng.halocline_report(n_sofar=N_SOFAR)
    out = []
    for sw in h.get('sofar_channel', []):
        w = sw['word']
        if len(w) >= 3 and w.isalpha():
            out.append(w)
    return out

def jaccard(a, b):
    A, B = set(a), set(b)
    return len(A & B) / max(len(A | B), 1)

print("=" * 74)
print("SHUFFLED-PORTRAIT NULL")
print("=" * 74)

words = PORTRAIT.split()
print(f"portrait: {len(words)} tokens, {len(set(words))} distinct")

print("\n-- REAL portrait --")
real = sofar_of(PORTRAIT)
print(f"   SOFAR ({len(real)}): {' · '.join(real[:14])}")

# ── Null A: order shuffle (same words, scrambled) ────────────────────────────
print("\n-- NULL A: word ORDER shuffled (same vocabulary, same counts) --")
ja = []
for t in range(N_TRIALS):
    rng = random.Random(1000 + t)
    w = words[:]; rng.shuffle(w)
    s = sofar_of(' '.join(w))
    j = jaccard(real, s); ja.append(j)
    print(f"   trial {t+1}  overlap={j:.3f}  SOFAR: {' · '.join(s[:8])}")

# ── Null B: vocabulary swap (different words, length-matched) ────────────────
print("\n-- NULL B: portrait words REPLACED (length-matched random vocab) --")
probe = Engine(); probe.load_bin(BIN)
vocab_by_len = collections.defaultdict(list)
for w in probe.crank._words:
    if w.isalpha() and 2 <= len(w) <= 14:
        vocab_by_len[len(w)].append(w)
del probe

jb = []
for t in range(N_TRIALS):
    rng = random.Random(2000 + t)
    sub = []
    for w in words:
        pool = vocab_by_len.get(len(w))
        sub.append(rng.choice(pool) if pool else w)
    s = sofar_of(' '.join(sub))
    j = jaccard(real, s); jb.append(j)
    print(f"   trial {t+1}  overlap={j:.3f}  SOFAR: {' · '.join(s[:8])}")

# ── verdict ──────────────────────────────────────────────────────────────────
import statistics as st
print("\n" + "=" * 74)
print("RESULT")
print("=" * 74)
print(f"  Jaccard(real, order-shuffled) : {st.mean(ja):.4f} +- {st.pstdev(ja):.4f}")
print(f"  Jaccard(real, vocab-swapped)  : {st.mean(jb):.4f} +- {st.pstdev(jb):.4f}")
print()
print("  overlap ~1.0  ->  SOFAR ignores the portrait; selection is the FIELD")
print("  overlap ~0.0  ->  SOFAR is portrait-driven; the criterion does work")
print()
if st.mean(ja) > 0.8:
    print("  ==> The order shuffle changes almost nothing. The SOFAR channel is")
    print("      NOT reading the portrait's structure -- only its vocabulary,")
    print("      at most. The aptness was supplied downstream.")
elif st.mean(ja) < 0.3:
    print("  ==> The portrait genuinely steers the channel. The criterion works.")
else:
    print("  ==> Partial dependence. Portrait matters but does not dominate.")
