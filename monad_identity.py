#!/usr/bin/env python3
"""monad_identity.py — build and read monad_identity.bin via ctypes.

The structs here MIRROR monad_identity.h field for field. ctypes gives us the
same memory layout Python-side, so the .bin is written by python and read by C
without a serialisation layer in between — which is the point: python is the
test bench, C is The Monad, and they share the bytes rather than a protocol.

WHAT IS AND IS NOT STORED

Stored: POSITIONS. Which channels are lit, which generation each letter carries,
who the parent is, how many digits the address runs to.

Not stored: the context code, and not the prime address either. Both are
RECOMPUTED from the channel list plus the header parameters, and only a
fingerprint is kept so a recomputation can be checked. That is what makes the
file discardable — it caches where the information is, never what it is.

python3 first. Port to PtolC/ once a result is significant.
"""

from __future__ import annotations
import ctypes as C
import math, os, struct, time
from typing import Dict, List, Optional, Sequence, Tuple

MI_MAGIC      = 0x4D4F4E4944454E54
MI_VERSION    = 1
MI_LETTER_CAP = 313
MI_N_GEN      = 4
MI_ALPHABET   = 26
MI_NO_PARENT  = 0xFFFFFFFF

FERMAT      = (3, 5, 17, 257)
FREQ_ORDER  = 'etaoinshrdlcumwfgypbvkjxqz'
SPELL_BASE  = 27
ROLE_CONCEPT, ROLE_POINTER, ROLE_MODIFIER = 0, 1, 2

# uint64 holds base-27 words up to floor(log_27(2^64)) = 13 letters. Longer
# words OVERFLOW, and a truncated spell is NOT bijective. Silent truncation is
# the exact fault this project forbids, so it is FLAGGED and excluded from the
# bijectivity claim rather than quietly wrapped.
MI_MAX_SPELL_LETTERS = 13
MI_FLAG_SPELL_OVERFLOW = 1 << 0


def _sieve(n: int) -> List[int]:
    sv = bytearray([1]) * (n + 1)
    sv[0] = sv[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(sv[i * i::i]))
    return [i for i in range(n + 1) if sv[i]]


_P = _sieve(3_000_000)
LETTER_POOL    = [p for p in _P if p <= MI_LETTER_CAP]
CONTEXT_PRIMES = [p for p in _P if p >  MI_LETTER_CAP]
LETTER_PRIME   = {c: LETTER_POOL[i] for i, c in enumerate(FREQ_ORDER)}


def generation(p: int) -> int:
    for n, f in enumerate(FERMAT):
        if p <= f:
            return n
    return MI_N_GEN


def fnv1a(b: bytes) -> int:
    h = 0xcbf29ce484222325
    for x in b:
        h = ((h ^ x) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


# ═══════════════════════════════════════════════════════════════════════
#  ctypes mirrors of monad_identity.h
# ═══════════════════════════════════════════════════════════════════════
class mi_section_t(C.Structure):
    _fields_ = [('offset', C.c_uint64), ('length', C.c_uint64),
                ('count',  C.c_uint64)]


class mi_header_t(C.Structure):
    _fields_ = [
        ('magic', C.c_uint64), ('version', C.c_uint32), ('header_bytes', C.c_uint32),
        ('letter_cap', C.c_uint32), ('n_generations', C.c_uint32),
        ('fermat', C.c_uint32 * MI_N_GEN),
        ('freq_order', C.c_uint8 * MI_ALPHABET),
        ('letter_prime', C.c_uint32 * MI_ALPHABET),
        ('letter_gen', C.c_uint8 * MI_ALPHABET),
        ('spell_base', C.c_uint32),
        ('context_prime_lo', C.c_uint32), ('n_channels', C.c_uint32),
        ('s_strings', mi_section_t), ('s_entries', mi_section_t),
        ('s_lineage', mi_section_t), ('s_channels', mi_section_t),
        ('s_phon', mi_section_t),    ('s_edges', mi_section_t),
        ('built_unix', C.c_uint64), ('corpus_fingerprint', C.c_uint64),
        ('checksum', C.c_uint64),
    ]


class mi_chan_t(C.Structure):
    _fields_ = [('channel', C.c_uint32), ('exponent', C.c_uint8),
                ('_pad', C.c_uint8 * 3)]


class mi_edge_t(C.Structure):
    _fields_ = [('from_', C.c_uint32), ('to', C.c_uint32),
                ('xor_class', C.c_uint8), ('kind', C.c_uint8),
                ('weight', C.c_uint16)]


class mi_entry_t(C.Structure):
    _fields_ = [
        ('index', C.c_uint32), ('surface_off', C.c_uint32),
        ('surface_len', C.c_uint16), ('n_letters', C.c_uint8), ('n_delims', C.c_uint8),
        ('spell', C.c_uint64),
        ('lineage_off', C.c_uint32), ('gen_hist', C.c_uint8 * MI_N_GEN),
        ('strut', C.c_uint8), ('box_kite', C.c_uint8),
        ('n_syllables', C.c_uint8), ('stress_pos', C.c_uint8),
        ('phon_off', C.c_uint32), ('phon_len', C.c_uint16),
        ('n_morphemes', C.c_uint16), ('morph_off', C.c_uint32),
        ('prefix_len', C.c_uint8), ('suffix_len', C.c_uint8),
        ('pos_mask', C.c_uint8), ('role', C.c_uint8),
        ('chan_off', C.c_uint32), ('chan_len', C.c_uint32),
        ('code_digits', C.c_uint16), ('addr_digits', C.c_uint16),
        ('delta', C.c_uint32), ('addr_fp', C.c_uint64),
        ('parent', C.c_uint32), ('edge_class', C.c_uint8), ('depth', C.c_uint8),
        ('n_children', C.c_uint16),
        ('charge', C.c_uint16), ('intent', C.c_uint16), ('_reserved', C.c_uint32),
    ]


# ═══════════════════════════════════════════════════════════════════════
#  the three faces, computed
# ═══════════════════════════════════════════════════════════════════════
def split_tiers(text: str) -> Tuple[str, str]:
    """TIER 0 out first — it is the APERTURE and never enters a polynomial."""
    L = [c.lower() for c in text if c.isalpha() and ord(c) < 128]
    D = [c for c in text if not (c.isalpha() and ord(c) < 128)]
    return ''.join(L), ''.join(D)


def spell(letters: str) -> int:
    v = 0
    for ch in letters:
        v = v * SPELL_BASE + (FREQ_ORDER.index(ch) + 1)
    return v


def unspell(v: int) -> str:
    out = []
    while v > 0:
        v, r = divmod(v - 1, SPELL_BASE)
        out.append(FREQ_ORDER[r])
    return ''.join(reversed(out))


def face12(surface: str) -> Dict[str, object]:
    letters, delims = split_tiers(surface)
    lin = tuple(generation(LETTER_PRIME[c]) for c in letters)
    hist = [0] * MI_N_GEN
    bits = 0
    for g in lin:
        if g < MI_N_GEN:
            hist[g] += 1
            bits |= (1 << g)
    kite = (bits & 0b0111) if (bits & 0b1000) else 0
    return {'letters': letters, 'delims': delims, 'spell': spell(letters),
            'lineage': lin, 'gen_hist': hist, 'strut': bits, 'box_kite': kite}


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2; r += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    n = max(2, n)
    if n % 2 == 0 and n > 2:
        n += 1
    while not _is_prime(n):
        n += 2
    return n


def face3(channels: Dict[int, int]) -> Dict[str, object]:
    """RECOMPUTE the code and the address from positions. Nothing is stored."""
    code = 1
    for c, e in sorted(channels.items()):
        code *= CONTEXT_PRIMES[c] ** e
    addr = next_prime(code)
    return {'code': code, 'addr': addr, 'delta': addr - code,
            'code_digits': len(str(code)), 'addr_digits': len(str(addr)),
            'addr_fp': fnv1a(str(addr).encode())}


# ═══════════════════════════════════════════════════════════════════════
#  writer
# ═══════════════════════════════════════════════════════════════════════
class Builder:
    def __init__(self) -> None:
        self.strings = bytearray()
        self.lineage = bytearray()
        self.phon    = bytearray()
        self.chans:  List[mi_chan_t] = []
        self.edges:  List[mi_edge_t] = []
        self.entries: List[mi_entry_t] = []
        self._sidx: Dict[str, int] = {}

    def _str(self, s: str) -> Tuple[int, int]:
        b = s.encode('utf-8')
        if s in self._sidx:
            return self._sidx[s], len(b)
        off = len(self.strings)
        self.strings += b + b'\0'
        self._sidx[s] = off
        return off, len(b)

    def add(self, surface: str, channels: Optional[Dict[int, int]] = None,
            phonemes: str = '', n_morphemes: int = 1, pos_mask: int = 0,
            role: int = ROLE_CONCEPT, parent: int = MI_NO_PARENT,
            depth: int = 0, syllables: int = 0, stress: int = 0) -> int:
        f = face12(surface)
        e = mi_entry_t()
        e.index = len(self.entries)
        e.surface_off, e.surface_len = self._str(surface)
        e.n_letters = min(255, len(f['letters']))
        e.n_delims  = min(255, len(f['delims']))
        sp = f['spell']
        if sp > 0xFFFFFFFFFFFFFFFF:
            e._reserved |= MI_FLAG_SPELL_OVERFLOW
            e.spell = 0                      # NOT a truncation. Absent, and said so.
        else:
            e.spell = sp
        e.lineage_off = len(self.lineage)
        self.lineage += bytes(f['lineage'])
        for i, v in enumerate(f['gen_hist']):
            e.gen_hist[i] = min(255, v)
        e.strut, e.box_kite = f['strut'], f['box_kite']
        e.n_syllables, e.stress_pos = syllables, stress
        if phonemes:
            e.phon_off, e.phon_len = len(self.phon), len(phonemes.encode())
            self.phon += phonemes.encode() + b'\0'
        e.n_morphemes, e.pos_mask, e.role = n_morphemes, pos_mask, role
        e.chan_off = len(self.chans)
        if channels:
            for c, x in sorted(channels.items()):
                ch = mi_chan_t(); ch.channel, ch.exponent = c, min(255, x)
                self.chans.append(ch)
            e.chan_len = len(channels)
            f3 = face3(channels)
            e.code_digits = min(65535, f3['code_digits'])
            e.addr_digits = min(65535, f3['addr_digits'])
            e.delta       = min(0xFFFFFFFF, f3['delta'])
            e.addr_fp     = f3['addr_fp']
        e.parent = parent
        e.edge_class = 0 if parent == MI_NO_PARENT else ((e.index ^ parent) & 0x0F)
        e.depth = min(255, depth)
        self.entries.append(e)
        return e.index

    def link(self, a: int, b: int, kind: int = 0, weight: int = 1000) -> None:
        ed = mi_edge_t()
        ed.from_, ed.to = a, b
        ed.xor_class = (a ^ b) & 0x0F
        ed.kind, ed.weight = kind, weight
        self.edges.append(ed)

    def write(self, path: str, corpus_fp: int = 0) -> Dict[str, int]:
        for e in self.entries:
            e.n_children = sum(1 for x in self.entries if x.parent == e.index)
        h = mi_header_t()
        h.magic, h.version = MI_MAGIC, MI_VERSION
        h.header_bytes = C.sizeof(mi_header_t)
        h.letter_cap, h.n_generations = MI_LETTER_CAP, MI_N_GEN
        for i, f in enumerate(FERMAT):
            h.fermat[i] = f
        for i, c in enumerate(FREQ_ORDER):
            h.freq_order[i] = ord(c)
            h.letter_prime[i] = LETTER_PRIME[c]
            h.letter_gen[i] = generation(LETTER_PRIME[c])
        h.spell_base = SPELL_BASE
        h.context_prime_lo = CONTEXT_PRIMES[0]
        h.n_channels = max((c.channel for c in self.chans), default=0) + 1
        h.built_unix = int(time.time())
        h.corpus_fingerprint = corpus_fp

        ent_b  = b''.join(bytes(e) for e in self.entries)
        chan_b = b''.join(bytes(c) for c in self.chans)
        edge_b = b''.join(bytes(e) for e in self.edges)
        cur = C.sizeof(mi_header_t)
        def sec(blob, count):
            nonlocal cur
            s = mi_section_t(); s.offset, s.length, s.count = cur, len(blob), count
            cur += len(blob)
            return s
        h.s_strings  = sec(bytes(self.strings), len(self._sidx))
        h.s_entries  = sec(ent_b,  len(self.entries))
        h.s_lineage  = sec(bytes(self.lineage), len(self.lineage))
        h.s_channels = sec(chan_b, len(self.chans))
        h.s_phon     = sec(bytes(self.phon), 0)
        h.s_edges    = sec(edge_b, len(self.edges))
        body = (bytes(self.strings) + ent_b + bytes(self.lineage)
                + chan_b + bytes(self.phon) + edge_b)
        h.checksum = fnv1a(body)
        with open(path, 'wb') as fh:
            fh.write(bytes(h)); fh.write(body)
        return {'bytes': C.sizeof(mi_header_t) + len(body),
                'entries': len(self.entries), 'channels': len(self.chans),
                'edges': len(self.edges)}


# ═══════════════════════════════════════════════════════════════════════
#  reader
# ═══════════════════════════════════════════════════════════════════════
class Reader:
    def __init__(self, path: str) -> None:
        with open(path, 'rb') as fh:
            self.buf = bytearray(fh.read())
        self.h = mi_header_t.from_buffer(self.buf)
        if self.h.magic != MI_MAGIC:
            raise ValueError('not a monad_identity.bin')
        s = self.h.s_entries
        self.entries = (mi_entry_t * s.count).from_buffer(self.buf, s.offset)
        s = self.h.s_channels
        self.chans = (mi_chan_t * s.count).from_buffer(self.buf, s.offset) if s.count else []
        s = self.h.s_edges
        self.edges = (mi_edge_t * s.count).from_buffer(self.buf, s.offset) if s.count else []

    def surface(self, e: mi_entry_t) -> str:
        o = self.h.s_strings.offset + e.surface_off
        return self.buf[o:o + e.surface_len].decode()

    def lineage(self, e: mi_entry_t) -> Tuple[int, ...]:
        o = self.h.s_lineage.offset + e.lineage_off
        return tuple(self.buf[o:o + e.n_letters])

    def channels(self, e: mi_entry_t) -> Dict[int, int]:
        return {self.chans[e.chan_off + i].channel: self.chans[e.chan_off + i].exponent
                for i in range(e.chan_len)}

    def recompute(self, e: mi_entry_t) -> Dict[str, object]:
        """THE DISCARDABILITY TEST: rebuild the address from POSITIONS alone."""
        return face3(self.channels(e))

    def verify(self) -> Dict[str, object]:
        body = bytes(self.buf[C.sizeof(mi_header_t):])
        ok_sum = (fnv1a(body) == self.h.checksum)
        spell_ok = addr_ok = overflow = 0
        for e in self.entries:
            if e._reserved & MI_FLAG_SPELL_OVERFLOW:
                overflow += 1
            elif unspell(e.spell) == split_tiers(self.surface(e))[0]:
                spell_ok += 1
            if e.chan_len:
                if self.recompute(e)['addr_fp'] == e.addr_fp:
                    addr_ok += 1
        n_ch = sum(1 for e in self.entries if e.chan_len)
        n_sp = len(self.entries) - overflow
        return {'checksum_ok': ok_sum, 'entries': len(self.entries),
                'spell_roundtrip': f'{spell_ok}/{n_sp}',
                'spell_overflow': f'{overflow} (>{MI_MAX_SPELL_LETTERS} letters — flagged, not truncated)',
                'address_recomputed': f'{addr_ok}/{n_ch}'}
