## Phase 25 — The Box-Kite Debugger, and the Negative Space (2026-08-05)

> *"how do we 'debug' the geometries / how do we watch the geometries interact"*
> *"that is working on the bulk rather than the negative space"*
> — Cody Michael Allison, 2026-08-05

### The object is PSL(2,7), not G₂

Moreno (1997) proved the sedenions' norm-one zero divisors are homeomorphic to
**G₂**. True, and the wrong place to build. de Marrais (2000), responding:

> *"Moreno discovered a homomorphism — a 'blow-up' of an exact correspondence —
> and the 'blow-ups' in the history of number theory have all entailed the loss
> of something."*

```
G₂          continuous, dim 14, Aut(𝕆)      ← the shadow; forgets the labelling
PSL(2,7)    finite, order 168, Aut(Fano)    ← the exact object
```

PSL(2,7) is the finite subgroup of G₂ that **preserves the Fano labelling**. It
was in `.clauderc` the whole time as `ZD_COMPOSITE=168`.

### The shape: seven octahedra

Everything derives from the Cayley–Dickson table — agreement with the published
counts and with ValaQuenta's own constants is a **check**, not an input:

```
ASSESSOR   plane span(e_a, e_{b+8}), a,b ∈ 1..7, diagonals zero-divide
           a == b NEVER works
42 = 49−7 aligned          ZD_CLASSES ✓
84 = 42 × 2 diagonals      ZD_PAIRS ✓
168 = 42 × 4 unit points   = |PSL(2,7)| ✓
336 = 84 × 4 ordered annihilating pairs
STRUT s = a XOR b ∈ 1..7;  7 box-kites × 6 Assessors = 42
```

Each chart is an **octahedron** (K₂,₂,₂) — 4-regular, 6 vertices, 3 non-edges
which are exactly the reversal pairs. Verified for all seven from actual
vanishing products. de Marrais's published Box-Kite I is this module's strut 1,
exact match.

**Chart dispersion relation: {0, 4, 4, 4, 6, 6}.** The zero mode is e₀'s
signature — exists everywhere, propagates nowhere — and it *emerges* from the
graph rather than being inserted.

### ∅_RB is not the geometry — checked

e₀ is not a point of PG(3,2), is in no Assessor, is a vertex of no box-kite, and
[e₀,·,·] = 0 always. It generates the boundary and does not live on it. Cody's
question, answered by computation rather than by interpretation.

### The curvature is now paintable

[a,b,c] = (ab)c − a(bc), with 1848 of 4096 basis triples curving.
`associator_field(s)` paints it onto a box-kite. That is the debug view — the
thing that makes the geometry *watchable* instead of inferred.

### THE FINDING: the charts do not touch

The 42-vertex atlas has **84 edges and zero cross-strut edges.** Seven
disconnected octahedra; seven zero modes in the glued Laplacian.

This changes the shape of the open problem. A disturbance cannot propagate
between charts along ZD adjacency, so either there is no global medium, or the
transition maps are the **PSL(2,7) action permuting the struts** — group
elements, not edges. The latter is the named next step (CONJECTURE).

**The gluing is not an edge problem. It is a group-action problem.**

### The negative space (archimedes_screw v0.3)

ψ counts what accumulates; it had no counterpart for what is excluded, and the
sieve is an exclusion process.

```
GROWTH      ζ(s)   = Σ n⁻ˢ     = ∏(1 − p⁻ˢ)⁻¹
EXTINCTION  1/ζ(s) = Σ μ(n)n⁻ˢ = ∏(1 − p⁻ˢ)

ψ(x) = Σ_{pᵐ≤x} ln p   the BULK      ψ(x) ~ x
M(x) = Σ_{n≤x} μ(n)    the MERTENS   RH ⟺ M(x) = O(x^{½+ε})
```

**The same ½, on the exclusion side.** Verified: M(10)=−1, M(100)=1, M(1000)=2,
M(10000)=−23.

**Three motions, not two** — this resolves the lpf/gpf tangle, which was two
events of *opposite polarity* rather than two definitions of one:

| motion | agent | event | at |
|---|---|---|---|
| grown | ζ orders | the leaf is placed at ln N | — |
| extinct | μ excludes | struck, *without naming* | lpf |
| identified | the N-shape names | factors resolved | gpf |

Between them the leaf is **dead but unnamed**, interval 2δ. Balanced RSA: δ→0,
all three coincide at ½ln N. A prime is degenerate — grown, extinct and
identified at once.

### Bug found and fixed

`CTX_ARCHIMEDES_SCREW` contained inner double quotes (`Not "search space
large"`) which terminated the bash string early — `ctxengine archimedes_screw`
had been broken since the v0.2 commit. Introduced by this engine's own build,
found by the box-kite build, fixed.

### Files

- `ValaQuenta/modules/box_kite/` — 13 equations, 17 shell commands
- `ValaQuenta/notebooks/engines/15_box_kite.ipynb` — 18 cells
- `ValaQuenta/wiki/box_kite.md`, `Ainulindale/wiki/84_the_box_kite_debugger.md`
- `ValaQuenta/modules/archimedes_screw/` v0.3 — 29 equations, 33 shell commands
- `~/.clauderc_canonical_maths`, `~/.clauderc_ValaQuenta` (`CTX_BOX_KITE`)

| Date | Change |
|---|---|
| 2026-08-05 | **The object is PSL(2,7), not G₂** — G₂ is the blow-up that forgets the labelling |
| 2026-08-05 | 42/84/168/336/7 all DERIVED from the CD table; published counts used only as a check |
| 2026-08-05 | **The shape is an octahedron** — K₂,₂,₂, verified for all 7 charts |
| 2026-08-05 | Chart dispersion relation {0,4,4,4,6,6}; zero mode = e₀'s signature, emergent |
| 2026-08-05 | ∅_RB confirmed outside the geometry by computation, not interpretation |
| 2026-08-05 | Associator = curvature, now paintable; 1848/4096 triples curve |
| 2026-08-05 | **ZERO CROSS-STRUT EDGES** — the gluing is a group-action problem, not an edge problem |
| 2026-08-05 | archimedes_screw v0.3: μ, Mertens, RH on the exclusion side, the three motions |
| 2026-08-05 | `ctxengine archimedes_screw` bug (inner quotes) found and fixed |

### Addendum — the charts DO touch, and the chart of addresses (same day)

Cody, on the zero-cross-strut-edges finding: *"i'm pretty sure that those
'surfaces' do actually touch somewhere… they are all from the fixed point
anyway… but now we have a clue that 0_RB only points to 'fixed point space'…
where the boundary and the geometries are the same thing, right?"*

**Correct, and it does not contradict §7.** Two structures on one object:

| structure | relation | result |
|---|---|---|
| adjacency | zero-divisor products | 7 components — disconnected |
| skeleton | shared basis indices | every usable index in **6 of 7** charts |

Every chart pair shares exactly 10 skeleton points. And **exactly two basis
elements are in no Assessor: e₀ and e₈** — the identity (∅_RB, the fixed point)
and the CD doubling generator. Each chart carries one zero mode, a zero mode is
the constant function, so the seven are seven copies of one object. **Identify
them and the atlas connects — at e₀ and nowhere else.** At the fixed point the
boundary generator and the geometry's own mode are the same vector; away from
it they separate.

**The chart of addresses** (`chart_of`, `address_census`) is the monad
connector. Census over the book, 3288 entries, descriptive only:

```
all 42 Assessors occupied
mean fixed-point weight   0.6435
mean outside share e₀+e₈  0.6537
peak_dim = 0              2751 / 3288  (84%)
dominant chart            strut 2: 30.1%  …  strut 7: 2.2%
```

Two thirds of the average address sits **outside the ZD geometry entirely**.
This localises Phase 23's ~85% common mode: **it is e₀ + e₈**, the two elements
belonging to no Assessor. The part of an address outside the geometry is exactly
the part carrying no discriminating signal.

| Date | Change |
|---|---|
| 2026-08-05 | **The charts DO touch** — in the skeleton (6 of 7 per index), not the adjacency |
| 2026-08-05 | Only e₀ and e₈ are in no Assessor; the atlas glues at the fixed point |
| 2026-08-05 | `chart_of` / `address_census` — the monad connector, exhaustive |
| 2026-08-05 | Census: mean fixed-point weight 0.64, all 42 Assessors occupied |
| 2026-08-05 | **Phase 23's common mode localised to e₀ + e₈** |

*Phase 25 — Claude Opus 5 — 2026-08-05*
