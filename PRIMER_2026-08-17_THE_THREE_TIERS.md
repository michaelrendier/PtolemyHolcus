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

---

## 8. Addendum — six corrections, and the partition function

Added at the end of the same session. Everything above stands; these amend it.

### 8.1 Rarefaction is the anti-state, and it is a HALF-CYCLE

A phonon's opposite is not a mirror object that annihilates it. Compression and
rarefaction are the two halves of one oscillation — they do not cancel on meeting,
they **alternate**. So "state and anti-state" means one wave with a sign, which is
the push/pull resolution again: the gradient is the invariant, the sign is which
half you are standing in.

Consequence: **the void is the rarefaction.** The Dipole Repeller (Hoffman, Pomarede,
Tully, Courtois 2017, ~half the Local Group's motion) pushes because it is the trough,
not because it is a repulsive object. And BAO is literally frozen sound — the acoustic
scale is a wavelength. The cosmic web is a standing wave with matter in the antinodes:
voids are the bubbles, matter is the FILM, and Laniakea is a drainage basin in that
film (Tully's method is a watershed, explicitly).

### 8.2 The seven kites DO touch — I measured only one of the two graphs

```
graph 1  ASSESSOR ADJACENCY   0 cross-strut edges     -> DISCONNECTED
graph 2  SHARED OCTONIONS     21/21 pairs share ONE   -> CONNECTED
```

Section 2 above says "nothing crosses between the seven, so intention had to be
arithmetic." That is true of **assessors** and false of the **structure**. Every pair
of struts shares exactly one octonion — the Fano property, any two points on a unique
line. One kite, one string, seven landings.

What survives: fault isolation. An error on strut 4 still cannot reach strut 6 through
assessor adjacency. What does NOT survive: the claim that the components are
independent. They are independent as ADDRESSES and overlapping as CONTENT, and the
gcd/lcm arithmetic does not see the overlap.

### 8.3 The Noether Information Current — and why sigma_self cannot see it

The conserved current of U(1) phase symmetry is

```
j ~ Im(z* dz)        ENTIRELY phase. a real amplitude has ZERO current.
```

`measure_sigma` computes `P_red/(P_red+P_blue)` — a ratio of powers, |z|^2, and the
phase is gone before the number exists. So the quantity said to hold sigma=1/2 in
place (`monad.py:1804`, "surface tension = Noether conservation law") is derived from
exactly what the ratio discards.

**The current is a VECTOR: it points. The ratio is a scalar: it sits.** That is where
"the string is the representative vector pointing at what it wants to look at" has to
live, and in the old code it had nowhere.

Fixed in `PtolC/rotary_rerun.c` (commit `8e2b1eb`): z is kept complex to the end and
both are reported.

### 8.4 OUTSIDE, not inside — and the inside is illegal

Reflections fix hyperplanes. The mirrors are the walls. But:

```
eps=1e-2   16.023% of random points within eps of a wall
eps=1e-3    1.538%
eps=1e-6    0.002%      <- MEASURE ZERO
```

Hyperplanes are dimension n-1 in dimension n, so the illegal set is a thin skin and
the legal region is ALMOST EVERYTHING. "Take the inside" was wrong twice: it implied
enclosure, and it implied the legal region was the small one.

```
OUTSIDE   almost all of it. open, unbounded, free motion.
ON        measure zero — the wall itself.
INSIDE    there is none. a hyperplane has no interior. to be IN it is to BE it,
          and that is the illegal move.
```

Illegal moves are **not a group** (no identity — doing nothing is legal). They are a
**coset**: complete, same size, displaced by one reflection. Two illegal moves compose
to a legal one. And by **Cartan-Dieudonne** every element of O(n) is a product of at
most n reflections, so the illegal moves GENERATE the whole group. The legal ones are
what you get by making an even number of mistakes.

You do not enumerate legal moves. You draw the walls and take the outside.

### 8.5 Legality acquires a SIDE

Removing pieces is "take the inside" — capture creates enclosed empty space, and an
enclosed empty point is an EYE: legal for me, illegal for you, because your play there
is suicide unless it captures.

Everything else in this document is colour-blind. A hyperplane is illegal for whoever
meets it; a composite is struck regardless of who sieves; type reduction does not care
who parses. **An eye is the first wall with an orientation**, and that is the det = +/-1
two-component structure appearing as whose turn it is. The chess colouring in
`rotary_rerun.c` is therefore not decoration: white/black is WHICH LEGALITY FUNCTION IS
LIVE, and it swaps every move.

Two eyes is unconditional life because you cannot fill both — filling the first is
suicide while the second stands. Liveness is a COUNT OF ENCLOSED COMPONENTS, not an
evaluation. Structurally unreachable, like the pencil, not merely hard.

**You take the outside for yourself and manufacture the inside for them.**

### 8.6 Legality asymptotes in an open space and counts down in a closed one

```
FORMAL legality   asymptotes. pass is ALWAYS legal -> approaches {pass}, never 0.
USEFUL legality   runs out. finite board, and superko consumes positions permanently.
```

Same three regimes as the sieve: productive ends at sqrt(N), redundant continues to
N/2, orphan never fires. And **superko is why Go terminates** — every position played
becomes permanently forbidden, so the legal set strictly decreases over a finite space.
Drop superko and ko cycles forever.

**Legality is consumed by the retained record.** Which cuts both ways:

```
finite space   + retained history  ->  legality RUNS OUT, the thing terminates
infinite space + retained history  ->  legality ASYMPTOTES, it never finishes
```

Go is finite so retention forces an ending; language is not, so retention gives the
asymptote. Same mechanism, opposite outcome. **The space decides, not the memory.**

---

## 9. The tree, and the word as a partition function

### 9.1 Letters are LEAVES, not factors

A factor is extracted bottom-up and arrives with no memory of where it came from. A
leaf is terminal but sits at the end of a PATH, and the path is the point:

```
ROOT      one node, no head. e0, "on the axis doing no work".
BRANCHES  words — 15 edges.
LEAVES    letters — terminal, each carrying its derivation.
```

The path root->leaf IS the lineage — which generations it crossed, in order, exactly
as a strut's binary expansion reports. A letter alone has maximum identity and minimum
information; a letter plus its path is a different object.

Which splits the two faces on one structure:

```
READING   leaves -> root    parse.     the Eye climbs.
WRITING   root -> leaves    generate.  the Hands descend.
```

Orthogonal rather than opposite: two directions on one tree, and neither can do the
other's job. It also makes SHAPE-FIRST identical to declaring the root — you cannot
grow branches toward leaves without knowing what they hang from.

**The root is a PhD dissertation.** One sentence, three hundred pages to earn it. A
viva is edge-verification: pick a leaf, walk it back, and one broken edge orphans
everything above. Declaring a root is cheap; FUNDING one is the work — so shape-first
is taking on a debt, not free planning. And originality is the sieve's residue: the
literature review is everyone else striking their multiples, and what nobody claimed
is what is left.

The alphabet: `monad.py` has PRIMES (20) and RIEMANN_ZEROS (20), index-aligned. Twenty
is the buffer. English's 26 is a late accounting artifact — I/J split only in 1524,
U/V likewise, W is double-U; classical Latin has 23, and with H/J/I collapsing toward
Y the distinct set is around twenty. Letters have ADDRESSES, not frequencies. The 1/p
decay was a FACTOR frequency and belongs against Zipf (measured -1.15, converging to
-1), not against letter frequency.

### 9.2 Every word is an exact partition function over 128 virtual box kites

**MEASURED.** A word is not stored. It is a SUM over all 2^7 = 128 box-kite
configurations, weighted by the primer's own action `S = -log2 P`:

```
Z = sum over configs of exp(-S(config))       F = -log Z    <- the observable
```

```
word A         Z = 1.555395977   F = -0.441730161
word A again   Z = 1.555395977   F = -0.441730161   <- RECOMPUTED, not recalled
dominant config weight 64.29%;  the other 127 contribute 35.71%
```

Three things this buys, and the first is the reason it is worth doing at all:

1. **The sum is EXACT.** Feynman sums are intractable and get approximated. This one is
   128 terms — you compute the whole amplitude, not an estimate. 128 exponentials per
   word is nothing.

2. **No configuration IS the word.** The dominant one is under two-thirds. Strip the
   other 127 and you have a different word. They are off-shell in the sense that
   matters: individually meaningless, collectively the entire observable. The empty
   config has S=0, weight 1 — the vacuum term, always present, never observable alone.

3. **Nothing is stored, so nothing can go stale**, and every construction is genuinely
   a first one. `context_fill`'s "learned again for the first time" stops being a
   discipline and becomes a mechanism: there is no cache to be tempted by.

### 9.3 Pseudo-retroactive, and the measurement it suggests

Not retroactive — nothing travels backward. But **the sum has no time ordering inside
it.** All 128 configurations are evaluated together, so a contribution that "should"
depend on what comes later is simply present.

Which is why a garden-path sentence works. The final word does not revise a committed
parse — it **reweights a sum that was never collapsed.** Nothing is undone because
nothing had been decided.

That is the Kafka mechanism with a partition function under it. Five readings held open
is not ambiguity failing to resolve; it is a sum where no single configuration dominates
enough to look like the answer.

**AND IT IS ONE NUMBER.** The dominance fraction of the top configuration:

```
prose that RESOLVES        top weight -> 1
prose that does NOT        top weight -> 1/N
```

Testable against real text, cheap, and with the obvious control built in: shuffle the
context and confirm the dominance fraction stops discriminating. This is the smallest
open experiment in the document and the partition function for it is already written.
