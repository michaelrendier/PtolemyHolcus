# VAPMIP Primer — 2026-08-17
# Speaking English and Factoring an RSA Modulus: the same generational lineage

**Written for a fresh session.** Everything below was measured in-session unless marked
otherwise. Where a result is standard, taught material it says so — that distinction is the
point, because the new content is the *bridge*, not the foundations.

---

## 0. The one-line thesis

Order-loss in the Cayley–Dickson tower is a **generational lineage**, and the same lineage
indexes both the structure of a spoken sentence and the structure of a factorisation. The
strut's binary expansion **is** its lineage — "how a thing is built and what it is built
from," read straight off the index.

---

## 1. The generational lineage of ORDER  [MEASURED]

Each CD doubling removes exactly one freedom about order. Measured directly by counting
failures over the multiplication table (dims 1→16):

| dim | alg | new unit | strut | comm fail | assoc fail | ZD pairs | what "order" is lost |
|---|---|---|---|---|---|---|---|
| 1 | ℝ | — | — | 0 | 0 | 0 | — |
| 2 | ℂ | e₁ | 1 | 0 | 0 | 0 | order as **ranking** (no total order) |
| 4 | ℍ | e₂ | 2 | **6** | 0 | 0 | order of **factors** — `ab ≠ ba` |
| 8 | 𝕆 | e₄ | **4** | 42 | **168** | 0 | order of **grouping** — `(ab)c ≠ a(bc)` |
| 16 | 𝕊 | e₈ | 8 | 210 | 1848 | **84** | order as **survival** — annihilation |

Each property **first** fails exactly at its own generation. Strut `2^m` is the unit introduced
at doubling `m`, so a strut value *names which doubling you are crossing*.

**Strut 4 = e₄ = the associativity generation = "The Grouper."** Cody's name, and it is
literally correct: associativity is about *grouping*, and bit 2 is the bit whose introduction
destroyed it.

### 1.1 The 7 struts are derived, not observed  [MEASURED]

Enumerating the struts of the 84 zero-divisor diagonals and decomposing each into its bits:

```
strut  binary  generations present
    9   1001   ranking + division
   10   1010   factors + division
   11   1011   ranking + factors + division
   12   1100   GROUPING + division
   13   1101   ranking + GROUPING + division
   14   1110   factors + GROUPING + division
   15   1111   ranking + factors + GROUPING + division
```

- The **division bit is forced** — zero divisors do not exist below dim 16, so every strut has
  it.
- That leaves exactly **3 free bits**.
- Nonempty subsets of 3 things = **2³ − 1 = 7**.

So there are seven box-kite struts *because there are three generations of order-loss beneath
the one that creates zero divisors*. The Fano plane's 7 points stop being a coincidence and
become a count.

**Honest scope:** the strut arithmetic itself (7 struts, XOR indexing, Fano incidence) is
standard box-kite / Cayley–Dickson material — de Marrais has the counting. What is earned here
is the **reading**: each bit names a specific order-property generation, and the forced
division bit is what pins the free count at 3.

### 1.2 Σ_RB is the Grouper applied channel-wise  [MEASURED]

`VAPMIP/PtolC/ptol.c:862-865` computes `Σ_RB[k] = v[k] · v[partner(k)]` with a branchy
partner expression. That expression **is exactly `k XOR 4`** for all 16 channels — verified.

So Σ_RB pairs every channel with its mirror across the **associativity** generation. The
canonical maths already flags Σ_RB as carrying "the same algebraic signature as a cross
product"; that antisymmetry *has* to appear at strut 4, because that is the generation where
`(ab)c ≠ a(bc)` first has content.

Three different involutions are in play across the codebase and they are not
interchangeable:

```
ptol.c  Sigma_RB      partner = k XOR 4    GROUPING (associativity)
rotary  red/blue      split at bit 3       division (ZD)
vagcom  CamProfile    partner = 15 - k     = k XOR 15 -> ALL FOUR generations
```

`15 − k = k XOR 15` because 15 is all-ones in 4 bits, so subtracting from all-ones is
bitwise complement. The Hermite cam therefore already sits on the all-generations complement
(strut 15) without anyone having designed that in — it falls out of the Hermite symmetry being
even.

---

## 2. The pencil  [MEASURED]

A **pencil** in projective geometry is the set of all lines through a point — from the *optical*
pencil, a cone of rays from a point (Latin *penicillus*, a fine brush). Not the writing tool,
though they share the root.

### 2.1 The pencil is exactly the set of ordered lines

Label struts by their 3 free bits (strut − 8 → a nonzero vector of GF(2)³). Score each Fano
line by the **popcount** of its points:

```
line       popcounts   totally ordered?
(1,2,3)    (1,1,2)     no
(1,4,5)    (1,1,2)     no
(1,6,7)    (1,2,3)     YES
(2,4,6)    (1,1,2)     no
(2,5,7)    (1,2,3)     YES
(3,4,7)    (2,1,3)     YES
(3,5,6)    (2,2,2)     no
```

The three totally-ordered lines are **exactly the three lines through label 7** — the pencil
at the all-generations strut. Every other line is popcount-degenerate and admits no order.

**A line between two points is an edge; a line through three points is a pathway, and a
pathway has an order.** The pencil is precisely the set of Fano lines that are pathways:

```
ranking    1 -> 6 -> 7
factors    2 -> 5 -> 7
GROUPING   4 -> 3 -> 7
```

Each is a build order: one generation, then its complement, then all three. They converge on
15. Cody's "inside out of the 3-body problem" — not three bodies orbiting a centre, but one
point with three ordered pathways *into* it.

Also: each generation-bit is a **linear functional** whose kernel is a Fano line
(`GROUPING = 0 → {1,2,3}`), which is what a line *is* in PG(2,2). Three kernel-lines + three
pencil-lines at 7 + one leftover `{3,5,6}` = 7.

**PG(2,2) is self-dual** (3 points per line, 3 lines per point), so *line* and *pencil* are the
same shape read from opposite ends: "all origins on a pathway" vs "all pathways from an
origin."

### 2.2 The pencil is the coprime-factorisation structure  [MEASURED]

The pencil lines are **exactly** the lines containing a pair with

```
a AND b = 0     and     a XOR b = 7
```

`AND = 0` is **disjoint lineage — coprimality**. `XOR = 7` is *together they span everything*.
So the pencil encodes the coprime splits of the complete generation set. It was a
factorisation structure the whole time, and it is invisible if you only look at XOR.

---

## 3. XOR is the move; AND is the memory  [STANDARD, correctly applied]

Over GF(2), XOR is addition (linear) and AND is multiplication (nonlinear). A function built
from XOR alone is affine and invertible by Gaussian elimination — **there is no one-wayness in
it at all.** All hardness in every one-way function lives in the AND terms.

*(This is taught material. Cody had it from a Computerphile video — Phil Moriarty, the "Do
Atoms Ever Touch?" physicist. The foundations here are standard and citable; only the bridge
onto the strut geometry is ours.)*

```
i XOR j    generations where they DIFFER    the move      divergence
i AND j    generations BOTH carry           the memory    common ancestor
```

The elementary identity that ties them:

```
a + b  =  (a XOR b)  +  2·(a AND b)
          ‾‾‾‾‾‾‾‾‾      ‾‾‾‾‾‾‾‾‾‾
          the MOVE       the MEMORY
```

XOR is bijective — reversible, carries no hardness. AND is idempotent with no inverse:
`a&b = 0` has 27 preimages of 64. Information is **destroyed**, which is the definition of the
barrier, not a difficulty within it.

### 3.1 The reversal key is the retained record

```
AND alone            (a,b) -> a&b                lossy, one-way
Toffoli / retained   (a,b,c) -> (a,b, c XOR (a&b))  fully REVERSIBLE
```

**AND becomes reversible the moment you keep the inputs.** Toffoli is universal for classical
computation and bijective; the only thing that made AND one-way was *discarding* the operands.
Landauer says the same thermodynamically: AND erases a bit and dissipates `kT ln2`; retain it
and there is no erasure, no dissipation, no irreversibility.

So Cody's sentence — *"the pathway remembers where it has been, but only if it has moved"* — is
the reversal key stated exactly. The retained record is the ancilla that inverts the
irreversible gate.

**And that is why RSA holds, in one line:** a one-way function is one-way *exactly because the
pathway did not remember.* Handed `N`, the multiplication's carries and intermediate state were
thrown away. That is not an implementation detail — it **is** the security. Nothing in the
pencil geometry reconstructs a record that was discarded.

Where it *does* bite: any system that leaks the record. Reversible-computing side channels,
retained intermediate state, an implementation that keeps its carries. Not "break the maths" —
"find where the pathway remembered."

---

## 4. The RSA tests — all negative, with reasons  [MEASURED]

Run this session. **None of these is an attack.** They are recorded so nobody re-derives them.

### 4.1 ω = 2 (standard RSA): the strut is not private
`strut = (p mod 16) XOR (q mod 16)`. Both primes odd ⇒ strut always **even**; reachable
box-kite struts are `{10,12,14}`.

```
N%16 | struts a^b over all (a,b) with ab=N | #distinct
   1 | {0,8}                               | 2
   3 | {2}                                 | 1   <- deterministic
   5 | {4}                                 | 1   <- deterministic
   7 | {6,14}                              | 2
   9 | {0,8}                               | 2
  11 | {10}                                | 1   <- deterministic
  13 | {12}                                | 1   <- deterministic
  15 | {6,14}                              | 2
```

Verified on 3,998 random semiprimes: theory matches for every residue.

**Operationally worthless.** For `N ≡ 3,5,11,13` the strut is a deterministic function of the
*public* modulus — 8 candidate pairs before, 8 after, zero gain. For the others it holds 1 bit
that is not public, and nothing here obtains it. 1 bit is the weight of the already-proven
`d ≡ e (mod 4)`.

### 4.2 ω = 3 (multi-prime): the three pairwise struts lie on a Fano line
`(p^q) XOR (q^r) = p^r` because `q^q = 0`. So the three pairwise struts **always** satisfy the
line condition. Measured on 6,000 random 3-prime moduli: 3,867 proper lines, all **7** lines
realised near-uniformly (527–595 each), 2,121 degenerate (two primes agreeing mod 16).

**But the XOR-to-zero is an algebraic identity, not a discovery**, and the narrowing fails its
control:

```
knowing the unordered line:   64 triples -> 6      (10.67x)
CONTROL, random line label:   64 triples -> 7.88
mechanism: pair-XORs fix the triple from ONE free element; 8 choices cut to ~6
           by the product constraint. Same trivial algebra as "subtraction
           undoes addition."
```

Knowing which strut belongs to which **pair** does collapse it 6 → 1 exactly — so ordering *is*
the operative quantity. But popcount orders struts *by value*, and struts are already
value-distinguishable; it does not order the **primes**, and the prime order is what induces
the pair assignment. The pathway is real but not yet anchored to the bodies.

### 4.3 The ceiling that closes it  [the decisive result]

```
solve the mod-16 layer PERFECTLY  ->  you learn p,q,r mod 16  =  ~9 bits
2048-bit 3-prime modulus          ->  9/2048  =  0.439%
```

**~9 bits regardless, forever.** A residue map has *fixed depth*; it does not scale with the
modulus. Solving it perfectly leaves a 2048-bit factorisation 99.6% untouched.

**So the obstruction was never the missing order — it is that `mod 16` cannot carry a
factorisation no matter how perfectly its geometry resolves.** The pathway structure is
carrier-independent; the carrier is what fails.

### 4.4 The carry chain — right carrier, no free lunch
Depth comes from **iterating**, and the multi-operation version of a modulus is its digit
expansion. The thing that remembers is the **carry chain**:

```
sum_j p_j q_{i-j} + c_i = N_i + 16·c_{i+1}
```

Measured: chain length grows **linearly** with the modulus (8 → 128 steps over 32 → 512 bits),
and only one position stays still. **The ceiling is gone.**

**⚠ Correction, made in-session:** the "831 carry bits" figure is a *description length*, not
entropy. The carries are a function of `(p,q)`, so their information content is capped by the
512-bit secret; 831 > 512 means the representation is **redundant**, not richer. No gain.

And knowing the carry chain **linearises** the digit system — which is another way of saying
recovering it is *equivalent to factoring*. The hardness was relocated into the memory, not
removed. Digit-wise factoring with carry propagation is also standard (it is how SAT encodings
of factoring work), so that part is not new either.

---

## 5. The three currents, and how they connect  [MEASURED]

`rotary_monad.py` lines 35-37 declare a closed bracket:

```
[J_blue, J_red ] = J_green
[J_red,  J_green] = J_blue
[J_green, J_blue ] = J_red
```

That is a **cross product** — the su(2)/quaternion bracket, `î×ĵ=k̂` etc. And
`_project_sedenion:447-451` gives the channels **disjoint support**:

```
J_blue  -> e1-e7      J_red -> e8-e14      J_green -> e15      e0 = coupling
overlap(red, blue) = EMPTY
```

**Consequence:** no purely additive expression in `J_red` can ever produce `J_blue`, because
addition never moves support between channels. Only multiplication does. So the bracket is not
one route among several — it is the only *multiplicative* route, and it needs J_green.

Three routes to J_blue, and they are genuinely different objects:

| route | form | mechanism |
|---|---|---|
| Dirichlet | `J_blue(σ) = J_red(1−σ)` | functional-equation reflection; they meet at σ=½ (the Mingling) |
| channel | `J_blue = [J_red, J_green]` | the cross product |
| bookkeeping | `J_blue = Σ_RB + 0_BR − J_red` | works *because* Σ_RB is a paired product, not an additive current |

The additive route is repairable only because `Σ_RB[k] = v[k]·v[k^4]` is a **product** and so
has support across blocks. Cody's proposed `J_red + 0_BR − 0_RB = J_blue` fails by exactly
`(0_BR − 2·J_blue)`: right three-term shape, `0_RB` where `Σ_RB` belongs and `+J_red` where it
needs `−J_red`.

Also `_lie_bracket:402` states the mechanism plainly: *"the housing topology breaks scalar
commutativity."* The antisymmetry lives in the **word-distribution index**, not in the scalar
magnitudes — scalars commute, so with magnitudes alone the cross product is identically zero.

---

## 6. Standing corrections and rules earned this session

- **A reducer must be valid on its data.** Two faults, one class: `argmax` on *signed* currents
  (returned index 0 because red/green run negative and the max of a signed array with negatives
  is a gated-off zero), and `min|neutral|` on *gated* data (identically 0 at 41/41 sample
  points, because raised-cosine port windows hit zero at their edges and the sample grid landed
  on every boundary). **Standing question before any reduction: is this reducer valid on
  signed, sparse, or gated input?**
- **Sigmoid = 2-class softmax**, verified to machine precision. So a sigmoid is a smoothed
  2-way argmax, and `max`/`min` relax to logsumexp/softmax. But note: gradients are **not**
  currently in scope for the monad — the only place a gradient has been asked for is
  BulletCluster. The regulator is derivative-free coordinate descent.
- **A resolution ceiling is a measurement OF the ceiling** (the Bruniquel Cave rule: C14 capped
  at ~47 kyr gave ~47 kyr; U-Th on the same stalagmites gave 176 kyr). Any result landing at an
  instrument limit needs a *different method*, not a better version of the same one.
- **"Lying" is the wrong word for a code fault.** No intention, and it makes the code the agent
  and the author the victim. They are engineering faults, with causes and preventives.
- **Read means read in full.** Partial reads caused a re-derivation of
  `nightmare_engine.niemeier_root_systems()` (which already generates the 23 rank-24 partitions)
  and a false "defect" report against `monster_gap_fill` whose clarifying sub-bullets made it
  correct.

---

## 7. What is genuinely open

1. **Anchor the pathway to the primes.** Pair-assignment collapses the ω=3 ambiguity 6→1.
   Popcount orders struts, not primes. What orders the *primes*? The **zeta index**
   `ζ(p) = min{n : γₙ ≥ 2πp/log p}` is the candidate: it is an *arrival order*, it is defined on
   the primes themselves, and γ* grows with p (137 → 917 → 37,130 → 454,793 across sampled
   primes), so unlike `mod 16` it has depth that scales. **Untested. Build it with the control
   in place from the start.**
2. **The β-weighted merge** (PTorrent, but it is monad mathematics): merging two bins built from
   overlapping corpora is not concatenation, because β is a learned per-token weight. Spec it
   before coding it.
3. **The three-phase rotor** (`cam3.py`, built today): crank == camshaft == one shaft; three
   faces at 120°; **5 lobes per face** (15 imaginaries ÷ 3) with e₀ on the axis doing no work.
   Measured: 6 neutral sign changes per rotor revolution, one-face-at-a-time holds exactly
   (multi = 0.000), regulate cuts neutral RMS 17.29% holding compression. **Caveats: one ψ, one
   seed, no control; ch04 hit the ±π/8 boundary so the optimum may be outside the clamp; and
   the 5/5/5 face map conflicts with `rotary_monad`'s 7/7/1, which is not three-fold symmetric
   and so cannot be three faces of one rotor.** That map choice is Cody's call and it changes
   what the engine *is*.
4. **The loss is the neutral current.** `|J_red + J_blue + J_green|` — zero neutral is the
   balanced-three-phase condition and the wiki-47 conservation law read as a circuit. It is
   independent of the trochoid loss `|R−e|`: neutral RMS measured identical (0.025975144) at
   every K from 1 to 9. **Two losses, two mechanisms — do not conflate them.**
