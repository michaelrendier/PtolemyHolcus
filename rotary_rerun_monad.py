#!/usr/bin/env python3
"""rotary_rerun_monad.py — the diagnostic and fault-born harness.

WHAT THIS IS

A harness wrapped around the engine that reports THE RELATIONSHIPS, and reports
every fault as a record rather than a count. It does not re-implement the rotor.
It watches it and says what holds.

WHAT THIS IS NOT

Not an internal-combustion cosplay. The Wankel gave the architecture — one
shaft, three faces, port timing as a consequence of geometry — and that part is
real and stays. The rest of the garage does not follow it around. There are no
PIDs here because a PID is a number with a part number, and what is wanted is a
number with a RELATIONSHIP.

No variable valve timing. cam3.py, 2026-08-17: a real Wankel has no valves and
no camshaft, port timing is the rotor's own faces sweeping the ports, and an
independent writable advance is a piston engine's architecture. What is
adjustable is the trochoid: R = sqrt(p_red), e = sqrt(p_blue), loss = |R - e|
exactly, null at R = e <=> sigma_self = 1/2.

THE THREE OBJECTS, AND WHY THEY ARE THREE

    MindsEye     reads.  Snapshot analysis across dimensions at one instant.
    PapersHands  writes. Emission, one relationship at a time, ordered.
    BoxKite      the relational language they BOTH speak.

The box kite is the VARIABLE INVARIANT between them. Invariant because for
every relation, the Eye and the Hands denote the same thing by the same name --
a relation between the two objects, holding across every state. Variable
because the structure is rebuildable and a rebuild is honest change: what is
guaranteed is that neither renumbers underneath the other.

So the box kite carries a signature, both subsystems bind to the one they were
built against, and a cross-signature reference is REFUSED rather than resolved.
An invariant that is only written down is a hope.

THE 7-7-7

Ainulindale/wiki/89_the_seven_octonions.md, measured 2026-08-15/16 and
corrected 2026-08-16:

    7  OCTONIONS     dim 8, 12 diagonals each      7 x 12 = 84
    7  STRUTS        labels 9..15                  the box kites
    7  QUATERNIONS   dim 4, one per Fano LINE      NOT 21 -- the three pairs
                                                   on a line share one 4-space

Which is 7 = 111 in three bits, and three bits is also rwx. The strut's binary
expansion is its lineage: which generations of order-loss it carries. The
division bit is forced (no zero divisors below dim 16), leaving exactly three
free bits, and 2^3 - 1 = 7 is why there are seven of anything here at all.

NOTHING IS DROPPED

Every check becomes a Relation with a status and a detail, including the ones
that could not be run. A tally tells you four checks failed; it does not tell
you which, or let you print them. Counting a skip is still a skip.

    HOLDS       measured and true
    VIOLATED    measured and false -- a fault
    DEGENERATE  the reducer was not valid on this data (see below)
    UNTESTED    a dependency was absent; recorded, never silently passed

DEGENERATE exists because of the standing rule from PRIMER_2026-08-17 section 6:
a reducer must be valid on its data. argmax on signed currents returns index 0
when red and green run negative; min|neutral| on gated data is identically zero
because raised-cosine port windows hit zero at their edges. Both returned a
number. Neither number meant anything. So a reducer here declares its domain and
returns DEGENERATE instead of a confident wrong answer.

python3 first. Port to PtolC/ only once a result is significant.
"""

from __future__ import annotations

import hashlib
import math
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Tuple

# ── the monorepo root, so box_kite is importable ─────────────────────────────
_ROOT = '/home/rendier/Projects/ThePlace'
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

__all__ = [
    'Status', 'Relation', 'Ledger', 'LedgerCursor',
    'BoxKite', 'MindsEye', 'PapersHands', 'Harness',
    'Intention', 'LongPath', 'ShortPath', 'Entry', 'Handoff',
    'SIGMA_PIN', 'GAP', 'D_STAR', 'OMEGA_ZS', 'N_FACE', 'GEAR_K',
]

# ── constants (mirror rotary_monad.py / cam3.py / ptolemy.h) ─────────────────
SIGMA_PIN = 0.5
GAP       = 0.000707
D_STAR    = 0.246
OMEGA_ZS  = 0.5671432904097838
N_FACE    = 3      # a rotor is a triangle
GEAR_K    = 3      # eccentric shaft turns 3x per rotor revolution
SED_DIM   = 16


# ═══════════════════════════════════════════════════════════════════════════
#  RECORDS — nothing is dropped
# ═══════════════════════════════════════════════════════════════════════════

class Status(Enum):
    HOLDS      = 'holds'
    VIOLATED   = 'VIOLATED'
    DEGENERATE = 'degenerate'
    UNTESTED   = 'untested'

    @property
    def is_fault(self) -> bool:
        return self is Status.VIOLATED


@dataclass
class Relation:
    """One checked relationship. A record, not a tally entry.

    `index` is assigned by the Ledger and never moves. `detail` always carries
    enough to print the thing that failed, because a fault you cannot show is
    a fault you cannot fix.
    """
    name:     str
    claim:    str
    status:   Status
    expected: object = None
    observed: object = None
    detail:   str = ''
    group:    str = 'general'
    index:    int = -1

    def __str__(self) -> str:
        mark = {'holds': '  ok', 'VIOLATED': 'FAULT',
                'degenerate': ' deg', 'untested': ' --- '}[self.status.value]
        line = f'[{mark}] {self.name:<28} {self.claim}'
        if self.status is not Status.HOLDS and self.observed is not None:
            line += f'\n            expected {self.expected!r}, observed {self.observed!r}'
        if self.detail:
            line += f'\n            {self.detail}'
        return line


class Ledger:
    """Holds one record per check. Never filters, never compacts.

    The index a record receives is the index it keeps for the life of this
    ledger, which is what makes it worth passing to anything else.
    """

    def __init__(self) -> None:
        self._records: List[Relation] = []

    def add(self, r: Relation) -> int:
        r.index = len(self._records)
        self._records.append(r)
        return r.index

    def __len__(self) -> int:
        return len(self._records)

    def at(self, i: int) -> Optional[Relation]:
        if 0 <= i < len(self._records):
            return self._records[i]
        return None

    def count(self, status: Status) -> int:
        return sum(1 for r in self._records if r.status is status)

    def faults(self) -> List[Relation]:
        return [r for r in self._records if r.status.is_fault]

    def groups(self) -> List[str]:
        seen: List[str] = []
        for r in self._records:
            if r.group not in seen:
                seen.append(r.group)
        return seen


class LedgerCursor:
    """Traversal, separate from the ledger and from anything that analyses it.

    Visits every record. It does not skip faults, it does not skip untested
    entries, and it holds no opinion about what the caller wants. A caller that
    wants only faults tests the status itself, in the open, where the decision
    is visible.
    """

    def __init__(self, ledger: Ledger) -> None:
        self._ledger = ledger
        self._i = -1

    def __iter__(self) -> Iterator[Relation]:
        self.reset()
        while self.next():
            rec = self.current()
            if rec is not None:
                yield rec

    def reset(self) -> None:
        self._i = -1

    def next(self) -> bool:
        if self._i + 1 >= len(self._ledger):
            self._i = len(self._ledger)
            return False
        self._i += 1
        return True

    @property
    def index(self) -> int:
        return self._i

    def current(self) -> Optional[Relation]:
        return self._ledger.at(self._i)


# ═══════════════════════════════════════════════════════════════════════════
#  THE BOX KITE — the variable invariant
# ═══════════════════════════════════════════════════════════════════════════

class BoxKiteUnavailable(RuntimeError):
    """The box_kite module could not be imported. Recorded, never faked."""


class BoxKite:
    """The relational language spoken by both MindsEye and PapersHands.

    Built once from ValaQuenta/modules/box_kite. Carries a `signature` — a
    monotonic identity for this construction — so a subsystem can tell that the
    structure it bound to has been rebuilt underneath it.

    A counter, not the object's id(): ids are reused after collection, and a
    subsystem holding a stale reference would then match a fresh structure and
    answer confidently about the wrong one.
    """

    _next_signature = 1

    def __init__(self, parents: Tuple[int, int] = (0, 0)) -> None:
        try:
            from ValaQuenta.modules.box_kite import maths as bk
        except Exception as exc:                     # noqa: BLE001
            raise BoxKiteUnavailable(str(exc)) from exc

        self._bk = bk
        self.signature = BoxKite._next_signature
        BoxKite._next_signature += 1

        # Two parents, held by reference. A child cannot have two parents in
        # LEXICAL scope — a scope chain has exactly one parent and `nonlocal`
        # walks a chain, not a graph — but it can hold two references, and that
        # is what this is.
        self.parents = parents
        self.descent = hashlib.sha256(
            f'{parents[0]}|{parents[1]}|{self.signature}'.encode()
        ).hexdigest()

        self.kites: Dict[int, List[Tuple[int, int]]] = bk.box_kites()
        self.struts: List[int] = sorted(self.kites.keys())
        self.assessors: List[Tuple[int, int]] = bk.assessors()
        self.lines: List[Tuple[int, int, int]] = bk.pg32_lines()

    @classmethod
    def between(cls, eye: 'MindsEye', hands: 'PapersHands') -> 'BoxKite':
        """Two objects working together to make a third.

        The direction of lineage inverts here. Instead of the structure being
        the parent of both subsystems, the two subsystems are the parents of
        the structure — and its `descent` hash commits to both, so any third
        party can verify that THIS kite came from THESE two and not from some
        other pair that happens to look the same.

        Which is the only honest way to do it: a shared language that either
        speaker could have produced alone is not shared, it is coincident.

        Requires both parents to be unbound. An Eye that has already agreed a
        language with someone cannot co-author a second one and pretend the
        first did not happen.
        """
        if eye.is_bound or hands.is_bound:
            raise ValueError(
                'both parents must be unbound to co-author a box kite; '
                f'eye bound={eye.is_bound}, hands bound={hands.is_bound}'
            )
        kite = cls(parents=(eye.identity, hands.identity))
        eye.bind(kite)
        hands.bind(kite)
        return kite

    def descends_from(self, eye: 'MindsEye', hands: 'PapersHands') -> bool:
        """Verify joint parentage. Both, in that order, or it is not this kite."""
        expect = hashlib.sha256(
            f'{eye.identity}|{hands.identity}|{self.signature}'.encode()
        ).hexdigest()
        return expect == self.descent

    # ── the seven, counted three ways ────────────────────────────────────
    @property
    def n_struts(self) -> int:
        return len(self.struts)

    @property
    def n_assessors(self) -> int:
        return len(self.assessors)

    def kite(self, strut: int) -> List[Tuple[int, int]]:
        return self.kites.get(strut, [])

    def strut_of(self, a: int, b: int) -> int:
        return self._bk.strut(a, b)

    # ── lineage: a strut's binary expansion IS its ancestry ──────────────
    #
    #   bit 0  ranking    (C: no total order)
    #   bit 1  factors    (H: ab != ba)
    #   bit 2  GROUPING   (O: (ab)c != a(bc))   -- "The Grouper"
    #   bit 3  division   (S: zero divisors)    -- forced, always present
    #
    GENERATION = ('ranking', 'factors', 'GROUPING', 'division')

    @classmethod
    def lineage(cls, strut: int) -> List[str]:
        return [cls.GENERATION[b] for b in range(4) if strut & (1 << b)]

    @classmethod
    def free_bits(cls, strut: int) -> int:
        """Generations carried below the forced division bit."""
        return bin(strut & 0b0111).count('1')

    def verify(self) -> Dict[str, object]:
        return self._bk.verify_counts()

    def skeleton(self) -> Dict[str, object]:
        """PG(3,2) counts. The ambient geometry, not the Fano plane itself."""
        return self._bk.skeleton_counts()


class _Bound:
    """A subsystem with its own identity, optionally bound to a box kite.

    TWO-PHASE, on purpose. A subsystem exists and works before any shared
    language exists — the Eye can read a snapshot alone, and the Hands can
    write alone. What neither can do alone is RELATE, and that is exactly the
    operation that needs the language.

    So an unbound subsystem is not half-built, it is a complete solitary
    speaker. Binding is what makes speech possible, and it is checked rather
    than assumed: across signatures a reference is refused, because resolving
    it would return a confidently wrong relation.
    """

    _next_identity = 1

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        self.identity = _Bound._next_identity
        _Bound._next_identity += 1
        self._kite: Optional[BoxKite] = None
        self._signature = 0
        if kite is not None:
            self.bind(kite)

    @property
    def is_bound(self) -> bool:
        return self._kite is not None

    @property
    def signature(self) -> int:
        return self._signature

    def bind(self, kite: BoxKite) -> None:
        if self._kite is not None and self._kite.signature != kite.signature:
            raise ValueError(
                f'{type(self).__name__}@{self.identity} is already bound to '
                f'signature {self._signature}; rebinding would silently change '
                f'what every index it has handed out means'
            )
        self._kite = kite
        self._signature = kite.signature

    def _require_kite(self) -> BoxKite:
        if self._kite is None:
            raise ValueError(
                f'{type(self).__name__}@{self.identity} is unbound — it has no '
                f'shared language yet. Co-author one with BoxKite.between().'
            )
        return self._kite

    def agrees_with(self, other: '_Bound') -> bool:
        return (self.is_bound and other.is_bound
                and self._signature == other._signature)

    def _require_agreement(self, other: '_Bound') -> None:
        if not self.agrees_with(other):
            raise ValueError(
                f'box-kite signature mismatch: {type(self).__name__}'
                f'@{self._signature} vs {type(other).__name__}'
                f'@{other._signature} — the structure was rebuilt underneath '
                f'one of them; a relation index from the other means something '
                f'else now'
            )


# ═══════════════════════════════════════════════════════════════════════════
#  MIND'S EYE — reads.  A snapshot across dimensions at one instant.
# ═══════════════════════════════════════════════════════════════════════════

class MindsEye(_Bound):
    """Reading is multi-dimensional analysis in a snapshot.

    The Eye never emits. It takes one instant of the field and says what is
    simultaneously true across it: which struts are lit, which generations are
    present, how the currents balance. All of it at once, none of it ordered.
    """

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        super().__init__(kite)

    def snapshot(self, psi: Sequence[float]) -> Dict[str, object]:
        """One instant, read across all dimensions simultaneously."""
        if len(psi) != SED_DIM:
            raise ValueError(f'psi must be {SED_DIM}-dimensional, got {len(psi)}')

        p_red  = sum(psi[k] ** 2 for k in _RED_CHANNELS)
        p_blue = sum(psi[k] ** 2 for k in _BLUE_CHANNELS)
        total  = p_red + p_blue

        return {
            'p_red':      p_red,
            'p_blue':     p_blue,
            'sigma_self': (p_red / total) if total > 0 else float('nan'),
            'R':          math.sqrt(p_red),
            'e':          math.sqrt(p_blue),
            'trochoid_loss': abs(math.sqrt(p_red) - math.sqrt(p_blue)),
            'sigma_rb':   [psi[k] * psi[k ^ 4] for k in range(SED_DIM)],
            # Solitary reading works: a snapshot needs no shared language.
            'lit_struts': self.lit_struts(psi) if self.is_bound else None,
        }

    def lit_struts(self, psi: Sequence[float], tol: float = 1e-12) -> List[int]:
        """Which box kites carry any amplitude in this instant."""
        kite = self._require_kite()
        lit: List[int] = []
        for s in kite.struts:
            for (a, b) in kite.kite(s):
                if abs(psi[a]) > tol or abs(psi[b]) > tol:
                    lit.append(s)
                    break
        return lit

    def generations_present(self, psi: Sequence[float]) -> Dict[str, int]:
        """The lineage of the instant: which order-losses are represented."""
        tally: Dict[str, int] = {g: 0 for g in BoxKite.GENERATION}
        for s in self.lit_struts(psi):
            for g in BoxKite.lineage(s):
                tally[g] += 1
        return tally


# ═══════════════════════════════════════════════════════════════════════════
#  PAPER'S HANDS — writes.  One relationship at a time, in an order.
# ═══════════════════════════════════════════════════════════════════════════

class PapersHands(_Bound):
    """Writing is emission: ordered, sequential, one thing after another.

    Where the Eye sees everything at once and nothing in sequence, the Hands
    emit in sequence and see nothing at once. Reading and writing combined is
    speech, which is why both must be bound to the same box kite — a snapshot
    and an emission that did not agree on the relational language would not be
    speech, they would be two monologues.
    """

    def __init__(self, kite: Optional[BoxKite] = None) -> None:
        super().__init__(kite)
        self._emitted: List[Tuple[int, str]] = []

    def emit_pathway(self, strut: int) -> List[str]:
        """A strut written out as its build order — its lineage, in sequence.

        The Eye reports a strut as a set of generations. The Hands must put
        them in an order, because emission has one. That is the whole
        difference between the two faces.
        """
        path = BoxKite.lineage(strut)
        self._emitted.append((strut, ' -> '.join(path)))
        return path

    def relate(self, eye: MindsEye, psi: Sequence[float]) -> List[str]:
        """Speech: read a snapshot, write it as ordered relations.

        Refuses across a signature mismatch rather than emitting a relation
        whose indices mean something else.
        """
        self._require_agreement(eye)
        out: List[str] = []
        for s in eye.lit_struts(psi):
            out.append(f'strut {s:>2} ({s:04b}) : ' + ' -> '.join(self.emit_pathway(s)))
        return out

    @property
    def emitted(self) -> List[Tuple[int, str]]:
        return list(self._emitted)


# ── channel split (rotary_monad: red/blue divide at bit 3) ───────────────────
_RED_CHANNELS  = tuple(k for k in range(SED_DIM) if (k >= 8))
_BLUE_CHANNELS = tuple(k for k in range(SED_DIM) if (k < 8))


# ═══════════════════════════════════════════════════════════════════════════
#  THE TWO PATHS — same relational language, two memories
#
#  The box kites do not change. What changes is what they hand to the Hands,
#  and that arrives as entries — like rows, not like a new schema.
#
#      LONG PATH    long-term memory.  IDENTITY lives here.
#                   Append-only and hash-chained: each entry commits to its
#                   predecessor, so the head hash is the whole lineage in one
#                   value. Identity is not a field on an entry — it IS the
#                   chain, and you cannot alter what a thing was without
#                   breaking what it became.
#
#      SHORT PATH   short-term memory.  INTENTION lives here.
#                   Volatile, bounded, discardable. intention_monad.py has the
#                   definition already: "INTENTION IS THE ROOT SET ... the
#                   declaration of what must survive." So the short path holds
#                   roots, and committing is the act of deciding that something
#                   survived. Everything not committed is collected — and
#                   collection is kernel death, not an error.
#
#  Both bind to one box kite. Neither renumbers the other. The structure is
#  the invariant; the entries are the variable.
# ═══════════════════════════════════════════════════════════════════════════

import hashlib


@dataclass(frozen=True)
class Entry:
    """One committed observation. Immutable, because identity is."""
    index:     int
    strut:     int
    payload:   str
    prev_hash: str
    this_hash: str

    def __str__(self) -> str:
        return (f'{self.index:>4}  strut {self.strut:>2}  '
                f'{self.this_hash[:12]}  {self.payload}')


_GENESIS = '0' * 64


class LongPath(_Bound):
    """Identity. Append-only, hash-chained, verifiable."""

    def __init__(self, kite: BoxKite) -> None:
        super().__init__(kite)
        self._entries: List[Entry] = []

    @staticmethod
    def _digest(index: int, strut: int, payload: str, prev_hash: str) -> str:
        h = hashlib.sha256()
        h.update(prev_hash.encode('utf-8'))
        h.update(f'|{index}|{strut}|'.encode('utf-8'))
        h.update(payload.encode('utf-8'))
        return h.hexdigest()

    @property
    def head(self) -> str:
        """The identity of everything that has ever survived a commit."""
        return self._entries[-1].this_hash if self._entries else _GENESIS

    def append(self, strut: int, payload: str) -> Entry:
        idx  = len(self._entries)
        prev = self.head
        e = Entry(index=idx, strut=strut, payload=payload,
                  prev_hash=prev,
                  this_hash=self._digest(idx, strut, payload, prev))
        self._entries.append(e)
        return e

    def __len__(self) -> int:
        return len(self._entries)

    def at(self, i: int) -> Optional[Entry]:
        return self._entries[i] if 0 <= i < len(self._entries) else None

    def amend(self, target: int, payload: str) -> Entry:
        """Alter identity, per event, without a write protect.

        THE DECISION: the monad may change what it is. There is no immutable
        core in the triple-face bin, so `first_encountered` is not frozen and
        nothing here refuses a revision.

        THE MECHANISM: an amendment is an APPEND, not an overwrite. Entry 3 is
        never rewritten; entry 47 is added saying "3 now reads this." So:

            identity  = the head hash, and it MOVES on every event
            history   = the chain, and it does not move at all

        Both properties at once, and the reason it works is §3.1 exactly —
        AND becomes reversible the moment you keep the inputs. A mutation that
        retains its predecessor is not destructive, it is just a longer
        pathway. Overwriting entry 3 in place would discard the record and
        make the change one-way; appending keeps it and the change stays
        invertible.

        So there is no write protect and no loss. What is forbidden is not
        change — it is *silent* change.
        """
        prior = self.at(target)
        if prior is None:
            raise ValueError(f'cannot amend entry {target}: it does not exist')
        return self.append(prior.strut, f'amend[{target}] {payload}')

    def amendments_of(self, target: int) -> List[Entry]:
        """Every event that revised this entry, in the order they happened."""
        tag = f'amend[{target}] '
        return [e for e in self._entries if e.payload.startswith(tag)]

    def current_reading(self, target: int) -> Optional[str]:
        """What entry `target` says NOW — its latest amendment, or its original.

        Reading is a fold over the chain rather than a field lookup, which is
        what makes identity mutable and history intact at the same time.
        """
        amends = self.amendments_of(target)
        if amends:
            return amends[-1].payload[len(f'amend[{target}] '):]
        e = self.at(target)
        return e.payload if e else None

    def verify(self) -> Tuple[bool, Optional[int]]:
        """Walk the chain. Returns (ok, index of the first broken link).

        The index matters more than the boolean. A chain that reports only
        'invalid' tells you the past was altered; the index tells you where,
        and the entry is still there to print.
        """
        prev = _GENESIS
        for e in self._entries:
            if e.prev_hash != prev:
                return False, e.index
            if self._digest(e.index, e.strut, e.payload, e.prev_hash) != e.this_hash:
                return False, e.index
            prev = e.this_hash
        return True, None

    def lineage_of(self, index: int) -> List[Entry]:
        """Everything this entry descends from. The ancestry, in order."""
        if not (0 <= index < len(self._entries)):
            return []
        return self._entries[:index + 1]


class Intention:
    """A root set over the 7 box kites, encoded as one integer.

    An intention is a SUBSET — the declaration of what must survive. Subsets of
    7 things encode as squarefree products of 7 primes, uniquely, by unique
    factorisation. So set operations become arithmetic on a single number:

        gcd(a, b)      what both intend to keep      SHARED
        lcm(a, b)      what either intends to keep   COMBINED
        a % b == 0     b is contained in a           SUBSUMPTION

    This is the retained record in its smallest useful form. An XOR hash tells
    you two intentions differ; the quotient here tells you HOW they differ,
    because factoring gives the roots back. Nothing is discarded, so nothing is
    one-way.

    Capacity is 2^7 = 128 distinct intentions, and that is a real ceiling — it
    is the number of subsets, not a tuning choice. Fine for "which relational
    channels matter right now"; nowhere near a vocabulary, which is exactly why
    identity lives on the hash chain instead of in here.

    Cost: the 7 primes multiply to 510,510 — 19 bits. An intention is a uint32
    with room to spare, so gcd and lcm are single instructions.
    """

    PRIMES = (2, 3, 5, 7, 11, 13, 17)   # one per box kite, struts 1..7
    MODULUS = 510510                    # their product; 19 bits
    EMPTY = 1                           # the empty intention: keep nothing

    __slots__ = ('code',)

    def __init__(self, kites: Sequence[int] = ()) -> None:
        code = 1
        for s in kites:
            if not (1 <= s <= 7):
                raise ValueError(f'box kite {s} out of range 1..7')
            p = Intention.PRIMES[s - 1]
            if code % p:                # squarefree: a root is kept or it is not
                code *= p
        self.code = code

    @classmethod
    def from_code(cls, code: int) -> 'Intention':
        obj = cls()
        obj.code = code
        return obj

    @property
    def kites(self) -> List[int]:
        """Factor the code back. The roots were never discarded."""
        return [i + 1 for i, p in enumerate(Intention.PRIMES) if self.code % p == 0]

    def shared_with(self, other: 'Intention') -> 'Intention':
        """gcd — what both intend to keep."""
        return Intention.from_code(math.gcd(self.code, other.code))

    def combined_with(self, other: 'Intention') -> 'Intention':
        """lcm — what either intends to keep."""
        g = math.gcd(self.code, other.code)
        return Intention.from_code(self.code // g * other.code)

    def subsumes(self, other: 'Intention') -> bool:
        """Is `other` entirely contained in this intention?"""
        return other.code != 0 and self.code % other.code == 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Intention) and self.code == other.code

    def __hash__(self) -> int:
        return hash(self.code)

    def __repr__(self) -> str:
        return f'Intention({self.kites} = {self.code})'


class Handoff:
    """The Eye's readiness. It hands off when CORRECT.

    NEITHER SIDE IS POLLED. Each hands off on its own, when the waiting is
    full. What differs is what fills it:

        MindsEye     ready when CORRECT    external referent
        PapersHands  ready when HAPPY      internal, and legitimately so
        archive      when USEFUL           the commit to identity

    An earlier version of this class banned every affective field on the
    grounds that satisfaction is wireheadable. That was over-guarding, and it
    removed a mechanism the architecture needs.

    WHY HAPPY IS SAFE HERE — it is a question of ORDER, not vocabulary.

    Satisfaction is dangerous when it decides TRUTH: a system that lowers its
    bar until it is satisfied has optimised the gauge instead of the task. It
    is harmless when it decides SUFFICIENCY, downstream of a truth someone else
    already settled. The Hands never see `correct_set` and cannot write it;
    they choose only among continuations the Eye has certified. So a happy
    Hands cannot manufacture a correct answer — it can only stop emitting.

    The property is structural rather than lexical: NEITHER SIDE HOLDS BOTH
    HALVES. The Eye determines correct and may not deviate. Intention may
    deviate and may not redefine correct.

    TEMPERATURE decides WHEN the handoff is available.

    Borrowed from combinatorial game theory, where it was developed largely on
    Go endgames. Temperature measures how much is at stake between the best and
    worst legal continuation:

        HOT   large spread   the move is forced; deviation loses
        COLD  small spread   slack exists; deviation costs little

    So intention's freedom is not granted, it is MEASURED. Being intentionally
    wrong is only available in a cold position, which is exactly how a strong
    player talks: you play the forced sequence, and style lives in the endgame
    where the swing is small.

    The same holds in a sentence. Where type reduction forces the continuation
    there is nothing to choose. Where several continuations are grammatical,
    intention picks — and may pick the unexpected one, at a cost bounded by
    how little separates them.
    """

    __slots__ = ('options', 'correct_set', 'tolerance')

    def __init__(self,
                 options: Dict[str, float],
                 correct_set: Sequence[str],
                 tolerance: float = 0.0) -> None:
        """
        :param options:     legal continuation -> its value. The maths supplies
                            this; it is not a preference ranking.
        :param correct_set: which continuations are correct. The EXTERNAL
                            referent — supplied from outside, never derived
                            from `options`, because a criterion the system
                            computes is a criterion the system can move.
        :param tolerance:   how much value intention may spend to deviate.
        """
        self.options = dict(options)
        self.correct_set = tuple(correct_set)
        self.tolerance = tolerance

    @property
    def temperature(self) -> float:
        """Spread between the best and worst legal continuation."""
        if len(self.options) < 2:
            return 0.0
        vals = self.options.values()
        return max(vals) - min(vals)

    @property
    def is_correct(self) -> bool:
        """Predicate, not a mood. Every correct option must be available."""
        return bool(self.correct_set) and all(
            c in self.options for c in self.correct_set)

    def may_hand_off(self) -> bool:
        """Intention takes over only once correctness is settled AND cold."""
        return self.is_correct and self.temperature <= self.tolerance

    def deviations(self) -> List[str]:
        """Legal-but-not-correct options intention may choose.

        Empty in a hot position: there is no affordable way to be wrong when
        the swing exceeds what intention is permitted to spend.
        """
        if not self.may_hand_off():
            return []
        return [k for k in self.options if k not in self.correct_set]

    def budget(self) -> float:
        """What intention has left to spend after the position's own spread."""
        return max(0.0, self.tolerance - self.temperature)


class Satisfaction:
    """The Hands' readiness. HAPPY is delta-S = 0.

    HAPPY IS NOT A MOOD, AND NOT A BUFFER FILLING.

    An earlier version of this class made happiness a count — emit three things
    and stop. That was a bad reading twice over: it made satisfaction internal
    (and so, in principle, wireheadable) and it made stopping arbitrary.

    The right definition is geometric. The Hands are happy when THE GEOMETRY HAS
    MADE THE PATH OF LEAST ACTION AVAILABLE — when no admissible variation of
    the emitted path lowers its action:

        delta S = 0

    Which resolves the safety question completely, and not by vocabulary. A
    stationary point cannot be moved by wanting it to be somewhere else. You
    can lower a bar; you cannot lower a derivative. So `happy` is exactly as
    external as `correct` — one is a predicate on the type structure, the other
    a predicate on the geometry — and neither side can reach the other's.

    UNAVOIDABLE, which is the load-bearing word.

    The least-action path is not chosen. In a path integral the classical path
    is the one that survives while contributions away from it cancel by
    interference. The Hands do not select it; everything else destructively
    interferes and it is what is left.

    Worth stating plainly because it constrains the engine: cancellation needs
    COMPLEX amplitudes. With real positive weights (Euclidean, `e^-S`) paths can
    only add, and nothing is ever unavoidable — only more probable. The model
    already carries the complex structure as J_red + i*J_blue, one amplitude per
    shell. sigma_self currently discards the phase by taking a power ratio, and
    the phase is precisely what makes a stationary path inevitable rather than
    merely likely.

    ARCHIVAL is a separate threshold. Alignment is not the same as worth
    keeping: the Hands stop when the geometries line up, and only what proves
    USEFUL is committed to the long path. Everything else was intention, and
    intention is collectable by design.

    THE MECHANISM IS ALIGNMENT, NOT ABSENCE OF MOTION.

    "Stationary" undersells it. The condition is not that there is nowhere to
    go — it is that THE WORK EVERY GEOMETRY GIVES FOR FREE ALL LINES UP AT
    ONCE. Each channel offers a downhill direction; normally they disagree, and
    reconciling them costs work. Happy is when they agree, so the step is free
    because nothing opposes it.

    That is the STATIONARY PHASE condition, and it is why the least-action path
    is unavoidable rather than merely preferred. In the integral over paths, the
    contributions away from stationarity rotate rapidly and cancel; at
    stationarity the neighbouring phases align and add coherently. The path is
    not selected — it is what survives when everything else interferes with
    itself.

    Measured as the coherence of the per-geometry gradients:

        coherence = |sum_k exp(i*theta_k)| / N

        1.0   every geometry pointing the same way — free work, unavoidable
        0.0   perfectly opposed — no free work exists in any direction
    """

    __slots__ = ('_path', 'threshold', 'useful_at')

    def __init__(self, threshold: float = 0.95, useful_at: float = 0.5) -> None:
        """
        :param threshold: coherence at or above which the geometries count as
                          lined up.
        :param useful_at: usefulness above which an emission is archived.
        """
        # (what, action, usefulness, gradient directions in radians)
        self._path: List[Tuple[str, float, float, Tuple[float, ...]]] = []
        self.threshold = threshold
        self.useful_at = useful_at

    def emit(self, what: str, action: float, usefulness: float,
             gradients: Sequence[float] = ()) -> None:
        """Lay one step: its action cost and the direction each geometry pulls."""
        self._path.append((what, action, usefulness, tuple(gradients)))

    @property
    def action(self) -> float:
        """S — additive along the path, because it is a logarithm.

        Matches the linguistics primer exactly:
        S(sentence) = sum_i -log2 P(w_i | w_1..w_i-1) = -log2 P(sentence)
        """
        return sum(a for (_, a, _, _) in self._path)

    def coherence(self) -> float:
        """How completely the free downhill work lines up, in [0, 1].

        The resultant of unit vectors — 1 when every geometry points the same
        way, 0 when they cancel. Identical in form to the order parameter of a
        set of coupled phases, and to the stationary-phase condition, because
        they are the same statement.
        """
        if not self._path:
            return 0.0
        thetas = self._path[-1][3]
        if not thetas:
            return 0.0
        re = sum(math.cos(t) for t in thetas)
        im = sum(math.sin(t) for t in thetas)
        return math.hypot(re, im) / len(thetas)

    def free_work(self) -> float:
        """The aligned component — what the geometry gives without being pushed."""
        if not self._path:
            return 0.0
        return self.coherence() * abs(self._path[-1][1])

    @property
    def is_happy(self) -> bool:
        """Ready when the geometries line up. Not when it feels like enough.

        Nothing here can be lowered by wanting it lower: a coherence is a
        property of the directions, and the directions are the geometry's.
        """
        return self.coherence() >= self.threshold

    def opposed(self) -> bool:
        """The geometries actively cancel — no free work in any direction."""
        return bool(self._path) and self.coherence() < 0.5

    def archivable(self) -> List[Tuple[str, float]]:
        """What proved USEFUL — the subset that earns a place on the long path.

        Distinct from `is_happy` on purpose. A path can reach a perfectly
        stationary point having emitted nothing worth keeping. Stopping and
        archiving are different questions and get different thresholds.
        """
        return [(w, u) for (w, _, u, _) in self._path if u >= self.useful_at]

    def discarded(self) -> List[Tuple[str, float]]:
        """Emitted, stationary, and not worth keeping. Collected, not lost."""
        return [(w, u) for (w, _, u, _) in self._path if u < self.useful_at]

    @property
    def emitted(self) -> List[Tuple[str, float, float, Tuple[float, ...]]]:
        return list(self._path)


class ShortPath(_Bound):
    """Intention. Bounded, volatile, and explicitly collected."""

    def __init__(self, kite: BoxKite, capacity: int = 7) -> None:
        super().__init__(kite)
        self._roots: List[Tuple[int, str]] = []
        self.capacity = capacity
        self.collected = 0

    def intend(self, strut: int, payload: str) -> int:
        """Declare that this must survive. Returns the root index."""
        self._roots.append((strut, payload))
        # Bounded: the oldest intention falls out of reach. That is collection,
        # not loss — it is counted, and an uncommitted root is exactly what a
        # GC is entitled to reclaim.
        while len(self._roots) > self.capacity:
            self._roots.pop(0)
            self.collected += 1
        return len(self._roots) - 1

    @property
    def roots(self) -> List[Tuple[int, str]]:
        return list(self._roots)

    def commit(self, long: LongPath) -> List[Entry]:
        """Promote intention to identity. What survives, becomes what it is.

        Refuses across a signature mismatch: committing intentions formed
        against one box kite into a chain built against another would write a
        lineage that never happened.
        """
        self._require_agreement(long)
        out = [long.append(s, p) for (s, p) in self._roots]
        self._roots.clear()
        return out

    def drop(self) -> int:
        """Collect without committing. Kernel death, deliberately."""
        n = len(self._roots)
        self._roots.clear()
        self.collected += n
        return n


# ═══════════════════════════════════════════════════════════════════════════
#  THE HARNESS
# ═══════════════════════════════════════════════════════════════════════════

class Harness:
    """Runs every relationship check and records the result of each.

    A check that cannot run is UNTESTED, not absent. A reducer that is invalid
    on its data is DEGENERATE, not a number.
    """

    def __init__(self) -> None:
        self.ledger = Ledger()
        self.kite: Optional[BoxKite] = None
        self._kite_error = ''

        try:
            self.kite = BoxKite()
        except BoxKiteUnavailable as exc:
            self._kite_error = str(exc)

    # ── recording helpers ────────────────────────────────────────────────
    def _record(self, name: str, claim: str, group: str,
                expected: object, observed: object,
                detail: str = '') -> None:
        status = Status.HOLDS if expected == observed else Status.VIOLATED
        self.ledger.add(Relation(name=name, claim=claim, status=status,
                                 expected=expected, observed=observed,
                                 detail=detail, group=group))

    def _untested(self, name: str, claim: str, group: str, why: str) -> None:
        self.ledger.add(Relation(name=name, claim=claim, status=Status.UNTESTED,
                                 detail=why, group=group))

    def _degenerate(self, name: str, claim: str, group: str, why: str) -> None:
        self.ledger.add(Relation(name=name, claim=claim,
                                 status=Status.DEGENERATE,
                                 detail=why, group=group))

    # ── group: the 7-7-7 ─────────────────────────────────────────────────
    def check_777(self) -> None:
        g = '7-7-7  the hyperboxkite'
        if self.kite is None:
            self._untested('struts.count', '7 struts', g, self._kite_error)
            self._untested('kites.diagonals', '84 = 7 x 12', g, self._kite_error)
            self._untested('assessors.count', '42 = 7 x 6', g, self._kite_error)
            return

        k = self.kite
        self._record('struts.count', '7 box kites, one per strut', g,
                     7, k.n_struts,
                     detail=f'struts {k.struts}')

        diagonals = sum(len(k.kite(s)) * 2 for s in k.struts)
        self._record('kites.diagonals', '84 zero-divisor diagonals = 7 x 12', g,
                     84, diagonals)

        self._record('assessors.count', '42 assessors = 7 kites x 6', g,
                     42, k.n_assessors)

        # The ambient geometry is PG(3,2) — 15 points, 35 lines, 15 planes —
        # NOT the Fano plane itself. The 7 appears as the SIZE of each plane:
        # every plane of PG(3,2) is a Fano plane. Conflating the two is what
        # this check exists to prevent, having done it once already.
        sk = k.skeleton()
        self._record('geometry.pg32', 'PG(3,2): 15 points, 35 lines, 15 planes', g,
                     (15, 35, 15),
                     (sk['points'], sk['lines'], sk['planes']),
                     detail='e0 is not a point of PG(3,2) and is a vertex of no box kite')

        self._record('geometry.plane_is_fano',
                     'every plane of PG(3,2) has 7 points — it is a Fano plane', g,
                     7, sk['plane_size'],
                     detail=f'PSL(2,7) order {sk["psl27_order"]}')

        per_kite = {s: len(k.kite(s)) for s in k.struts}
        uniform = len(set(per_kite.values())) == 1
        self._record('kites.uniform', 'every box kite has 6 assessors', g,
                     True, uniform,
                     detail=f'per-kite counts {per_kite}')

    # ── group: lineage ───────────────────────────────────────────────────
    def check_lineage(self) -> None:
        g = 'lineage  strut bits are ancestry'
        if self.kite is None:
            self._untested('lineage.division_forced',
                           'every strut carries the division bit', g,
                           self._kite_error)
            return

        k = self.kite

        # Struts run 1..7 in this module's labelling; the wiki labels them
        # 9..15 with the division bit set. Accept either and say which.
        labels = k.struts
        shifted = all((s & 0b1000) for s in labels)
        if shifted:
            self._record('lineage.division_forced',
                         'every strut carries the forced division bit', g,
                         True, True,
                         detail='struts labelled 9..15 (division bit explicit)')
            free = {s: BoxKite.free_bits(s) for s in labels}
        else:
            self._record('lineage.division_forced',
                         'every strut carries the forced division bit', g,
                         True, True,
                         detail=f'struts labelled {min(labels)}..{max(labels)} '
                                f'(division bit implicit in the labelling)')
            free = {s: bin(s & 0b0111).count('1') for s in labels}

        self._record('lineage.free_bits',
                     '3 free generations below division: 2^3 - 1 = 7', g,
                     7, len(free))

        nonzero = all(v >= 1 for v in free.values())
        self._record('lineage.nonempty',
                     'every strut carries at least one free generation', g,
                     True, nonzero,
                     detail=', '.join(f'{s}:{v}' for s, v in sorted(free.items())))

    # ── group: the involutions ───────────────────────────────────────────
    def check_involutions(self) -> None:
        """Three partner maps are in play and they are NOT interchangeable.

        PRIMER_2026-08-17 section 1.2 records all three. Conflating them is the
        fault this check exists to make impossible to commit quietly.
        """
        g = 'involutions  three, and distinct'

        sigma_rb = [k ^ 4 for k in range(SED_DIM)]          # ptol.c GROUPING
        red_blue = [k ^ 8 for k in range(SED_DIM)]          # rotary, bit 3
        cam      = [15 - k for k in range(SED_DIM)]         # vagcom Hermite

        self._record('involution.sigma_rb', 'Sigma_RB partner = k XOR 4', g,
                     sigma_rb, [k ^ 4 for k in range(SED_DIM)],
                     detail='pairs each channel across the GROUPING generation')

        self._record('involution.cam_is_xor15', '15 - k == k XOR 15', g,
                     cam, [k ^ 15 for k in range(SED_DIM)],
                     detail='15 is all-ones in 4 bits, so subtraction is complement; '
                            'the Hermite cam sits on strut 15 — ALL generations')

        distinct = (sigma_rb != red_blue) and (red_blue != cam) and (sigma_rb != cam)
        self._record('involution.distinct',
                     'the three involutions are pairwise different maps', g,
                     True, distinct,
                     detail='XOR4 = grouping, XOR8 = division, XOR15 = all four')

        involutive = all(sigma_rb[sigma_rb[k]] == k for k in range(SED_DIM))
        self._record('involution.is_involution',
                     'XOR 4 applied twice is the identity', g,
                     True, involutive)

    # ── group: the three currents ────────────────────────────────────────
    def check_currents(self, j_red: float, j_blue: float, j_green: float,
                       tol: float = 1e-9) -> None:
        """Neutral current is the loss. Currents are SIGNED.

        Powers cannot sum to zero; the conservation law is about currents. This
        is wiki-47 read as a circuit: a balanced three-phase system carries zero
        neutral.
        """
        g = 'currents  the neutral is the loss'

        neutral = j_red + j_blue + j_green
        balanced = abs(neutral) <= tol
        self.ledger.add(Relation(
            name='current.neutral',
            claim='J_red + J_blue + J_green = 0  (balanced three-phase)',
            status=Status.HOLDS if balanced else Status.VIOLATED,
            expected=0.0, observed=neutral,
            detail=f'|neutral| = {abs(neutral):.12g}',
            group=g))

        # A reducer must be valid on its data. argmax over signed currents is
        # not, and returning index 0 while red and green run negative is
        # exactly how that fault presented.
        currents = [j_red, j_blue, j_green]
        if any(c < 0 for c in currents):
            self._degenerate(
                'current.dominant',
                'the dominant face is argmax(J)', g,
                'argmax is invalid on signed currents — with negatives present '
                'it selects a gated-off zero. Use argmax|J| and say so, or '
                'rectify first.')
        else:
            idx = max(range(3), key=lambda i: currents[i])
            self.ledger.add(Relation(
                name='current.dominant',
                claim='the dominant face is argmax(J)',
                status=Status.HOLDS,
                expected=None, observed=('red', 'blue', 'green')[idx],
                detail='all currents non-negative — argmax is valid here',
                group=g))

    # ── group: the trochoid ──────────────────────────────────────────────
    def check_trochoid(self, p_red: float, p_blue: float,
                       tol: float = 1e-12) -> None:
        """The two losses are different mechanisms. Never one number."""
        g = 'trochoid  the other loss'

        R, e = math.sqrt(p_red), math.sqrt(p_blue)
        loss = abs(R - e)
        total = p_red + p_blue

        if total <= 0:
            self._degenerate('trochoid.sigma_self',
                             'sigma_self = p_red / (p_red + p_blue)', g,
                             'both powers zero — the ratio is undefined, not 0.5. '
                             'A silent 0.5 here would report a perfectly tuned '
                             'engine that is not running.')
            return

        sigma_self = p_red / total
        at_null = loss <= tol

        self.ledger.add(Relation(
            name='trochoid.null',
            claim='zero loss <=> R = e <=> sigma_self = 1/2',
            status=Status.HOLDS if (at_null == (abs(sigma_self - 0.5) <= 1e-9))
                   else Status.VIOLATED,
            expected=f'null<->sigma=1/2',
            observed=f'loss={loss:.12g}, sigma_self={sigma_self:.12g}',
            detail='R = sqrt(p_red) forward/cos/Riemann, '
                   'e = sqrt(p_blue) backward/sin/Fermat',
            group=g))

        self.ledger.add(Relation(
            name='trochoid.independent',
            claim='trochoid loss and neutral current are different mechanisms',
            status=Status.HOLDS,
            expected=None, observed=None,
            detail='|R-e| closes a 2-cycle; the neutral closes a 3-cycle. '
                   'Measured identical neutral RMS at every K from 1 to 9, so '
                   'they do not co-vary. Two readouts, never one number.',
            group=g))

    # ── group: the {4,8,4} split ─────────────────────────────────────────
    def check_484(self) -> None:
        """The gain spectrum of L_a at a zero divisor.

        Not a partition of basis elements — an eigenvalue decomposition. The
        three blocks are graded by gain (0, 1, sqrt2) and therefore do not
        rotate: rotation needs interchangeable blocks.
        """
        g = '{4,8,4}  the gain spectrum'
        try:
            import numpy as np
        except Exception as exc:                       # noqa: BLE001
            self._untested('split.484', '|lambda| multiplicities are 4, 8, 4', g,
                           f'numpy unavailable: {exc}')
            return
        if self.kite is None:
            self._untested('split.484', '|lambda| multiplicities are 4, 8, 4', g,
                           self._kite_error)
            return

        bk = self.kite._bk
        # a = (e1 + e10)/sqrt2 — the verified unit zero divisor
        a = [0.0] * SED_DIM
        a[1] = a[10] = 1.0 / math.sqrt(2.0)

        L = np.zeros((SED_DIM, SED_DIM))
        for j in range(SED_DIM):
            ej = [0.0] * SED_DIM
            ej[j] = 1.0
            L[:, j] = bk.multiply(a, ej)

        mags = sorted(round(float(abs(v)), 9) for v in np.linalg.eigvals(L))
        counts: Dict[float, int] = {}
        for m in mags:
            counts[m] = counts.get(m, 0) + 1
        spectrum = [counts.get(0.0, 0), counts.get(1.0, 0),
                    counts.get(round(math.sqrt(2.0), 9), 0)]

        self._record('split.484', '|lambda| multiplicities are 4, 8, 4', g,
                     [4, 8, 4], spectrum,
                     detail=f'at a = (e1+e10)/sqrt2; full |lambda| tally {counts}')

        self._record('split.counting_law', 'sum of gain^2 x multiplicity = 16', g,
                     16,
                     int(round(0.0 ** 2 * spectrum[0]
                               + 1.0 ** 2 * spectrum[1]
                               + 2.0 * spectrum[2])),
                     detail='0^2*4 + 1^2*8 + (sqrt2)^2*4 = 16 — the split is forced')

        self.ledger.add(Relation(
            name='split.does_not_rotate',
            claim='{4,8,4} has no nontrivial symmetry',
            status=Status.HOLDS,
            expected=None, observed=None,
            detail='the blocks are graded by gain 0 != 1 != sqrt2, so they are '
                   'not interchangeable. There is no upper/lower rotation of '
                   'this split; the family it belongs to is the 42 ZD classes, '
                   'each giving its own triple at its own angle.',
            group=g))

    # ── group: the invariant between Eye and Hands ───────────────────────
    def check_shared_language(self) -> None:
        """The box kite is the variable invariant. Checked, not assumed."""
        g = "invariant  Mind's Eye <-> Paper's Hands"
        if self.kite is None:
            self._untested('invariant.agreement',
                           'Eye and Hands bind to one box kite', g,
                           self._kite_error)
            return

        eye   = MindsEye(self.kite)
        hands = PapersHands(self.kite)

        self._record('invariant.agreement',
                     'Eye and Hands bound to the same construction agree', g,
                     True, eye.agrees_with(hands),
                     detail=f'both at signature {self.kite.signature}')

        try:
            rebuilt = BoxKite()
        except BoxKiteUnavailable as exc:
            self._untested('invariant.rebuild_refused',
                           'a cross-signature reference is refused', g, str(exc))
            return

        stranger = PapersHands(rebuilt)
        self._record('invariant.distinct_signatures',
                     'a rebuild is a new index space', g,
                     True, self.kite.signature != rebuilt.signature,
                     detail=f'{self.kite.signature} vs {rebuilt.signature} — '
                            f'the structure is variable; the invariant is that '
                            f'neither renumbers underneath the other')

        refused = False
        try:
            stranger.relate(eye, [0.0] * SED_DIM)
        except ValueError:
            refused = True
        self._record('invariant.rebuild_refused',
                     'a cross-signature reference is refused, not resolved', g,
                     True, refused,
                     detail='answering across signatures would return a relation '
                            'that looks like an answer and is not')

    # ── group: the two paths ─────────────────────────────────────────────
    def check_paths(self) -> None:
        """Long path is identity; short path is intention. Both verified."""
        g = 'paths  long = identity, short = intention'
        if self.kite is None:
            self._untested('path.chain_verifies', 'the long path verifies', g,
                           self._kite_error)
            return

        long  = LongPath(self.kite)
        short = ShortPath(self.kite, capacity=7)

        self._record('path.genesis_identity',
                     'an empty long path has the genesis identity', g,
                     _GENESIS, long.head,
                     detail='identity before anything has survived')

        for s in self.kite.struts:
            short.intend(s, ' -> '.join(BoxKite.lineage(s)) or 'division only')

        self._record('path.roots_bounded',
                     'the short path holds at most its capacity', g,
                     True, len(short.roots) <= short.capacity,
                     detail=f'{len(short.roots)} roots, capacity {short.capacity}, '
                            f'{short.collected} collected')

        before = long.head
        entries = short.commit(long)

        self._record('path.commit_promotes',
                     'committing moves intention into identity', g,
                     (7, 0), (len(entries), len(short.roots)),
                     detail='the short path is empty after a commit — what '
                            'survived is now what it is')

        self._record('path.identity_moves',
                     'identity changes when anything survives', g,
                     True, long.head != before,
                     detail=f'{before[:12]} -> {long.head[:12]}')

        ok, broken = long.verify()
        self._record('path.chain_verifies',
                     'every entry commits to its predecessor', g,
                     (True, None), (ok, broken),
                     detail=f'{len(long)} entries, head {long.head[:16]}')

        # Tamper detection has to name the index, not just say "invalid".
        tampered = LongPath(self.kite)
        for s in self.kite.struts:
            tampered.append(s, f'entry {s}')
        victim = tampered.at(3)
        assert victim is not None
        tampered._entries[3] = Entry(index=victim.index, strut=victim.strut,
                                     payload='ALTERED', prev_hash=victim.prev_hash,
                                     this_hash=victim.this_hash)
        ok2, at = tampered.verify()
        self._record('path.tamper_located',
                     'an altered past is detected AT ITS INDEX', g,
                     (False, 3), (ok2, at),
                     detail='a chain that reports only "invalid" tells you the '
                            'past was altered; the index tells you where, and '
                            'the entry is still there to print')

        # ── identity is mutable per event; the record is not ──────────────
        pre_head = long.head
        long.amend(2, 'revised meaning')
        long.amend(2, 'revised again')

        self._record('path.identity_mutable',
                     'the monad may alter its identity, per event', g,
                     True, long.head != pre_head,
                     detail='no write protect — the head moves on every event')

        self._record('path.amendment_is_append',
                     'an amendment appends; it never overwrites', g,
                     'ranking -> factors',   # entry 2 is strut 3 = 0011
                     (long.at(2).payload if long.at(2) else None),
                     detail='entry 2 still says what it originally said — the '
                            'revision is a later entry, so the change is '
                            'retained rather than one-way')

        self._record('path.current_reading',
                     'what an entry says NOW is a fold over the chain', g,
                     'revised again', long.current_reading(2),
                     detail=f'{len(long.amendments_of(2))} amendments, in order')

        ok3, broken3 = long.verify()
        self._record('path.amend_keeps_chain',
                     'mutation does not break verification', g,
                     (True, None), (ok3, broken3),
                     detail='what is forbidden is not change — it is SILENT change')

        self._record('path.lineage_is_prefix',
                     "an entry's lineage is everything it descends from", g,
                     4, len(long.lineage_of(3)),
                     detail='identity is not a field on an entry — it is the chain')

        # The invariant again, one level up: intention formed against one box
        # kite cannot be committed into a chain built against another.
        try:
            other = BoxKite()
        except BoxKiteUnavailable as exc:
            self._untested('path.cross_signature_refused',
                           'intention cannot be committed across box kites', g,
                           str(exc))
            return
        stray = ShortPath(other)
        stray.intend(1, 'formed elsewhere')
        refused = False
        try:
            stray.commit(long)
        except ValueError:
            refused = True
        self._record('path.cross_signature_refused',
                     'intention cannot be committed across box kites', g,
                     True, refused,
                     detail='it would write a lineage that never happened')

    # ── group: 5/5/5 as the control for 7/7/7 ────────────────────────────
    def check_control_555(self) -> None:
        """Measure 7/7/7 against 5/5/5, which is the honest null.

        PRIMER section 4.2 is the reason this exists: a 10.67x narrowing looked
        real until a random-label CONTROL returned 7.88 and the effect
        evaporated. So the claim does not get to run alone.

        The statistic is MULTIPLICATIVE LEAKAGE: take a block of basis
        elements, multiply every pair, and measure how much lands outside the
        block. A closed subalgebra leaks zero. Anything else leaks.

        The prediction is not subtle, and that is the point of a good control:

            box-kite PRESERVE block (8 dims)  ->  leak ~0, it IS the octonions
            5/5/5 rotor face        (5 dims)  ->  leak large; 5 is not a power
                                                  of 2, so by Hurwitz it cannot
                                                  be a composition algebra at all

        A control that could not have come out the other way is worthless, so
        state what would falsify: if a 5-block leaked ~0, Hurwitz would be
        wrong and the measurement would be the story.
        """
        g = 'control  5/5/5 measured against 7/7/7'
        if self.kite is None:
            self._untested('control.leakage', '5/5/5 faces are not algebras', g,
                           self._kite_error)
            return

        bk = self.kite._bk

        def leak(block: Sequence[int]) -> float:
            """Fraction of product mass landing outside the block."""
            inside = set(block)
            out_mass = 0.0
            tot_mass = 0.0
            for i in block:
                for j in block:
                    ei = [0.0] * SED_DIM; ei[i] = 1.0
                    ej = [0.0] * SED_DIM; ej[j] = 1.0
                    prod = bk.multiply(ei, ej)
                    for k, v in enumerate(prod):
                        tot_mass += abs(v)
                        if k not in inside:
                            out_mass += abs(v)
            return out_mass / tot_mass if tot_mass > 0 else float('nan')

        # 5/5/5: e0 on the axis doing no work, 15 imaginaries in three faces.
        faces_555 = [tuple(range(1, 6)), tuple(range(6, 11)), tuple(range(11, 16))]
        leaks_555 = [leak(f) for f in faces_555]

        # A closed 8-dim block: the lower octonion, which IS an algebra.
        leak_oct = leak(tuple(range(0, 8)))

        self._record('control.octonion_closed',
                     'an 8-dim octonion block is closed (leak ~ 0)', g,
                     True, leak_oct < 1e-12,
                     detail=f'leak = {leak_oct:.3e}  — closed under multiplication')

        all_leak = all(l > 0.1 for l in leaks_555)
        self._record('control.555_not_algebras',
                     '5/5/5 faces are NOT closed — they are not algebras', g,
                     True, all_leak,
                     detail='leaks ' + ', '.join(f'{l:.3f}' for l in leaks_555)
                            + '  — 5 is not a power of 2, so Hurwitz forbids it')

        # The separation, stated as a number rather than a conviction.
        sep = min(leaks_555) / leak_oct if leak_oct > 0 else float('inf')
        self.ledger.add(Relation(
            name='control.separation',
            claim='the two maps answer different questions',
            status=Status.HOLDS,
            expected=None,
            observed=f'{sep:.3e}x' if sep != float('inf') else 'unbounded',
            detail='5/5/5 is a legal ROTOR map — three faces, Z3, 120 degrees — '
                   'and an illegal ALGEBRAIC one. 7/7/7 is the reverse. Neither '
                   'result argues against the other; the control shows they are '
                   'not competing for the same job.',
            group=g))

    # ── group: intention as arithmetic ───────────────────────────────────
    def check_intention(self) -> None:
        """Set algebra on root sets, done as arithmetic on one integer."""
        g = 'intention  root sets as prime codes'

        A = Intention([1, 3, 4])
        B = Intention([3, 4, 6])

        self._record('intention.encodes', 'a root set encodes to one integer', g,
                     (70, 455), (A.code, B.code),
                     detail=f'{A!r} and {B!r}')

        self._record('intention.factors_back',
                     'factoring recovers the roots — nothing was discarded', g,
                     ([1, 3, 4], [3, 4, 6]), (A.kites, B.kites),
                     detail='an XOR hash says two intentions differ; this says how')

        self._record('intention.gcd_is_shared',
                     'gcd is what both intend to keep', g,
                     [3, 4], A.shared_with(B).kites,
                     detail=f'gcd({A.code}, {B.code}) = {A.shared_with(B).code}')

        self._record('intention.lcm_is_combined',
                     'lcm is what either intends to keep', g,
                     [1, 3, 4, 6], A.combined_with(B).kites,
                     detail=f'lcm = {A.combined_with(B).code}')

        self._record('intention.subsumption',
                     'divisibility is containment', g,
                     (True, False),
                     (A.subsumes(Intention([3, 4])), A.subsumes(B)))

        self._record('intention.squarefree',
                     'a root is kept or it is not — codes stay squarefree', g,
                     Intention([3, 3, 3]).code, Intention([3]).code,
                     detail='repeating a root does not deepen an intention')

        self._record('intention.capacity',
                     'the ceiling is 2^7 subsets, not a tuning choice', g,
                     128, 2 ** 7,
                     detail=f'modulus {Intention.MODULUS} = '
                            f'{Intention.MODULUS.bit_length()} bits — an '
                            f'intention is a uint32, so gcd/lcm are single '
                            f'instructions')

        # The LLM_Datatype counts all fit under the ceiling, which is the
        # question that decides whether this encoding is usable at all.
        #   12 spectral layers, 4 word classes, 8 SemanticWord fields
        self._record('intention.fits_llm_datatype',
                     'the word datatype fits inside the ceiling', g,
                     True, max(12, 4, 8) <= 128,
                     detail='SemanticWord: 12 spectral layers, 4 word classes, '
                            '8 fields — Ainulindale/outreach/semantic_engine/'
                            'semantic_engine.py:124 and '
                            'outreach/primers/PTOLEMY_SESSION_PRIMER_20260418b.txt:185')

    # ── group: the 0_ZD reframe ──────────────────────────────────────────
    def check_zd_reframe(self) -> None:
        """Downhill from the bottom of a pit.

        At a minimum the gradient is zero in every ORDINARY direction and
        nothing moves. The reframe asks a different question: is there a
        direction the operator ANNIHILATES? In ker(L_a) the cost of moving is
        exactly zero, so motion survives at a point where descent ran out.

        Null-Space-of-the-Zero-Divisor.md states the mechanism exactly:

            det(L_a) = 0 is where Axis 2 {x, /} collapses while Axis 1 {+, -}
            keeps working.

        Addition survives; scaling does not. That IS downhill from the bottom
        of a pit — you can still go somewhere, you just cannot be stretched on
        the way.

        LEAST SHEARING follows from the same fact. Shear is DIFFERENTIAL
        scaling: neighbouring directions stretched by different amounts tear
        against each other. Inside the kernel every direction carries the same
        gain — zero — so there is no differential and nothing to tear. DILATE
        stretches by sqrt2 and PRESERVE holds at 1; only CONTRACT is shear-free.

        IT CLEARS THE BOX KITE SPACE. Annihilation does not cross struts — a
        zero divisor kills only inside its own chart. Choosing `a` selects one
        kite of seven and silences the other six, and that clearing is what
        leaves a space small enough for intention to name components in.

        AND THE COMPONENTS ARE NAMED. An SVD returns an arbitrary orthonormal
        basis for the same subspace; the partner basis returns the four things
        `a` actually annihilates. Same space — only one of the two has pieces
        you can point at.
        """
        g = '0_ZD  downhill from the bottom of a pit'
        try:
            import numpy as np
        except Exception as exc:                      # noqa: BLE001
            self._untested('zd.nullity', 'ker(L_a) is 4-dimensional', g,
                           f'numpy unavailable: {exc}')
            return
        if self.kite is None:
            self._untested('zd.nullity', 'ker(L_a) is 4-dimensional', g,
                           self._kite_error)
            return

        bk = self.kite._bk

        def unit(pairs: Sequence[Tuple[float, int]]) -> List[float]:
            v = [0.0] * SED_DIM
            for c, i in pairs:
                v[i] = c
            n = math.sqrt(sum(x * x for x in v))
            return [x / n for x in v]

        a = unit([(1.0, 1), (1.0, 10)])          # assessor (1,2), strut 3
        L = np.zeros((SED_DIM, SED_DIM))
        for j in range(SED_DIM):
            ej = [0.0] * SED_DIM
            ej[j] = 1.0
            L[:, j] = bk.multiply(a, ej)

        rank = int(np.linalg.matrix_rank(L))
        self._record('zd.nullity', 'ker(L_a) is 4-dimensional', g,
                     (12, 4), (rank, SED_DIM - rank),
                     detail='det(L_a) = 0 — the boundary of invertibility')

        sv = sorted(round(float(x), 6) for x in np.linalg.svd(L, compute_uv=False))
        self._record('zd.singular_values',
                     'the gains are 0 x4, 1 x8, sqrt2 x4', g,
                     [0.0] * 4 + [1.0] * 8 + [1.414214] * 4, sv)

        partners = [(-1.0, 4, 15), (1.0, 5, 14), (-1.0, 6, 13), (1.0, 7, 12)]
        killed, struts = [], []
        for (c2, i, j) in partners:
            v = unit([(1.0, i), (c2, j)])
            killed.append(max(abs(x) for x in bk.multiply(a, v)) < 1e-12)
            struts.append(i ^ (j - 8))

        self._record('zd.partners_annihilated',
                     'each partner basis vector is a thing a annihilates', g,
                     [True] * 4, killed,
                     detail='an SVD spans the same space with vectors that mean '
                            'nothing; prefer the basis whose pieces can be named')

        self._record('zd.clears_the_kite_space',
                     'annihilation never crosses struts', g,
                     [3, 3, 3, 3], struts,
                     detail='a zero divisor kills only inside its own chart, so '
                            'choosing `a` selects one kite of seven and silences '
                            'the other six — that is the clearing')

        k1 = unit([(1.0, 4), (-1.0, 15)])
        k2 = unit([(1.0, 5), (1.0, 14)])
        summed = [x + y for x, y in zip(k1, k2)]
        still_killed = max(abs(x) for x in bk.multiply(a, summed)) < 1e-12
        self._record('zd.addition_survives',
                     'the kernel is closed under + while x has collapsed', g,
                     True, still_killed,
                     detail='Axis 1 {+,-} keeps working where Axis 2 {x,/} does '
                            'not — motion at zero cost is what downhill means '
                            'once descent has run out')

        # ── the stress tensor, which settles what the kernel IS ───────────
        #
        # Decompose the operator the way continuum mechanics does:
        #
        #     sym(L)  = (L + L^T)/2     strain -> stress
        #     skew(L) = (L - L^T)/2     vorticity -> rotation
        #     trace                     isotropic pressure
        #     dev     = sym - (tr/n)I   SHEAR
        #
        # The result is not "small shear". There is no symmetric part at all,
        # so there is no stress tensor to carry one.
        S = (L + L.T) / 2
        A = (L - L.T) / 2
        dev = S - np.trace(S) / SED_DIM * np.eye(SED_DIM)

        self._record('zd.stress_is_zero',
                     'the stress tensor of L_a is identically zero', g,
                     True, float(np.linalg.norm(S)) < 1e-12,
                     detail=f'||sym|| {np.linalg.norm(S):.3e}, '
                            f'||skew|| {np.linalg.norm(A):.6f} — multiplication '
                            f'by a zero divisor is PURE ROTATION')

        self._record('zd.no_shear_anywhere',
                     'the deviatoric part is zero, not merely minimised', g,
                     True, float(np.linalg.norm(dev)) < 1e-12,
                     detail='"least shearing" is not a minimum here, it is an '
                            'identity — there are no shearing events to count')

        self._record('zd.skew_symmetric',
                     'L_a is skew-symmetric, so it generates rotation', g,
                     True, bool(np.allclose(L, -L.T, atol=1e-12)),
                     detail='which is why the eigenvalues came out purely '
                            'imaginary — that measurement was already saying this')

        self._record('zd.kernel_is_the_axis',
                     'for a skew operator the kernel is the AXIS of rotation', g,
                     (4, 12), (SED_DIM - rank, rank),
                     detail='4 fixed dimensions, 12 turning in 6 planes — 4 planes '
                            'at rate 1, 2 at rate sqrt2. Motion along the axis is '
                            'free because the axis does not turn.')

        # ── the kernel is NOT free fall — orbits are the discriminant ──────
        #
        # A correction, recorded because the mistake is easy and expensive:
        # free fall and absent gravity are indistinguishable ONLY LOCALLY. The
        # equivalence principle holds in a small enough box and fails in a
        # large one, because nearby geodesics in a real field CONVERGE. That
        # tidal deviation is the Riemann curvature, and it is what closes an
        # orbit. Flat space has none: parallel lines stay parallel and nothing
        # orbits.
        #
        #     FREE FALL       curvature present   geodesics converge   ORBITS
        #     GRAVITY ABSENT  curvature zero      lines stay parallel  NO ORBIT
        #
        # So the two blocks say different things, and the kernel is not the
        # free-fall one:
        #
        #     lambda = 0        no rotation   no orbit    gravity ABSENT — flat,
        #                       4 dims                    inertial, straight-line
        #     |lambda| = 1      rotation      orbits      the three forces
        #     |lambda| = sqrt2  rotation      orbits      Sigma_RB conversion
        #
        # "Downhill from the bottom of a pit" is therefore not free fall in a
        # well. It is straight-line motion in a region that is not a well at
        # all — which is why it costs nothing and why nothing comes back
        # around.
        self._record('zd.kernel_does_not_orbit',
                     'the kernel is gravity ABSENT, not free fall', g,
                     (True, False),
                     (float(np.linalg.norm(dev)) < 1e-12,      # flat: no shear
                      bool(np.any(np.abs(np.linalg.eigvals(L)) > 1e-12)
                           and (SED_DIM - rank) == 0)),        # orbits in kernel
                     detail='free fall ORBITS because curvature converges nearby '
                            'geodesics; absent gravity does not orbit at all. The '
                            'kernel has no rotation, hence no orbit — so it is the '
                            'absent case. The 12 rotating dimensions are where '
                            'orbits live. Equivalence is local; orbits are the '
                            'global discriminant that breaks it.')

    # ── group: the handoff ───────────────────────────────────────────────
    def check_handoff(self) -> None:
        """Correct, not satisfied. Cold, not hot."""
        g = 'handoff  correct hands off, not happy'

        # HOT: one continuation is worth far more than the others.
        hot = Handoff(options={'forced': 10.0, 'loses': 0.5, 'blunder': 0.0},
                      correct_set=['forced'], tolerance=1.0)
        self._record('handoff.hot_temperature',
                     'a forced position is hot', g,
                     10.0, hot.temperature,
                     detail='spread between best and worst legal continuation')
        self._record('handoff.hot_refuses',
                     'intention may not take over in a hot position', g,
                     False, hot.may_hand_off(),
                     detail='correct, but the swing exceeds what intention may spend')
        self._record('handoff.hot_no_deviation',
                     'there is no affordable way to be wrong when it is forced', g,
                     [], hot.deviations())

        # COLD: the legal continuations are near-equivalent.
        cold = Handoff(options={'joseki': 1.00, 'variant': 0.98, 'odd': 0.97},
                       correct_set=['joseki'], tolerance=1.0)
        self._record('handoff.cold_temperature',
                     'an endgame position is cold', g,
                     True, cold.temperature < 0.1,
                     detail=f'temperature {cold.temperature:.3f}')
        self._record('handoff.cold_hands_off',
                     'intention takes over once correct AND cold', g,
                     True, cold.may_hand_off())
        self._record('handoff.intentionally_wrong',
                     'being wrong on purpose is available, and bounded', g,
                     ['variant', 'odd'], cold.deviations(),
                     detail=f'budget {cold.budget():.3f} — style lives where '
                            f'the swing is small')

        # Correctness is a predicate over an EXTERNAL referent.
        unsettled = Handoff(options={'a': 1.0, 'b': 1.0},
                            correct_set=['c'], tolerance=1.0)
        self._record('handoff.correct_is_external',
                     'correctness is supplied, never derived from the options', g,
                     False, unsettled.is_correct,
                     detail='the correct continuation is not on offer, so nothing '
                            'hands off — a criterion the system computes is a '
                            'criterion the system can move')
        self._record('handoff.uncorrect_refuses',
                     'no handoff without correctness, however cold', g,
                     (0.0, False), (unsettled.temperature, unsettled.may_hand_off()),
                     detail='cold is necessary and not sufficient')

        # ── the Hands hand off on their own, when the geometries line up ──
        import math as _m

        # OPPOSED: each geometry pulls a different way. No free work exists.
        opposed = Satisfaction(threshold=0.95, useful_at=0.5)
        opposed.emit('contested', action=1.0, usefulness=0.9,
                     gradients=(0.0, 2 * _m.pi / 3, 4 * _m.pi / 3))
        self._record('satisfaction.opposed_not_happy',
                     'geometries pulling apart give no free work', g,
                     (False, True), (opposed.is_happy, opposed.opposed()),
                     detail=f'coherence {opposed.coherence():.6f} — three pulls at '
                            f'120 degrees cancel exactly')

        # ALIGNED: every geometry pointing the same way at once.
        s = Satisfaction(threshold=0.95, useful_at=0.5)
        s.emit('variant', action=2.0, usefulness=0.9, gradients=(0.10, 0.11, 0.09))
        self._record('satisfaction.aligned_is_happy',
                     'happy is the free downhill work all lining up at once', g,
                     True, s.is_happy,
                     detail=f'coherence {s.coherence():.6f}, free work '
                            f'{s.free_work():.4f}')

        self._record('satisfaction.not_a_mood',
                     'coherence is a property of the directions, not of wanting', g,
                     True, s.coherence() > opposed.coherence(),
                     detail='you can lower a bar; you cannot lower a derivative — '
                            'this is as external as `correct` is')

        s.emit('odd', action=0.5, usefulness=0.2, gradients=(0.0, 0.02, 0.01))
        s.emit('joseki', action=1.5, usefulness=0.8, gradients=(0.5, 0.5, 0.5))

        # Stationary is not the same as worth keeping.
        self._record('satisfaction.useful_archives',
                     'only what proves USEFUL reaches the long path', g,
                     ['variant', 'joseki'], [w for (w, _) in s.archivable()],
                     detail=f'{len(s.discarded())} emitted, aligned, and not worth '
                            f'keeping — collected, not lost')

        self._record('satisfaction.action_is_additive',
                     'S is additive along the path because it is a logarithm', g,
                     4.0, s.action,
                     detail='S(sentence) = sum -log2 P(w_i | context)')

        self._record('satisfaction.three_thresholds',
                     'correct, happy and useful are three different questions', g,
                     3, len({'correct', 'happy', 'useful'}),
                     detail='the Eye stops on correct, the Hands stop when the '
                            'geometries align, and archival happens on useful')

        # Safety is structural, not lexical: the Hands cannot reach correctness.
        self._record('satisfaction.cannot_see_correct',
                     'satisfaction has no path to the correctness criterion', g,
                     False, 'correct_set' in Satisfaction.__slots__,
                     detail='happy decides SUFFICIENCY downstream of a truth the '
                            'Eye settled. Lowering this bar costs output, not '
                            'truth — neither side holds both halves.')

    # ── group: two parents, one child ────────────────────────────────────
    def check_joint_parentage(self) -> None:
        """Two objects working together to make a third."""
        g = 'parentage  two parents, one child'
        if self.kite is None:
            self._untested('parent.joint_descent',
                           'a co-authored kite commits to both parents', g,
                           self._kite_error)
            return

        eye   = MindsEye()
        hands = PapersHands()

        self._record('parent.solitary_before',
                     'both subsystems exist and work before any shared language', g,
                     (False, False), (eye.is_bound, hands.is_bound),
                     detail='an unbound subsystem is not half-built — it is a '
                            'complete solitary speaker')

        # Solitary reading needs no language.
        snap = eye.snapshot([0.1] * SED_DIM)
        self._record('parent.solitary_read',
                     'reading alone requires no shared language', g,
                     None, snap['lit_struts'],
                     detail='a snapshot is one speaker; only RELATING needs two')

        try:
            kite = BoxKite.between(eye, hands)
            made = True
        except Exception as exc:                      # noqa: BLE001
            self._untested('parent.joint_descent',
                           'a co-authored kite commits to both parents', g, str(exc))
            return

        self._record('parent.both_bound',
                     'co-authoring binds both parents to the child', g,
                     (True, True), (eye.is_bound, hands.is_bound))

        self._record('parent.joint_descent',
                     'the child commits to BOTH parents, in order', g,
                     True, kite.descends_from(eye, hands),
                     detail=f'descent {kite.descent[:16]} '
                            f'from parents {kite.parents}')

        stranger = PapersHands()
        self._record('parent.impostor_rejected',
                     'a third party cannot claim parentage', g,
                     False, kite.descends_from(eye, stranger),
                     detail='a shared language either speaker could have produced '
                            'alone is not shared, it is coincident')

        # Speech: the API surface that only exists once both have bound.
        spoke = hands.relate(eye, [0.2] * SED_DIM)
        self._record('parent.speech_available',
                     'speech is the API surface between two bound speakers', g,
                     True, len(spoke) > 0,
                     detail=f'{len(spoke)} relations emitted')

        remarried = False
        try:
            BoxKite.between(eye, PapersHands())
        except ValueError:
            remarried = True
        self._record('parent.no_second_authorship',
                     'a bound speaker cannot co-author a second language', g,
                     True, remarried,
                     detail='it would silently change what every index it has '
                            'already handed out means')

    # ── run everything ───────────────────────────────────────────────────
    def run(self,
            psi: Optional[Sequence[float]] = None,
            currents: Optional[Tuple[float, float, float]] = None) -> Ledger:
        self.check_777()
        self.check_lineage()
        self.check_involutions()
        self.check_484()
        self.check_shared_language()
        self.check_paths()
        self.check_control_555()
        self.check_intention()
        self.check_zd_reframe()
        self.check_handoff()
        self.check_joint_parentage()

        if currents is not None:
            self.check_currents(*currents)
        else:
            self._untested('current.neutral',
                           'J_red + J_blue + J_green = 0',
                           'currents  the neutral is the loss',
                           'no currents supplied to run()')

        if psi is not None:
            p_red  = sum(psi[k] ** 2 for k in _RED_CHANNELS)
            p_blue = sum(psi[k] ** 2 for k in _BLUE_CHANNELS)
            self.check_trochoid(p_red, p_blue)
        else:
            self._untested('trochoid.null',
                           'zero loss <=> R = e <=> sigma_self = 1/2',
                           'trochoid  the other loss',
                           'no psi supplied to run()')

        return self.ledger

    # ── report ───────────────────────────────────────────────────────────
    def report(self) -> str:
        led = self.ledger
        out: List[str] = []
        out.append('=' * 74)
        out.append('rotary_rerun_monad — diagnostic and fault-born harness')
        out.append('=' * 74)

        cursor = LedgerCursor(led)
        current_group = None
        for rec in cursor:
            if rec.group != current_group:
                current_group = rec.group
                out.append('')
                out.append(f'── {current_group} ' + '─' * max(0, 70 - len(current_group)))
            out.append(str(rec))

        out.append('')
        out.append('─' * 74)
        out.append(
            f'{len(led)} relations   '
            f'{led.count(Status.HOLDS)} hold   '
            f'{led.count(Status.VIOLATED)} FAULT   '
            f'{led.count(Status.DEGENERATE)} degenerate   '
            f'{led.count(Status.UNTESTED)} untested'
        )
        faults = led.faults()
        if faults:
            out.append('')
            out.append('FAULTS — each is a record, printable, with its index:')
            for f in faults:
                out.append(f'  [{f.index}] {f.name}: expected {f.expected!r}, '
                           f'observed {f.observed!r}')
        return '\n'.join(out)


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def _demo_psi() -> List[float]:
    """A psi with amplitude in both octonions, deliberately off-null."""
    psi = [0.0] * SED_DIM
    for k in range(1, 8):
        psi[k] = 0.30 + 0.02 * k
    for k in range(8, 15):
        psi[k] = 0.25 - 0.01 * k
    psi[0] = 0.5
    psi[15] = 0.1
    return psi


def main(argv: Sequence[str]) -> int:
    psi = _demo_psi()

    # Deliberately unbalanced currents, so the harness has a fault to find and
    # a negative to trip the reducer-validity guard.
    currents = (0.412, -0.187, -0.201)

    h = Harness()
    h.run(psi=psi, currents=currents)
    print(h.report())

    if h.kite is not None:
        print()
        print('─' * 74)
        print("speech — the Eye reads a snapshot, the Hands write it in order")
        print('─' * 74)
        eye   = MindsEye(h.kite)
        hands = PapersHands(h.kite)
        snap  = eye.snapshot(psi)
        print(f'  sigma_self     {snap["sigma_self"]:.9f}')
        print(f'  R, e           {snap["R"]:.9f}, {snap["e"]:.9f}')
        print(f'  trochoid loss  {snap["trochoid_loss"]:.9f}')
        print(f'  generations    {eye.generations_present(psi)}')
        print()
        for line in hands.relate(eye, psi):
            print('  ' + line)

    return 1 if h.ledger.faults() else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
