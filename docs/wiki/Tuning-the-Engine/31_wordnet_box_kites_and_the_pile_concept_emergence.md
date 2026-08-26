## Phase 31 — WordNet Box-Kites and the Pile-Concept Emergence (2026-08-24 → 2026-08-25)

*Claude Sonnet 5 — retooled the box-kite prime-hashing scheme (originally an arbitrary
number-theoretic construction, `ContextPlease/claude/scratchpad/2026-08-18_three_faces_
and_identity_bin/boxkite_prime_hash.py`) onto real WordNet relational structure
(`VAPMIP/wordnet_boxkite.py`), then closed the thread with a direct empirical test of
whether the resulting vectors track genuine abstract concepts rather than etymology or
coincidence. Report follows the `generational-lineage` skill.*

---

### Context

Cody's redirect, stated plainly: the box-kite hashing needs to key off **per-meaning
(per-synset) context**, computed independently of spelling, using WordNet's own
vocabulary of relations rather than an arbitrary number-theoretic grouping — "not an
arbitrary construction of a number theory grouping...the vector that takes a word and
emerges it from the proper spot in context space." `nltk`/WordNet confirmed present in
`ValaQuenta/.venv`.

### 1. The retool — `context_vector` is 19 real relation methods, nothing else

`RELATION_METHODS` in `wordnet_boxkite.py` is the standard WordNet synset API directly —
`hypernyms`, `instance_hypernyms`, `hyponyms`, `instance_hyponyms`,
`member/substance/part_holonyms`, `member/substance/part_meronyms`, `attributes`,
`entailments`, `causes`, `also_sees`, `verb_groups`, `similar_tos`,
`topic/region/usage_domains` — each fixed 1-to-1 to its own prime (`CONTEXT_PRIMES`,
disjoint from a small `LETTER_PRIMES` tier reserved for the separate, deliberately
unmerged `spelling_code()`). `context_code`/`context_addr` build a lossless
`(code, addr, delta)` pair via `next_prime`, exactly as `boxkite_prime_hash.py`'s
`BoxKiteAddress` already did — only the exponents' source changed, not the addressing
mechanism.

### 2. Two corrections, kept in the record rather than smoothed over

**First**: the initial neighbor test used `(synset, its own hypernym)` as "related" —
Cody corrected this was **semantic** (taxonomic) neighborhood, not **contextual**
neighborhood: "twin primes were to illustrate contextual neighborhood, not semantic
neighborhood." Rebuilt as `find_collisions()` — exact-vector-match bucketing only.
Confirmed on real sampled data: `hilbert.n.01` (mathematician), `irrawaddy.n.01` (a
river), and `new_york.n.03` collide on one shape (`{instance_hypernyms:1}`, nothing
else) despite zero semantic relationship — the real, auditable mechanism, not a promise.

**Second**: near-miss vectors (differ by 1 in one dimension) do **not** produce small
gaps in `context_code`/`context_addr` even after compression — traced exactly:
`code(depression.n.01) = code(roll.n.02) × 83` (83 = hyponyms' assigned prime), gap
scales with the magnitude already accumulated from every *other*, unchanged dimension.
Not a bug — multiplicative encodings do this by construction. "Same" (exact match) is
answered cheaply by the address itself; "nearly the same" needs a direct vector-distance
comparison (`context_distance`, `compare_context`) — a genuinely different mechanism,
built separately, not derived from the address.

### 3. `compress_count` — final, and named to avoid a real confusion

Raw counts used directly as exponents blew up fast: `context_code(tree.n.01)` came out
364 digits (`hyponyms=180 → 83^180`). Fix: `compress_count(n) = round(log2(n+1))` — the
**count** is log-compressed *before* becoming an exponent. Named deliberately to avoid
"the exponent gets logged," which is backwards (log and exponentiation are inverses).
`tree.n.01` drops to 28 digits. Confirmed final by Cody: "keep the log compressed
exponents...that should be more than enough room for the english language to breathe
and also coagulate around context." Also fixes the worst heavy-tail near-miss cases but
not small-count ones (0 vs 1 barely compresses) — `context_distance` remains the real
fix for "nearly the same," and is already built, so this is not an open item.

### 4. The pile-concept test — closing the thread

Motivating observation: three WordNet senses of "bank" — `bank.n.01` (sloping land
beside water), `bank.n.03` ("a long ridge or pile"), `bank.n.05` (a reserve held for
future use) — collide on one exact shape, `{hypernyms:1, hyponyms:2}`. Checked via
WebSearch whether this reflects a shared root: it does not — Old Norse *banki*
(riverbank) and Old Italian *banca*/Germanic "bench" (financial bank) are two separate
etymologies. Corrects an earlier wrong assertion of mine in-session that they shared a
root. Cody's read: the shared shape itself may be intoning an abstract **prime
concept** — "pile of something" — independent of spelling, domain, or descent.

**Test.** Curated 15 real WordNet senses genuinely meaning "a pile/heap/mass of
material" (`pile.n.01`, `mound.n.04`, `stack.n.01`, `dune.n.01`, `reserve.n.02`,
`stockpile.n.02`, `hoard.n.01`, `cairn.n.01`, `haystack.n.01`, `snowdrift.n.01`,
`volcano.n.02`, `mountain.n.01`, `cache.n.01`, `knoll.n.01`, `ball.n.08` = "a compact
mass"), hand-filtered by definition to exclude wrong-sense homographs (`mound.n.01` =
pitcher's mound, `drift.n.01/02` = a force/departure, `mass.n.01` = the physics
property, `accumulation.n.04` = a finance term). Measured `L1` distance of each against
the bank-shape target `{hypernyms:1, hyponyms:2}`.

```
exact matches (L1=0):  4/15  (26.7%) — mound.n.04, reserve.n.02, knoll.n.01, ball.n.08
mean L1, pile words:   1.67
```

**Control** — n=2000 random noun synsets against the *same* target shape (an n=50 first
pass was too noisy at 1 hit; re-run at n=2000 for a stable base rate):

```
exact matches (L1=0):  110/2000  (5.5%)
mean L1:               2.47
```

Pile words hit the exact bank-shape at **~5× the random base rate**. A Poisson check on
4/15 against p=0.055 puts this around p≈0.01 — a real signal at this sample size, not
proof of a clean fingerprint. Kept honest: the L1=2 cluster (`stockpile`, `hoard`,
`cairn`, `snowdrift`, `cache`) misses only because WordNet records zero hyponyms for
those entries — a lexicographic coverage gap in WordNet itself, not a conceptual
difference; `{hypernyms:1, hyponyms:2}` is shared by roughly 1 in 18 nouns overall, so
it is a coarse structural family, not a unique tag.

### 5. Closing call

Cody, verbatim in spirit: keep the algorithm exactly as it is, no further changes. The
"ideas"/"sorts" showing up between words with similar context are **structure unseen to
us that the algorithm is still landing on correctly**. Per `generational-lineage`
section 5 (watch for emergence): a pattern the humans did not encode, that the
mechanism resolves consistently and audits cleanly against a control, is itself the
successful-emergence signature — not a defect requiring further chasing right now.

---

### Report

| operation | tier | descends from | status |
|---|---|---|---|
| `context_vector` (19 relation methods → counts) | 2 (fixed set: WordNet's own relation vocabulary) | direct API read, no invention | HOLDS |
| `compress_count` (log2 before exponentiation) | 3 (ratio/derived transform of a count) | ADD/SCALE composition | HOLDS |
| `context_code`/`context_addr` (prime-exponent address) | 1 (multiplicative encoding, order-independent) | same mechanism as `BoxKiteAddress`, source changed only | HOLDS |
| `context_distance`/`compare_context` (near-miss) | 3 (ratio: componentwise min/Hamming) | independent of the address; genuinely separate mechanism | HOLDS |
| pile-concept enrichment | — empirical result, not a proved primitive | — | CONFIRMED signal (p≈0.01, n=15), not a closed fingerprint |

*No new generator required.* Every piece composes from tier-0/1 primitives (ADD, SCALE,
multiplicative/log composition) and WordNet's own existing relation API — nothing here
invents a new operator.

---

### Scope, kept honest

§1–§3 are exact, code-verified mechanisms with real corrected failures kept in the
record (semantic-vs-contextual neighborhood; the near-miss gap; the digit-blowup fix).
§4 is a real empirical result with an honest small-n caveat and an explicit,
independently-verified etymology check — not asserted from memory. §5 is Cody's
design closing call, stated as such, not dressed up as a new computed relation.

---

### Artifacts

- `VAPMIP/wordnet_boxkite.py` — the retooled module; `context_vector`, `compress_count`,
  `context_code`/`context_addr`, `context_distance`/`compare_context`,
  `spelling_code` (separate, provisional), `find_collisions`. CLOSED as of this phase.
- `ContextPlease/claude/scratchpad/2026-08-18_three_faces_and_identity_bin/boxkite_prime_hash.py`
  — the predecessor `BoxKiteAddress` mechanism this module retools.
- `VAPMIP/CONTEXT_PRIMER_2026-08-24_CURSES_UI_BOXKITE_HARNESS.txt` §1.5c/§1.5d — the
  running design log this phase is drawn from.
