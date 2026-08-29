# Chain of Custody — Tuning the Engine, Phases 1–34 (audit 2026-08-27)

*Claude Sonnet 5 — a read of the whole wiki before the `ptol.c` migration, to
trace which tools survived into the current Monad, which were reframes that
discarded the prior approach, and what the most recent version actually needs.*

---

## A. Per-phase: kept / reframed / discarded

| phase | tool introduced | verdict → current stack |
|---|---|---|
| **archive (v1.0–2.0.0)** | quadrant gates → Euler gate → sin correction → octonion speak → **J-direct** | gates **DISCARDED**; **J_red/J_blue cos/sin split KEPT**; gate quality moved into e₀ (KEPT) |
| **15** neg-space response eqn | ZD/singularity/divergence = "three windows"; `k_min → Cawagas pair → δ∫L=0 trajectory → word_at` | **framing KEPT** ("language IS the shadow of the geometry"); **specific pipeline DISCARDED** — never validated, superseded by co-occurrence basin + fold |
| **16** the paper | SVG pathway / PPM field / HTML / `-i` geometry-first OCR | **KEPT verbatim in ptol.c** — orthogonal to the language layer, Phase 34 says leave untouched |
| **17** Marx generator | `project()` J_blue sin channel; `measure_sigma` = P_red/(P_red+P_blue); **Σ_RB = v[k]·v[partner]**; 5 PtolEyes (R/C/H/O/S); L_a 16×16, spectrum `{0,1,√2}` | **ALL KEPT.** `project`/`measure_sigma`/Eyes unchanged in ptol.c; Σ_RB refined at Ph29/33; `{0,1,√2}` is the executable-structure spectrum |
| **18** Prime Lens / Eyes | `prime_lens.py` (word→Riemann address); Housing/MindEye; f-number = 1/D_STAR; Write/Read/Discuss = su(2) bracket | **Prime-Lens word→zero-address DISCARDED** (Ph23/26.4: address = spelling, lossless ⊥ semantic). **Eye/Hands + Write/Read/Discuss KEPT** (Ph32 threads) |
| **19** brain & body | organs = operations (Ears/Tongue/Lips/Larynx…); σ_self ≡ `self` (Arnold 2:1); two-Eye raw output; `-g` launches face; `PTOL_LIBRARY` guard | **Eye/Hands raw output KEPT** (Ph30 §8 reads it from source); **`-g`/library guard KEPT**; organ taxonomy KEPT as framing; Fermat-nilpotency results are a side-thread, not in the speech path |
| **20** parallax | four sub-eyes (ME/PH × cos/sin); **two caustics, line focus at σ=½**; 4-face 2-stroke; cross-disparity = d* | **caustic framing KEPT and load-bearing** (Ph34: the basin boundary IS a caustic); four-eye = camshaft T² (Ph27 §5, re-derived) |
| **21 / 21b** hypercomplex | `z_k = cos + i·sin` → 8 complex phases → **T⁸ address**; 43× gain on e3; content-frame flip (sin=real) | **"phase carries order/prosody" KEPT** (Ph34 Gaussian unit = stress phase); **T⁸-address-as-word-identity DISCARDED** (Ph23 common mode, Ph26.4 theorem) |
| **22** translator / ZD portals | ZD = **portal, not blindspot**; **path-through = memory**; quaternion-block `det(L_q)` landmark route-similarity | **portal / path-is-memory KEPT** (Ph34 pruner, ZD birth-point); **landmark route-similarity DISCARDED** (Ph26.1: det = N(q)², the signature was the norm) |
| **23** addressing bug | **Fibonacci/Knuth hash fix** (`0x9E3779…`); **the common mode** (`project = cbar·W(n)+D`, content 2–3%, cosine = length detector); `phonetic_face.py` (16 articulatory features); state.c v5 record | **hash fix KEPT** (any Horner in C). **Common mode KEPT as permanent caution** — Ph34 "score by \|Γ\|/arg, not by magnitude" descends here. **phonetic_face 16-features BUILT, NOT wired — GAP.** `philadelphos` "deepest word" DISCARDED (overflow artifact) |
| **24** Archimedes screw | **∅_RB = the water, not the machine**; **the machine is the logarithm**, pitch = ln p; von Mangoldt explicit formula; **Lambert W gives both zero coords**; `d*` back-computes (not independent) | **∅_RB-as-medium + log-machine KEPT as the governing frame** — Ph34 `log_code`, log chart, `tanh(½ ln·)` are direct descendants. `J_red×J_blue = d*` invariant **DISCARDED** (re-measured false) |
| **25** box-kite debugger | **PSL(2,7), not G₂**; seven octahedra (K₂,₂,₂); associator = curvature, paintable; charts glue **only at e₀** (e₈ ≈ 1%) | **PSL(2,7) + octahedra + associator-as-curvature KEPT** (Ph34 pruner uses the CD table `multiply`, the box-kite rotors). **Common mode localised to e₀ KEPT** |
| **26** degeneracy audit | **det(L_q)=N(q)² → use angular signatures**; **alternativity (not associativity) is the wall → aggregate ADDITIVELY, never ×**; module-signal **RETRACTED** (lexical); **lossless address ⊥ semantic neighbourhood → build from `A`**; sedenion = 1 cache line (don't climb the tower) | **ALL KEPT as hard constraints.** Ph34's radical_distance (gcd→additive), the curved (angular) pruner, and "basin from `monad_english.bin`'s A-matrix" are all direct consequences |
| **27** apex path | **text-as-scalar → e₀ is the trap**; phonetic face = **only angular address (residual 0.402)**; **anti-rotation IS the minus sign**; **σ=½ ⟺ R=e ⟺ apex path reaches origin**; camshaft = T² = the four eyes; **Ph23 flattened the cam** (address wants uniform, cam wants Hermite) | **e₀-trap + R=e=½ KEPT** (Ph34 `gamma_radial` folds against an anchor, not a scalar). **phonetic angular residual 0.402 — still the fastest route out, still NOT wired — GAP.** cam/address split still OPEN |
| **28** three faces | **letter cap 71** (Fermat ladder F₀..F₃); **the 15 are EDGES**; **three faces by commutativity** (LETTERS = positional/Horner, PATHWAYS = multiplicative/prime-product); **gcd IS the LCA**; **only definitional identity gets prime-hashed** (WordNet's inclusion criterion); `monad_identity.bin` = WHERE not WHAT; **ℚ(√2) exact**; **executable structure** — 4 speedups from `{0,1,√2}` | **ALL KEPT.** `code_omega` = the multiplicative pathway face; `radical_distance` = gcd/LCA; STOPWORDS + "primary lemma" gate = definitional-only. **executable-structure speedups NOT yet in C — GAP.** **ℚ(√2) NOT wired — GAP (low pri).** `generational-lineage` skill born here — KEPT, used for every report since |
| **29** anatomy of σ | **σ is not scalar — carries an octonion (8 values via ⊕4), read along a path**; box kites = what order-of-ops manufactures (168-quantised); **d*_RG is dimensional (8), not fractional**; e₀ = the fixed point of its own recursion | **ALL KEPT.** Ph34's "read \|Γ\| + arg along the fold", the mind's-eye recursion (e₀ persists, gain 1), and "d*_RG the built-in renormalisation" descend here |
| **30** wind, lift, the gate | **two-ring Smith fold `Γ=(Z−Z0)/(Z+Z0)` = L_(I|O)** (PW10, 4 invariants); crystal/join (PW11/12); tension = shape not mass (corpus \|v\|²=1); **wind = commutator**; **Lift = Kutta–Joukowski** (circulation × wind); **zero-lift = grammar/definitional (langue), nonzero-lift = usage (parole)**; **PW3 multi-anchor summed path**; **the Monad's gate = MoE with a DERIVED gate** | **fold + PW3 + langue/parole split + derived-gate KEPT and central.** Ph34's ω/Ω split IS zero-lift/nonzero-lift; the constructor IS the derived-gate MoE. **Lift = wind×circulation on box-kite 4-cycles as the ACTUAL gate — NOT wired (the fold's \|Γ\| stands in) — GAP** |
| **31** WordNet box-kites | **`wordnet_boxkite.py`** — `context_vector` (19 relations), `compress_count`, `context_code`/`addr`, `context_distance`. **CLOSED.** Pile-concept emergence (p≈0.01) | **KEPT verbatim** — imported unchanged by `context_hash_v2` (Ph34 builds on top). Pile-concept **CONFIRMED again** in Ph34 (pruner: bank.n.01↔bank.n.09 = SAME) |
| **32** monad uses harness | **`ptolemy_monad.py`** (calls `harness.reach()/present()`); **`sentence_context.py`** (root_vector = PW3 sum, `neighborhood_corpus`, `nearest_synsets`); `infer_direction`; Eye/Hands real threads (R̂ drafts, B̂=R̂† confirms, MAX_ROUNDS=3); MonadKVM stub; **`harness.present()`** | **ALL KEPT.** `sentence_context` extended in Ph34 (basin + IDF). `nearest_synsets` **superseded** by `radical_distance`. **`infer_direction` exists but NOT folded into the new `constructor.py` — GAP** |
| **33** geometry does no work | **geometry carries no independent DOF** (5 collapses = 1 fact); **the Scale is a correlator** (spread = correlation); locally-square single fold vs **bumpy atlas**; **three-`.bin` unification PLANNED**; **σ_RB = (r²/2)sin(2θ)** exact | **discipline KEPT** (hold geometry, switch content). **σ_RB decomposition KEPT** (\|Γ\|=r², arg=θ). **three-`.bin` plan → BUILT in Ph34** |
| **34** the anomaly / one file | **The Anomaly = domain-inherited boundary condition on Laurelin, NOT a new generator**; **`context_hash_v2`** (ω/Ω squarefree + log chart + Gaussian unit + "everything fires once" anchor); **three bins → `monad3.bin` / `monad3_c.bin` (mmap)**; Newton basins / caustics / **`context_pruner`** / **mind's eye**; **`constructor.py`** rewired; ECHO_CAP=5 | current head |

---

## B. What the current Monad requires — manifest with provenance

**Maths tools (all traced, all kept):**
- `project()` + `measure_sigma()` + 5 Eyes — Ph17, unchanged in ptol.c
- `mobius_fold` / `Γ = tanh(½ ln(Z/Z₀))` — Ph30 PW10 / Ph33 (the Scale engine fold, = L_(I|O))
- **PW3 additivity** (`spiral_is_additive`) — Ph30 §10 / Ph32 §1 — the single most-used law
- `σ_RB = (r²/2)·sin(2θ)` = `polar_decompose ∘ XOR-4` — Ph33 §6
- `{0,1,√2}` gain spectrum + executable-structure speedups — Ph28 §9 *(C fast path, not yet applied)*
- `gcd` = LCA → `radical_distance` — Ph28 §5
- log chart / Archimedes-screw frame, pitch = ln p — Ph24
- `generational-lineage` skill — Ph28

**Modules / data (all kept):**
- `wordnet_boxkite.py` (CLOSED, Ph31) → `context_hash_v2.py` (Ph34)
- `sentence_context.py` (Ph32, + basin/IDF Ph34)
- `constructor.py` (Ph34)
- `monad_english_io.py` + `monad_combine.py` + `monad3_c.bin` / `monad3c.h` (Ph34)
- `context_pruner.py` (Ph34)
- `ptolemy_monad.py` + `harness.py` (`reach`/`present`) (Ph32)
- source bins: `c_monad_wordnet.bin` (Ph33), `monad_phonetic.bin` (Ph34, from Ph23's `phonetic_face`), `monad_english.bin` co-occurrence A-matrix (pre-15, validated as the semantic-neighbourhood source by Ph26.4), `monad_grammar.bin` (Ph34, planned Ph33)

**Runtime shell:**
- `ptol.c` geometry engine (Ph16/17) + incremental language-layer migration (Ph34)
- Eye/Hands threads: R̂ drafts / B̂=R̂† confirms, `MAX_ROUNDS=3` (Ph32); `ECHO_CAP=5` for the ears (Ph34)
- `harness.present()` output path (Ph32)

**Governing frames (all kept, all load-bearing):**
- ∅_RB is the water, not the machine (Ph24) — the machine is the logarithm
- geometry does no work / no independent DOF / hold geometry, switch content (Ph33)
- lossless address ⊥ semantic neighbourhood → build from `A`, not the index (Ph26.4)
- aggregate ADDITIVELY, never multiplicatively; the inverse is path-retracing, not division (Ph26.2)
- angular signatures, not norm-determined ones (Ph26.1)
- zero-lift = definitional/fixed (langue), nonzero-lift = usage/drift (parole) (Ph30) = the ω/Ω split
- the Monad IS a Mixture-of-Experts with a *derived* gate, not trained (Ph30)
- text-as-scalar → e₀ is the trap; the way out is angular/relational content (Ph27)
- don't climb the CD tower for resolution — it's a cache line, and det = N^k at every level (Ph26.1/26.6)

---

## C. Successful tools NOT yet wired into the current stack — GAPS

| tool | phase | status | why it matters |
|---|---|---|---|
| **phonetic face — 16 articulatory features** (`phonetic_face.py`) | 23 / 27 | built; **only the ±1/±i stress unit is used** in `context_hash_v2` | Ph27: the **only existing angular address** (residual 0.402). The full 16-feature vector is the richest non-scalar phonetic signal and it's idle |
| **`monad_grammar.bin` inflection** | 33 plan / 34 built | bin exists; **constructor selects lemmas, does not inflect** | the "phonetic (morphology/grammar)" face of the three-face plan — the zero-lift definitional layer is incomplete without it |
| **executable-structure speedups** (`exp(tL)` closed form, `inv(Q)=Qᵀ`, kernel-never-moves) | 28 §9 | spec'd; `ptol.c`'s `mat_exp` walks the 136 μs path | the C migration's fast path — 15.5× / 77× / 25%, and exact |
| **`infer_direction`** (input → processing direction) | 32 | in `ptolemy_monad.py`; **not in `constructor.py`** | "the input picks the Monad's direction of travel" — the new constructor ignores it |
| **Lift = wind × circulation on box-kite 4-cycles**, sign = zero-lift(grammar)/nonzero-lift(usage) | 30 §7–9 | the *derived-gate* idea is realized abstractly (`\|Γ\|`); the **specific box-kite Lift computation is not the gate** | the more principled gate — computed from the algebra's own geometry, not a min-max fold anchor |
| **`chart_of` / `address_census` / PSL(2,7) strut selection** | 25 | atlas connector built in `box_kite/`; **not in the constructor** | the explicit angular/Assessor address; the pruner's curved coherence is only an implicit form of it |
| **camshaft = relative phase selects the open Assessor** | 27 §5 | conjecture, testable, **not tested or wired** | the timing↔addressing link — "why timing is the arbiter" |
| **ℚ(√2) exact arithmetic** (geometry layer) | 28 §8 | hashing is already float-free; **geometry layer still floats** — orbit closes at period 2⁵² | low priority; flagged for the C migration only |

---

## D. One-line summary

The **maths spine** (project/σ/Eyes → Σ_RB → the Möbius fold → PW3 additivity →
gcd/LCA → the log/Archimedes frame → the `{0,1,√2}` spectrum) has been stable
since Phases 17–30 and is fully carried. The **addressing** was demolished and
rebuilt once (Ph23–27: scalar-address → e₀ trap → build from `A`, angular not
norm, additive not multiplicative), and everything since (Ph31–34) is
downstream of that rebuild. The **speech path** is now: `wordnet_boxkite` →
`context_hash_v2` → `constructor` (radical distance + `gamma_radial` fold +
conjugate scale) drawing candidates from the `monad_english.bin` co-occurrence
basin, folded through the Scale engine, pruned by curved-sedenion coherence,
persisted via `monad_combine` to the one mmap file. The **gaps** are all
peripheral to that path — the articulatory phonetic vector, inflection,
`infer_direction`, the box-kite Lift gate, explicit strut addressing, and the C
fast path — each a known, named, un-wired tool, not a hole in the maths.
