# Grammar Resources for `monad_sentences.bin`

*Companion to [King's Maille — Box-Kite Rings as Sentences](Kings-Maille-Box-Kite-Rings-As-Sentences.md)
and `Ainulindale/wiki/119_unified_chainmaille_theory.md`. Written 2026-09-05.*

`monad_sentences.bin` is a higher-order `monad_wordnet.bin`: where WordNet gives
lexical nodes (synsets) and a few semantic relations, this adds the layer above
the word — **verb valency, clause construction, and the dependency skeleton** —
so the monad can *check* a sentence's construction, not only generate words.

The check is an `L_(I|O)` reading: you are always given `theta` (the words) and
never `beta` (the intended construction). You infer `beta` by **reduction to the
shadow**, run it forward, and see whether the shadow it casts is consistent with
`theta`. Descent (reduce) is free and single-pass; only the lexical granularity
costs, and it is a bounded frame-lookup, not a search.

Corpora live in `datasets/` (`.gitignored`; `bash datasets/fetch.sh`).
Stay with **standard usage only** for now — no wordsmithing, no figures.

---

## 0. The reduced / negative shadow

The **shadow** of a sentence is the sentence with the lexis stripped, keeping the
structure:

    words        →   POS sequence
                 →   dependency graph   (verb-rooted, ~37 UD edge labels)
                 →   function map       (S P O_d O_i C_s C_o A  — SPOCA)
                 →   clause pattern     (one of the 7: SV SVO SVC SVA SVOO SVOC SVOA)
                 →   verb valency frame (does the verb license exactly these args?)

The **negative** reading is the complement: the shadow also names what the
sentence *is not* — the constructions the realised pattern excludes. A legal
`SVO` clause casts "not `SVC`, not `SVOO` unless the verb licenses it, …". A
well-formed sentence's forward construction and its reduced shadow **agree** —
call it *prime* (irreducible as given). A malformed or non-standard one leaves a
**residue** between the two — *composite*. Same half-turn / full-turn winding
parity as the prime range-check, applied to grammar.

    CHECK  (free, descent):   parse → shadow; is the shadow a closed, legal clause?
    REALISE(work,  ascent):   given a target shadow, which verb + synsets fill it?

The reference grammars supply the **shadow alphabet** (finite, closed). The
machine resources supply the **frames** (which shadow a verb can cast) and the
**granularity** (which word fills a slot).

---

## 1. The three reference grammars — the shadow alphabet

Books, not data. They define the closed set the check runs against.

- **Quirk, Greenbaum, Leech & Svartvik**, *A Comprehensive Grammar of the English
  Language* (1985). The **7 clause patterns**, keyed by verb valency:

  | pattern | example | verb type |
  |---|---|---|
  | S V | Birds fly. | intransitive |
  | S V O | She reads books. | monotransitive |
  | S V C | He is happy. | copular (subject complement) |
  | S V A | He is in the garden. | copular (obligatory adverbial) |
  | S V O O | She gave him a book. | ditransitive |
  | S V O C | They elected her chair. | complex-transitive (object complement) |
  | S V O A | She put it on the table. | complex-transitive (adverbial) |

  Plus the SPOCA function set. **This is the equation for a clause**: 3 bits of
  skeleton, fixed once you know the verb's frame.

- **Huddleston & Pullum**, *The Cambridge Grammar of the English Language* (2002).
  Canonical-clause inventory; the tie-breaker authority.

- **Reed & Kellogg** (1877). Sentence **diagramming** — the recursive
  slot-in-slot constituency rules (how adjectivals/adverbials/subordinate clauses
  hang off the SPOCA slots). Penn Treebank brackets are Reed–Kellogg made
  machine-readable.

---

## 2. The machine resources

### 2.1 Universal Dependencies — `datasets/UD_English-EWT/`, `UD_English-GUM/`

CoNLL-U, CC BY-SA 4.0 / CC BY 4.0. Gold **dependency** trees: one token per line,
`ID  FORM  LEMMA  UPOS  XPOS  FEATS  HEAD  DEPREL  DEPS  MISC`. The finite verb is
`HEAD 0` (root); every other token points at its head with one of ~37 `DEPREL`
labels (`nsubj obj iobj obl nmod amod advmod acl advcl case cc conj cop mark …`).

**Role:** the *reduced shadow* in instance form — thousands of gold skeletons to
validate the monad's own reducer against, and to learn the legal skeleton
distribution (which patterns actually occur, how deep modifiers stack). EWT =
web genre; GUM = 12 genres, the cross-check.

### 2.2 VerbNet 3.4 — `datasets/verbnet/verbnet3.4/`

XML, ~270 classes over ~6 000 verbs. Each class: a **thematic-role list**
(`Agent Theme Recipient Instrument …`), **syntactic frames** (the surface
realisations the class allows), **selectional restrictions**, and Levin
**alternations** (dative shift, causative/inchoative, …). Verbs inherit from
Levin's semantic classes.

**Role:** *which shadows a verb can cast.* A verb in `give-13.1` licenses both
`SVOO` and `SVO` + `to`-`obl`; a verb in `run-51.3.2` licenses `SV` and, via the
caused-motion alternation, `SVOA`. The check reads: does the parsed shadow match
one of this verb's licensed frames?

### 2.3 PropBank frame files — `datasets/propbank-frames/frames/`

XML, CC BY-SA 4.0, one file per lemma. Each **roleset** (`give.01`, `give.02`, …)
lists numbered args `Arg0`–`Arg5` with descriptors (`Arg0: giver`, `Arg1: thing
given`, `Arg2: recipient`) plus modifier tags (`ArgM-TMP`, `ArgM-LOC`, …).
Aligned to the Penn Treebank and to VerbNet/FrameNet via the Unified Verb Index.

**Role:** the **predicate–argument bridge** from shadow to lexis — the canonical
"this verb sense has exactly these slots." The step that turns a clause pattern
into a set of fillable roles.

### 2.4 FrameNet 1.7 — not in `datasets/` (ICSI licence)

Fillmore's frame semantics: ~1 200 **frames** (`Giving`, `Commerce_buy`, …), each
with **frame elements** (`Donor`, `Theme`, `Recipient`), ~13 000 lexical units
that evoke them, ~200 k annotated sentences, and a small **Constructicon** (~70
Construction-Grammar entries — form ⊗ meaning pairs above the verb).

Get it: register at `framenet.icsi.berkeley.edu`, or
`nltk.download('framenet_v17')` for the redistributable subset.

**Role:** the semantic frame layer (coarser than PropBank, richer meaning) and
the entry point to Construction Grammar.

### 2.5 Construction Grammar (Goldberg) — theory, no single dataset

Constructions are **form–meaning pairs at the phrasal level** that carry meaning
independent of the verb: the caused-motion construction ("she sneezed the napkin
off the table"), the ditransitive, the resultative, the way-construction. The
FrameNet Constructicon is the only sizeable machine inventory.

**Role:** the shadows **beyond the 7 patterns** — legal clause skeletons the
verb alone does not predict. When the parsed shadow does not match any of the
verb's VerbNet frames, the check asks: is it a licensed *construction*?

### 2.6 Penn Treebank — not in `datasets/` (LDC, paid)

Bracketed constituency (`(S (NP …) (VP (V …) (NP …)))`) — machine-readable
Reed–Kellogg. Free 10 % WSJ sample: `nltk.download('treebank')`. UD (2.1) is the
free dependency substitute; PTB adds the constituency bracketing if the
slot-in-slot rules need gold data.

---

## 3. The sedenion window — a 16-bit sentence

The window (`lio_monad.py`, `N_SLOTS = 16`; the "sedenion window" of
`ptolemy_monad.py`) currently indexes 16 prime channels. For sentence work it
indexes **16 word-slots**:

    e0        the finite verb — the root. No head, does no work (the anchor).
    e1 … e15  the 15 dependents.  Edges = UD relation labels (the 15 relations
              of PG(3,2)-on-the-edges; parse the relation, not the word).
    N_HOLES = {1, 11, 15}   slots a regular clause cannot fill from the verb
              alone — they require a licensing construction (§2.5).

Sentences of ≤ 16 words are the common case, so a typical sentence **is** a
sedenion: 1 real slot (the verb) + 15 imaginary (the dependents). Longer
sentences spill into a second window and stitch (the King's-Maille recursion —
pair of pairs).

This does not replace the prime-channel reading; it is a second addressing of the
same 16-slot object. The reducer writes a sentence into the window; the check
reads whether `e0`'s valency frame accounts for the occupied `e1…e15` and whether
any occupied `N_HOLE` is backed by a construction.

---

## 4. Shape of `monad_sentences.bin`

Built bottom-up — "from the language up":

    LAYER 0  word-sense     WordNet synset            (monad_wordnet.bin — reuse)
    LAYER 1  verb frame     VerbNet class + alternations
                            · PropBank roleset (Arg0…ArgN)
                            · FrameNet frame + frame elements
                            keyed by verb synset  →  {licensed shadows}
    LAYER 2  clause shadow  the 7 patterns  +  Constructicon entries
                            each = (slot sequence ⊗ dependency skeleton ⊗ schema)
    LAYER 3  sentence       verb-rooted dependency graph in the 16-slot window
                            + Reed–Kellogg bracketing for modifier attachment

The relation alphabet (Layer 3 edges) is the ~37 UD `DEPREL` labels, mapped onto
the 15 sedenion edges. `descend(sentence)` = Layers 3→2→1, single pass, the
shadow check. `build_up(shadow)` = Layers 1→3, a bounded choice of filler synsets
given the frame.

---

## 5. Build order

1. `datasets/fetch.sh` — corpora in place (done).
2. A CoNLL-U reader + a VerbNet/PropBank frame-file reader (stdlib XML) —
   `engine/grammar/` ports, module-independent per repo convention.
3. The **reducer**: sentence → shadow (POS → dep graph → SPOCA → clause pattern).
   Validate against UD gold: the reducer's pattern label must match the derivable
   one on ≥ N % of EWT dev.
4. The **check**: shadow + verb → does a VerbNet frame or a Constructicon entry
   license it? Report `prime` / `composite (+residue)`.
5. `monad_sentences.bin` writer: Layers 0–2 as a static index (synset →
   frames → shadows); Layer 3 is per-sentence, not stored.
6. Wire into the Face / Archimedes sentence path as the grammaticality gate
   before lexical realisation.

Wordsmithing (figures, rhythm, Christensen's cumulative sentence) is **notated
for later** — not this pass.
