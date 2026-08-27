#!/usr/bin/env python3
"""
make_grammar_bin.py -- build monad_grammar.bin: the finite, closed
morphology/inflection rule set proposed in Phase 33
(docs/wiki/Tuning-the-Engine/33_folded_in_context_and_the_geometry_that_does_no_work.md),
built for real here.

Two tiers, both already-existing, real, external data -- nothing invented:
  EXCEPTIONS  -- 5,952 irregular inflected-form -> lemma pairs, shipped as
                 WordNet's own {noun,verb,adj,adv}.exc files
                 (/usr/share/wordnet/*.exc).
  RULES       -- 25 regular suffix-substitution rules, NLTK's own
                 WordNetCorpusReader.MORPHOLOGICAL_SUBSTITUTIONS table.

This is the same hierarchy morphy() already checks silently inside every
wn.synsets() call: exceptions first (closed, memorized), rules second
(open, generative) -- pulled out and named as its own addressable object,
the same move wordnet_boxkite.py already made on WordNet's relation
methods (Phase 31).

Binary format (little-endian):
  magic 'GRAM' (4 bytes) | version:u32 | n_exceptions:u32 | n_rules:u32
  n_exceptions * { pos:u8 (ascii char) | inflected_len:u8 | inflected:bytes
                   | lemma_len:u8 | lemma:bytes }
  n_rules * { pos:u8 | rule_id:u8 | from_len:u8 | from:bytes
              | to_len:u8 | to:bytes }
"""

import struct
import sys

EXC_FILES = {
    'n': '/usr/share/wordnet/noun.exc',
    'v': '/usr/share/wordnet/verb.exc',
    'a': '/usr/share/wordnet/adj.exc',
    'r': '/usr/share/wordnet/adv.exc',
}

MORPHOLOGICAL_SUBSTITUTIONS = {
    'n': [('s', ''), ('ses', 's'), ('ves', 'f'), ('xes', 'x'), ('zes', 'z'),
          ('ches', 'ch'), ('shes', 'sh'), ('men', 'man'), ('ies', 'y')],
    'v': [('s', ''), ('ies', 'y'), ('es', 'e'), ('es', ''), ('ed', 'e'),
          ('ed', ''), ('ing', 'e'), ('ing', '')],
    'a': [('er', ''), ('est', ''), ('er', 'e'), ('est', 'e')],
    'r': [],
    's': [('er', ''), ('est', ''), ('er', 'e'), ('est', 'e')],
}

OUT_PATH = '/home/rendier/Projects/ThePlace/VAPMIP/PtolC/monad_grammar.bin'


def load_exceptions():
    entries = []
    for pos, path in EXC_FILES.items():
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 2:
                    continue
                inflected = parts[0]
                # some lines list multiple candidate lemmas; keep the first
                # (morphy's own behaviour) and record it as the primary
                lemma = parts[1]
                entries.append((pos, inflected, lemma))
    return entries


def load_rules():
    entries = []
    for pos, subs in MORPHOLOGICAL_SUBSTITUTIONS.items():
        for rule_id, (frm, to) in enumerate(subs):
            entries.append((pos, rule_id, frm, to))
    return entries


def write_bin(exceptions, rules, path):
    with open(path, 'wb') as f:
        f.write(b'GRAM')
        f.write(struct.pack('<I', 1))
        f.write(struct.pack('<I', len(exceptions)))
        f.write(struct.pack('<I', len(rules)))

        for pos, inflected, lemma in exceptions:
            ib = inflected.encode('utf-8')
            lb = lemma.encode('utf-8')
            f.write(struct.pack('<B', ord(pos)))
            f.write(struct.pack('<B', len(ib)))
            f.write(ib)
            f.write(struct.pack('<B', len(lb)))
            f.write(lb)

        for pos, rule_id, frm, to in rules:
            fb = frm.encode('utf-8')
            tb = to.encode('utf-8')
            f.write(struct.pack('<B', ord(pos)))
            f.write(struct.pack('<B', rule_id))
            f.write(struct.pack('<B', len(fb)))
            f.write(fb)
            f.write(struct.pack('<B', len(tb)))
            f.write(tb)


def read_bin(path):
    """Round-trip check -- read back what write_bin just wrote."""
    with open(path, 'rb') as f:
        magic = f.read(4)
        assert magic == b'GRAM', magic
        version, = struct.unpack('<I', f.read(4))
        n_exc, = struct.unpack('<I', f.read(4))
        n_rules, = struct.unpack('<I', f.read(4))

        exceptions = []
        for _ in range(n_exc):
            pos = chr(struct.unpack('<B', f.read(1))[0])
            ilen, = struct.unpack('<B', f.read(1))
            inflected = f.read(ilen).decode('utf-8')
            llen, = struct.unpack('<B', f.read(1))
            lemma = f.read(llen).decode('utf-8')
            exceptions.append((pos, inflected, lemma))

        rules = []
        for _ in range(n_rules):
            pos = chr(struct.unpack('<B', f.read(1))[0])
            rule_id, = struct.unpack('<B', f.read(1))
            flen, = struct.unpack('<B', f.read(1))
            frm = f.read(flen).decode('utf-8')
            tlen, = struct.unpack('<B', f.read(1))
            to = f.read(tlen).decode('utf-8')
            rules.append((pos, rule_id, frm, to))

    return version, exceptions, rules


def main():
    exceptions = load_exceptions()
    rules = load_rules()
    print(f"Loaded {len(exceptions):,} exceptions, {len(rules)} rules")

    write_bin(exceptions, rules, OUT_PATH)
    import os
    size = os.path.getsize(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({size:,} bytes)")

    version, exc2, rules2 = read_bin(OUT_PATH)
    ok = (exc2 == exceptions) and (rules2 == rules)
    print(f"Round-trip check: version={version}  "
          f"exceptions match={exc2 == exceptions}  rules match={rules2 == rules}  "
          f"OVERALL={'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit(1)

    # Spot-check the real content, not just structural round-trip
    sample = [e for e in exceptions if e[1] in ('mice', 'went', 'better', 'geese')]
    print("Spot check:", sample)
    tesla_rule = [r for r in rules if r[0] == 'v' and r[3] == 'e']
    print("Sample verb rules (X -> e):", tesla_rule)


if __name__ == '__main__':
    main()
