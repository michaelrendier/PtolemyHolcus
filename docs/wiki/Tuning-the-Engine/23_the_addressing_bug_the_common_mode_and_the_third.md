# 23 — Phase 23: The Addressing Bug, the Common Mode, and the Third Face

**Date:** 2026-07-28  
**Source:** [Tuning-the-Engine.md](../Tuning-the-Engine.md) — seed paper, lines 4393–4648  
**Wiki:** [00_index.md](00_index.md)

---

*Claude Opus 5 — new device bring-up; four translator constructions, all negative; one real bug in `monad.c` found and fixed*

---

### Context

New phone, bare proot-distro Ubuntu 26.04 aarch64. Nothing was installed — no
gcc, no python3 (the `PATH` leaks Termux binaries that resolve for
`command -v` but live outside the rootfs against a different libc). Full
toolchain rebuilt; `.claude/setup_environment.sh` now reproduces it. Two
traps worth carrying: the storage mount CANNOT hold the exec bit (`chmod +x`
silently succeeds and does nothing — binaries must be copied into the rootfs
to run), and Python 3.14 is PEP-668 managed so it is apt, never pip.

---

### THE BUG — `monad_word_coords` could not address 60% of English

```c
uint64_t v = 0;
for (...) v = v * 95ULL + ci;              /* base-95 Horner   */
double seed = fmod((double)v * MONAD_PHI, 1.0);
```

`(double)v` carries a 53-bit mantissa. `95^8 = 6.63e15` fits under
`2^53 = 9.01e15`; `95^9 = 6.30e17` does not. Past `2^53` the low-order bits —
the **only** bits `fmod(.,1.0)` depends on — are gone and seed collapses to
exactly `0.0`. Every word of 8+ characters therefore landed on zero 0 with
`E = D_STAR = 0.246`, the *minimum possible* E, and then lost the
`E > vocab[idx].E` contest at line 464.

Measured on the WordNet build, 101,916 unique tokens:

| len | in corpus | seated | survival |
|-----|-----------|--------|----------|
| 6   | 11547     | 4836   | 41.88%   |
| 7   | 14044     | 47     | 0.33%    |
| 8   | 15013     | 0      | 0.00%    |
| 9+  | ~60000    | 0      | 0.00%    |

62,961 tokens piled onto idx 0. **`philadelphos` sat at z#0 with β=7.552 —
"the deepest word in the field", quoted in this document — because its
address overflowed to zero.** Correctly addressed it is β=0.008995, an
ordinary word. The Voice-of-Mathematics section above should be read with
that in mind: `holcus` was selected on the old addressing.

**The fix** — Fibonacci/Knuth multiplicative hashing, exact in integer
arithmetic. Since `phi = 1 + 1/phi` and v is an integer,
`frac(v*phi) == frac(v/phi)`, so this computes the same quantity the old line
was reaching for, without asking a double to hold the low bits of a big int:

```c
uint64_t h    = v * 0x9E3779B97F4A7C15ULL;   /* round(2^64/phi), wraps */
double   seed = (double)h / 18446744073709551616.0;
```

Verified in Python **before** touching C (`VAPMIP/monad_addressing.py`):

| | old | new |
|---|---|---|
| chi2 (df=99) | 3,833,102 (z=+272,400) | **100.0** (z=+0.1) |
| KS D (crit 0.00426) | 0.6178 NOT UNIFORM | **0.0025 UNIFORM** |
| max pile-up | 62,961 | **14** |
| occupied zeros | 14,173 | **24,590** (expected 24,576) |

Rebuilt: **vocab 13,752 → 24,551, A-edges 690,064 → 1,911,478.** Deepest β
moved from the `philadelphos` artifact to `muster` (z#1894). ~83% of tokens
change address; all 8 corpus bins rebuilt.

**Old bins do not error under the new binary — they silently mislead.** The
state file stores `(word, idx)`, so on load the word map repopulates with
OLD addresses while any unseen word is addressed with the NEW hash. Two
incompatible address spaces coexist in one field.

**STILL OPEN — capacity, and it is now the binding constraint.** 101,916
tokens into N=25,000 zeros collide ~4:1 by pigeonhole. Worse, `E = D_STAR +
seed*(OMEGA_ZS-D_STAR)` with seed now uniform makes **E a frequency-blind
random tiebreaker**: a hapax with a luckier hash evicts a word seen 50,000
times. `dark`, `hot`, `water` and `man` are all currently unseated. Seating
policy should key on frequency/β, not on hash-derived E. Not changed.

Also: `monad.h:9` still claims "surface → *bijective* base-95 Horner int n".
It is not bijective — it wraps at uint64 and lands in N slots. It is a hash,
and always was.

---

### THE COMMON MODE — why every translator attempt failed

`project()` decomposes exactly. Writing each character code as `c_i = cbar + d_i`:

```
project(text,k,sigma) = cbar * W(n,k,sigma)  +  D(content)
                        ^ depends ONLY on length and channel
```

Measured: content is **2-3%** of the signal, `cos(actual, common) = +0.9998`,
and for `zzz` the content term is **exactly 0.0** (all characters equal the
mean — the decomposition proven, not estimated). Consequence, cosine is a
**length detector**:

```
|len(a)-len(b)| = 0 -> mean|cos| = 0.994
                = 5 -> mean|cos| = 0.868
cos(a, aaaaaaaa) = 0.759   <- largest separation in the set, same character
listen/silent    = 0.99965 <- word order barely registers
```

Worse for the engine: `ptol.c` then normalises `v[k] = _x[k]/norm`, which
**divides out cbar** — the only content-carrying scalar — leaving the pure
length kernel. Same-length inputs give near-identical normalised state
(`max|v_hot - v_cat| = 0.018`).

---

### Four constructions, four negatives — all the same cause

1. **DisCoCat** (`ValaQuenta/modules/translator_discocat/`) — pregroup algebra
   6/6 incl. three negative controls; word order +0.9913.
2. **VSA/HDC** (`translator_vsa/`) — identities 4/4; unbind **exactly at
   chance** (0.333); word order +0.9999997, cannot see it at all.
3. **L_(I|O) on the (sigma,theta) tower** (`translator_monad.py`) — **below**
   chance (top1 0.000 vs 0.091). Diagnosed: `beta = theta - alpha` with
   `|theta|/|alpha| = 41.9x` and theta the FIXED spoke grid, so the signature
   is 98% input-independent constant.
4. **L_(I|O) two-trees** (`lio_monad.py`) — rebuild using
   `engines/e06_two_trees.py`'s decomposition (Telperion cos / Laurelin sin at
   EVERY prime, giving a genuine quadrature pair `z_k = T_k + i*L_k`, which
   `ptol.c`'s shell-split cannot form). **Phase is exactly scale-invariant**
   (residual 4.441e-16 under x7.3) because cbar is a SCALE and `arg()` is a
   ratio — this removes the common mode without centering, and without the
   zero-vector degeneracy centering introduces. Crowding 0.990 → 0.634.
   Translation still refuted by its own probe.

**The `hot -> cold` hit is an artifact, and it recurs.** Phase 22 v2 reported
`hot->cold` as its one clean antonym match; `lio_monad.py` reproduced exactly
that pattern. Probing it: `cold` ranks **8th of 12**, below `told`, `word`,
`gold`, `fold`; the top hit is `ice`, the only other 3-letter word. It is
length structure, not semantics. Two unrelated mechanisms singling out the
same pair was the warning.

**Phase 22's resolution hypothesis, tested and rejected for this
construction.** 256x more dimensions (16 → 4096) changes crowding by ~0.03.
Phase 22's collisions were pigeonhole exhaustion of a DISCRETE route alphabet
(~192 routes vs 4000 words); this is a CONTINUOUS common-mode offset. Same
symptom, different mechanism — T32/T64 would not touch it.

**`prime_path` is not a path.** `|z_k|` grows monotonically with prime size,
so `ptol.c`'s spiral `idx[]` is essentially sorting the primes (1–3 inversions
vs sorted order for short inputs). It carries little input-dependent
information. This also confounds the N-holes test below.

---

### 0_RB — what L_(I|O) can and cannot do inside it

**Transfers:** the degenerate-point discipline. `s_rb[k] == s_rb[partner(k)]`
IDENTICALLY (partner is an involution, 16/16; product commutative) — only **8
of 16 entries are independent**. Named and claimed in `translator_monad.py`;
the free 2x is still unclaimed in `ptol.c`. Also the lens equation
`beta = theta - alpha` genuinely IS wiki/52's reverse-definer.

**Does not transfer:** Kaiser-Squires is irreducibly 2D; `s_rb` pairs
cos-at-p_k with sin-at-p_{k+4} — **different primes every time** (2 with 11,
3 with 13, ...), so there is no spin-2 object to invert.

**`J_red x J_blue = d* = 0.24600 conserved at all sigma` (lines 13 and 111)
is FALSE** — re-measured this session at `[-0.0729, +0.1230]`. The claim now
fails in code (`test_d_star_invariant`), not just in a context file. Still
uncorrected in `ptol.c` itself.

---

### THE THIRD FACE — phonetic (new)

The monad had **edges** (real) and **semantic** (nominal only — E comes from
the Horner address of the *spelling*). Phonetic did not exist anywhere.

`VAPMIP/phonetic_face.py` — 16 standard articulatory features (vocalic,
consonantal, voiced, nasal, continuant, strident, labial, coronal, dorsal,
glottal, high, low, back, round, tense, stressed) over CMUdict's 123,455
pronunciations. Not a projection: there are 16 natural feature contrasts and
16 sedenion slots, nothing padded or truncated. A word's vector is the MEAN
feature profile over its phonemes — length-normalised by construction.

**The length bias is gone** (spread 0.0398 across phoneme-count groups, and
non-monotonic; the character encoder ran 0.994 → 0.868 monotonically).

**And it is genuinely phonetic, not orthography in disguise:**

```
eight / ate     cos = +1.0000    EY1 T  vs EY1 T     homophones, spelled differently
though/ tough   cos = +0.7591    DH OW1 vs T AH1 F   near-identical spelling, LOWEST
```

**Etymology carries (Cody's correction, and the data agrees).** Families mean
0.958 vs unrelated controls 0.820; ablaut sharpest, where the sound change IS
the grammar: `drank/drunk` 0.9895, `sing/sang` 0.9474, `tooth/teeth` 0.9459.
With the honest limit: `sing/desk` (unrelated, 0.9177) outscores `foot/feet`
(a real family, 0.9095). Usable when a family is already suspected; not a
family detector alone. An earlier claim of mine that "phonetic similarity is
not meaning similarity" is withdrawn — too strong.

**No `monad_phonetic.bin` is needed.** The face is a pure function, not
accumulated state. A phonetic *field* is the only version that would need a
bin, and the counts rule out the small versions: 39 phonemes = 0.16% of the
field, 1,263 bigrams = 5.1%, 17,468 trigrams = 69.9% (and those would contend
with the ~102k word tokens that already do not fit). If phonetics should ride
in the field, the right move is a **v5 vocab record** carrying `phon[16]`
alongside E/strata — `state.c` already versions the record exactly this way.

---

### New tooling

- `VAPMIP/ptol_state.py` — first reader for PTOL state binaries. Layout
  transcribed from `state.c`'s header comment and cross-checked against every
  `fwrite`. Validated: no trailing bytes, and vocab/edges/word_count/E/β and
  the top A-edge all match `ptolemy -F` and `-w`. Note the A-key packing is
  **15-bit** (`ai = key>>15`, `aj = key&0x7FFF`) — max index 32767; a build
  with N > 32767 would silently alias.
- `VAPMIP/discocat_corpus.py` — A-matrix → DisCoCat verb tensor (Kronecker and
  relational). Noun-vector crowding **0.982 → 0.548**. Caveat: the A-matrix
  stores PAIRS, not (subject,verb,object) TRIPLES, so no construction from it
  fully recovers a transitive verb's argument structure.
- `VAPMIP/monad_addressing.py`, `phonetic_face.py`, `lio_monad.py`,
  `translator_monad.py`; `.claude/setup_environment.sh`.

**Two real PtolC bugs, unfixed:** the Makefile `corpus` target uses `-L`,
which is not a valid flag (`-l`); and `-c <path>` silently no-ops unless the
file ALREADY EXISTS (`find_checkpoint` only returns candidates it can
`fopen`), so the save falls back to the protected default. Pre-create with
`: > path` — `state_load` reports bad magic and continues from ground state.

---

### Changelog

| Date | Change |
|---|---|
| 2026-07-28 | **BUG FIXED**: `monad_word_coords` lost the low bits past 2^53; every word of 8+ chars collapsed to idx 0 with E=D_STAR. ~60k of 102k tokens unaddressable |
| 2026-07-28 | Fix = Fibonacci hashing (`0x9E3779B97F4A7C15`), exact in uint64. chi2 3.8M→100.0, KS 0.618→0.0025, pile-up 62961→14 |
| 2026-07-28 | Rebuilt: vocab 13,752→24,551, A-edges 690k→1.91M. All 8 corpus bins rebuilt. Old bins silently mix two address spaces — do not reuse |
| 2026-07-28 | `philadelphos` at z#0 β=7.552 was an OVERFLOW ARTIFACT, not a field selection. Correctly β=0.008995 |
| 2026-07-28 | Common mode found: `project = cbar*W(n) + D`, content 2-3%; cosine is a length detector; normalisation divides out the only content-carrying scalar |
| 2026-07-28 | Four translator constructions, all negative, all the same cause. `hot->cold` (incl. Phase 22 v2's) shown to be a length artifact |
| 2026-07-28 | Phase 22's under-resolution hypothesis tested and REJECTED for this construction (16→4096 dims changes crowding ~0.03) |
| 2026-07-28 | `arg(z)` is exactly common-mode-immune (4.4e-16); two-trees gives the quadrature pair `ptol.c`'s shell-split cannot |
| 2026-07-28 | 0_RB: only 8 of 16 `s_rb` entries independent (involution 16/16). d*=0.246 invariant re-measured FALSE at [-0.073,+0.123] |
| 2026-07-28 | **NEW: phonetic face** — 16 articulatory features over CMUdict. Length bias gone (spread 0.040). `eight/ate`=1.0000, `though/tough`=0.7591 |
| 2026-07-28 | Etymology carries: families 0.958 vs controls 0.820, ablaut sharpest. Noisy — overlap with unrelated pairs |
| 2026-07-28 | OPEN: seating is frequency-blind (E is a random tiebreaker); `dark`/`hot`/`water`/`man` unseated. Capacity 25,000 vs 101,916 tokens |

*Phase 23 — Claude Opus 5 — 2026-07-28*

---

← [22 — The Translator: Zero-Divisors as Portals, Landmark Navigation](22_the_translator_zero_divisors_as_portals_landmark.md)  
↑ [Tuning the Engine — index](00_index.md)
