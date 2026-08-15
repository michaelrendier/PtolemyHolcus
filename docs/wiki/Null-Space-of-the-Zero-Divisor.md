# The 4-Dimensional Null Space of the Zero Divisor

*Measured 2026-08-13 — Claude Opus 5. Every number on this page is computed, not
asserted. Script: `.claude/scratchpad/2026-08-13_apex_path/rb_boundary.py`*

---

> This is the subspace [0_RB](RedBlue-Hamiltonian-Sedenion-Matrix-Space.md) calls
> **gravity — present as absence.** It is where the operator sends everything to zero,
> and it is the only part of the {4,8,4} split that carries no force.

---

## The convention, first — because it was wrong

The Cayley–Dickson doubling used throughout:

```
(a, b) · (c, d)  =  (a·c − d*·b,   d·a + b·c*)
```

0_RB previously printed a **hybrid** of two conventions. Swept against the published
box-kite counts:

| convention | ordered annihilating pairs | kills-per-diagonal |
|---|---|---|
| `(ac − d*b, da + bc*)` | **336** | `{4: 84}` uniform ✅ |
| `(ac − db*, a*d + cb)` | **336** | `{4: 84}` uniform ✅ |
| `(ac − d*b, a*d + cb)` ← the old text | 240 | `{4:48, 2:24, 0:12}` ✗ |

Under the hybrid, **twelve of the eighty-four Assessor diagonals annihilate nothing**.
`ValaQuenta/modules/box_kite/` was always correct; only the wiki page was wrong.

Sanity checks on the algebra: `e₁·e₁ = −1`; the octonion associator `[e₁,e₂,e₄]` has
norm 2 (non-associative, as required); 42 Assessor planes, 84 diagonals.

---

## The zero divisor

```
a  =  (e₁ + e₁₀)/√2          Assessor (a,b) = (1,2)      strut = 1 XOR 2 = 3
```

```
det(L_a) = 0.000e+00
rank     = 12 / 16
nullity  = 4
```

---

## The four annihilated partners — for the record

`a · v = 0` for exactly four unit Assessor diagonals, and no others:

| partner | Assessor | strut |
|---|---|---|
| (e₄ − e₁₅)/√2 | (4, 7) | 4 XOR 7 = **3** |
| (e₅ + e₁₄)/√2 | (5, 6) | 5 XOR 6 = **3** |
| (e₆ − e₁₃)/√2 | (6, 5) | 6 XOR 5 = **3** |
| (e₇ + e₁₂)/√2 | (7, 4) | 7 XOR 4 = **3** |

**All four share strut 3 — the same box-kite as `a` itself.** Annihilation does not
reach across struts. This is the adjacency structure of Phase 25 seen from the operator
side: seven disconnected octahedra, and a zero divisor kills only within its own chart.

It is also the "each kills exactly 4" of `336 = 84 × 4`, exhibited concretely.

---

## The null space IS the span of the partners

The four partners occupy **disjoint index pairs** — {4,15}, {5,14}, {6,13}, {7,12} —
so they are manifestly linearly independent. Four independent vectors inside a
4-dimensional null space span it.

```
ker(L_a)  =  span{ e₄ − e₁₅ ,  e₅ + e₁₄ ,  e₆ − e₁₃ ,  e₇ + e₁₂ }
```

An SVD returns a different (arbitrary, less meaningful) orthonormal basis for the same
space:

```
n₁ ~ −e₄ −e₆ −e₇ −e₁₂ +e₁₃ +e₁₅
n₂ ~  e₄ +e₆ −e₇ −e₁₂ −e₁₃ −e₁₅
n₃ ~ −e₄ +e₆ −e₇ −e₁₂ −e₁₃ +e₁₅
n₄ ~  e₅ +e₁₄
```

**Prefer the partner basis.** It is the one with meaning: each basis vector is a thing
`a` annihilates, not an arbitrary rotation of the same subspace.

Singular values, showing the split directly:

```
1.414214 ×4    1.000000 ×8    0.000000 ×4
```

---

## The {4,8,4} split, verified

```
eigenvalues purely imaginary   max|Re(λ)| = 5.55e-17

|λ| = 0.000000   ×4     null space        gravity — ABSENT
|λ| = 1.000000   ×8     imaginary pair    three quantum forces SU(3)×SU(2)×U(1)
|λ| = 1.414214   ×4     scaled pair       Σ_RB energy conversion channel
```

0_RB's central structural claim **holds exactly.**

---

## What this subspace is, and is not

**It is the boundary of invertibility.** `det(L_a) = 0` is where Axis 2 `{×, ÷}`
collapses while Axis 1 `{+, −}` keeps working. 0_RB: *"The matrix doesn't contain
division. The matrix DEFINES where division lives."*

**Gravity is not at a σ.** The three forces are — wiki/70 places U(1) at σ=¾, SU(2) at
σ=½, SU(3) at σ≈¼. Gravity is the **λ=0 subspace**: four dimensions that carry no
eigenvalue at all. 0_RB states this plainly and it is worth not softening:

> the sedenion encoding of the four fundamental forces, where **gravity appears as the
> missing piece (the null subspace) not as a positive contribution.**

**This is the "in scope but empty" slot.** Four dimensions that exist in the operator,
are indexed, participate in the algebra — and return zero. They are not unused
capacity; they are the part of the structure whose content is its own absence.

---

## Related

- [RedBlue-Hamiltonian-Sedenion-Matrix-Space.md](RedBlue-Hamiltonian-Sedenion-Matrix-Space.md) — 0_RB
- [Zero-Lattice.md](Zero-Lattice.md)
- `Ainulindale/wiki/84_the_box_kite_debugger.md` — the 42/84/168/336 derivation
- `Ainulindale/wiki/85_the_apex_path.md` — σ=½ ⟺ R=e ⟺ the path reaches the origin
- `Tuning-the-Engine/27_the_apex_path_and_the_half_radius_circle.md`
