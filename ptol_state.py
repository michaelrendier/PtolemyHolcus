#!/usr/bin/env python3
"""
ptol_state.py — reader for PtolC monad state binaries (magic "PTOL").

Written 2026-07-28 to get at the A-matrix from Python. `ptolemy` only
exposes lookups (-w) and summaries (-F); the co-occurrence edges are the
actual relational data in the field and nothing could read them out.

Layout is NOT guessed — it is transcribed from PtolC/state.c's own header
comment and cross-checked against the fwrite() calls in state_save():

    Header:  magic[4] version[4] N[4] vocab_size[4] A_size[4] wc[4]
             threshold[8]            (double)
             affect[4]               (float, v>=4 only)
    Beta:    N * double
    Age:     N * int32
    Vocab:   vocab_size * ( idx[4] wlen[2] E[8]
                            home_stratum[1] gen_stratum[1] prose_seen[1]
                            word[wlen] )
             v1: no stratum bytes
             v2: + home_stratum, gen_stratum
             v3: + prose_seen
             v4: + affect in header
    A:       A_size * ( i[4] j[4] weight[8] )

All little-endian.

NOTE on the A-matrix index packing (state.c state_save):
    ai = key >> 15
    aj = key & 0x7FFF
so both indices are 15-bit — max 32767. N is 25000 in current builds, which
fits, but a build with N > 32767 would silently alias. Recorded here
because the reader cannot detect it after the fact.

This is a READER. It does not write, and it does not modify state.

Author: Cody Michael Allison + Claude (Anthropic), 2026-07-28
"""

import struct
import sys
from array import array
from typing import Dict, Iterator, List, Optional, Tuple

MAGIC = b'PTOL'
CURRENT_VERSION = 4


class PtolStateError(Exception):
    pass


class VocabEntry:
    __slots__ = ('idx', 'word', 'E', 'home_stratum', 'gen_stratum', 'prose_seen')

    def __init__(self, idx, word, E, hs, gs, ps):
        self.idx = idx
        self.word = word
        self.E = E
        self.home_stratum = hs
        self.gen_stratum = gs
        self.prose_seen = ps

    def __repr__(self):
        return (f"VocabEntry({self.word!r} idx={self.idx} E={self.E:.6f} "
                f"home={self.home_stratum} gen={self.gen_stratum})")


class PtolState:
    """
    A loaded monad state.

    Attributes:
        version, N, vocab_size, a_size, word_count, threshold, affect
        beta[N]        field depth per zero          (list of float)
        age[N]         age counter per zero          (list of int)
        vocab          list of VocabEntry, in file order
        by_word        {word: VocabEntry}
        by_idx         {zero index: VocabEntry}
        edges          list of (i, j, weight)
    """

    def __init__(self):
        self.path = None
        self.version = None
        self.N = 0
        self.vocab_size = 0
        self.a_size = 0
        self.word_count = 0
        self.threshold = 0.0
        self.affect = 0.0
        self.beta: List[float] = []
        self.age: List[int] = []
        self.vocab: List[VocabEntry] = []
        self.by_word: Dict[str, VocabEntry] = {}
        self.by_idx: Dict[int, VocabEntry] = {}
        self.edges: List[Tuple[int, int, float]] = []
        self._adj: Optional[Dict[int, List[Tuple[int, float]]]] = None

    # ── neighbourhood access — what the A-matrix is actually for ────────────

    def adjacency(self) -> Dict[int, List[Tuple[int, float]]]:
        """
        {zero_index: [(neighbour_index, weight), ...]} — built once, cached.

        Edges are stored ONE WAY in the file (i, j). This returns them as
        written, symmetrised in neither direction, because state.c does not
        record whether the source A-matrix was symmetric and inventing a
        symmetry here would be a claim the file does not support.
        """
        if self._adj is None:
            adj: Dict[int, List[Tuple[int, float]]] = {}
            for i, j, w in self.edges:
                adj.setdefault(i, []).append((j, w))
            for k in adj:
                adj[k].sort(key=lambda t: -t[1])
            self._adj = adj
        return self._adj

    def neighbours(self, word: str, n: int = 10) -> List[Tuple[str, float]]:
        """Top-n co-occurrence neighbours of a word, by edge weight."""
        e = self.by_word.get(word)
        if e is None:
            return []
        out = []
        for j, w in self.adjacency().get(e.idx, [])[:n]:
            nb = self.by_idx.get(j)
            out.append((nb.word if nb else f"<zero {j}>", w))
        return out

    def summary(self) -> str:
        deg = {}
        for i, j, _w in self.edges:
            deg[i] = deg.get(i, 0) + 1
        seated = len(self.vocab)
        return (f"PtolState({self.path})\n"
                f"  version={self.version} N={self.N} vocab={self.vocab_size} "
                f"A_edges={self.a_size} word_count={self.word_count}\n"
                f"  threshold={self.threshold:.10g} affect={self.affect:.4f}\n"
                f"  seated words={seated}  zeros with out-edges={len(deg)}\n"
                f"  beta: min={min(self.beta):.8g} max={max(self.beta):.8g}")


def _read_exact(f, n: int, what: str) -> bytes:
    b = f.read(n)
    if len(b) != n:
        raise PtolStateError(f"truncated reading {what}: wanted {n}, got {len(b)}")
    return b


def read_state(path: str, load_edges: bool = True) -> PtolState:
    """
    Parse a PTOL state file.

    load_edges=False skips the A-matrix body (still reports a_size from the
    header) for when only vocab/beta are needed.
    """
    st = PtolState()
    st.path = path
    with open(path, 'rb') as f:
        magic = _read_exact(f, 4, 'magic')
        if magic != MAGIC:
            raise PtolStateError(
                f"bad magic {magic!r} in {path} — expected {MAGIC!r}. "
                f"Pickle-format bins (b'\\x80\\x04') are a DIFFERENT engine "
                f"(monad.py Engine.load_checkpoint), not this format.")

        (st.version, st.N, st.vocab_size,
         st.a_size, st.word_count) = struct.unpack('<5I', _read_exact(f, 20, 'header'))
        (st.threshold,) = struct.unpack('<d', _read_exact(f, 8, 'threshold'))

        if st.version >= 4:
            (st.affect,) = struct.unpack('<f', _read_exact(f, 4, 'affect'))

        if st.version > CURRENT_VERSION:
            print(f"[ptol_state] warning: version {st.version} is newer than "
                  f"{CURRENT_VERSION}; layout may have changed", file=sys.stderr)

        beta = array('d'); beta.frombytes(_read_exact(f, 8 * st.N, 'beta'))
        if sys.byteorder != 'little':
            beta.byteswap()
        st.beta = list(beta)

        age = array('i'); age.frombytes(_read_exact(f, 4 * st.N, 'age'))
        if sys.byteorder != 'little':
            age.byteswap()
        st.age = list(age)

        # Vocab — the per-version tail bytes are the fiddly part
        has_hg = st.version >= 2
        has_ps = st.version >= 3
        for _ in range(st.vocab_size):
            idx, wlen = struct.unpack('<IH', _read_exact(f, 6, 'vocab idx/wlen'))
            (E,) = struct.unpack('<d', _read_exact(f, 8, 'vocab E'))
            hs = gs = ps = 0
            if has_hg:
                hs, gs = struct.unpack('<BB', _read_exact(f, 2, 'strata'))
            if has_ps:
                (ps,) = struct.unpack('<B', _read_exact(f, 1, 'prose_seen'))
            word = _read_exact(f, wlen, 'word').decode('utf-8', 'replace')
            e = VocabEntry(idx, word, E, hs, gs, ps)
            st.vocab.append(e)
            st.by_word[word] = e
            st.by_idx[idx] = e

        if load_edges:
            raw = _read_exact(f, 16 * st.a_size, 'A edges')
            unpack = struct.Struct('<IId').unpack_from
            st.edges = [unpack(raw, o) for o in range(0, len(raw), 16)]

            trailing = f.read()
            if trailing:
                print(f"[ptol_state] warning: {len(trailing)} trailing bytes "
                      f"after A-matrix — layout may not match", file=sys.stderr)

    return st


def _main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("usage: ptol_state.py <state.bin> [word ...]")
        return 2
    st = read_state(argv[1])
    print(st.summary())
    words = argv[2:] or []
    if words:
        for w in words:
            e = st.by_word.get(w)
            if e is None:
                print(f"\n{w!r}: NOT IN VOCAB")
                continue
            print(f"\n{w!r} idx={e.idx} E={e.E:.6f} beta={st.beta[e.idx]:.6f} "
                  f"home={e.home_stratum} gen={e.gen_stratum} prose_seen={e.prose_seen}")
            nb = st.neighbours(w, 10)
            if not nb:
                print("   no out-edges")
            for word, wt in nb:
                print(f"   {word:24} w={wt:.6f}")
    return 0


if __name__ == '__main__':
    sys.exit(_main(sys.argv))
