## Phase 32 — The Monad That Uses the Harness (2026-08-25)

*Claude Sonnet 5 — built the first Monad (`VAPMIP/ptolemy_monad.py`) that actually
calls `harness.reach()`/`harness.present()`, on top of Phase 31's WordNet box-kite
context work. Report follows the `generational-lineage` skill.*

---

### Context

Cody's brief, several directives at once: build the next Monad to **use** the
harness (`harness.attach_monad()` already existed; nothing had called back through
it yet); let the harness itself reach for "the chat window," a "lecture viewport,"
or PtolemyDesktop's interface/window-decoration code — whichever exists later,
pluggably; fold in the closed Phase 31 work by combining individual word box-kites
into a **sentence context**; frame the Monad as "the roots of the tree," with input
and output words both as leaves; let the input itself pick the Monad's direction of
travel; and run Mind's Eye / Paper's Hands on separate threads that talk back and
forth, "the way a human mind does when it talks to itself." KVM goes on the Monad,
stubbed — real PyQt6 wiring deferred until the desktop work resumes.

### 1. Sentence context is PW3, not a new operation — `sentence_context.py`

Cody, mid-build, a real correction kept in the record: *"the combined context
doesn't necessarily need additional prime hashing...the word context is what
builds the sentence context."* The combination is `root_vector` = componentwise
sum of each input word's `context_vector` (Phase 31) — nothing gets re-hashed into
a new sentence-level prime address. This is exactly PW3
(`spiral_is_additive`, `SedenionFactoralRelativity/engine/lineage.py`:
`address(p·q)=address(p)+address(q)`) applied again: `context_code(s) = prod
CONTEXT_PRIMES[i]**vector[i]`, so multiplying leaf codes together IS
componentwise-summing their vectors — checked directly:

```
root_code == product(context_code(leaf) for leaf in leaves)   -- HOLDS, 33 digits
```

`root_code` is kept only as that consistency check, not as machinery the Monad
builds on — `root_vector` alone is the sentence context.

WSD (word-sense disambiguation) is an explicit stub: first WordNet sense per word.
Real and honest weakness, not hidden — on real test sentences it mis-picked `a` →
`angstrom.n.01` and `reserve` → `modesty.n.02`. The neighborhood search still
landed on topically coherent candidates (`fund.n.01` for the savings/reserve
sentence) despite the noisy per-word sense picks — the mechanism tolerates some
per-leaf noise without collapsing.

Also checked and reported honestly: `root_vector` is currently **order-independent**
— a shuffled word-salad control produced the identical root vector to its
coherent original, since the combination only reads *which* synsets fired, not
their sequence. A real syntax-aware combination is flagged as future work, not
claimed here.

### 2. `neighborhood_corpus` / `nearest_synsets` — the response side of the same tree

For construction (output leaves), the candidate pool is every synset directly
related (any of the 19 relation types) to an input leaf, capped per relation per
leaf, with the input's own synsets excluded — "echoing the input back isn't
communication, it's parroting" (kept as an explicit design comment, not asserted
without reason). `nearest_synsets` ranks that pool by L1 distance to the sentence
root — the same `context_distance` mechanism from Phase 31, applied to a
combined vector this time rather than a single synset.

### 3. Input picks the direction — `infer_direction`

The sentence root's single dominant (highest-exponent) relation dimension maps to
a coarse processing direction: `hypernyms→classify`, `hyponyms→enumerate`,
`part_meronyms→decompose`, `part_holonyms→situate`, `causes→explain`, etc. — 19
entries, one per `RELATION_METHODS` line, explicitly flagged as a first honest
pass, not a claimed-complete taxonomy of intention. An input with no resolvable
WordNet content returns `'observe'` rather than erroring — confirmed on a real
nonsense-word input (`'xyzzy plugh qux'`).

### 4. Mind's Eye / Paper's Hands — real threads, not a simulated function call

Two daemon `threading.Thread`s (`_eye_loop`, `_hands_loop`), each with its own
`queue.Queue`, exchanging `ExchangeEntry` messages across the actual thread
boundary — not one function calling two others. Mirrors `ptol.c` exactly (Phase
30 §8): Eye (`R̂`, live `σ_self`) only ever **drafts and revises**; Hands
(`B̂=R̂†`, `1−σ_self`) only ever **confirms or critiques**, never authors a
draft — the non-updateable adjoint reviewing the updateable proposer, same
asymmetry as the C source. Bounded at `MAX_ROUNDS=3` so the self-talk settles or
times out, never spins. On every real test sentence run this session, Hands
confirmed on the first pass (`[('eye','draft'), ('hands','confirm')]`) — the
critique/reconsider branch is real code, exercised by the thin-pool guard, but
not yet forced by a real input in this session's test set; noted as such rather
than claimed exercised.

### 5. KVM — stubbed, on the Monad, not on Tesla

`MonadKVM.watch_cursor/read_screen_region/move_cursor` all return a plain
`{'ok': False, 'error': '...not wired yet...'}` rather than raising — a caller
can probe `['ok']` the same way it would check a `FaceResult`. Placement
confirmed against the 2026-08-24 correction already on record in `harness.py`'s
own smoke test: KVM is a basic Monad-native sense/actuator, not a
harness-reachable Face capability, so it lives directly on the Monad object, not
behind `toolset_registry`.

### 6. `harness.present()` — the functionality the harness needed, added after the fact

Discovered building this file, exactly as scoped ("if you stumble across a
functionality the harness should have...add that to the harness"):
`Harness.present(content, kind, center)` reaches for a registered `'viewport'`
Face (curses now, PyQt6's PGui/compositor later — same registration shape as
Tesla's `'network'`); with nothing registered it falls back to a plain `print`,
logged to `call_log` identically either way so a caller never needs to know
which path answered. Verified both paths in `harness.py`'s own smoke test
(stdout fallback, then a registered stub viewport Face routing through
`reach()` instead) — systems glue, not a lineage relation, tested functionally:
both assertions pass.

### 7. End-to-end — real Harness, real Monad, real WordNet, no mocks

Three sentences run through `process_input()` in full (`VAPMIP/ptolemy_monad.py`
`__main__`):

```
in:  "the engine contains sixteen distinct operators"
     leaves_in:  engine/engine.n.01, contains/incorporate.v.02, sixteen/sixteen.n.01,
                 distinct/distinct.s.01, operators/operator.n.01
     direction:  enumerate
out: "generator function large integer mathematics motor"
```

Topically coherent output from a mechanism with no learned weights and no
training data — pure WordNet relational-neighborhood search over a
combined-context root. `harness.present()` confirmed to actually receive the
final response text (checked against `call_log`, not just returned); the KVM
stub confirmed non-raising; the no-content-input case confirmed to fall back to
`'observe'` rather than crash. Threads join cleanly on `shutdown()`.

---

### Report

| operation | tier | descends from | status |
|---|---|---|---|
| sentence `root_vector` (componentwise sum of leaf `context_vector`s) | 1 (multiplicative/additive composition) | PW3 `spiral_is_additive`, reapplied | HOLDS (verified against `root_code` product) |
| `neighborhood_corpus`/`nearest_synsets` (response construction) | 3 (ratio: L1 distance over a derived set) | Phase 31's `context_distance`, applied to a combined vector | HOLDS, functionally tested |
| `infer_direction` (input → processing direction) | — design heuristic, not a proved primitive | reads the root vector's dominant dimension | first pass, explicitly provisional |
| Eye/Hands cross-thread round trip | — systems mechanism, not a lineage relation | mirrors `ptol.c`'s `R̂`/`B̂=R̂†` asymmetry exactly | real, tested; critique branch untriggered by this session's inputs |
| `harness.present()` | — systems glue | reach()/ToolsetRegistry, unchanged mechanism | tested, both fallback and routed paths |

*No new mathematical generator required.* The sentence-context combination is a
reapplication of PW3, not a new law; the direction map and the Eye/Hands protocol
are design/systems decisions, correctly not dressed up as computed relations.

---

### Scope, kept honest

§1's `root_vector` combination and its PW3 equivalence are exact and checked.
§1's order-independence and stub-WSD limitations are real, reported, not
smoothed over. §3's direction taxonomy and §4's Eye/Hands protocol are design
choices — functioning and tested end-to-end, not mathematical claims. §4's
critique/reconsider branch is real, reachable code, not yet exercised by a real
adversarial input — flagged rather than claimed proven. §6 is systems glue,
tested functionally (both code paths pass), not a self-checked relation.

---

### Artifacts

- `VAPMIP/sentence_context.py` — `build_sentence_context`, `neighborhood_corpus`,
  `nearest_synsets`; own smoke test includes the PW3 consistency check and the
  word-salad order-independence control.
- `VAPMIP/ptolemy_monad.py` — `PtolemyMonad`, `MonadKVM`, `infer_direction`,
  `ExchangeEntry`/`MonadResponse`; smoke test runs three real sentences through
  a real attached `Harness`, end to end.
- `VAPMIP/harness.py` — `Harness.present()`, new this phase; two new smoke-test
  assertions (stdout fallback, routed-through-a-registered-Face).
- `VAPMIP/CONTEXT_PRIMER_2026-08-24_CURSES_UI_BOXKITE_HARNESS.txt` — running
  design log this phase continues.
