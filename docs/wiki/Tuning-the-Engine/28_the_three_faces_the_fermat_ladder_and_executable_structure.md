## Phase 28 — The Three Faces, the Fermat Ladder, and Structure as a Fast Path (2026-08-18)

*Claude Opus 5 — a long session. Corpus measurement, the prime hashing algorithm,
`monad_identity.bin`, and four benchmarked speedups. Several retractions, one of
them mine three times over.*

---

### Context

A session that started as "catch up on last night's primer" and ran the length of
the stack: the harness, the corpus, the hashing algorithm, the binary format, and
back down to the algebra. What follows is organised by what was **measured**, and
the retractions are kept rather than tidied away.

---

### 1. The harness was broken at HEAD, and is now 124 relations

`rotary_rerun_monad.py` crashed on `Intention.shared_with` — the operators had
moved to `Reading` when Intention became a state, and `Handoff`/`Satisfaction`
were referenced by `check_handoff` but existed nowhere. 27 relations had been
unreachable since `f91aa5d`.

Now: **124 relations, 122 hold, 1 FAULT, 1 degenerate, 0 untested** — the fault
and the degenerate are the ones `main()` plants deliberately.

Added since: the two gates, the correctness referent, `Unpack`, the annihilation
gradient, continuity, evaluation, and executable structure. Groups now run
**isolated**, so a break costs its own relations and nothing else — the same
fault-isolation property the seven kites have, at the harness level. Proved by
injecting the original `AttributeError`: it now costs 3 relations while the other
101 still run.

---

### 2. Three kinds of wrong

```
CODE fault    the check did not run.               The claim is UNJUDGED.
MATHS fault   both sides measured, they disagree.  The claim is false.
METHOD error  code correct, maths correct.         Invisible to both.
```

Gate 1 **cannot** catch a design error, and that is correct behaviour —
correctness is about what is written. Method errors surface downstream as a
parting that should have been impossible, and **the detector is the clarifier
failing**: a natural divergence is recoverable, an unnatural one is not, because
the method destroyed the distinction upstream.

Found live in `monad.py`: `_horner_hash` clamps digits from below only, so
`U+200B` yields coefficient 8171 in a base-95 positional system and `'​'`
collides with `'v!'`. Not a code fault, not a maths fault — a tier-0 object fed to
a tier-1 operation.

---

### 3. The letter cap is 71, not 313 — and the ladder is Fermat

`313` is the **65th** prime. It is the sieve's regime boundary (last prime
claiming anything new at N=1e5), not the letter cap. `monad.py` already had it
right: PRIMES and RIEMANN_ZEROS both hold 20 entries ending at **71**.

But 313 was not arbitrary either, and the reason is better than the one it was
given:

```
F_n = 2^(2^n) + 1  IS the Cayley-Dickson doubling index
F_0 = 3    ranking     F_2 = 17   GROUPING
F_1 = 5    factors     F_3 = 257  division      F_4 = 65537  (outside)

3 x 5 x 17 x 257 = 65535 = 2^16 - 1     <- the sedenion dimension
```

Any cap in `[257, 65537)` admits exactly the four generations the box kite has.
A letter's prime **carries its generation**, read off its Fermat band.

And the counts close: the 15 nonempty subsets of `{3,5,17,257}` are the 15 points
of PG(3,2) (verified against `skeleton_counts`), and forcing the division bit
leaves `2^3 - 1 = 7` — the struts.

**Budget consequence:** with the cap at 71, 42 assessors = 94 digits and fit under
100, where at 313 they were 112 and did not. The cap error was costing the
encoding its entire assessor layer.

---

### 4. The 15 are EDGES, not places

The 15 "points" of PG(3,2) are the 15 nonzero **XOR differences** between 16
sedenion placeholders — kinds of relationship, not positions.

```
C(16,2) = 120 pairs;  15 differences x 8 pairs each = 120, exactly
```

A spanning tree on 16 nodes has 15 edges, which is why **e0 is "not a point"**: it
is the ROOT, and the root owns no edge. A LINE is three relations that compose
(`a XOR b = c`, all 35 verified). A PENCIL is the **7 ways to factor one relation
into two others** — and 7 is not a design choice anywhere, it is 105/15.

Primer step 5 had this right all along: *"15 edges = a dependency TREE."*

---

### 5. The three faces, split by commutativity

```
LETTERS / WORDS   order MATTERS      -> POSITIONAL     (Horner, bijective)
PATHWAYS          order does NOT     -> MULTIPLICATIVE (prime product)
```

Not a convenience: commutativity is lost at CD generation 1 and the faces sit on
opposite sides of that loss. `'dog' != 'god'`; `{animal, mammal} == {mammal,
animal}`.

The join needs nothing assigned by hand: each letter carries a generation, OR the
bits and you get the word's **strut**, and the strut selects the box kite.

Measured on 73,457 words: **73,457 distinct spell codes, 0 collisions, round-trip
exact**, mean 11.6 digits.

**`gcd` IS the LCA.** With one channel per ancestor, `gcd(code_A, code_B)` is the
path from the lowest common ancestor to the root — the descent is one division,
never a tree walk:

```
dog / wolf       descend 48 digits, climb 6 each     LCA canine
oak / justice    descend  3 digits, climb 32 / 28    LCA entity
```

Which makes "how much context do you need" exact: **enough to reach the common
ancestor of prompt and response.** Not less (no path exists), not more (you start
discarding what they shared, and at the limit reach e0, which carries nothing).

---

### 6. Only definitional identity gets prime hashed

Cody's rule, and it closes what looked like a corpus gap. A concept has an
address; a pointer has no position, so there is nothing to give it a prime for.

WordNet excludes closed-class words — measured: no `of`, `the`, `and`, `to`,
`because`. **That is not a gap: WordNet's inclusion criterion IS the hashing
criterion.** Function words are labels on edges (~150–300, closed) and populate
`edge.kind`. The prime ladder never grows to accommodate grammar.

WordNet also encodes pointers as **edges but not as words** — the relation
`mero_part` exists, the word "of" does not. The corpus agrees with the trichotomy
while being unable to supply it.

---

### 7. `monad_identity.bin`

`.claude/scratchpad/monad_identity.h` + `monad_identity.py`. Layouts verified
against gcc `sizeof`/`offsetof`: header 384 B, entry 96 B, chan 8 B, edge 12 B,
every probed offset matching. Python writes the bytes, C reads them, no
serialisation layer.

**Stores WHERE, never WHAT.** The context code and the prime address are never
written — only the sparse channel list plus an FNV-1a fingerprint. Real build:

```
3,081 entries | 24,993 channels | 3,080 edges | 594 KB | 193 B/entry
checksum_ok            True
spell_roundtrip        2591/2591
spell_overflow         490 (>13 letters — FLAGGED, not truncated)
address_recomputed     3081/3081        <- the discardability test
ONE root | depth <= 18 | all 16 xor classes used
```

The overflow flag exists because the first version masked with
`& 0xFFFFFFFFFFFFFFFF` — a **silent truncation**, and a truncated spell is not
bijective. Flagged rather than wrapped.

---

### 8. IEEE contains no irrational numbers

```
math.sqrt(2) == 6369051672525773 / 4503599627370496     denominator = 2^52
(sqrt2)^2 in float = 2.0000000000000004
```

And that **inverts** the property measured in Phase 25: the orbit is dense on T²
because `1 : sqrt2` is irrational. In floats it is rational, so the computed orbit
**closes** with period 2^52. More precision only lengthens the period — float128
gives 2^112, still finite, still periodic. Bruniquel rule: a result at the
instrument's limit needs a different **method**, not a finer one.

The cheap exact fix: the whole spectrum lives in **ℚ(√2)** — one irrational, a
quadratic surd, two integers per value, closed arithmetic. Verified `sqrt2^2 == 2`
exactly, the counting law `== 16` exactly, `sqrt2^12 == 64` where float gives
`64.00000000000006`.

**The hashing algorithm is already float-free.** All exposure is in the geometry
layer.

---

### 9. Structure is executable — four benchmarked speedups

The measured facts are not descriptive. They are a fast path.

```
1. exp(tL) closed form vs Taylor+squaring     15.5x    and EXACT in t
2. orthogonal inverse = transpose             77x      and exact
3. kernel never moves — skip 4 of 16 dims     25% fewer ops per step
4. skew + sparse storage                      256 -> 120 doubles, 12% fill
```

Because the spectrum is `{0, 1, √2}` and nothing else:

```
exp(tL) = P0 + cos(t)P1 + sin(t)L1 + cos(√2 t)P2 + (sin(√2 t)/√2)L2
```

Three projectors precomputed once; every step after that is three scalar
evaluations and five scaled adds. Agrees with Taylor to 2.7e-14 across
t ∈ {0.25, 1, 2.5, 7}. `ptol.c`'s `mat_exp` currently walks the 136 μs path.

`inv(Q) == Qᵀ` to 1.3e-15 — 77× and *more* accurate. `exp(tL)·(P₀v) = P₀v` to
3.6e-16, so a quarter of the per-step work is provably unnecessary.

What does **not** speed up: ℚ(√2) is slower per operation. It buys correctness,
not throughput, and the two uses do not overlap.

Checked in the harness as group `executable  the structure IS the fast path`, so
the shortcut can never silently diverge from the general method.

---

### 10. Retractions

Kept, per standing rule, so nobody re-derives them.

- **"The name clusters wrongly."** Sharpened: names are high-precision
  (86% of name-class neighbours really are near in behaviour) and **low-recall**
  (1.6 vs 6.6 neighbours per test). They are sparse, not wrong — the classes do
  not tile the space, so nothing interpolates across them.
- **Register headroom.** Hypothesis: more surface variety where scolding
  operates. **Measured 0.896x — false.** And the instrument could not have
  answered it: member count conflates synonymy with register, and `noun.plant`
  leads only because 25.1% of its members are Latin binomials.
- **`√2` band = Σ_RB.** The primer records `|λ|=√2` as "Σ_RB conversion"
  (XOR 4). Measured, the band is closed under **XOR 8**, not XOR 4.
- **`{0,1,√2}` as "reflection part and dilation part".** Loose. Those are
  singular values of the **generator**; polar-decomposing the **flow** gives
  `||U − I|| = 1.5e-15` — no stretch at all. Dilation integrates away.
- **My own prose contradicting my own numbers, three times** — chocolate
  headroom, register headroom, and the acetone monolayer. Cause: writing the
  interpretation into a `print` statement before the measurement returned, so it
  emitted regardless. Now a standing check in the `generational-lineage` skill.

---

### 11. Still open

1. **`Ri_c = 1/4` vs `σ = 1/2`.** A ratio of squared frequencies, so a critical
   amplitude ratio of ½. Suggestive, **not a result** — Miles–Howard's ¼ has no
   derived connection to zeta. To make it one, derive it from the conservation
   law that fixes σ with no fluid input.
2. **`d*` measured independently.** `delta = OMEGA_ZS − d*·ln10 = 0.00070736`
   is a restatement while `d*` back-computes from it to 1.55e-07. It becomes a
   prediction only if `d*` is measured from the box-kite geometry alone.
3. **The closed-class table.** Small, finite, ~150–300 words. WordNet will never
   supply it.
4. **Generation bands are lopsided** — 2/1/4/19 across generations 0–3, so 72% of
   words land in kites 5 and 7. Either fine (context does the discriminating) or
   the letter→prime assignment should balance the bands. Undecided; measure
   whether kite occupancy matters downstream before choosing.
5. **The monad has kinematics and no rheology.** It describes what moves, not
   what resists. Three continuum-mechanics tools unused: the material derivative
   (follow a parcel — reading vs speaking), the constitutive relation, and
   Cauchy vs Piola–Kirchhoff stress (the Eye/Hands frame problem).

---

### Artefacts

| Path | What |
|---|---|
| `rotary_rerun_monad.py` | the harness — 124 relations |
| `lineage_hash.py` | the three-faces hashing algorithm |
| `prime_hash.py` | earlier draft; `gcd == LCA` on hypernym paths |
| `PtolC/monad_identity.h` | the C struct format |
| `monad_identity.py` | ctypes builder + reader (layouts verified against gcc) |
| `PRIMER_2026-08-18_...md` | the context primer for a fresh session |
| `~/.claude/skills/generational-lineage/` | the emergence-watching skill |

---

*Previous: [27_the_apex_path_and_the_half_radius_circle.md](27_the_apex_path_and_the_half_radius_circle.md)*
