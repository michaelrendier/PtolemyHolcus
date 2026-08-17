#!/usr/bin/env python3
"""Intention as a garbage collector: reachability is the image, collection is the kernel.

Cody, 2026-08-15: "build me a monad in python. intention...garbage collector
has intention...lets start there..."

WHY A GC IS THE RIGHT PLACE TO START

A garbage collector is the smallest complete system that has an intention. It
does not ask what an object MEANS. It asks one question -- *can I still get
there from a root* -- and everything follows from the answer. That question is
reachability, and reachability is the IMAGE of the reference relation. What is
unreachable is the KERNEL, and collecting it is kernel death.

Measured today, and this module is built on it:

    ker(AB) contains ker(B)     composing only ever ADDS to the kernel

so a run of the collector is a MONOTONE DESCENT. The kernel only grows, the
image only shrinks, and rank + nullity = dim at every step. Past is what can
no longer be reached; future is what still can; now is the split.

INTENTION IS THE ROOT SET. That is the whole design claim. A collector with no
roots collects everything; a collector that roots everything collects nothing.
Intention is neither a goal nor a preference here -- it is the DECLARATION OF
WHAT MUST SURVIVE, and every other decision is derived from it by transitive
closure.

WHAT THIS IS NOT

Not a monad in the Haskell sense -- no unit/bind laws are claimed or checked.
"Monad" here is the engine's own usage (VAPMIP monad.c / monad.py): one
self-contained object holding a field and the operations on it.

Provenance is DESTROYED on collection, deliberately. That is not a defect: a
semantic memory is an episodic one with the source stripped, and stripping is
what makes it reusable. The ear preserves provenance; the Mind's Eye discards
it. This is the Mind's Eye.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

__all__ = ['Cell', 'IntentionMonad', 'Sweep']


@dataclass
class Cell:
    """One addressable object in the field.

    :ivar name: stable identity. NOT a position -- slots are never reused, so
        a name always denotes the same cell (see monad.c vocab_get, which is
        append-only for the same reason).
    :ivar payload: whatever the cell holds. The collector never inspects it.
    :ivar refs: names this cell reaches directly.
    :ivar born: sweep number at which the cell was created.
    """
    name: str
    payload: Any = None
    refs: Set[str] = field(default_factory=set)
    born: int = 0


@dataclass
class Sweep:
    """The record of one collection. RELATIONAL -- it needs a before and after.

    :ivar n: sweep index.
    :ivar roots: the intention in force for this sweep.
    :ivar image: names reachable from the roots (the future).
    :ivar kernel: names collected (the past).
    :ivar rank: len(image).
    :ivar nullity: len(kernel).
    :ivar dim: rank + nullity, the whole field before the sweep.
    :ivar stamp: content hash of the surviving field.
    """
    n: int
    roots: Tuple[str, ...]
    image: Tuple[str, ...]
    kernel: Tuple[str, ...]
    rank: int
    nullity: int
    dim: int
    stamp: str

    def __repr__(self) -> str:
        return (f"<Sweep {self.n} rank={self.rank} nullity={self.nullity} "
                f"dim={self.dim} stamp={self.stamp[:12]}>")


class IntentionMonad:
    """A field of cells whose only intention is a root set.

    Reachability from the roots is the image; everything else is the kernel and
    is collected. Cumulative nullity never decreases -- that is the arrow.

    :param roots: the initial intention. May be empty; then everything falls.
    """

    def __init__(self, roots: Iterable[str] = ()) -> None:
        self._cells: Dict[str, Cell] = {}
        self._roots: Set[str] = set(roots)
        self._sweeps: List[Sweep] = []
        self._cumulative_kernel: Set[str] = set()
        self._n = 0

    # -- field construction ------------------------------------------------

    def hold(self, name: str, payload: Any = None,
             refs: Iterable[str] = ()) -> 'IntentionMonad':
        """Add or replace a cell. Chainable.

        :param name: stable identity for the cell.
        :param payload: contents; never inspected by the collector.
        :param refs: names this cell reaches directly.
        :returns: self, so calls chain.
        :rtype: IntentionMonad
        :raises ValueError: if ``name`` was already collected -- a collected
            name is gone, and reusing it would silently resurrect the past.
        """
        if name in self._cumulative_kernel:
            raise ValueError(
                f"{name!r} was collected in an earlier sweep. Collected names "
                f"are not reusable: the kernel only grows, and reusing a name "
                f"would make a stale reference resolve to a stranger."
            )
        self._cells[name] = Cell(name, payload, set(refs), self._n)
        return self

    def intend(self, *roots: str) -> 'IntentionMonad':
        """Declare what must survive. This is the intention.

        :param roots: names to root. Replaces any previous root set.
        :returns: self.
        :rtype: IntentionMonad
        """
        self._roots = set(roots)
        return self

    def also_intend(self, *roots: str) -> 'IntentionMonad':
        """Widen the intention without discarding it.

        :param roots: names to add to the root set.
        :returns: self.
        :rtype: IntentionMonad
        """
        self._roots |= set(roots)
        return self

    # -- the two faces -----------------------------------------------------

    def reachable(self) -> Set[str]:
        """Compute the image: names reachable from the current roots.

        Transitive closure over ``refs``. Dangling references are ignored --
        a name that was never held cannot be reached.

        :returns: the reachable set.
        :rtype: set[str]
        """
        seen: Set[str] = set()
        stack = [r for r in self._roots if r in self._cells]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(r for r in self._cells[n].refs
                         if r in self._cells and r not in seen)
        return seen

    def sight(self) -> Dict[str, Any]:
        """One guarded read: would a sweep collect anything?

        Cheap -- computes reachability, collects nothing. Use in a loop; call
        :meth:`sweep` only when this reports work to do.

        :returns: keys ``would_collect``, ``rank``, ``nullity``, ``dim``.
        :rtype: dict[str, typing.Any]
        """
        img = self.reachable()
        return {'would_collect': len(self._cells) - len(img),
                'rank': len(img),
                'nullity': len(self._cells) - len(img),
                'dim': len(self._cells)}

    def sweep(self) -> Sweep:
        """Collect everything unreachable. Irreversible.

        The kernel is discarded outright -- payloads, refs and provenance all
        go. Only the fact of collection survives, in the returned Sweep.

        :returns: the record of this sweep.
        :rtype: Sweep
        """
        img = self.reachable()
        ker = set(self._cells) - img
        dim = len(self._cells)
        for n in ker:
            del self._cells[n]
        self._cumulative_kernel |= ker
        h = hashlib.sha256()
        for n in sorted(self._cells):
            h.update(n.encode()); h.update(repr(self._cells[n].payload).encode())
        self._n += 1
        s = Sweep(self._n, tuple(sorted(self._roots)), tuple(sorted(img)),
                  tuple(sorted(ker)), len(img), len(ker), dim, h.hexdigest())
        self._sweeps.append(s)
        return s

    # -- the arrow ---------------------------------------------------------

    def bearing(self) -> Dict[str, Any]:
        """Relate the sweeps to each other. Needs at least two.

        :returns: keys ``sweeps``, ``cumulative_nullity``, ``monotone``,
            ``rank_trace``, ``nullity_trace``.
        :rtype: dict[str, typing.Any]
        :raises ValueError: if fewer than two sweeps have run -- a single
            sweep is definitional and cannot show movement.
        """
        if len(self._sweeps) < 2:
            raise ValueError(
                "bearing() needs two sweeps. One sweep is a datum: it says "
                "what is, not what moved."
            )
        cum, run = [], 0
        for s in self._sweeps:
            run += s.nullity
            cum.append(run)
        return {'sweeps': len(self._sweeps),
                'cumulative_nullity': cum,
                'monotone': all(cum[i] <= cum[i + 1] for i in range(len(cum) - 1)),
                'rank_trace': [s.rank for s in self._sweeps],
                'nullity_trace': [s.nullity for s in self._sweeps]}

    def __repr__(self) -> str:
        return (f"<IntentionMonad cells={len(self._cells)} "
                f"roots={len(self._roots)} sweeps={self._n} "
                f"collected={len(self._cumulative_kernel)}>")
