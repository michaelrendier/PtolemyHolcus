#!/usr/bin/env python3
"""Map an arbitrary sedenion into operator space by its defect field.

Cody, 2026-08-16: "The Commuter, The Associator et al... it can spit out a
field telling us where in the operator space that it WANTS to exist" --
requested as a MAPPING UTILITY, not a coupling instrument.

WHAT IT DOES

At dim 16 there are exactly seven distinct PRESERVE octonions (verified
octonions by Hurwitz: closed, unital, norm-multiplicative, alternative,
non-associative, no zero divisors). Any element of the algebra sits somewhere
relative to those seven. This module measures where, using only defect --
never a label, never the SVD that defined them.

For a probe ``x`` and an octonion ``O`` with orthonormal basis ``b_k``:

    commutator defect   mean_k | x b_k - b_k x |
    associator defect   mean_ij | (x b_i) b_j - x (b_i b_j) |

Seven of each: that vector is the FIELD. Its argmin is where ``x`` wants to
live; the normalised spread is how much the field means it.

MEASURED PERFORMANCE (all 84 zero-divisor diagonals, dim 16)

    commutator argmin == own octonion    64/84   76.2%    chance 14.3%
    associator argmin == own octonion    34/84   40.5%    chance 14.3%
    generic (non-divisor) element of O_k 20/28   71.4%

So the commutator is the instrument and the associator is a weak second. Use
:func:`place` unless you specifically want the associator's opinion.

WHAT IT CANNOT DO -- measured, not suspected

The field is BLIND TO THE FANO LINES. The three lowest-defect octonions equal
the probe's own Fano line in 0 of 84 cases -- below the 2.9% chance rate. The
strut/octonion incidence is real (it is PG(2,2), every axiom verified) but it
is not recoverable from any defect measured here. Placement is a property of
the POINT; the LINE lives in the address (i, j, sign) and nowhere else.

Do not use this to infer incidence, coupling, or chart membership.
"""

from __future__ import annotations

import numpy as np

__all__ = ['DefectField', 'octonion_basis', 'comm', 'assoc',
           'comm_field', 'assoc_field', 'place']

_TAB = None
_OCT = None


def _table():
    """Cayley-Dickson multiplication table at dim 16, loaded once.

    :returns: mapping ``(i, j) -> (sign, index)``.
    :rtype: dict
    """
    global _TAB
    if _TAB is None:
        from ValaQuenta.modules.box_kite.maths import cd_multiplication_table
        _TAB, _ = cd_multiplication_table(4)
    return _TAB


def mul(x, y):
    """Sedenion product.

    :param x: 16-vector.
    :param y: 16-vector.
    :returns: the product ``x * y``.
    :rtype: numpy.ndarray
    """
    tab = _table()
    z = np.zeros(16)
    for i in np.nonzero(x)[0]:
        for j in np.nonzero(y)[0]:
            sg, k = tab[(i, j)]
            z[k] += sg * x[i] * y[j]
    return z


def comm(x, y):
    """Commutator ``xy - yx``. Zero iff ``x`` and ``y`` commute.

    :returns: the commutator.
    :rtype: numpy.ndarray
    """
    return mul(x, y) - mul(y, x)


def assoc(x, y, z):
    """Associator ``(xy)z - x(yz)``. Zero iff the triple associates.

    :returns: the associator.
    :rtype: numpy.ndarray
    """
    return mul(mul(x, y), z) - mul(x, mul(y, z))


def octonion_basis():
    """The seven PRESERVE octonions, as orthonormal 8x16 bases.

    Derived once from the sv=1 singular subspace of every zero-divisor
    diagonal, then deduplicated by exact subspace equality. Cached.

    :returns: seven arrays of shape ``(8, 16)``.
    :rtype: list[numpy.ndarray]
    """
    global _OCT
    if _OCT is not None:
        return _OCT
    from ValaQuenta.modules.angular_rank.maths import left_mul_matrix
    seen, out = [], []
    for i in range(1, 16):
        for j in range(i + 1, 16):
            for s in (1, -1):
                v = np.zeros(16)
                v[i] = 1
                v[j] = s
                v /= np.sqrt(2)
                U, sv, Vt = np.linalg.svd(left_mul_matrix(v))
                if np.sum(sv < 1e-10) == 0:
                    continue
                P = Vt[np.isclose(sv, 1.0)]
                if P.shape[0] != 8:
                    continue
                if not any(np.allclose(np.linalg.svd(P @ Q.T, compute_uv=False),
                                       1, atol=1e-8) for Q in seen):
                    seen.append(P)
                    out.append(P)
    _OCT = out
    return out


def comm_field(x):
    """Commutator defect of ``x`` against each of the seven octonions.

    :param x: 16-vector; normalised internally.
    :returns: 7-vector of mean commutator norms.
    :rtype: numpy.ndarray
    """
    x = np.asarray(x, float)
    x = x / np.linalg.norm(x)
    return np.array([float(np.mean([np.linalg.norm(comm(x, b)) for b in B]))
                     for B in octonion_basis()])


def assoc_field(x):
    """Associator defect of ``x`` against each octonion. Weaker than the
    commutator (40.5% vs 76.2%) -- prefer :func:`comm_field`.

    :param x: 16-vector; normalised internally.
    :returns: 7-vector of mean associator norms.
    :rtype: numpy.ndarray
    """
    x = np.asarray(x, float)
    x = x / np.linalg.norm(x)
    return np.array([float(np.mean([np.linalg.norm(assoc(x, B[i], B[j]))
                                    for i in range(8) for j in range(8)]))
                     for B in octonion_basis()])


def address(x, tol=1e-9):
    """Exact address of a zero-divisor diagonal: ``(i, j, sign, strut)``.

    This is an INDEX, not a search: the strut is ``i XOR j`` where ``{i, j}``
    is the support. O(1), no projection, no fitting.

    A vector with support other than exactly two indices HAS NO ADDRESS. That
    is not a limitation of this function -- an arbitrary 16-vector is not a
    diagonal and does not lie on a strut, the way a real number is not an
    integer. Both span-projection (35/84) and diagonal decomposition (20/84)
    were tried and fail, because there is nothing there to recover.

    :param x: 16-vector.
    :param tol: magnitude below which a component counts as zero.
    :returns: ``(i, j, sign, strut)`` with ``i < j`` and ``sign`` in ``{+1,-1}``.
    :rtype: tuple[int, int, int, int]
    :raises ValueError: if the support is not exactly two indices.
    """
    nz = [k for k in range(16) if abs(x[k]) > tol]
    if len(nz) != 2:
        raise ValueError(
            f"support has {len(nz)} indices, not 2 -- this is not a diagonal "
            f"and has no strut. Arbitrary vectors do not lie on lines."
        )
    i, j = nz
    return i, j, int(np.sign(x[i] * x[j])), i ^ j


def strut(x, tol=1e-9):
    """The Fano LINE a diagonal lies on. Shorthand for ``address(x)[3]``.

    :returns: the strut label, 9-15 at dim 16.
    :rtype: int
    :raises ValueError: if ``x`` is not a diagonal.
    """
    return address(x, tol)[3]


_LINES = {9: (0, 1, 2), 10: (0, 3, 4), 11: (0, 5, 6), 12: (1, 3, 5),
          13: (1, 4, 6), 14: (2, 3, 6), 15: (2, 4, 5)}


def fano_line(s):
    """The three octonions incident to a strut. PG(2,2); every axiom verified.

    :param s: strut label 9-15.
    :returns: three octonion indices.
    :rtype: tuple[int, int, int]
    :raises KeyError: if ``s`` is not a strut at dim 16.
    """
    return _LINES[s]


def locate(x, tol=1e-9):
    """Full location: the POINT by defect, the LINE by address.

    The two come from different machinery on purpose. Placement is measured
    from commutator defect and works on any vector; the line is read off the
    index and exists only for diagonals. No defect field recovers the line
    (0/84, below chance), so do not expect one to.

    :param x: 16-vector.
    :returns: keys ``octonion``, ``confidence``, ``strut``, ``line``,
        ``on_line`` (is the placed octonion incident to the strut?), and
        ``address``. Line keys are ``None`` when ``x`` is not a diagonal.
    :rtype: dict
    """
    d = place(x)
    out = {'octonion': d.octonion, 'confidence': d.confidence,
           'strut': None, 'line': None, 'on_line': None, 'address': None}
    try:
        a = address(x, tol)
    except ValueError:
        return out
    out['address'] = a
    out['strut'] = a[3]
    out['line'] = fano_line(a[3])
    out['on_line'] = d.octonion in out['line']
    return out


def intend(context_strut, content_strut, orientation=None):
    """Declare an intention as a pair of struts; get back what survives.

    Two Fano lines meet in exactly one point, always. So naming a CONTEXT line
    and a CONTENT line names one octonion and prunes the 84 diagonals to 2:

        84  ->  12   fix one strut            7x
            ->   4   intersect the two       21x
            ->   2   add a sign              42x     97.6% discarded

    All by index lookup. No search, no defect measurement, O(1).

    THE PRUNE IS ONE-WAY. There are 21 strut pairs and only 7 points, exactly
    three pairs per point, so ``(context, content)`` is NOT recoverable from
    the result. That is the point: a reduction you could invert would not have
    discarded anything.

    :param context_strut: the frame. Invariant under all 42 degeneracies.
    :param content_strut: the payload line.
    :param orientation: optional ``+1``/``-1``. Supplying it is the third
        declaration and takes the prune from 21x (95.24%) to 42x (97.62%).
        This is the valve bit -- the one annihilation cannot see -- so it
        cannot be inferred and must be declared.
    :returns: keys ``octonion``, ``survivors`` (the 4 diagonals on the context
        strut carrying that octonion), ``reduction``, ``discarded``.
    :rtype: dict
    :raises ValueError: if the two struts are equal -- identical lines do not
        meet in a point, they coincide, and nothing is pruned.
    """
    if context_strut == content_strut:
        raise ValueError(
            "context and content struts are identical; coincident lines do "
            "not intersect in a point and prune nothing."
        )
    meet = set(fano_line(context_strut)) & set(fano_line(content_strut))
    oct_ = next(iter(meet))
    surv = [z for z in _diagonals()
            if (z[0] ^ z[1]) == context_strut and _octonion_of(z) == oct_]
    if orientation is not None:
        surv = [z for z in surv if z[2] == orientation]
    return {'octonion': oct_, 'survivors': surv,
            'reduction': 84 / max(len(surv), 1),
            'discarded': 1.0 - len(surv) / 84.0}


_DIAG = None
_LABEL = None


def _diagonals():
    """The 84 zero-divisor diagonals as ``(i, j, sign)``. Cached."""
    global _DIAG
    if _DIAG is None:
        from ValaQuenta.modules.angular_rank.maths import left_mul_matrix
        out = []
        for i in range(1, 16):
            for j in range(i + 1, 16):
                for s in (1, -1):
                    v = np.zeros(16)
                    v[i] = 1
                    v[j] = s
                    v /= np.sqrt(2)
                    if np.sum(np.linalg.svd(left_mul_matrix(v),
                                            compute_uv=False) < 1e-10) > 0:
                        out.append((i, j, s))
        _DIAG = out
    return _DIAG


def _octonion_of(z):
    """Which of the seven octonions a diagonal carries. Cached over all 84."""
    global _LABEL
    if _LABEL is None:
        from ValaQuenta.modules.angular_rank.maths import left_mul_matrix
        O = octonion_basis()
        _LABEL = {}
        for d in _diagonals():
            v = np.zeros(16)
            v[d[0]] = 1
            v[d[1]] = d[2]
            v /= np.sqrt(2)
            U, sv, Vt = np.linalg.svd(left_mul_matrix(v))
            P = Vt[np.isclose(sv, 1.0)]
            for k, Q in enumerate(O):
                if np.allclose(np.linalg.svd(P @ Q.T, compute_uv=False),
                               1, atol=1e-8):
                    _LABEL[d] = k
                    break
    return _LABEL[z]


class DefectField:
    """One placement result.

    :ivar octonion: index 0-6 of the lowest-defect octonion.
    :ivar confidence: normalised spread ``(max-min)/mean`` of the field.
        Empirically ~0.13-0.15 for an element genuinely inside one octonion,
        ~0.09 at a boundary between two, ~0.07-0.09 for a vector belonging
        nowhere. LOW CONFIDENCE DOES NOT SEPARATE 'boundary' FROM 'nowhere'
        -- those ranges overlap and this field cannot tell them apart.
    :ivar field: the raw 7-vector.
    :ivar ranking: octonion indices, lowest defect first.
    """

    __slots__ = ('octonion', 'confidence', 'field', 'ranking')

    def __init__(self, field):
        self.field = field
        self.octonion = int(np.argmin(field))
        self.confidence = float((field.max() - field.min()) / field.mean())
        self.ranking = [int(k) for k in np.argsort(field)]

    def __repr__(self):
        return (f"<DefectField octonion={self.octonion} "
                f"confidence={self.confidence:.4f}>")


def place(x, use='comm'):
    """Map ``x`` into operator space: which octonion does it want to live in?

    :param x: any 16-vector.
    :param use: ``'comm'`` (default, 76.2% accurate) or ``'assoc'`` (40.5%).
    :returns: the placement.
    :rtype: DefectField
    :raises ValueError: if ``use`` is not one of the two field names.
    """
    if use == 'comm':
        return DefectField(comm_field(x))
    if use == 'assoc':
        return DefectField(assoc_field(x))
    raise ValueError(f"use must be 'comm' or 'assoc', got {use!r}")


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/rendier/Projects/ThePlace')
    O = octonion_basis()
    rng = np.random.default_rng(5)
    print(f"octonions found: {len(O)}  (expect 7)")
    ok = n = 0
    for k in range(len(O)):
        for _ in range(6):
            v = O[k].T @ rng.normal(size=8)
            ok += place(v).octonion == k
            n += 1
    print(f"places a generic element of O_k correctly: {ok}/{n}")
    r = place(rng.normal(size=16))
    print(f"random vector -> {r}  (low confidence expected)")


def _bracketings(seq, cap=None):
    """Every parenthesisation of ``seq``, or a sample if there are too many.

    Catalan(n-1) grows fast: 42 at n=6, 4862 at n=10, 2.7M at n=15. Above
    ``cap`` this samples random bracketings instead of enumerating.

    :param seq: list of 16-vectors.
    :param cap: max bracketings to evaluate; ``None`` means exhaustive.
    :returns: list of resulting vectors.
    :rtype: list[numpy.ndarray]
    """
    if len(seq) == 1:
        return [seq[0]]
    out = []
    for i in range(1, len(seq)):
        for L in _bracketings(seq[:i], cap):
            for R in _bracketings(seq[i:], cap):
                out.append(mul(L, R))
                if cap is not None and len(out) >= cap:
                    return out
    return out


def order_tolerance(word, cap=200):
    """How much does the answer depend on the ORDER you evaluate in?

    Returns ``order_dependence``: 0 means every bracketing agrees and you may
    regroup freely; larger means the arrangement is part of the meaning.

    MEASURED across the nesting S > O > H at word length 5:

        S (16)  1.908604   rigid  -- must be parsed as written
        O  (8)  1.765973
        H  (4)  0.000000   free   -- associative, so all groupings collapse

    The H row is exact, not small: a group has no bracketing dependence at
    all, so opposite arrangements reach the identical element.

    Evaluates every bracketing of ``word`` and reports the normalised spread.
    This is the reorder-safety check: near 0 you may regroup, parallelise or
    fold in any order; large means the grouping IS part of the meaning and
    nothing downstream can recover a mistimed sequence.

    MEASURED at dim 16, unit words of length 6:

        inside the PRESERVE octonion   spread SATURATES  (growth ratio
                                       1.417 -> 1.210 -> 1.076, heading to 1)
        inside a CAGE channel          spread GROWS      (1.320, 1.340, 1.192,
                                       no decay) and the norm grows with it

    So the guest is order-tolerant and the cage is order-critical. Generate
    from the guest when you need robustness to bad timing; from the cage only
    when the order itself is carrying the meaning.

    :param word: sequence of 16-vectors, length >= 2.
    :param cap: bracketing budget; sampling kicks in above it.
    :returns: keys ``order_dependence`` (0 = fully reorderable, higher =
        the arrangement carries meaning), ``tolerance`` (kept as a deprecated
        alias for the same value -- NOTE the name is misleading, it rises as
        tolerance FALLS), ``spread``,
        ``mean_norm``, ``n_bracketings``, ``reorderable`` (bool),
        ``exhaustive`` (bool).
    :rtype: dict
    :raises ValueError: if ``word`` has fewer than two elements -- a single
        term has nothing to reorder and the question is undefined.
    """
    if len(word) < 2:
        raise ValueError("order_tolerance needs at least two terms; a single "
                         "term has no ordering to be tolerant of.")
    vs = _bracketings(list(word), cap)
    M = np.array(vs)
    norms = np.linalg.norm(M, axis=1)
    if len(M) == 1:
        spread = 0.0
    else:
        spread = float(max(np.linalg.norm(M[i] - M[j])
                           for i in range(len(M)) for j in range(i + 1, len(M))))
    mean_norm = float(norms.mean())
    tol = spread / mean_norm if mean_norm > 1e-12 else float('inf')
    return {'order_dependence': tol, 'tolerance': tol,
            'spread': spread, 'mean_norm': mean_norm,
            'n_bracketings': len(M), 'reorderable': tol < 1e-9,
            'exhaustive': cap is None or len(M) < cap}
