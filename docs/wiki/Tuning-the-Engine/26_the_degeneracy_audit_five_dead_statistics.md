## Phase 26 — The Degeneracy Audit: Five Dead Statistics (2026-08-08)

One question ran through this whole session and earned its keep five times:

> **What does this quantity actually vary over?**

Every failure below is the same disease. A statistic was being used to
discriminate between things it is *constant* on. Not miscalibrated — **dead**.
Cheap to detect, and it killed three standing hypotheses in an afternoon.

Scripts: `.claude/scratchpad/2026-08-08_*/` (persistent scratchpad established
this session; `/tmp` is no longer used).

### 26.1 det(L_q) = N(q)² — the landmark signature was the norm, four times

Phase 22's landmark navigation used each quaternion block's 4×4
regular-representation **determinant** as the signature. Verified numerically:

```
det(L_q) = N(q)²      ratio 1.000000 across random q
spec(L_q) = {±i, ±i}  identical to 6 dp for EVERY unit pure-imaginary q
```

The determinant is a **function of the norm alone**. Every angular degree of
freedom — where meaning lives — was discarded before any comparison. `hot` /
`love` / `up` / `true` collapsing to one bucket was never pigeonholing: the
statistic is **constant on spheres**.

**⚠ This supersedes the "insufficient resolution" diagnosis.** T32 changed
nothing and T64 would also have changed nothing — det = N^k at *every* level of
the Cayley–Dickson tower. The degeneracy is scale-invariant. Climbing the tower
cannot repair a statistic that throws away direction.

Replacement signatures must be **angular**: the assessor/Fano-line address from
`chart_of`, or the spectrum of the off-diagonal coupling block of
M(a,b) = [[L_a, −R_b∘κ], [L_b∘κ, R_a]] — the only part not norm-determined.

### 26.2 The wall is ALTERNATIVITY, not associativity

The bracketing test, built to answer Cody's own worry that "code has less
limitations than actual mathematics." Given a and c = a·b, recover b as a⁻¹·c:

| algebra | left-division error | associator | bracketing disagreement |
|---|---|---|---|
| quaternion | 1.4×10⁻¹⁶ | ~0 | 0 |
| **octonion** | **1.6×10⁻¹⁶** | 1.10 | **113.9%** |
| **sedenion** | **0.52** | 1.30 | 131.5% |
| T32 | 0.74 | 1.37 | — |

Octonions are **not associative** — the two bracketings of a triple product
disagree by a median 114% — yet division is exact to machine precision, because
**alternativity** is exactly the property that makes division well-defined.
Sedenions lose alternativity at the CD step, and division goes with it.

**Consequence:** any code that appears to invert a sedenion operation is
returning a bracketing artifact, and **52% is the size of the artifact.**

**This supports the Phase 22 design rather than refuting it.** It proves the
inverse cannot be algebraic division — which is precisely what "the path through
the ZD holes IS memory" already asserts. Retracing the path is the *correct*
response to non-invertibility.

**Engineering rule:** aggregate addresses **additively** (mean of 16-vectors).
Never aggregate by multiplying sedenions — the result depends on the order and
the parenthesisation the loop happened to use.

### 26.3 ⚠ RETRACTION — the module signal is LEXICAL, not semantic

Two-arm test over the 3,288 `monad_sedenion_addresses.pkl` entries, grouped by
parent module (92 modules, ≥4 members). Null shuffles the name→vector
assignment, 200 shuffles per arm.

```
raw 16D          within 0.8851 | null 0.7425 ± 0.0049  ->  z = +28.99
e₀ projected out within 0.6849 | null 0.3959 ± 0.0093  ->  z = +31.22
e₀+e₈ out        within 0.6882 | null 0.4025 ± 0.0093  ->  z = +30.75
```

Read alone, that is a strong positive, and the e₀ projection **doubles the
effect size** (gap 0.142 → 0.289) rather than creating it.

**Then the lexical-matched null was run, and it does not survive.** Same-module
symbols share long substrings by construction (`skills.config.Path.`). Matching
11,979 same-module pairs 1:1 against cross-module pairs at equal character-
trigram similarity:

```
mean lexical sim : same 0.6495  vs matched cross 0.6501   (matched)
mean address cos : same 0.7226  vs matched cross 0.8068
GAP = -0.0842 ± 0.0029 (SE)     t = -28.8      NEGATIVE

corr(lexical, address)                  = +0.3216
corr(same-module, address)              = +0.2193
PARTIAL corr(same-module, address | lex) = -0.0572
```

**The entire z = +31 was spelling.** Control for lexical similarity and the
module effect vanishes and slightly inverts. corr(lexical, address) = +0.32 says
plainly what the addresses encode: **the address is a function of the name.**

This is the exact objection a reviewer would have raised first, and it would
have been fatal. Found before publication, it is a result.

### 26.4 The Hyperwebster incompatibility — a lossless address CANNOT be a semantic neighbourhood

Sedenion addresses are used here in the Hyperwebster sense: a (start, length)
pointer into an exhaustive enumeration, from which data reconstructs losslessly.
Two walls, and only one is real.

**Wall 1 — it never compresses. Ratio exactly 1.0000.**

```
a-z,   length 1024:  index 4813.3 bits ; data 4813.3 bits   ratio 1.0000
bytes, length 1024:  index 8192.0 bits ; data 8192.0 bits   ratio 1.0000
```

Any bijection between strings and indices preserves length — the counting
argument. The index is not a pointer *to* the data; it **is** the data in
another base. **The character set is not the wall** — text is already a number
in base-256, and that bijection is free.

**Wall 2 — the index metric measures spelling.**

```
cat / car       index distance                 2    UNRELATED
cat / dog                                  1,027    co-hyponym
cat / feline           3,817,157,994,289,027       SYNONYM
big / large                5,646,664,168,650       SYNONYM
```

**The theorem, and it is the real content of the wall:**

> A **lossless canonical address** cannot be a **semantic neighbourhood**.
> Lossless ⟹ injective ⟹ `cat` and `feline` are far apart. Semantic ⟹ synonyms
> are close ⟹ the spelling distinction is collapsed ⟹ lossy. The requirement is
> **contradictory**, not merely hard. No enumeration is clever enough.

**Resolution — two objects, not one:**

| job | tool | property |
|---|---|---|
| identity / reconstruction | Hyperwebster index | lossless, canonical, zero semantics |
| neighbourhood / meaning | co-occurrence geometry (`A`) | lossy, geometry means something |

Semantic neighbourhoods come from **distributional statistics** (Firth 1957),
not enumeration order. The raw material is already in `monad_english.bin`:
164,283 vocab, ~1.9M edges. **Build the 16-D address from `A`, not from the
index.** The wall dissolves by not being crossed.

26.3 is 26.4 measured: those addresses encode spelling because they were built
from names rather than from company kept.

### 26.5 Correction to Phase 25 — the common mode is e₀, not e₀ + e₈

Phase 25 recorded "the common mode is e₀ + e₈." Its own census numbers say
otherwise:

```
mean fixed_point_weight (e₀ alone)  0.6435
mean outside_share      (e₀ + e₈)   0.6537
difference             (e₈ alone)   0.0102   ← ~1%
```

**e₈ carries about 1%.** The doubling generator is nearly empty; the fixed point
does all of it. Independently confirmed by 26.3, where projecting out e₈ in
addition to e₀ changed the within-module cosine by 0.0033 (0.6849 → 0.6882).

**Project out e₀. e₈ is optional.**

### 26.6 The sedenion is exactly one cache line — measured

Sedenion product throughput, 2²⁰ products, fp32, on the i7-8550U + UHD 620
(`intel-opencl-icd` installed this session; verified correct against CPU):

| implementation | time | GFLOP/s |
|---|---|---|
| numpy, untiled | 326 ms | 1.65 |
| C / AVX2, 1 thread | 177 ms | 3.03 |
| C / AVX2, 8 threads | 33 ms | 16.19 |
| **iGPU UHD 620, zero-copy** | **18.5 ms** | **29.09** |
| *RAM ceiling* | *8.1 ms* | *66* |

```
16 × fp32 = 64 bytes = exactly ONE cache line
16 × fp64 = 128 bytes = two lines  ->  3.05 vs 1.61 GFLOP/s
```

Arithmetic intensity is 2.7 FLOP/byte — the product is **memory-bound**, so RAM
speed is the correct ceiling. The iGPU reaches 44% of it; it shares system DRAM,
so zero-copy works and there is no PCIe tax.

**⚠ This cuts against climbing the tower.** T32/fp32 = 2 cache lines, T64/fp32 =
4. The sedenion is the unique cache-line-aligned point on x86-64; going up for
resolution forfeits the alignment that produced the discount.

### 26.7 RSA — enumerating the standard's constraints is a dead end by construction

| probe | measured effect |
|---|---|
| last-digit / last-two-digit filter | **1.000×** — none |
| wheel sieve, all primes ≤ 10⁶ | 24.6× (bounded by ~1/ln B) |
| FIPS 186-5 separation \|p−q\| > 2⁹²⁴ | excludes **3.155×10⁻³⁰** of the space |
| GNFS vs naive | 10³⁰⁵ → 10³⁵ |

The last-digit filter gives *nothing* because q ≡ N·p⁻¹ (mod m) is **determined**
by p — the constraint binds the pair and is automatically satisfied. The
digit-window/Hensel construction gives nothing because each further digit of N
supplies **one equation in two unknowns**, so the tree branches by 10 per digit
and 10³⁰⁹ leaves remain.

> **There is no equation in p alone.** N gives one equation in two unknowns, and
> every derived constraint inherits that. The only way to get an equation in p
> by itself is to factor.
>
> Same shape as 26.1: the diagonal blocks are norm-determined and carry nothing;
> all information lives in the **coupling**, and it cannot be decoupled.

**The meta-result:** every constraint in the RSA standard exists *to remove the
searchable cases*. FIPS separation is set exactly so Fermat needs 2⁸²³ steps and
no tighter. Enumerating those constraints tells you where the weak keys are not
— and what remains is, by construction, the part with no known handle. Partial
digits do break RSA (Coppersmith 1996), but the threshold is **half of p's
bits**: ~154 of 308 decimal digits for RSA-2048. Below half, nothing.

### Change table

| Date | Change |
|---|---|
| 2026-08-08 | **det(L_q) = N(q)²** — Phase 22 landmark signature was the norm; supersedes the resolution diagnosis |
| 2026-08-08 | **Alternativity, not associativity, is the wall** — sedenion division 52% wrong, octonion exact |
| 2026-08-08 | Aggregate addresses additively; never multiplicatively |
| 2026-08-08 | **RETRACTED: the module signal is lexical** — survives shuffling (z=+31), dies under lexical matching (t=−28.8) |
| 2026-08-08 | **Lossless address ⊥ semantic neighbourhood** — provably incompatible; build addresses from `A`, not the index |
| 2026-08-08 | Hyperwebster indexing compresses by exactly 1.0000× — never |
| 2026-08-08 | Phase 25 corrected: common mode is **e₀** (e₈ ≈ 1%) |
| 2026-08-08 | Sedenion fp32 = exactly one cache line; iGPU 29 GFLOP/s, 44% of RAM ceiling |
| 2026-08-08 | Tower-climbing costs cache alignment AND cannot fix norm-degenerate statistics |
| 2026-08-08 | RSA constraint enumeration is a dead end by construction |
| 2026-08-08 | **BLOCKED:** vocabulary run — no per-word 16-D addresses exist (primer §14 step 4) |

*Phase 26 — Claude Opus 5 — 2026-08-08*
