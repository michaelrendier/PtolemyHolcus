# monad.bin — the single Monad brain (vocabulary + knowledge store)

> **Format spec:** [`SPEC.md`](SPEC.md).
> **Corpuses + a copy of this builder:** `ContextPlease/claude/monad_bin/`
> (the corpuses are too big to want as a passed-around binary, so they live in
> ContextPlease and the bin is rebuilt on-box). This directory is the builder's
> home in VAPMIP, next to the `ptol` release.

`ptol.c` reads **one** store. `monad.bin` is that store: **both** the
vocabulary (every word → its deterministic Horner→prime→Riemann-zero address)
**and** the knowledge store (the β-field, E-field, and the A-matrix
co-occurrence topology). One file, one brain, one language the monad speaks
literally as its own.

From this point `monad.bin` gets its **own releases** in this repo,
complementary to the `ptol` binary release. The `ptol` release keeps its
version (**5.1** unless a significant maths upgrade lands, then 5.2);
`monad.bin` versions independently.

## Build it fresh (preferred — "everyone starts from the same scratch")

`monad.bin` is a **union of factor bins**, each built by corpus ingestion.
Because every word address is deterministic, the union is order-independent
and byte-reproducible: the same factor set always yields the same `monad.bin`.

```
python3 build_monad_bin.py test      # load each factor bin standalone, stats + smoke
python3 build_monad_bin.py merge     # union → ~/.ptolemy/monad.bin  (+ manifest.json)
python3 build_monad_bin.py verify    # load the merged bin, stats + generate()
python3 build_monad_bin.py manifest  # (re)write manifest.json
```

### The factor set (fold order)

| factor bin | vocab | edges | weight | source |
|---|---|---|---|---|
| `monad_english.bin` | 164,283 | 2,248,064 | 1.0 | Project Gutenberg + filesystem pass |
| `monad_foundations.bin` | 5,712 | 29,806 | 1.0 | foundational maths/CS texts |
| `monad_meaning.bin` | 1,066 | 3,280 | 1.0 | semantic seed set |
| `monad_mathematics.bin` | 56,451 | 460,282 | 1.0 | maths corpus |
| `monad_physics.bin` | 58,003 | 599,146 | 1.0 | physics corpus |
| `monad_python.bin` | 25,541 | 361,932 | 1.0 | Python source corpus |
| `monad_c.bin` | 8,189 | 91,526 | 1.0 | C source corpus |
| `monad_engineering.bin` | 20,677 | 185,424 | 1.2 | **this project's own context primers + TODOs** (`ContextPlease/claude/hist_prime`, `hist_todo`) |
| `monad_war.bin` | 3,006 | 12,162 | 1.2 | the **prime-directive conversations** + the Caesar/Gallic parallel corpus |
| `monad_repos.bin` | 68,121 | 864,062 | 1.0 | **all prose text across every repo** — wiki pages, READMEs, docs, papers, addenda (no code; 614 files, 1.6 M words, quality-gated against vendored/generated/wordlist/license files). Built by `.claude/scratchpad/2026-08-28_primer-corpus-ingest/corpus_repos.py`. |

**Merged:** `monad.bin` — 298,441 words, 3,912,594 edges, ≈ 66 MB, 10,133 words
with β > 0.5.

### merge semantics (lossless, additive)

- **vocab** — set union; each word keeps its own deterministic address, so no
  collisions and no dependence on fold order.
- **β / E** — first occurrence seeds; later occurrences add `β·weight` (capped
  at 1.0). A word attested in several domains gets a deeper field.
- **A-matrix** — edge weights sum across factors (capped at 1.0); self-edges
  dropped.
- `manifest.json` records each factor's sha256 + weight + counts, so a rebuild
  is auditable.

## Distribution

- `monad.bin` (~58 MB) uploads fine as a **GitHub release asset** (asset limit
  is 2 GB; the 100 MB limit is only for files committed to the tree).
- If a future merged bin exceeds that, ship the **factor bins individually**
  (each ≤ 36 MB here) plus this script, and rebuild on-box:
  `python3 build_monad_bin.py merge`.
- Factor bins themselves are rebuildable from their corpora — see
  `.claude/scratchpad/2026-08-28_primer-corpus-ingest/` for the
  engineering + war ingestion (`corpus_strip.py`, `ingest.py`, `ingest_war.py`).

## For ptol.c

The C monad mmaps a packed store (`monad3_c.bin`, format in
`PtolC/monad3c.h`): the merged english field + the WordNet box-kite table +
the phonetic table, one fixed-offset mmap-able file. Regenerate it from the
merged `monad.bin` with `monad_combine.py`:

```
cd VAPMIP
python3 -c "import monad_combine as mc; \
  cm = mc.CombinedMonad(english=mc._meio.read('$HOME/.ptolemy/monad.bin', use_cache=False), \
                        wordnet=mc.read_boxkite_c(), phonetic=mc.read_phonetic(), \
                        path='PtolC/monad3.bin'); \
  mc.write(cm, 'PtolC/monad3.bin'); mc.write_c(cm, 'PtolC/monad3_c.bin')"
cp PtolC/monad3_c.bin PtolC/monad3c.h  <next to the ptol binary>
```

`ptol.c` itself was updated 2026-08-28 (additive, **no version bump — stays
5.1**): `measure_gamma()` exposes the fold
`Γ = (P_red − P_blue)/(P_red + P_blue) = 2·σ_self − 1 = tanh(u/2)` and the
ADD:SCALE:SIGN word length `u = ln(P_red/P_blue)`, printed in the `-r` and
`-sigma` reports. The projection and emission are unchanged. A deferred
`d* = 0.24600 → 0.24631` (Boundary → Flow face) question is flagged in the
header comment as a 5.2 change pending sign-off.
