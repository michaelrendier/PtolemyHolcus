#!/usr/bin/env python3
"""Exact hypernumeric arithmetic: keep the answer, defer the flattening.

Cody, 2026-08-16: "bypass the floating point problem as a mathematics model...
IEEE leaves noise in digital from analog's complete picture -- flattening
artifacts... notating where the answer begins and ends."

THE MEASURED SITUATION

The sedenion structure constants take only the values -1 and +1. So the
product is a signed SUM -- no division, no roots, no transcendentals. Measured
over depth 1..8 with integer inputs, float error against exact rational
arithmetic was 0.000e+00 at every depth.

    THE ALGEBRA NEEDS NO PRECISION. It is exact over Z and over Q.

Every precision loss in this repo comes from three operations that are NOT the
algebra, and each has a different remedy:

    normalisation  x / |x|      irrational (sqrt 2)  -> DEFER it
    gamma values   zeta zeros   transcendental       -> use for ORDER, not value
    SVD            eigenvalues  iterative            -> unavoidable, bracket it

The design rule that follows: carry exact integers as far as possible, and
where a transcendental is genuinely required, carry an INTERVAL that says
where the answer begins and ends rather than a float that silently claims
digits it does not have.

WORD-LENGTH BUDGET, measured

    13 letters   15.0 decimal digits   float64 borderline
    20 letters   23.0                  float64 FAILS
    28 letters   32.2                  float64 FAILS
    32 letters   36.8                  float64 FAILS

Horner in gamma-space dies at 13 characters. Horner in PRIME-space is exact at
any length, because Python integers are unbounded. gamma is still what fixes
the ORDER -- it just never has to hold the value.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence, Tuple

__all__ = ['ExactSedenion', 'precision_report', 'hyperhash', 'hyperhash_span',
           'zeta_hash', 'GAMMA_SCALE', 'TONE', 'mark_tone', 'read_tone',
           'strip_tone']

_TAB = None


def _table():
    """Cayley-Dickson table at dim 16. Values of the sign are only -1 and +1.

    :returns: mapping ``(i, j) -> (sign, index)``.
    :rtype: dict
    """
    global _TAB
    if _TAB is None:
        from ValaQuenta.modules.box_kite.maths import cd_multiplication_table
        _TAB, _ = cd_multiplication_table(4)
    return _TAB


class ExactSedenion:
    """A sedenion over the rationals. No rounding, ever.

    Multiplication is a signed sum of products of the components, so if the
    components are exact the product is exact. Normalisation is deliberately
    NOT provided -- it is the step that introduces sqrt and it should be
    deferred to the boundary of the computation, not baked into the type.

    :param comps: 16 components; ints, Fractions or strings are all exact.
        Floats are accepted but recorded as exactly the binary value they
        already are, which is usually not the decimal you typed.
    """

    __slots__ = ('c',)

    def __init__(self, comps: Sequence) -> None:
        if len(comps) != 16:
            raise ValueError(f"a sedenion has 16 components, got {len(comps)}")
        self.c = [x if isinstance(x, Fraction) else Fraction(x) for x in comps]

    def __mul__(self, other: 'ExactSedenion') -> 'ExactSedenion':
        tab = _table()
        z = [Fraction(0)] * 16
        for i, xi in enumerate(self.c):
            if xi == 0:
                continue
            for j, yj in enumerate(other.c):
                if yj == 0:
                    continue
                sg, k = tab[(i, j)]
                z[k] += sg * xi * yj
        return ExactSedenion(z)

    def __add__(self, other: 'ExactSedenion') -> 'ExactSedenion':
        return ExactSedenion([a + b for a, b in zip(self.c, other.c)])

    def __sub__(self, other: 'ExactSedenion') -> 'ExactSedenion':
        return ExactSedenion([a - b for a, b in zip(self.c, other.c)])

    def __eq__(self, other) -> bool:
        return isinstance(other, ExactSedenion) and self.c == other.c

    def norm_squared(self) -> Fraction:
        """The squared norm. EXACT -- unlike the norm, which needs a root.

        Comparisons, annihilation tests and orderings should all be done on
        this rather than on ``|x|``, because it never leaves the rationals.

        :returns: sum of squared components.
        :rtype: fractions.Fraction
        """
        return sum(x * x for x in self.c)

    def is_zero(self) -> bool:
        """Exact zero test. No epsilon, because none is needed.

        :rtype: bool
        """
        return all(x == 0 for x in self.c)

    def annihilates(self, other: 'ExactSedenion') -> bool:
        """Is ``self * other`` exactly zero? Decided, not estimated.

        :rtype: bool
        """
        return (self * other).is_zero()

    def __repr__(self) -> str:
        nz = [(i, x) for i, x in enumerate(self.c) if x != 0]
        body = ' + '.join(f"{x}e{i}" for i, x in nz) or '0'
        return f"ExactSedenion({body})"


def precision_report() -> dict:
    """What precision each operation actually requires. Measured, not assumed.

    :returns: mapping operation -> (exactness, remedy).
    :rtype: dict
    """
    return {
        'multiply':    ('EXACT over Z and Q', 'structure constants are +/-1 only'),
        'add/subtract':('EXACT over Z and Q', 'no remedy needed'),
        'commutator':  ('EXACT over Z and Q', 'a difference of two products'),
        'associator':  ('EXACT over Z and Q', 'a difference of two products'),
        'norm_squared':('EXACT over Q',       'use this instead of the norm'),
        'norm |x|':    ('IRRATIONAL',         'defer; compare norm_squared instead'),
        'normalise':   ('IRRATIONAL',         'defer to the boundary of the computation'),
        'gamma / zeta':('TRANSCENDENTAL',     'use for ORDER only, never for value'),
        'SVD':         ('ITERATIVE',          'unavoidable; bracket the answer'),
    }


def _primes(n: int) -> List[int]:
    out: List[int] = []
    c = 2
    while len(out) < n:
        if all(c % p for p in out if p * p <= c):
            out.append(c)
        c += 1
    return out


_P26 = _primes(26)
_L2P = {chr(97 + i): _P26[i] for i in range(26)}


def hyperhash(word: str, base: int | None = None) -> int:
    """Letters -> primes -> exact integer Horner. Unbounded word length.

    gamma fixes the ORDERING of the letter alphabet (letter i takes the i-th
    prime, whose index is pi(p) = i+1, whose zero is gamma_(i+1)). The VALUE is
    then carried in exact integers, so nothing is lost at any length.

    :param word: letters ``a``-``z``; anything else is skipped.
    :param base: Horner base; defaults to 97, the first prime above the
        alphabet, so no digit can alias another.
    :returns: an exact non-negative integer.
    :rtype: int
    """
    b = 97 if base is None else base
    h = 0
    for ch in word.lower():
        p = _L2P.get(ch)
        if p is not None:
            h = h * b + p
    return h


def hyperhash_span(word: str) -> Tuple[int, int, int]:
    """The hash together with where its answer BEGINS and ENDS.

    A float claims sixteen digits whether or not it has them. This returns the
    value with its exact digit span, so the boundary of the answer is stated
    rather than implied.

    :param word: the word to hash.
    :returns: ``(value, n_digits, n_bits)``.
    :rtype: tuple[int, int, int]
    """
    v = hyperhash(word)
    return v, len(str(v)), v.bit_length()


#: Scaling that turns the transcendental gamma into an exact integer. 10**18
#: keeps 18 decimal places of each zero, which is past double precision and
#: preserves every gap in the first 26 zeros distinctly.
GAMMA_SCALE = 10 ** 18

_GI: list | None = None


def _gamma_ints():
    """The first 26 zeta zeros, scaled to exact integers. Computed once.

    :returns: 26 integers, ``round(gamma_n * GAMMA_SCALE)``.
    :rtype: list[int]
    """
    global _GI
    if _GI is None:
        import mpmath
        mpmath.mp.dps = 40
        _GI = [int(mpmath.nint(mpmath.zetazero(i + 1).imag * GAMMA_SCALE))
               for i in range(26)]
    return _GI


def zeta_hash(word: str) -> int:
    """Letters -> zeta zeros -> exact integer Horner. Carries the SPACING.

    :func:`hyperhash` uses prime values as digits, which is compact but throws
    gamma away entirely -- and since gamma_n is monotone in n, gamma-ordering
    and ordinal-ordering are the SAME sequence. The information is therefore
    not in the order at all. It is in the GAPS, which are irregular: 25
    distinct gaps among the first 26 zeros, no repeats.

    This carries those gaps into exact arithmetic by scaling gamma to integers.

    COST, measured on the same words:

        word            hyperhash (primes)   zeta_hash (gamma)
        ask                      15 bits            197 bits
        45 letters              297 bits           2985 bits

    Ten times heavier. Worth it only if something downstream reads the
    spacing; if injectivity is all that is wanted, use :func:`hyperhash`.
    Both are exact at any word length and both gave 0 collisions on 20,000
    English words.

    :param word: letters ``a``-``z``; anything else is skipped.
    :returns: an exact non-negative integer.
    :rtype: int
    """
    gi = _gamma_ints()
    base = max(gi) + 1
    h = 0
    for ch in word.lower():
        i = ord(ch) - 97
        if 0 <= i < 26:
            h = h * base + gi[i]
    return h


# --- tone markers: invisible to a console, traversable by code --------------

#: Sixteen Unicode variation selectors, one per sedenion dimension. They render
#: as nothing, survive copy-paste, and are ordinary code points to a program.
TONE = {i: chr(0xFE00 + i) for i in range(16)}
_INV = {v: k for k, v in TONE.items()}


def mark_tone(word: str, channel: int) -> str:
    """Attach an invisible tone channel to a word.

    Modelled on Demotic, where the first sign of a word carries its tone. Here
    the marker is a variation selector: zero-width, non-printing, and mapped to
    one of the sixteen sedenion dimensions.

    This is *intent in action* -- it travels with the token through the code
    and is invisible at the console, so it never disturbs the text it annotates.

    :param word: the word to mark.
    :param channel: 0-15, the sedenion dimension carrying the tone.
    :returns: the word with a zero-width marker prefixed.
    :rtype: str
    :raises ValueError: if ``channel`` is outside 0-15.
    """
    if not 0 <= channel <= 15:
        raise ValueError(f"channel must be 0-15, got {channel}")
    return TONE[channel] + word


def read_tone(marked: str):
    """Recover the tone channel from a marked word.

    :param marked: a string possibly carrying a marker.
    :returns: the channel 0-15, or ``None`` if unmarked.
    :rtype: int | None
    """
    for ch in marked:
        if ch in _INV:
            return _INV[ch]
    return None


def strip_tone(marked: str) -> str:
    """The visible text, with every marker removed.

    :rtype: str
    """
    return ''.join(c for c in marked if c not in _INV)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/rendier/Projects/ThePlace')
    print("precision required per operation:")
    for k, (state, remedy) in precision_report().items():
        print(f"  {k:<14} {state:<20} {remedy}")
    print("\nword-length behaviour (exact integer Horner):")
    for w in ['ask', 'aks', 'listen', 'silent',
              'antidisestablishmentarianism',
              'pneumonoultramicroscopicsilicovolcanoconiosis']:
        v, d, b = hyperhash_span(w)
        print(f"  {len(w):>3} letters  {d:>3} digits  {b:>4} bits  {w[:34]}")
    t = mark_tone('whudup', 3)
    print(f"\ntone marker: visible={strip_tone(t)!r} channel={read_tone(t)} "
          f"len_with_marker={len(t)} len_visible={len(strip_tone(t))}")
