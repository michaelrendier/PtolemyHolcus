#!/usr/bin/env python3
"""
make_phonetic_bin.py -- build monad_phonetic.bin: real ARPAbet pronunciation
+ stress data, for every word cmudict actually covers.

Raised 2026-08-27 (Cody): dictionary pronunciation guides sit "right behind
all syllable decompositions of the word" -- this is that data, already
shipped with NLTK (the same toolchain wordnet_boxkite.py already uses),
not something to build from scratch. Source: nltk.corpus.cmudict, the
Carnegie Mellon Pronouncing Dictionary.

Each word can have MULTIPLE pronunciations (heteronyms: 'record' the noun
vs. 'record' the verb stress different syllables for a real meaning/POS
difference) -- kept as a list per word, not collapsed to one.

ARPAbet phonemes already carry stress as a digit suffix on vowels only
(0=unstressed, 1=primary, 2=secondary; consonants carry no digit) --
syllable count and primary-stress position are DERIVED from that, not
separately encoded, the same "don't store what you can recompute exactly"
discipline as compress_count().

Honest limit, not hidden: cmudict covers ~123k common words. Rare/archaic
words (its own docstring example: 'thaumaturge') are simply absent --
recorded as a real coverage gap, not silently padded.

Binary format (little-endian):
  magic 'PHON' (4 bytes) | version:u32 | n_words:u32
  n_words * {
    word_len:u8 | word:bytes | n_pron:u8
    n_pron * {
      n_phon:u8
      n_phon * { phon_len:u8 | phon:bytes }   # ARPAbet token, e.g. 'AO1', 'K'
    }
  }
"""

import struct
import sys


def load_cmudict():
    from nltk.corpus import cmudict
    return cmudict.dict()


def syllable_count(pron):
    """Count of phonemes carrying a stress digit -- vowels only, so this
    IS the syllable count, not an approximation."""
    return sum(1 for p in pron if p[-1] in '012')


def primary_stress_index(pron):
    """Index (0-based, among syllables only) of the primary-stressed
    vowel, or -1 if none (rare, but real -- some entries are all
    secondary/unstressed)."""
    syll_idx = 0
    for p in pron:
        if p[-1] in '012':
            if p[-1] == '1':
                return syll_idx
            syll_idx += 1
    return -1


def write_bin(cmu, path):
    with open(path, 'wb') as f:
        f.write(b'PHON')
        f.write(struct.pack('<I', 1))
        f.write(struct.pack('<I', len(cmu)))
        for word, prons in cmu.items():
            wb = word.encode('utf-8')
            f.write(struct.pack('<B', len(wb)))
            f.write(wb)
            f.write(struct.pack('<B', len(prons)))
            for pron in prons:
                f.write(struct.pack('<B', len(pron)))
                for phon in pron:
                    pb = phon.encode('ascii')
                    f.write(struct.pack('<B', len(pb)))
                    f.write(pb)


def read_bin(path):
    with open(path, 'rb') as f:
        magic = f.read(4)
        assert magic == b'PHON', magic
        version, = struct.unpack('<I', f.read(4))
        n_words, = struct.unpack('<I', f.read(4))
        out = {}
        for _ in range(n_words):
            wlen, = struct.unpack('<B', f.read(1))
            word = f.read(wlen).decode('utf-8')
            n_pron, = struct.unpack('<B', f.read(1))
            prons = []
            for _ in range(n_pron):
                n_phon, = struct.unpack('<B', f.read(1))
                pron = []
                for _ in range(n_phon):
                    plen, = struct.unpack('<B', f.read(1))
                    pron.append(f.read(plen).decode('ascii'))
                prons.append(pron)
            out[word] = prons
    return version, out


OUT_PATH = '/home/rendier/Projects/ThePlace/VAPMIP/PtolC/monad_phonetic.bin'


def main():
    cmu = load_cmudict()
    print(f"Loaded {len(cmu):,} words from cmudict")

    write_bin(cmu, OUT_PATH)
    import os
    print(f"Wrote {OUT_PATH} ({os.path.getsize(OUT_PATH):,} bytes)")

    version, cmu2 = read_bin(OUT_PATH)
    ok = (cmu2 == cmu)
    print(f"Round-trip check: version={version}  words match={ok}  "
          f"OVERALL={'PASS' if ok else 'FAIL'}")
    if not ok:
        sys.exit(1)

    # Real spot checks, not synthetic
    for w in ['record', 'present', 'thaumaturge', 'read']:
        prons = cmu.get(w)
        if prons is None:
            print(f"  {w}: NOT COVERED (honest gap, not padded)")
            continue
        for p in prons:
            print(f"  {w}: {p}  syllables={syllable_count(p)}  "
                  f"primary_stress_syllable={primary_stress_index(p)}")


if __name__ == '__main__':
    main()
