#!/usr/bin/env python3
"""
context_pruner.py -- two functions, both useful:

  coherent(a, b)  -- the DIAGNOSTIC. Given two 16-D focal points, is there a
                     sedenion-sphere rotation that carries one onto the
                     other?  SAME  = one object at different perspectives
                     SEPARATE = genuinely distinct attractors
                     AMBIGUOUS = same shape (rotation-invariants match) but
                                 no rotation found in the tested family.

  prune(vectors)  -- the CONTEXT PRUNER. Pairwise coherent() + union-find:
                     collapse perspective-redundant foci, keep the distinct
                     ones. This is the narrative -> dissertational transform
                     as an operation (long-winded = perspective-copies of
                     few real points).

"Perspective" here is NOT a flat plane rotation -- god does not build with
straight lines. It is LEFT-MULTIPLICATION BY A UNIT SEDENION, which bends
space through the non-associative table and is not even an isometry (the
{0, 1, sqrt2} gain spectrum). The swept family is the curved great circles
u_k(t) = cos t . e_0 + sin t . e_k  (exp of a unit imaginary), tried singly
and in two-step products -- a curved 2-patch of the sphere's own moves.
"""
from __future__ import annotations

import numpy as np

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ValaQuenta.modules.box_kite.maths import multiply as _sed_mul  # real S product

DIM = 16


def sed_exp(t, k):
    """The unit sedenion exp(t e_k) = cos t . e_0 + sin t . e_k  (e_k^2=-1)."""
    u = [0.0] * DIM
    u[0] = float(np.cos(t))
    u[k] = float(np.sin(t))
    return u


def perspective(u, x):
    """A curved perspective shift: x -> u . x  (left sedenion product).
    NOT a rotation -- |u.x| != |x| in general."""
    return np.asarray(_sed_mul(list(map(float, u)), list(map(float, x))), float)


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n else v


def coherent(a, b, tol=0.06, nsteps=180, two_step=True):
    """Verdict + evidence. Is there a unit-sedenion perspective carrying
    direction(a) onto direction(b)?  a, b: length-16."""
    a = _unit(np.asarray(a, float)); b = _unit(np.asarray(b, float))
    ts = np.linspace(0.0, 2 * np.pi, nsteps, endpoint=False)

    best = {'residual': 2.0, 'move': None}
    # one curved great circle at a time
    for k in range(1, DIM):
        for t in ts:
            r = np.linalg.norm(_unit(perspective(sed_exp(t, k), a)) - b)
            if r < best['residual']:
                best = {'residual': float(r), 'move': (f'e{k}', round(float(t), 3))}
    # two-step curved patch (coarser grid)
    if two_step and best['residual'] >= tol:
        ts2 = np.linspace(0.0, 2 * np.pi, 24, endpoint=False)
        for j in range(1, DIM):
            for tj in ts2:
                aj = _unit(perspective(sed_exp(tj, j), a))
                for k in range(1, DIM):
                    for tk in ts2:
                        r = np.linalg.norm(
                            _unit(perspective(sed_exp(tk, k), aj)) - b)
                        if r < best['residual']:
                            best = {'residual': float(r),
                                    'move': (f'e{j}', round(float(tj), 2),
                                             f'e{k}', round(float(tk), 2))}
        # cheap early accept can miss; that's why AMBIGUOUS exists

    inv_gap = float(np.linalg.norm(np.sort(np.abs(a)) - np.sort(np.abs(b))))
    gain_gap = abs(np.linalg.norm(perspective(a, a))
                   - np.linalg.norm(perspective(b, b)))

    if best['residual'] < tol:
        verdict = 'SAME'
    elif inv_gap < tol and gain_gap < tol:
        verdict = 'AMBIGUOUS'       # rotation-invariants match, no move found
    else:
        verdict = 'SEPARATE'
    return {'verdict': verdict, 'residual': best['residual'],
            'move': best['move'], 'invariant_gap': inv_gap,
            'gain_gap': float(gain_gap)}


def prune(vectors, tol=0.06):
    """BOTH functions run off ONE Newton-basin collection: `vectors` is the
    focal-point set from a single attractor run. prune() computes the full
    pairwise coherent() matrix once -- the merge groups AND every pairwise
    verdict fall out of that one sweep (coherent() alone is just the
    2-element case, for when you don't have the whole collection).

    Returns {'groups': [[member idx]], 'reps': [rep idx per group],
             'kept': n_groups, 'dropped': n - n_groups,
             'pairs': [(i, j, verdict)]}"""
    V = [np.asarray(v, float) for v in vectors]
    n = len(V)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            c = coherent(V[i], V[j], tol=tol)
            pairs.append((i, j, c['verdict']))
            if c['verdict'] == 'SAME':
                parent[find(i)] = find(j)

    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    glist = list(groups.values())
    reps = [max(g, key=lambda k: np.linalg.norm(V[k])) for g in glist]
    return {'groups': glist, 'reps': reps, 'kept': len(glist),
            'dropped': n - len(glist), 'pairs': pairs}


# --- helper: 19-D context_vector -> 16-D (drop the 3 rarest relations) ---
_DROP = None


def embed16(context_vec19):
    global _DROP
    if _DROP is None:
        from wordnet_boxkite import RELATION_METHODS
        rare = ['usage_domains', 'causes', 'entailments']   # nz-rate < 1%
        _DROP = sorted(RELATION_METHODS.index(r) for r in rare)
    return np.array([c for k, c in enumerate(context_vec19) if k not in _DROP],
                    float)


# ==========================================================================
if __name__ == '__main__':
    import random
    from nltk.corpus import wordnet as wn
    from wordnet_boxkite import context_vector

    random.seed(20260827); np.random.seed(20260827)
    L = '-' * 66

    def cv16(name):
        return embed16(context_vector(wn.synset(name)))

    print(L + "\n1. SANITY  a synset vs itself under a curved perspective shift\n" + L)
    a = cv16('dog.n.01')
    a2 = perspective(sed_exp(random.uniform(0.3, 2.5), random.randint(1, 15)), a)
    print("  dog.n.01  vs  (unit-sedenion . dog.n.01) :", coherent(a, a2)['verdict'])

    print("\n" + L + "\n2. SEPARATE  two unrelated synsets\n" + L)
    for x, y in [('dog.n.01', 'algebra.n.01'), ('rain.n.01', 'democracy.n.01'),
                 ('hammer.n.02', 'sadness.n.01')]:
        c = coherent(cv16(x), cv16(y))
        print(f"  {x:16s} vs {y:18s} -> {c['verdict']:9s} "
              f"resid={c['residual']:.3f} inv_gap={c['invariant_gap']:.3f}")

    print("\n" + L + "\n3. THE QUESTION  related pairs -- one object or separate?\n" + L)
    tests = [
        ('dog.n.01', 'canine.n.02', 'hyponym/hypernym'),
        ('bank.n.01', 'bank.n.09', 'financial vs river (homograph)'),
        ('car.n.01', 'automobile.n.01', 'near-synonym'),
        ('happy.a.01', 'glad.a.01', 'adj near-synonym'),
        ('bank.n.01', 'depository_financial_institution.n.01', 'gloss synonym'),
    ]
    for x, y, note in tests:
        try:
            c = coherent(cv16(x), cv16(y))
        except Exception as e:
            print(f"  {x} / {y}: {e}"); continue
        print(f"  {x:14s} / {y:34s} {c['verdict']:9s} "
              f"resid={c['residual']:.3f} move={str(c['move']):22s}  ({note})")

    print("\n" + L + "\n4. prune()  on a candidate pool\n" + L)
    pool = ['car.n.01', 'automobile.n.01', 'auto.n.01', 'truck.n.01',
            'motorcycle.n.01', 'bicycle.n.01', 'vehicle.n.01', 'wheel.n.01']
    P = prune([cv16(p) for p in pool])
    print(f"  {len(pool)} in -> {P['kept']} kept, {P['dropped']} pruned")
    for g, r in zip(P['groups'], P['reps']):
        print("   ", " + ".join(pool[k] for k in g), " -> keep", pool[r])
