#!/usr/bin/env python3
"""sieve_clock.py — a clock for the standard life of a factor.

THE QUESTION

When are all residual factors gone? When is the sieve finished?

The textbook answer is "stop at sqrt(N)" and it is stated as a rule. It is not
a rule. It is a MEASUREMENT, and this instrument takes it: the sieve stops when
striking stops doing anything, and sqrt(N) is where that happens rather than
where someone decided it should.

THE LIFE OF A FACTOR — three regimes, and every prime lives in exactly one

Sieving to N, a prime p can be in one of three conditions, and which one is
decided entirely by its size:

    PRODUCTIVE   p <= sqrt(N)      p*p <= N, so p strikes at least one number
                                   nothing has struck before. This is the only
                                   regime doing new work.

    REDUNDANT    sqrt(N) < p <= N/2  p still has multiples in range and still
                                   strikes them — but every one of them was
                                   already struck by a smaller prime. Real
                                   work, zero information.

    ORPHAN       p > N/2           2p > N, so p has no multiple in range at
                                   all. It never claims anything. Not prime-
                                   as-in-special: prime and simply UNUSED,
                                   this time around.

An orphan is not a defect and not a gap. It is a factor whose turn has not
come because the universe it was asked about was too small. Extend N and it is
adopted — every orphan at N is productive or redundant at 2N.

TERMINATION IS OBSERVED, NOT IMPOSED

The instrument never assumes sqrt(N). It watches the strikes and reports the
last prime that struck something NEW. That number is then compared against
sqrt(N) afterwards, as a check on the measurement rather than as its
definition.

python3 first. Port to PtolC/ only once a result is significant.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = ['FactorLife', 'SieveClock', 'Regime']


class Regime:
    PRODUCTIVE = 'productive'
    REDUNDANT  = 'redundant'
    ORPHAN     = 'orphan'


@dataclass
class FactorLife:
    """One prime's whole working life, recorded rather than tallied."""
    p:            int
    born:         int = -1     # tick of its first strike ever
    died:         int = -1     # tick of its last strike ever
    strikes:      int = 0      # every strike it made
    first_claims: int = 0      # strikes that marked a number for the FIRST time
    smallest_new: int = -1     # the first number it alone was responsible for
    largest_new:  int = -1     # the LAST number it was ever first to claim
    left_at:      int = -1     # tick of its final first-claim — when it LEFT

    @property
    def regime(self) -> str:
        if self.strikes == 0:
            return Regime.ORPHAN
        return Regime.PRODUCTIVE if self.first_claims > 0 else Regime.REDUNDANT

    @property
    def lifespan(self) -> int:
        """Ticks between first and last strike. Zero for an orphan."""
        return 0 if self.born < 0 else self.died - self.born

    def __str__(self) -> str:
        return (f'p={self.p:<8} {self.regime:<11} strikes={self.strikes:<8} '
                f'new={self.first_claims:<8} lifespan={self.lifespan}')


class SieveClock:
    """Sieve of Eratosthenes with a clock on every strike.

    The clock ticks once per strike — not per prime and not per number — so
    the unit of time is the unit of work.
    """

    def __init__(self, n: int) -> None:
        if n < 4:
            raise ValueError('n must be at least 4')
        self.n = n
        self.tick = 0
        self.lives: Dict[int, FactorLife] = {}
        self.primes: List[int] = []
        self.last_new_claim_tick = 0
        self.last_new_claim_prime = 0

        self._run()

    def _run(self) -> None:
        n = self.n
        composite = bytearray(n + 1)          # 0 = unmarked
        struck_by = [0] * (n + 1)             # how many primes have struck it

        for p in range(2, n + 1):
            if composite[p]:
                continue
            self.primes.append(p)
            life = FactorLife(p=p)
            self.lives[p] = life

            m = p * p if p * p <= n else 2 * p
            # start at p*p for the productive range, else the first multiple
            # in range; either way we are asking what this prime CLAIMS.
            while m <= n:
                self.tick += 1
                if life.born < 0:
                    life.born = self.tick
                life.died = self.tick
                life.strikes += 1

                if not composite[m]:
                    composite[m] = 1
                    life.first_claims += 1
                    if life.smallest_new < 0:
                        life.smallest_new = m
                    life.largest_new = m
                    life.left_at = self.tick        # keeps moving until it stops
                    self.last_new_claim_tick = self.tick
                    self.last_new_claim_prime = p

                struck_by[m] += 1
                m += p

        self._composite = composite
        self._struck_by = struck_by

    # ── census ───────────────────────────────────────────────────────────
    def by_regime(self) -> Dict[str, List[int]]:
        out: Dict[str, List[int]] = {Regime.PRODUCTIVE: [],
                                     Regime.REDUNDANT: [],
                                     Regime.ORPHAN: []}
        for p, life in self.lives.items():
            out[life.regime].append(p)
        return out

    def boundaries(self) -> Dict[str, float]:
        """Where the regimes actually change, measured."""
        reg = self.by_regime()
        return {
            'last_productive': max(reg[Regime.PRODUCTIVE]) if reg[Regime.PRODUCTIVE] else 0,
            'first_redundant': min(reg[Regime.REDUNDANT]) if reg[Regime.REDUNDANT] else 0,
            'last_redundant':  max(reg[Regime.REDUNDANT]) if reg[Regime.REDUNDANT] else 0,
            'first_orphan':    min(reg[Regime.ORPHAN]) if reg[Regime.ORPHAN] else 0,
            'sqrt_n':          math.sqrt(self.n),
            'n_over_2':        self.n / 2.0,
        }

    def wasted_strikes(self) -> Tuple[int, int]:
        """(strikes that claimed nothing new, total strikes)."""
        new = sum(l.first_claims for l in self.lives.values())
        return self.tick - new, self.tick

    def multiplicity(self) -> Dict[int, int]:
        """How many distinct primes struck each composite — omega(n)."""
        hist: Dict[int, int] = {}
        for k in range(4, self.n + 1):
            c = self._struck_by[k]
            if c:
                hist[c] = hist.get(c, 0) + 1
        return hist

    def departure_order(self) -> List[FactorLife]:
        """The order the factors LEAVE — by final first-claim, not final strike.

        A factor leaves when it stops claiming anything new. It usually keeps
        striking long after that, which is why departure is measured on
        first-claims: work continuing is not the same as work mattering.
        """
        alive = [l for l in self.lives.values() if l.left_at > 0]
        return sorted(alive, key=lambda l: l.left_at)

    def departure_is_entry_order(self) -> bool:
        """Do they leave in the order they arrived?"""
        dep = [l.p for l in self.departure_order()]
        return dep == sorted(dep)

    def report(self) -> str:
        reg = self.by_regime()
        b = self.boundaries()
        wasted, total = self.wasted_strikes()
        out: List[str] = []

        out.append('=' * 68)
        out.append(f'sieve_clock  N = {self.n:,}   primes = {len(self.primes):,}'
                   f'   ticks = {self.tick:,}')
        out.append('=' * 68)
        out.append('')
        out.append('THE LIFE OF A FACTOR')
        for r in (Regime.PRODUCTIVE, Regime.REDUNDANT, Regime.ORPHAN):
            ps = reg[r]
            frac = 100.0 * len(ps) / len(self.primes)
            rng = f'{min(ps):,}..{max(ps):,}' if ps else '-'
            out.append(f'  {r:<11} {len(ps):>8,} primes  {frac:>5.1f}%   {rng}')
        out.append('')
        out.append('WHEN DOES THE SIEVE STOP — measured, not assumed')
        out.append(f'  last prime to claim anything NEW : {self.last_new_claim_prime:,}')
        out.append(f'  sqrt(N)                          : {b["sqrt_n"]:,.2f}')
        out.append(f'  agreement                        : '
                   f'{self.last_new_claim_prime <= b["sqrt_n"] < b["first_redundant"]}')
        out.append(f'  last tick that mattered          : {self.last_new_claim_tick:,}'
                   f' of {self.tick:,}'
                   f'  ({100.0*self.last_new_claim_tick/self.tick:.1f}%)')
        out.append('')
        out.append('RESIDUAL WORK — strikes that changed nothing')
        out.append(f'  wasted {wasted:,} of {total:,} strikes '
                   f'({100.0*wasted/total:.1f}%)')
        out.append('')
        out.append('ORPHANS — primes that claimed nothing this time around')
        orph = reg[Regime.ORPHAN]
        if orph:
            out.append(f'  {len(orph):,} orphans, all in ({self.n//2:,}, {self.n:,}]')
            out.append(f'  every one is adopted by N = {2*self.n:,}')
        else:
            out.append('  none')
        return '\n'.join(out)


def growth_table(bounds: List[int]) -> str:
    """Does the orphan fraction settle as the universe gets bigger?"""
    rows = ['', 'ORPHAN FRACTION AS N GROWS',
            f'  {"N":>12}  {"primes":>10}  {"orphans":>9}  {"orphan %":>9}  '
            f'{"wasted %":>9}']
    for n in bounds:
        sc = SieveClock(n)
        reg = sc.by_regime()
        orph = len(reg[Regime.ORPHAN])
        wasted, total = sc.wasted_strikes()
        rows.append(f'  {n:>12,}  {len(sc.primes):>10,}  {orph:>9,}  '
                    f'{100.0*orph/len(sc.primes):>8.1f}%  '
                    f'{100.0*wasted/total:>8.1f}%')
    return '\n'.join(rows)


def main(argv: List[str]) -> int:
    n = int(argv[0]) if argv else 1_000_000
    sc = SieveClock(n)
    print(sc.report())
    print(growth_table([10_000, 100_000, 1_000_000]))

    print()
    print('MULTIPLICITY — how many distinct primes claim each composite')
    mult = sc.multiplicity()
    for k in sorted(mult):
        print(f'  omega={k:<3} {mult[k]:>10,}')

    print()
    print('=' * 68)
    print('THE ORDER THE FACTORS LEAVE')
    print('=' * 68)
    dep = sc.departure_order()
    print(f'  departure order == entry order?  {sc.departure_is_entry_order()}')
    print()
    print(f'  {"p":>8}  {"new claims":>11}  {"first new":>12}  {"last new":>12}'
          f'  {"left at tick":>13}')
    for l in dep[:14]:
        print(f'  {l.p:>8,}  {l.first_claims:>11,}  {l.smallest_new:>12,}'
              f'  {l.largest_new:>12,}  {l.left_at:>13,}')
    if len(dep) > 20:
        print(f'  {"...":>8}')
        for l in dep[-6:]:
            print(f'  {l.p:>8,}  {l.first_claims:>11,}  {l.smallest_new:>12,}'
                  f'  {l.largest_new:>12,}  {l.left_at:>13,}')

    print()
    print('  the first new claim is always p*p — check:',
          all(l.smallest_new == l.p * l.p for l in dep))
    print(f'  the last factor to leave: p = {dep[-1].p:,}'
          f'   with {dep[-1].first_claims:,} claim(s), on {dep[-1].largest_new:,}')
    print(f'  sqrt(N) = {math.sqrt(sc.n):,.2f}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
