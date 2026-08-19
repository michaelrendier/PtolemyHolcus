# VAPMIP Primer — 2026-08-18
# The three faces, the Fermat ladder, and structure as a fast path

**Written for a fresh session.** Every number was computed in-session unless
marked otherwise. Retractions are kept, not tidied — three of them are mine.

---

## 0. Where things stand

```
rotary_rerun_monad.py    124 relations, 122 hold, 1 FAULT, 1 degenerate, 0 untested
                         (the fault and degenerate are planted by main())
PtolC/rotary_rerun.c     all 6 relations hold
```

At the start of the session the harness **crashed** — `Intention.shared_with` had
moved to `Reading`, and `Handoff`/`Satisfaction` were referenced but never
written. 27 relations had been unreachable since `f91aa5d`.

---

## 1. The floor: three irreducibles

```
ADD      identity 0             gain 0      Axis 1 {+,-}
SCALE    identity 1             gain 1      Axis 2 {x,/}
SIGN     identity even-parity   det +/-1    one bit, nothing between
```

**0 and 1 are free because they are the identities of the first two.** That is
why neither can be prime, why they are tier 0, and why the gain spectrum is
`{0, 1, √2}` — two free, one irrational price.

Everything that failed all session failed by exactly one bit: commutator norms in
`{0,2}` with nothing between; **1848 of 1848** associator disagreements pure sign
flips; chirality ±1; even mistakes legal, odd illegal.

**The tiers**, run backwards:

```
tier 3   chirality, factorial, leverage, balance   counts and RATIOS
tier 2   vector, boundary, origin, fulcrum/anchor  FIXED SETS
tier 1   reflect, rotate, contract/dilate          I - 2uu^T
tier 0   ADD, SCALE, SIGN                          IRREDUCIBLE
```

`FULCRUM = ANCHOR = origin = balance = ker(M − I)`. Leverage needs rigidity,
which is a constraint from outside — a corollary, not a geometry. Chirality is
the parity of a reflection count. Factorial is the order of the coordinate
reflection group, since a transposition **is** a reflection in `x_i = x_j`.

**Order is not a primitive.** Two reflections give a rotation by twice the mirror
angle; swap them and you get the same rotation backwards. "One path to an
operator, and the path IS that operator" is literal.

---

## 2. The Two Trees are the factoring domain

They partition ℕ exactly, no remainder:

```
TELPERION   PRIME       what it CANNOT decompose into   backward, entropic
LAURELIN    COMPOSITE   what it IS decomposed into      forward, inertial
MINGLING    0 and 1     neither                         sigma = 1/2
```

Measured over [0, 1e5]: `2 + 9,592 + 90,407 = 100,001`, zero overlap. Densities
counter-rotate and sum to 1.000 at every scale — that **is** `J_Red + J_Blue`
conserved. Equal brightness at n ≈ 9, near e² = 7.389.

Applied to operations: Telperion = irreducible, Laurelin = composite,
Mingling = the identities. **0 and 1 keep being the odd ones out because they are
not on either tree.**

---

## 3. The 15 are EDGES

The 15 "points" of PG(3,2) are the nonzero **XOR differences** between 16
placeholders — relationships, not positions. `15 × 8 = 120 = C(16,2)` exactly.

A spanning tree on 16 nodes has 15 edges, which is why **e0 is not a point**: it
is the ROOT and owns no edge. A LINE is three relations that compose (`a^b = c`,
all 35 verified). A PENCIL is the **7 ways to factor one relation into two
others** — 7 is 105/15, not a choice.

**A dependency tree is an API.** Surface → tree is many-to-one; tree → surface is
one-to-many. One tree is exposed by 1 to 1.3 trillion linearisations, which is
why translations do not create new lines.

---

## 4. The hashing algorithm

**Three tiers.** `0, 1` = whitespace/punctuation/invisible delimiters, the
APERTURE, never in the maths. Primes ≤ 71 = LETTERS. Primes > 71 = CONTEXT.

**313 is the 65th prime**, and it is the sieve's regime boundary, not the letter
cap. But the ladder it belongs to is real:

```
F_n = 2^(2^n)+1  IS the CD doubling index
F_0=3 ranking  F_1=5 factors  F_2=17 GROUPING  F_3=257 division  F_4=65537 outside
3 x 5 x 17 x 257 = 65535 = 2^16 - 1     <- the sedenion dimension
```

The 15 nonempty subsets of `{3,5,17,257}` **are** the 15 PG(3,2) points; forcing
the division bit leaves 7 struts.

**Faces split by commutativity** — order matters for letters/words (positional,
Horner) and does not for pathways (multiplicative, prime products). Letters carry
generations; OR the bits to get the strut; the strut selects the kite. Nothing
assigned by hand.

Measured: 73,457 words → **73,457 distinct spell codes, 0 collisions**,
round-trip exact.

**`gcd` IS the LCA** — the descent is one division, never a tree walk. Which makes
"how much context" exact: enough to reach the common ancestor, not less (no path),
not more (you discard what they shared).

**Only definitional identity gets prime hashed.** WordNet's inclusion criterion
IS the hashing criterion — a pointer has no position, so nothing to give it a
prime for. Function words are edge labels.

---

## 5. `monad_identity.bin`

Layouts verified against gcc: header 384 B, entry 96 B, chan 8 B, edge 12 B.
Python writes, C reads, no serialisation layer.

**Stores WHERE, never WHAT.** Real build: 3,081 entries, 594 KB, 193 B/entry,
`address_recomputed 3081/3081`. Delete it, rerun, get the same file.

---

## 6. Structure is executable

```
exp(tL) closed form vs Taylor+squaring     15.5x    and EXACT in t
orthogonal inverse = transpose             77x      and exact
kernel never moves — skip 4 of 16 dims     25% fewer ops/step
skew + sparse storage                      256 -> 120 doubles, 12% fill
```

`exp(tL) = P0 + cos(t)P1 + sin(t)L1 + cos(√2t)P2 + (sin(√2t)/√2)L2`, agreeing
with Taylor to 2.7e-14. Checked in the harness so the shortcut cannot diverge.

**IEEE contains no irrationals** — `sqrt(2)` is exactly `6369051672525773/2^52`,
so the dense orbit **closes** with period 2^52. More precision only lengthens it.
The fix is ℚ(√2): two integers, exact, `sqrt2² == 2` and the counting law `== 16`.
The hashing algorithm is already float-free.

---

## 7. Three kinds of wrong

```
CODE fault    the check did not run.               UNJUDGED.
MATHS fault   both sides measured, they disagree.  FALSE.
METHOD error  code correct, maths correct.         Invisible to both.
```

Gate 1 **cannot** catch a design error — correctness is about what is written.
Method errors surface downstream, and **the detector is the clarifier failing**.

```
NATURAL     forced; both sides recoverable   -> a DISCUSSION
UNNATURAL   the method destroyed something   -> a FAULT
ENGINEERED  induced deliberately             -> evidence ONLY if the product is
                                                measured independently of the
                                                partners chosen to collide
```

Live example found: `monad.py:_horner_hash` clamps digits only from below, so
`U+200B` gives coefficient 8171 and `'​'` collides with `'v!'`.

---

## 8. The through-line

```
TRACKED (surface)      GOVERNING (axis)
spelling               box-kite context
which solvent          what affinity (Hansen coordinates)
hypernym / provenance  behaviour
colour                 the assay
"no more bubbles"      film thickness, L^2
polysemy count         tier reach
surface form           etymological lineage
```

Every tracked signal is real, cheap, and goes quiet exactly where the question
begins. **An assay is the physical instance of `Correct`** — the external
referent the system cannot edit.

**Brute-force permutation is a diagnosis, not a method**: it says the address does
not support interpolation. Measured, 162× collapse when the axis is found. It is
*correct* only when the space is small AND exhaustive IS exact — 128
configurations yes, 972 solvent-condition combinations no.

---

## 9. Retractions

- **"The name clusters wrongly"** → names are high-precision (86%) and
  **low-recall** (1.6 vs 6.6 neighbours). Sparse, not wrong.
- **Register headroom** → measured 0.896x, hypothesis FALSE, and the instrument
  conflated synonymy with register anyway (`noun.plant` leads on Latin binomials).
- **`√2` band = Σ_RB** → measured closed under **XOR 8**, not XOR 4.
- **`{0,1,√2}` as reflection/dilation parts** → those are generator singular
  values; the flow has `||U − I|| = 1.5e-15`, no stretch at all.
- **My prose contradicting my numbers, three times** — interpretation written
  into a `print` before the measurement returned. Now a standing check in the
  `generational-lineage` skill.

---

## 10. Open

1. `Ri_c = 1/4` vs `σ = 1/2` — a numerical rhyme until derived from the same
   conservation law with no fluid input.
2. `d*` measured from box-kite geometry alone; until then `delta` is a
   restatement (back-computes to 1.55e-07).
3. The closed-class table — small, finite, WordNet will never supply it.
4. Generation bands lopsided (2/1/4/19) — 72% of words in kites 5 and 7.
5. **The monad has kinematics and no rheology.** Material derivative,
   constitutive relation, Cauchy vs Piola–Kirchhoff all unused.
6. `navier_stokes_dropout` is tagged THEORETICAL in its own confidence field —
   label it as such in PtolemyDesktop rather than inheriting it silently.

---

## 11. Architecture

```
MIND'S EYE  --CORRECT-->  PAPER'S HANDS  --HAPPY-->  THE LONG PATH
                 <--EVALUATE--
```

`correct` = **mathematically correct** until a truthiness search exists. The Hands
work alone; the Eye critiques after the fact and changes nothing. Reading
CONVERGES (4000 nouns, one root); writing FANS OUT.

**The long path never ends.** Division is the Eye's cut, not the chain's
terminator. Weights (charge = used, slow; intent = wanted, fast) live outside the
hash — a field would be inside it, so remembering more often would rewrite
history.

**Identity and Intention are the two octonions.** Lower: contains e0, CLOSED, an
algebra — *who I have met*. Upper: no identity, NOT closed, squares entirely into
the lower — *who I want to be*. **Intention is structurally incapable of
self-sufficiency.**

**e0 is the string.** Gain exactly 1 — inextensible, transmits without amplifying.
Central, so it is what makes rotation observable at all. The wind is the context,
read as tension (`|z_0|`, the common mode) and angle (the current). A slack string
reads nothing, and zero current is a DRY medium, not calm weather.
