## Phase 34 — The Anomaly, the Caustic, and the One File (2026-08-27)

*Claude Sonnet 5 — a long session that (1) put the recurring "heavy tail" through
the `generational-lineage` skill and got a verdict, (2) delivered the semantic
prime-hash retooling the primer's Part 4 named, (3) built the three-`.bin`
unification Phase 33 only planned, and (4) reframed the candidate pool as a
Newton-basin caustic with a pruner and a mind's eye. Report follows the skill.*

---

### Context

Continuation of Phase 33 (which *planned* the three-`.bin` unification and left
the semantic hash "not yet retooled"). This session opened on a scratchpad
investigation — `ContextPlease/claude/scratchpad/2026-08-27_spectral-vs-residual-hash/`
— of whether the phonetic side is genuinely *spectral* and the semantic hash
therefore *residual*. That produced a clean number (the tail index) worth a
lineage pass, which set up everything after it.

---

### 1. The Anomaly — a boundary condition on Laurelin, not a new generator

**Measured (CSN discrete power-law fit, `csn_powerlaw.py`, 12k synsets):** the
WordNet total relation-degree distribution is a genuine power law — tail
exponent γ = 2.73, stable-α = **1.73**, goodness-of-fit **p = 0.83**. It
decomposes by relation: the power law is carried by the **part/whole relations**
— `member_meronyms` (α 1.43), `part_meronyms` (1.51), `hyponyms` (1.85) — and is
*absent* from `hypernyms` (γ rails to 6, effectively bounded).

**Method error caught (skill §6):** an earlier McCulloch (`levy_stable._fitstart`)
pass reported "α = 2.00 everywhere" — that was the estimator **clipping to its
valid-range boundary** on sparse discrete columns, not a measurement. CSN (the
right tool for discrete counts) gave the clean sub-2 values above. Recorded as
a METHOD error: right code, right maths, wrong tool.

**Lineage trace (`lineage_anomaly.py`).** The tail is *born at G0* — the raw
`len(getattr(syn, method)())` counts, i.e. WordNet's own scale-free graph.
`compress_count` (the `log2`) then **suppresses** it (0/13 columns Lévy after
it); mean-centring **re-exposes** it as an artifact of sparse columns. Per-column
shuffle keeps the tail — it is a property of the *marginals*, not of
cross-relation composition.

**Verdict (skill §9): NO NEW GENERATOR REQUIRED.** The four §3 questions land it
on **tier 2 — a fixed set / corollary of the domain**. Two Trees: **Laurelin**,
the composite tree ("what IS decomposed into"), showing through in the
relation-count marginals. Every operation that touches it — count (tier 3),
`compress_count` (SCALE/DILATE, tier 1), the multiplicative code (tier 2), the
log (tier 0 ADD), mean-centre (tier 2), SVD rank-1 removal (tier 3→2) — is
DERIVED. None of the §5 emergence signatures fire.

**"Leave it in the maths"** — mandated, because it passes GoF (it's real), it is
the factoring relation's own signature (removing it deletes Laurelin from the
representation), and it is the boundary the composition runs *against*.

**The `√(-1)` reframe.** Tested (`zd_gain_and_tower.py`): the sedenion ZD gain
spectrum is `{0, 1, √2}` — annihilation is one of *three* branches, not the only
one. The inverse of annihilation is not gain-√2 (that is constructive
interference); it is that the product passes *through* 0 onto the imaginary
axis. A zero divisor in dimension `n` is the shadow of a genuine `√(-1)` in
dimension `n+1` — the Cayley–Dickson doubling seed `(0,1)²  = -1`. Same event,
two names: the new imaginary unit, and the annihilation it enables projected
back down. `i` = `√SIGN`, emerging at `ℤ/2 → ℤ/4` as the tower doubles.

---

### 2. `context_hash_v2.py` — the semantic prime hash retooled (primer Part 4)

Evolved from `wordnet_boxkite.context_vector` / `context_code`, nothing in that
(closed) file mutated:

- **ω/Ω split.** 18 relations carry supersense information only in their
  PRESENCE (ω-type); only `hyponyms` carries it in the COUNT (Ω-type — measured,
  depth-gain ≈ 0 on 18/19 relations, +0.007 on hyponyms). So
  `code_omega = ∏_{i≠hyp} p_i^{[v_i>0]}` — **squarefree**, radical = the support
  set, exact round-trip (4000/4000). `code_depth = p_hyp^{compress_count}`.
- **Log chart is the working coordinate.** The product is STORAGE
  (PW3-composable); `log_code = Σ v_i ln p_i` is native and keeps the α ≈ 1.7
  tail the `compress_count` renormalises away.
- **Gaussian-integer valued.** `unit ∈ {1, i, -1, -i}` from the phonetic origin
  (`(-1)^{syllable parity} · i^{primary-stress-index parity}`) — the `√(SIGN)`
  the pure-magnitude hash lacks. `reCORD` / `REcord` → `code` vs `i·code`,
  demonstrated on real heteronyms.
- **"Everything fires once" anchor** (Cody's pick): `LOG_ANCHOR = Σ_{i≠hyp}
  ln p_i`. `gamma_radial = tanh(½ ln(log_code / LOG_ANCHOR))` — <0
  dissertational, >0 narrative, ~0 at the anchor. Correlates with independent
  signals: relation count +0.64, hyponym depth +0.78, SemCor frequency +0.31.
- **Supersense Fisher:** old `context_vector` 0.329 → evolved 0.345 — modest,
  and the evolved form is simpler and exactly invertible.

**Two bugs found in the corpus test (`context_hash_v2.py` `__main__`), both
things the session had flagged:**
1. Folding `signed_code` (~e⁷⁰) instead of `log_code` saturates `tanh` to −1
   for every synset — violated the session's own "the product is storage, the
   log is the working chart" rule.
2. Folding `log_code · unit` mixes the phase into `Re(Γ)` via
   `tanh(a ± iπ/2) = coth(a)`. The phase must rotate the **output**:
   `gamma = gamma_radial · phon_unit`. Now `|Γ|` = semantic scale, `arg(Γ)` =
   phonetic — the clean `σ_RB = (r²/2)·sin(2θ)` split.

---

### 3. `constructor.py` rewired end to end

| axis | before | after |
|---|---|---|
| ring1 | L1 on 19-D `context_vector` | `radical_distance(seed_omega, code_omega(s))` — log-mass of the support-set symmetric difference — + the one Ω depth-gap + the faked `setting` term |
| ring2 | `\|syllables − target_syllables\|` | `\|cand_info_scale − output_scale\|`, where `output_scale = (1−register)(1−input_scale) + register·input_scale` — the **conjugate** (narrative ⟂ dissertational) relation. `cand_info_scale = ½·(short-word-ness) + ½·`gamma_radial`` |
| `_fake_setting` | — | seed's dominant supersense frame, content-side, stubbed like the WSD stub |
| `echo` | — | lineage counter passed through; loop drivers increment it and stop feeding output back at `ECHO_CAP` |

The narrative↔dissertational axis is the Phase-33-planned "scale ring" made
real: measured in the sum test (`recursion_step_factor.py`) — adding words drives
the combined tail index up (α 4.4→8.6 over n=1..15) and kurtosis toward 1, so
more words = more relational / lower density. Detail and relation are a
conjugate (Fourier-dual) pair.

`neighborhood_corpus` and this contextual vector are the SAME fold over the
seed's leaves in two semirings — the pool is the leaves' neighborhood under
set-**union** (the support), `u_root` is it under PW3 **addition** (the
weights). One contextual measure; context-building and semantic neighborhood
sit next to each other, not as two organs.

---

### 4. The Newton basins, the caustic, the pruner

**The pool is a Newton basin.** Roots = words; the co-occurrence A-matrix is the
dynamics; a seed iterated through it converges to a word. Topic-scoped bins
(`monad_physics.bin`, …) are sub-regions of the fractal. **The fractal basin
boundary is a caustic** — the envelope of the seed-trajectory family, singular
exactly where `det J = 0`, which is *also* the ZD condition and where `i`
emerges. One locus, three names.

**Cody's correction:** `basin()` as first wired is *neighborhood* maths (a
one-hop IDF-weighted co-occurrence set = topic strength), not *attractor* maths
(iterate to the focal point). Attractor maths = random-walk-with-restart on `A`
seeded from the input; the stationary distribution's concentration IS the
"catastrophic dumpout to a focal point" already in ptol.c's σ¹⁶ iteration
(`psi_prev` is the carried state). **Anisotropy** (from the sedenion product)
splits the single focus into **multiple focal points**, and the open question is
whether they are one object at different perspectives or genuinely separate.

**`context_pruner.py` — two functions, both off one basin collection:**
- `coherent(a, b)` — the diagnostic. Is there a **curved** perspective (unit-
  sedenion *multiplication*, not a flat SO(16) plane rotation — "god does not
  build with straight lines"; the gain spectrum `{0,1,√2}` means it isn't even
  an isometry) carrying one focal point onto the other? SAME / SEPARATE /
  AMBIGUOUS.
- `prune(vectors)` — pairwise `coherent` + union-find. A **schema extractor**:
  collapse perspective-redundant foci, keep the distinct ones. This is the
  narrative → dissertational transform as an *operation* (long-winded =
  perspective-copies of few real points).

`bank.n.01` (money) ↔ `bank.n.09` (river) → **SAME**, via a 2-step curved move.
Not a bug: the hash carries relation *degree*, not target *identity*, so it
correctly reports "one **pile schema** at different perspectives" — re-detecting
the Phase 31 pile-concept by an independent route. `prune()` on 8 vehicles →
merges `car + automobile + auto`, keeps the rest.

---

### 5. Three bins → one file

**`monad_english_io.py`** — `read` / `write` (atomic, `.bak`) / `deepen`
(`max(existing, new)` — repeats deepen context, never renormalise) / `hear`
(universal intake: everything the monad says, sees, hears, reads; unknown words
added, not dropped) / `neighbors` / `basin` (IDF-corrected, content-word gate:
primary-lemma check kills acronym expansions like `an → associate_in_nursing`).
Wired into `neighborhood_corpus` as a second candidate source alongside WordNet
relations. `basin(['cook','kitchen','recipe'])` pulls `condiment, churn, liquor`
— cook-vocabulary WordNet relations alone don't give.

**The ears vs the mind's eye (Cody).** Feedback from the ears —
`speak → hear() → deepen() → speak` — is real recursion; uncapped it
**stack-overflows**. `ECHO_CAP = 5` bounds it: content that has looped back 5×
stops being heard; external input is always echo 0. The **mind's eye** —
"rethink a phrase repeatedly" to set an alarm or hold a shopping list — is a
**flat held loop**: `rehearse(intention, times)` does no output, no `hear()`, no
`deepen()`, no RNG. It cannot overflow (iteration, not recursion) and is not
feedback ("just repetition unphased by noise"). Work is exchanged for salience
on a held intention, nothing else. Verified: 5,111 rehearsals leave the
A-matrix untouched.

**`monad_combine.py`** — `combine()` reads all three source formats
(`c_monad_wordnet.bin` C-binary `BXKT` 82-byte `BoxKiteEntry`; `monad_phonetic.bin`
`PHON`; `monad_english.bin` pickle) → one `monad3.bin` (57.7 MB, `read()` in
1.1 s, **536 MB RSS**). `CombinedMonad.lookup(word)` hits all three at once.

**`monad3_c.bin` + `monad3c.h` — the mmap-able, low-bandwidth form.** Fixed
offsets, packed structs read in place: no pickle parse, no copy, no alloc on
load. **`WordRec` is a 4-tuple** `(name_off, eng_idx, wn_idx, phon_idx)` — one
binary search on the sorted word table → indices into all three stores (Cody:
"easily a single tuple solution"). The A-matrix is **CSR** (`rowptr / col / w`)
— no pointer-chasing, cache-linear. `read_c()` is the Python mirror of what
ptol.c would do. *The pure-Python `write_c()` emit is slow (per-token
`struct.pack` over ~150k phonetic + 146k boxkite entries) and needs a
vectorisation pass; the format is settled.*

**Not done, deliberately.** `ptol.c` (1039 lines — Dirichlet sedenion
projection, Noether σ, J_red/J_blue shells, SVG/PPM/HTML rendering, curses
windows) was **not** rewritten from scratch. Stale build artifacts (`*.o`, the
old binaries) were archived to `PtolC/.archive_2026-08-27/`; all source and data
are intact. The migration is incremental: swap ptol.c's `ptol_layer.py`
shell-out for `mmap(monad3_c.bin)` + the `monad3c.h` structs, then port the
language-center functions one at a time with the Python as reference, keeping
the sedenion geometry engine as-is.

---

### 6. Operations used — tier / descent / status

| operation | tier | descends from | status |
|---|---|---|---|
| `len(relation_targets)` → the count | 3 | COUNT of a fixed set | DERIVED |
| `compress_count` (`round(log2·)`) | 1 | SCALE iterated (a DILATE) | DERIVED |
| `code_omega` (squarefree ∏) | 2 | SCALE composed (product) | DERIVED |
| `log_code`, `radical_distance` (gcd → additive) | 0 | ADD (log returns product to sum) | DERIVED |
| `phon_unit` (`(-1)^a · i^b`) | 0→ | SIGN, and `√SIGN` = `i` at `ℤ/2→ℤ/4` | DERIVED (branch, not graft) |
| `gamma_radial` = `tanh(½ ln(·/anchor))` | — | the Möbius fold `= (Z−Z₀)/(Z+Z₀)` | DERIVED (Scale engine) |
| mean-centre / SVD rank-1 removal | 2 / 3→2 | ORIGIN fixed set / REFLECT + ratios | DERIVED |
| RWR / personalized PageRank on `A` | — | iterated SCALE (power iteration) + ADD (restart) | DERIVED |
| curved `coherent()` (unit-sedenion `L_u`) | — | sedenion product; **not** an isometry | DERIVED |
| `prune()` union-find | 3 | COUNT of equivalence classes | DERIVED |
| `rehearse()` flat loop | — | ADD (salience += work), no recursion | DERIVED |

**The Anomaly** — no new generator; tier-2 boundary condition on Laurelin.
**`i`** — not a graft; emerges at the doubling boundary as `√SIGN`, `ℤ/2 → ℤ/4`.
**No §5 emergence signature fired this session** — everything built descends by
composition from ADD / SCALE / SIGN.

---

### ADD / SCALE / SIGN — the floor made importable

The table above was written by hand each phase. It is now a function.

- `add_scale_sign.py` (new, VAPMIP root) — the shared primitive the
  `generational-lineage` skill §1 named but never carried. `classify` /
  `describe` run the §3 four-question test; `root_of` walks any DERIVED
  operation past REFLECT/DILATE to the one tier-0 root under it. `AFF1` names
  `Aff(1,ℝ) = ADD ⋊ (SCALE × SIGN) = (fold count) ⋊ (size × direction)`,
  bracket `[SCALE, ADD] = ADD`. `FINDINGS` carries this session's
  decomposition paths (primes = SIGN recursed over the prior-primes pathway;
  factorial = the multiplicative integral, exact inverse `n!/(n−1)! = n`;
  `e` = quantization; **folds not steps**).
- `e10_generational_lineage.py` **R9** `r_add_scale_sign_floor` — measures the
  floor instead of asserting it: sedenion ZD gain spectrum `{0, 1, √2}` (two
  identities free, one irrational price), and **105/105** non-commuting unit
  pairs disagree by a pure sign flip. 9/9 relations hold. `decompose_operation`
  added as the module entry point.
- `SFR/engine/lineage.py` — `root_irreducible()` (with a printed `root_path`),
  `ROOT_OF`, `AFF1`; `decompose()` gains a `root` key. The 40-entry `TIERS`
  table is unchanged.
- Reference page: `ValaQuenta/wiki/add_scale_sign.md`.

### The Sieve IS the generational lineage

Cody's bet — *"the Sieve IS Generational Lineage ... fibonacci under factoring
waves ... the list of primes is the list of decompositional order"* — tested,
7/7 (`.claude/scratchpad/2026-08-27_sieve-is-lineage/`):

| | result |
|---|---|
| `generation(n) = π(spf(n))` | exact — the ordered prime list **is** the decomposition order |
| one forward sweep, `π(√N)` passes, no backtracking | **why the lineage is stable** — one pass per prime, not a convergence |
| Legendre `φ(x,a)=φ(x,a−1)−φ(x/pₐ,a−1)` | Fibonacci's 2-term shape; 2nd term SCALE-shifted by a prime, not `+1` |
| `φ = Σ_{d\|Pₐ} μ(d)⌊x/d⌋` | ADD ∘ SIGN ∘ SCALE — signed division waves |
| ordering | prime set + partition order-invariant; `gen = π(spf)` and min entropy **only** for the ordinal order; ζ-weight `ln p/√p` scrambles it |

Wired: `e10` R10–R12 + `sieve_lineage()`; `SFR sieve_lineage` / `sieve_recurrence`.

### The biological factoral tower (stub)

`SFR/engine/bio.py` — `TOWER_LEVELS` (knot 𝕊/16 → molecule T₃₂ → DNA T₆₄ →
protein T₁₂₈ → genome T₂₅₆), `molecular_decomposition` / `dna_decomposition`
as `plan_only` stubs. Structural only — **no medical inference**. ADD = the
reading frame, SCALE = the tower level, SIGN = chirality / strand sense.

---

### Forward

- `write_c()` vectorisation (the format is done; the emit is slow).
- `basin()` as attractor maths (RWR + `psi_prev` as carried state), not the
  one-hop neighborhood measurement.
- `topic=` strength coupled to `(1 − input_scale)` — a myopic seed topic-locks
  its own basin.
- The anisotropic multi-focal test: rotate the sedenion spheres, check whether
  the foci are one object at different perspectives (invariant caustic type,
  merge under a subgroup) or genuinely separate (independent orbits).
- The incremental `ptol.c` migration onto `monad3_c.bin`.
- The compositional recursion — word → sentence → paragraph → book, same fold
  via PW3 summation; whether the caustic types stay `fold`/`cusp` up the tower.
- **The algorithmic decompositional analysis tool** — one interface over
  `factor_lineage` / `pathway_decomposition` / `unit_lineage_decompose` /
  `root_irreducible` / `sieve_lineage` / `bio.*` that takes an arbitrary
  structured object (number, process DAG, unit signature, molecule graph,
  symbol stream) and returns its factoral lineage + ADD/SCALE/SIGN reading.
  The `bio.py` parsers (SMILES, codon stream) are the first two clients.
