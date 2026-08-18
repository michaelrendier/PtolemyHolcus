# VAPMIP Primer — 2026-08-17 (late)
# Letters, Words, Pathways: the three tiers, and what was measured under them

**Written at the end of a long session, for a fresh one.** Every number below was
computed in-session unless marked otherwise. Where a result is standard it says so —
that distinction is the point.

---

## 0. The thesis, in Cody's words

```
LETTERS    are spelling    are MUSCLE MEMORY
WORDS      are CONTEXT-BEARING INTENTION, and their ORDER MATTERS
IDEAS      and concepts are built in PATHWAYS
SPEAKING   is the order in which those pathways flow through you
```

Speaking is not a tier. It is the **traversal order** of the third tier. That is why
order is a constructor and not a formatting choice, and it is why Boehm-Jacopini
matters: SEQUENCE is one of the three constructs, not a convenience.

---

## 1. What got built

| file | state |
|---|---|
| `VAPMIP/rotary_rerun_monad.py` | committed `9e6629e`, extended `5b1d927`; 78 relations, 76 hold |
| `VAPMIP/sieve_clock.py` | committed `5b1d927` |
| `VAPMIP/context_fill.py` | committed `5b1d927` |
| `PTorrent/core/c/` | committed `5787ed3`; 291 checks, clean ASan/UBSan/-fanalyzer |

`Intention` was rewritten **after** `5b1d927` and is uncommitted: it is now a STATE
(mutable, decaying, stamped) rather than a definition, and a vector (prime exponent =
magnitude) rather than a set.

---

## 2. Measured this session — the numbers

### The zero divisor is a rotation
```
||sym(L_a)||        0.000e+00      L_a is EXACTLY skew-symmetric
||skew(L_a)||       4.000000       pure vorticity, no strain
exp(L_a)^T exp(L_a) = I  to 9.85e-16,  det = +1.000000000000
```
So `L_a ∈ so(16)` and `exp(L_a) ∈ SO(16)`. Zero stress tensor. "Least shearing" is
an **identity**, not a minimum — there is no symmetric part to carry shear.

### {4,8,4}
```
nullity 4, rank 12.  gains 0 x4, 1 x8, sqrt2 x4.
all four annihilated partners on STRUT 3 — annihilation never crosses struts.
```
The kernel is the **axis of rotation** (4 fixed, 12 turning in 6 planes).
**It does NOT orbit** — so it is gravity-ABSENT, not free fall. Orbits are the global
discriminant that breaks local equivalence.

### The kites do not touch
```
0 cross-strut edges,  84 within-strut,  degree 4 uniform on all 42 assessors
associator across struts: 0.000000 on all 21 pairs
```
No orphans, no coordination deficit, no weak residual. Seven disconnected octahedra.
**This is why intention had to be arithmetic** — no path between kites to interpolate
along — and it is also **fault isolation**: an error in one component cannot propagate.

### The two halves are not the same kind of thing
```
lower e0..e7    leak 0.000e+00    CLOSED — an algebra
upper e8..e15   leak 1.000e+00    NOT closed — not an algebra
```
`(0,b)(0,d) = (-d*b, 0)`. The upper squares into the lower. You need the sedenion to
see it; neither half can from inside. And the doubling rule
`(a,b)(c,d) = (ac - d*b, da + bc*)` carries BOTH a conjugation (inversion) and an
order swap (reversal) — conjugation kills commutativity at H, order swap kills
associativity at O.

### 5/5/5 as the control for 7/7/7
```
8-dim octonion block   leak 0.000e+00
three 5-dim faces      leak 0.520, 1.000, 1.000
```
Hurwitz forbids a 5-dim composition algebra. **5/5/5 is a legal ROTOR map and an
illegal ALGEBRAIC one; 7/7/7 is the reverse.** They are not competing for the same job.

### The sieve — the standard life of a factor
```
N=1e5   last prime to claim anything NEW = 313      sqrt(N)=316.23
N=1e6   997        N=4e6  1999        measured, never assumed
productive 0.107% of primes at N=4e6;  65.9% of strikes wasted
168 speakers settle 100% of a million; nine settle 90%
ORPHAN FRACTION -> 1/2, not 0.  Residual factors are NEVER gone.
```
Every factor's first claim is exactly p*p. Departure order == entry order.

### Zero neighbourhoods
```
50 exact LMFDB zeros.  unfolded spacing mean 0.9970, min 0.3868
gaps below s=0.3: 0 of 49.   Poisson predicts 12.7.
```
Hard floor. Level repulsion. A neighbourhood is an **exclusion zone**, bounded on both
sides — the minimum from repulsion, the maximum from the counting law. Lagrange:
position is where two competing constraints balance.

### The primes come back out of the zeros
```
D(u) = sum_n cos(gamma_n u),  peaks at u = log(p^k):
log2 -0.00113   log3 +0.00030   log4 -0.00208   log5 -0.00009
log7 -0.00013   log8 +0.00295   log9 +0.00246          7 for 7
```
Cepstral separation: primes are the SOURCE, zeros the FILTER, and `log` is the bridge
because primes combine multiplicatively and zeros additively.

### Coherence and the N=1 degeneracy
```
N=1  coherence 1.0000 ALWAYS      max alignment and NO alignment are the same number
N=2  zero requires antiparallel   the only way to cancel is to fight
N=3  zero at 120 deg              no two oppose and the sum still vanishes
```
Three is the minimum for alignment to be a measurement rather than a tautology.
**alpha = coherence** sets groove depth in `novelty = c + (1-c)/n^alpha`. Repetition
raises n and leaves alpha alone — measured: `turns` read more often than `rotor` and
grooved LESS deeply.

### Controls that came back negative — recorded so nobody re-derives them
```
d* / Omega vs hydrogen orbital features:  z = -0.39 vs 200 random constants
   (578 dimensionless ratios from 35 radial features, n=1..5). BELOW chance.
Lambert W is in H2+ and Wien's law, NOT in atomic hydrogen (Laguerre, closed form).
W has TWO real branches, not three.
GAP is DEFINED as |Omega - d*ln10| = 0.000707, so those are one constant, not two.
GAP contributes 0.084% of the A-edge denominator at the closest observed pair —
   a regulator for a divergence level repulsion already forbids by 1195x.
strut-1 pairing apply/abstract, bind/name, branch/iterate is AUTHORSHIP:
   OP_NAMES was written in dual pairs at consecutive indices, and strut 1 is
   "differ in bit 0". The uncontaminated test is struts 2 and 4.
```

---

## 3. Corrections that stuck (mine, mostly)

- **trustable, not invariant** — then sharpened: it IS an invariant, a RELATIONAL one,
  between two objects, scoped to one index space. Not a claim about time.
- **the kernel is gravity-ABSENT, not free fall.** Equivalence is local; orbits are the
  global discriminant. Free fall orbits because curvature converges geodesics.
- **coprime alone is not the resolver.** Six coprime pairs exist over 3 bits; only
  THREE span. `gcd` says the strings are disjoint; `lcm` says whether they complete.
- **push/pull is the sign convention on a gradient.** The Dipole Repeller (Hoffman et
  al. 2017) is a measured cosmological push — an underdensity repels because everything
  is relative to the mean. Le Sage push gravity at planetary scale is dead (drag,
  heating, aberration).
- **intention is a STATE, not a definition** — so every read must be stamped, and two
  readings from different moments refuse to combine.
- **'happy' is legitimate.** Safety is ORDERING, not vocabulary: satisfaction downstream
  of a truth cannot manufacture that truth. Then sharpened again: happy is not a buffer
  filling, it is `delta S = 0` — the geometries giving free downhill work all lining up
  at once. Stationary PHASE, which is why the least-action path is unavoidable rather
  than merely likely.
- **translations do not create new lines.** Structure is the invariant; word choice is
  the coordinate. Brod's composite DID change structure — that is a different object.
- **the shape of the response is determined FIRST.** Shape-after-reading can be shaped
  TO the reading. Declaring first is pre-registration, and it is the same discipline as
  committing `hash(j_expr + prediction)` before touching the data.

---

## 4. The architecture as it now stands

```
MindsEye      reads   — snapshot, all at once, no ordering
PapersHands   writes  — sequence, one at a time, no simultaneity
BoxKite       the relational language BOTH speak — co-authored by the two,
              descent hash commits to both parents

LongPath      IDENTITY   hash-chained, tamper located AT ITS INDEX,
                         mutable per event (amend = APPEND, never overwrite)
ShortPath     INTENTION  bounded, volatile, explicitly collected

Three readiness thresholds, three owners, NEITHER SIDE POLLED:
  Eye     hands off on CORRECT   external predicate it cannot edit
  Hands   hand off when the geometries ALIGN   coherence, stationary phase
  archive happens on USEFUL      a path can align having emitted nothing worth keeping
```

Eye and Hands are **orthogonal, not opposite**. Opposites cancel; orthogonals span.
A pencil pair is an orthogonal decomposition, and the friction is the guarantee that
both dimensions are still there.

---

## 5. The response order (step 0 added late, and it matters most)

```
0  SHAPE       declared BEFORE reading — an intention VECTOR over the 7 kites,
               magnitudes included. The TYPE of the response, never its content.
1  APERTURE    the shape says what to read FOR (personality IS the aperture)
2  TOKENIZE    above letters; Unicode codepoint stays the pointer
3  ADDRESS     word -> Horner prime hash -> pi(p) -> gamma
4  SCORE       240 directed edges in a 16-window
5  SPAN        15 edges = a dependency TREE. e0 is the ROOT (no head, "does no work")
6  TYPE-REDUCE does it reach the declared shape?    <- CORRECT, external
7  ITERATE     3->6; types and tree co-determine. This is the recursion.
8  STOP        delta S = 0. Measured, not scheduled.
9  READ        snapshot, coherence
10 HANDOFF     correct AND cold (temperature = spread between best and worst legal move)
11 WRITE       in order
12 ARCHIVE     only what proved useful reaches the long path
```

**Step 6 diagnoses componentwise.** `gcd(declared, observed)` gives four distinct
repairs, and they are different repairs:
```
held in full     nothing to do
over-declared    lower the magnitude, keep the string
unsupported      drop the string           <- re-declare
missed           input lit what we never reached for  <- widen the APERTURE
```
Disconnected kites mean an error in one does not propagate. Shape-before-reading is
survivable because you get to be **partially right**, which is the normal condition of
answering anything.

---

## 6. Still open

1. **The face map.** `{1:5:5:5}` (Z3, rotor-legal) vs `{1:7:7:1}` (Z2) vs
   `7 | 7 | boxkite` (two volumes + a relational boundary). Cody's call; it changes what
   the engine IS. cam3.py flags it.
2. **The edge cost** for step 4 — reuse `w = EiEj/((|gi-gj|+GAP)d)` or define new?
3. **The type inventory** for step 6 — the Zork 16 (`identity, negate, bind, name,
   apply, abstract, branch, iterate, recurse, allocate, query, dereference, compose,
   parallelize, interrupt, emit`) are already indexed to e0..e15, but they type
   OPERATIONS, not nouns.
4. **The zeta index** `zeta(p) = min{n : gamma_n >= 2pi p/log p}` — monotone (proved),
   zero free parameters, UNTESTED. Build the control first.
5. **{4,8,4} across all 42 ZD classes** — one verified. `TODO.md:73`.
6. **PTorrent: does ACQUIRE end at the corpus or at the bin?** Ending at the corpus
   keeps PTorrent 100% open and takes the maths out of it.
7. **Brod's composite.** `Beschreibung eines Kampfes` Fassung A and B were interleaved
   by Brod into one readable text; S. Fischer separated them only in 1993. The 1958
   Stern translation (in Glatzer's Complete Stories, 1971) descends from the composite.
   A is theatrical, B is musical — "they do not tell the same story twice."

---

## 7. Standing rules earned or re-earned

- **A reducer must be valid on its data.** `argmax` over signed currents selects a
  gated-off zero. Return DEGENERATE, not a confident wrong number.
- **Nothing is dropped.** Every input becomes a record with a status. Counting a skip
  is still a skip.
- **Iteration and modification are different objects** — which is what lets them share
  one index space and AGREE on it. A cross-space index is refused, not resolved.
- **A control before the measurement, not after.** Two claims died this session under
  controls that took ninety seconds each.
- **Find what does not move when you do — ACROSS SCOPE.** A reference dangles across a
  scope boundary; a value survives. Everything trusted today was normalised to cross:
  unfolded spacings, coherence /N, sigma as a ratio, gcd/lcm, det = +/-1.
