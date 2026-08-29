#!/usr/bin/env python3
"""
add_scale_sign.py -- the ADD / SCALE / SIGN decomposition, as a shared,
importable primitive.

The three irreducibles (generational-lineage skill, section 1). Every
operation lands on exactly one of them or is DERIVED from them by
composition; if it lands on none the domain is incomplete, if on two the
decomposition is wrong.

    IRREDUCIBLE   identity        content            group factor of Aff(1,R)
    ADD           0               the flow / count   R          (translations)
    SCALE         1               gain, size         R_{>0}     (dilations)
    SIGN          even parity     one bit, det +/-1  Z/2        (the flip)

    Aff(1,R) = R  |x|  (R_{>0} x Z/2)  =  ADD |x| (SCALE x SIGN)
             = (step/fold COUNT) |x| (SIZE x DIRECTION)

  - SCALE ~= ADD in the log chart (exp/log): same abstract group R, but
    ADD has no fixed point (affine), SCALE fixes 0 (linear).
  - the ONLY non-trivial bracket is  [SCALE, ADD] = ADD  -- dilate-then-
    translate != translate-then-dilate, by a translation. "order matters"
    for ADD; SIGN and SCALE commute.
  - identities 0, 1, +1 are the three "does nothing" elements -> off both
    Two Trees (the Mingling).

Tiers (skill section 2):
    tier 3  chirality, factorial, leverage, balance   -- COUNTS / RATIOS
    tier 2  vector, boundary, origin, fulcrum/anchor  -- FIXED SETS
    tier 1  reflect, rotate, contract/dilate          -- I - 2uu^T ; {0,1,sqrt2}
    tier 0  ADD, SCALE, SIGN

The four-question test (skill section 3), asked IN ORDER:
    1. count or ratio of something else?      -> tier 3, DERIVED
    2. a fixed set?                            -> tier 2, DERIVED
    3. changes length? -> needs DILATE ; preserves length? -> from REFLECT
    4. needs an added constraint to exist?     -> COROLLARY, not a geometry
Only what survives all four is a candidate primitive.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ── the three, as data ────────────────────────────────────────────────────
IRREDUCIBLES = {
    'ADD':   {'identity': '0',        'axis': '{+,-}', 'group': 'R (translations)',
              'content': 'the flow / the count; order-dependent'},
    'SCALE': {'identity': '1',        'axis': '{x,/}', 'group': 'R_{>0} (dilations)',
              'content': 'gain / size; ~= ADD in the log chart'},
    'SIGN':  {'identity': 'even parity', 'axis': 'det +/-1', 'group': 'Z/2 (the flip)',
              'content': 'one bit, nothing between; chirality; mountain/valley fold'},
}
BRACKET = '[SCALE, ADD] = ADD'            # the only non-trivial one
IDENTITIES = ('0', '1', '+1')             # ADD, SCALE, SIGN -- the Mingling

# Aff(1,R) = R |x| (R_{>0} x Z/2). The semidirect factor structure, named.
AFF1 = {
    'group':   'Aff(1,R) = R |x| (R_{>0} x Z/2)',
    'factors': (('ADD',   'R',        'the normal factor -- translations, the flow'),
                ('SCALE', 'R_{>0}',   'acts on ADD by scaling the translation'),
                ('SIGN',  'Z/2',      'acts on ADD by flipping it; commutes with SCALE')),
    'reading': '(fold COUNT) |x| (fold SIZE x fold DIRECTION)',
    'why_semidirect': 'SCALE and SIGN reparametrise ADD, so the product is not '
                      'direct: [SCALE, ADD] = ADD is the one non-trivial bracket. '
                      'ADD alone is affine (no fixed point); SCALE alone is linear '
                      '(fixes 0); together they are every 1-D similarity.',
}

# The roll-down: every DERIVED operation, traced past its immediate parent to
# the tier-0 root it ultimately rests on. REFLECT is SIGN + a fixed axis, so
# everything whose content is "a reflection / a parity / a fixed set of a
# reflection" roots on SIGN; everything that changes a length roots on SCALE;
# only the raw flow / count roots on ADD.
_ROOT_OF = {
    # tier 1
    'reflect': 'SIGN', 'rotate': 'SIGN', 'dilate': 'SCALE', 'contract': 'SCALE',
    'quotient': 'SCALE',            # collapse R -> R/I, gain 0 on I
    'bifurcation': 'SCALE', 'spiral': 'SCALE', 'tuning': 'SCALE',
    # tier 2 -- fixed sets of a reflection
    'vector': 'SIGN', 'boundary': 'SIGN', 'origin': 'SIGN', 'fulcrum': 'SIGN',
    'anchor': 'SIGN', 'balance': 'SIGN', 'ideal': 'SIGN', 'radical': 'SIGN',
    'zero-divisor': 'SIGN', 'basin': 'SIGN', 'pathway': 'ADD',
    'inside-outside': 'SIGN',
    # tier 3 -- counts and ratios
    'chirality': 'SIGN', 'factorial': 'SIGN', 'factoral': 'SIGN',
    'leverage': 'SIGN', 'unit': 'SCALE', 'associator': 'SIGN',
    'primary-decomposition': 'ADD', 'self-similar': 'SCALE', 'fractal': 'SCALE',
    'orbit-trap': 'ADD', 'orbit-curvature': 'SIGN', 'lyapunov': 'SCALE',
    # tier 0
    'add': 'ADD', 'scale': 'SCALE', 'sign': 'SIGN', 'gcd': 'SCALE',
}


def root_of(name: str) -> Optional[str]:
    """The tier-0 irreducible a named operation ultimately rests on.

    None means the name is not in the domain -- per skill section 5 that is
    the emergence signal, not a licence to invent a root.
    """
    return _ROOT_OF.get(name.strip().lower())


# Which of the four questions fires for each named operation -- so a bare name
# can be classified without the caller re-supplying the flags every time.
_KNOWN_SPECS = {
    # Q1  count / ratio -> tier 3
    'chirality': dict(is_count_or_ratio=True), 'factorial': dict(is_count_or_ratio=True),
    'factoral': dict(is_count_or_ratio=True), 'unit': dict(is_count_or_ratio=True),
    'associator': dict(is_count_or_ratio=True), 'self-similar': dict(is_count_or_ratio=True),
    'fractal': dict(is_count_or_ratio=True), 'orbit-trap': dict(is_count_or_ratio=True),
    'orbit-curvature': dict(is_count_or_ratio=True), 'lyapunov': dict(is_count_or_ratio=True),
    'primary-decomposition': dict(is_count_or_ratio=True),
    # Q2  fixed set -> tier 2
    'vector': dict(is_fixed_set=True), 'boundary': dict(is_fixed_set=True),
    'origin': dict(is_fixed_set=True), 'fulcrum': dict(is_fixed_set=True),
    'anchor': dict(is_fixed_set=True), 'balance': dict(is_fixed_set=True),
    'ideal': dict(is_fixed_set=True), 'radical': dict(is_fixed_set=True),
    'zero-divisor': dict(is_fixed_set=True), 'basin': dict(is_fixed_set=True),
    'pathway': dict(is_fixed_set=True), 'inside-outside': dict(is_fixed_set=True),
    # Q3a  changes length -> tier 1, SCALE
    'dilate': dict(changes_length=True), 'contract': dict(changes_length=True),
    'bifurcation': dict(changes_length=True), 'spiral': dict(changes_length=True),
    'tuning': dict(changes_length=True), 'quotient': dict(changes_length=True),
    # Q3b  preserves length -> tier 1, SIGN
    'reflect': dict(preserves_length=True), 'rotate': dict(preserves_length=True),
    # Q4  needs a constraint -> COROLLARY
    'leverage': dict(needs_added_constraint=True),
    # tier-0 primitives (named directly)
    'add': dict(order_dependent=True), 'scale': dict(),
}
_TIER0 = {'add': 'ADD', 'scale': 'SCALE', 'sign': 'SIGN', 'gcd': 'SCALE'}


def describe(name: str, **overrides) -> Decomposition:
    """Classify a bare operation NAME. Uses the known-spec table; `overrides`
    win, for an unknown name or to correct a lookup. When the name has a
    roll-down root, that root is trusted over flag inference (name-level
    knowledge beats a guessed flag) and any disagreement is noted."""
    key = name.strip().lower()
    if (not overrides and key not in _TIER0 and key not in _KNOWN_SPECS
            and key not in _ROOT_OF):
        return Decomposition(name, None, None,
                             'not in the domain', 'UNPLACED', '—', root=None,
                             notes=['skill section 5 emergence signal: show it is '
                                    'reachable by composition from ADD/SCALE/SIGN, '
                                    'or pass the four-question flags explicitly'])
    if key in _TIER0 and not overrides:
        r = _TIER0[key]
        return Decomposition(name, 0, r if key != 'gcd' else None,
                             IRREDUCIBLES[r]['group'] if key != 'gcd' else 'SCALE (division)',
                             'IRREDUCIBLE' if key != 'gcd' else 'DERIVED',
                             'TELPERION', root=r,
                             notes=['named tier-0 floor' if key != 'gcd'
                                    else 'one division = the LCA of two lineages'])
    spec_kw = dict(_KNOWN_SPECS.get(key, {}))
    spec_kw.update(overrides)
    d = classify(OpSpec(name, **spec_kw))
    rt = root_of(key)
    if rt and d.root and rt != d.root:
        d.notes = list(d.notes) + [f'roll-down root {rt} overrides flag-inferred {d.root}']
        d.root = rt
    elif rt and not d.root:
        d.root = rt
    return d

TIER = {
    3: ('chirality', 'factorial', 'leverage', 'balance'),          # counts / ratios
    2: ('vector', 'boundary', 'origin', 'fulcrum', 'anchor'),      # fixed sets
    1: ('reflect', 'rotate', 'contract', 'dilate'),                # I - 2uu^T
    0: ('ADD', 'SCALE', 'SIGN'),
}

TWO_TREES = {
    'TELPERION': ('ADD', 'SCALE', 'SIGN', 'REFLECT', 'DILATE'),    # irreducible
    'LAURELIN':  ('chirality', 'factorial', 'vector', 'boundary',  # composite
                  'origin', 'fulcrum', 'balance', 'leverage'),
    'MINGLING':  IDENTITIES,                                        # 0 and 1
}


@dataclass
class Decomposition:
    name: str
    tier: int
    irreducible: Optional[str]        # 'ADD'|'SCALE'|'SIGN' if it IS one; else None
    descends_from: str
    status: str                       # 'IRREDUCIBLE' | 'DERIVED' | 'COROLLARY'
    tree: str                         # TELPERION | LAURELIN | MINGLING
    root: Optional[str] = None        # the tier-0 irreducible it ultimately rests on
    notes: list = field(default_factory=list)


@dataclass
class OpSpec:
    """What you know about the operation, for the four-question test."""
    name: str
    is_count_or_ratio: bool = False   # Q1
    is_fixed_set: bool = False        # Q2
    changes_length: bool = False      # Q3a
    preserves_length: bool = False    # Q3b
    needs_added_constraint: bool = False  # Q4
    order_dependent: bool = False     # informs ADD vs the rest
    is_identity: bool = False


def classify(spec: OpSpec) -> Decomposition:
    """The section-3 test, in order. Returns where it lands and why.

    `root` is filled from the roll-down table when the name is known, so a
    DERIVED op still reports which of ADD/SCALE/SIGN it ultimately rests on.
    """
    n = spec.name
    known_root = root_of(n)
    if spec.is_identity:
        return Decomposition(n, -1, None, 'the operation resting', 'IRREDUCIBLE',
                             'MINGLING', root=None,
                             notes=['an identity: 0 / 1 / +1 -- off both trees'])
    # Q1
    if spec.is_count_or_ratio:
        return Decomposition(n, 3, None, 'a COUNT or RATIO of the layer below',
                             'DERIVED', 'LAURELIN', root=known_root or 'SIGN',
                             notes=['chirality = parity of a reflection count; '
                                    'factorial = order of the coordinate reflection '
                                    'group -- counts of SIGN-compositions'])
    # Q2
    if spec.is_fixed_set:
        return Decomposition(n, 2, None, 'a FIXED SET  ker(M - I)', 'DERIVED',
                             'LAURELIN', root=known_root or 'SIGN',
                             notes=['fulcrum = anchor = origin = balance -- one '
                                    'computation, several names; the name records '
                                    'what you were resisting'])
    # Q4 (corollary check before granting primitive status)
    if spec.needs_added_constraint:
        return Decomposition(n, 2, None, 'needs an added constraint to exist',
                             'COROLLARY', 'LAURELIN', root=known_root or 'SIGN',
                             notes=['remove the constraint and it is gone (leverage '
                                    'needs rigidity; the fulcrum survives, leverage '
                                    'does not)'])
    # Q3
    if spec.changes_length:
        return Decomposition(n, 1, 'SCALE', 'needs DILATE (gain != 1)', 'DERIVED',
                             'TELPERION', root='SCALE',
                             notes=['tier-1 dilation; the SCALE part of a spectrum'])
    if spec.preserves_length:
        return Decomposition(n, 1, 'SIGN', 'reachable from REFLECT (I - 2uu^T)',
                             'DERIVED', 'TELPERION', root='SIGN',
                             notes=['tier-1 reflection; its CONTENT is SIGN + a fixed axis'])
    # survived all four -> a tier-0 irreducible; pick by its axis
    if spec.order_dependent:
        return Decomposition(n, 0, 'ADD', 'the additive group (R, +), translations',
                             'IRREDUCIBLE', 'TELPERION', root='ADD',
                             notes=['no fixed point; the flow / the fold count; '
                                    'order-dependent -- [SCALE, ADD] = ADD'])
    return Decomposition(n, 0, 'SCALE', 'the multiplicative group (R_{>0}, x)',
                         'IRREDUCIBLE', 'TELPERION', root='SCALE',
                         notes=['one fixed point (0); the size; ~= ADD via log'])


# ── the recent findings, as decomposition facts (kept with the primitive) ──
FINDINGS = {
    'primes': ('SIGN recursed over the ordered pathway of prior primes. Each '
               'sieve rung is SIGN (the divisibility bit) over SCALE-generated '
               'multiples, marched by ADD, mex-selected; recursion depth pi(sqrt n). '
               'Not Fibonacci (that is pure ADD). A prime\'s definition is the '
               'conjunction "for all q < p: q does not divide p" -- it references '
               'every prior prime.'),
    'factorial': ('the MULTIPLICATIVE integral: n! = prod_{k=1}^n k (product-integral '
                  'of the identity). Its opposite (un-integral) is the ratio of '
                  'consecutive terms: n!/(n-1)! = n, EXACTLY, no +C. After log: '
                  'ln(n!) = sum ln k, and ln(n!) - ln((n-1)!) = ln n exactly. '
                  'Cleaner inverse pair than d/dx vs integral (which loses the '
                  'constant). In lineage terms factorial = the order of the '
                  'coordinate reflection group = SIGN-compositions counted -> tier 3.'),
    'fold_vs_step': ('the affine triple reads as FOLD count / FOLD size / FOLD '
                     'direction (mountain vs valley = SIGN), not step. Origami is a '
                     'partitioning algorithm; the Two Trees domain is the factoring '
                     'map; folding = partitioning = factoring, all the way up and '
                     'down the tower.'),
    'e': ('quantization, not growth. e is the base that makes ln a step-counter: one '
          'e-multiply advances ln by exactly 1. d/dx e^x = e^x is the fixed point of '
          'differentiation (step = state), not a rate. e = sum 1/k! -- a sum over '
          'discrete arrangements.'),
}


if __name__ == '__main__':
    tests = [
        OpSpec('translation', order_dependent=True),
        OpSpec('dilation', changes_length=True),
        OpSpec('reflection', preserves_length=True),
        OpSpec('factorial', is_count_or_ratio=True),
        OpSpec('origin', is_fixed_set=True),
        OpSpec('leverage', needs_added_constraint=True),
        OpSpec('the number 1', is_identity=True),
        OpSpec('multiplication', order_dependent=False),
    ]
    print("ADD / SCALE / SIGN decomposition\n" + "=" * 58)
    print(f"  {'operation':16s} {'tier':>4}  {'IS':6s} {'ROOT':6s} {'status':11s} tree")
    print("  " + "-" * 56)
    for t in tests:
        d = classify(t)
        irr = d.irreducible or '-'
        root = d.root or '-'
        print(f"  {t.name:16s} {d.tier:>4}  {irr:6s} {root:6s} {d.status:11s} {d.tree}")

    print("\n  describe() -- bare names, no flags:")
    for nm in ('factorial', 'dilate', 'reflect', 'origin', 'leverage',
               'pathway', 'add', 'scale', 'sign', 'gcd', 'associator'):
        d = describe(nm)
        print(f"    {nm:16s} tier {d.tier:>2}  root={d.root or '-':5s} {d.status}")
    assert describe('factorial').root == 'SIGN' and describe('factorial').tier == 3
    assert describe('dilate').root == 'SCALE' and describe('dilate').tier == 1
    assert describe('add').tier == 0 and describe('sign').tier == 0
    print("\n  " + AFF1['group'])
    print("  " + AFF1['reading'])
    print(f"  only non-trivial bracket:  {BRACKET}")
    print(f"  identities (the Mingling): {IDENTITIES}")
    # roll-down spot checks
    assert root_of('factorial') == 'SIGN'
    assert root_of('dilate') == 'SCALE'
    assert root_of('pathway') == 'ADD'
    assert root_of('nonsense') is None
    print("\n  roll-down: factorial->SIGN  dilate->SCALE  pathway->ADD  nonsense->None  OK")
    print("  recent findings folded in:", ", ".join(FINDINGS))
