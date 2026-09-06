# datasets/ — grammar corpora for `monad_sentences.bin`

Reference grammars + the machine-readable resources that stand in for a
"higher-order WordNet." **The corpora are `.gitignored`** (bulky, redistributable
but not ours to re-ship); this README + `fetch.sh` are the tracked provenance.
Re-download with `bash datasets/fetch.sh`.

Design context: `docs/wiki/Grammar-Resources-For-Monad-Sentences.md`.

| dir | resource | commit | size | licence | format | role |
|---|---|---|---|---|---|---|
| `UD_English-EWT/` | Universal Dependencies — English Web Treebank | `4a4d77f` | 19M | CC BY-SA 4.0 | CoNLL-U | gold **dependency** skeletons (verb-rooted graph, ~37 labelled edges) — the *reduced shadow*, instance form |
| `UD_English-GUM/` | UD — Georgetown Univ. Multilayer Corpus | `1fe6355` | 26M | CC BY 4.0 | CoNLL-U | second dependency treebank, wider genre spread — cross-check the shadow distribution |
| `verbnet/` | VerbNet 3.4 (U. Colorado) | `ae8e9cf` | 3.8M | academic; commercial use needs licence review | XML | verb **valency classes** + Levin **alternations** — which shadows a verb can cast |
| `propbank-frames/` | PropBank frame files (v3.4) | `c66e0cc` | 43M | CC BY-SA 4.0 | XML | per-lemma **rolesets** (Arg0…ArgN + function tags) — the predicate–argument bridge from shadow to lexis |

## Not fetched (licence)

- **FrameNet 1.7** — ICSI licence, register at `framenet.icsi.berkeley.edu`.
  Redistributable subset: `nltk.download('framenet_v17')`. Role: Fillmore
  **frames** + frame elements + the small **Constructicon** (Construction
  Grammar entries — shadows that carry meaning independent of the verb).
- **Penn Treebank** — LDC, paid. Free 10% WSJ sample: `nltk.download('treebank')`
  (bracketed constituency = machine-readable **Reed–Kellogg**). UD above is the
  free dependency substitute for the full PTB.

## The three reference grammars (books, not data — the *shadow alphabet*)

- **Quirk, Greenbaum, Leech & Svartvik**, *A Comprehensive Grammar of the English
  Language* (1985) — the **7 clause patterns** (SV, SVO, SVC, SVA, SVOO, SVOC,
  SVOA) and the SPOCA function set. The closed finite basis.
- **Huddleston & Pullum**, *The Cambridge Grammar of the English Language* (2002)
  — canonical-clause inventory; the modern authority where the two disagree.
- **Reed & Kellogg** (1877) — sentence **diagramming**: the recursive
  slot-in-slot constituency rules (how modifiers hang). PTB brackets are this,
  machine-readable.

## Shape of `monad_sentences.bin`

Bottom-up — "from the language up":

    word-sense           WordNet synset            (monad_wordnet.bin, already built)
      ↳ verb frame       VerbNet class + alternations · PropBank roleset · FrameNet frame
          ↳ clause shadow  one of the 7 patterns · + Constructicon entries
              ↳ sentence   dependency graph, verb-rooted, ≤ 16 word-slots

The **sedenion window** carries a sentence: 16 word-slots, `e0` = the finite verb
(the root — no head, does no work), `e1…e15` = the 15 dependents, edges = the UD
relation labels. `N_HOLES = {1, 11, 15}` (see `lio_monad.py`) = the slots a
regular clause cannot fill from the verb alone — they need a licensing
construction. Sentences of ≤ 16 words are the common case: a **16-bit sentence**.
