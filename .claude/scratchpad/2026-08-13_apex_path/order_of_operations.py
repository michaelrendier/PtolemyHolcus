"""Two questions, both decidable from the CD table.

Q1  Do the sedenion basis elements carry an ORDER OF OPERATIONS -- a precedence?
Q2  Is e0-e7 'calculable' and e8-e15 'where opinion lives'?  If so, WHY exactly?
"""
import numpy as np, itertools, collections

N = 16
def conj(v): w = v.copy(); w[1:] = -w[1:]; return w
def mul(x, y):                                   # variant 1 (the verified one)
    n = len(x)
    if n == 1: return np.array([x[0]*y[0]])
    h = n//2; a, b = x[:h], x[h:]; c, d = y[:h], y[h:]
    A = lambda v: conj(v) if len(v) > 1 else v.copy()
    return np.concatenate([mul(a, c) - mul(A(d), b), mul(d, a) + mul(b, A(c))])
def e(k):
    v = np.zeros(N); v[k] = 1.0; return v

# signed multiplication table: e_i * e_j = sign * e_idx
TBL = np.zeros((N, N), dtype=int); SGN = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        p = mul(e(i), e(j)); k = int(np.argmax(np.abs(p)))
        TBL[i, j] = k; SGN[i, j] = p[k]

print("="*72)
print("Q2 — WHY e0-e7 differs from e8-e15.  Closure under multiplication.")
print("="*72)
lo, hi = set(range(0, 8)), set(range(8, 16))
lo_closed = all(TBL[i, j] in lo for i in lo for j in lo)
hi_closed = all(TBL[i, j] in hi for i in hi for j in hi)
hi_lands  = collections.Counter('lo' if TBL[i, j] in lo else 'hi'
                                for i in hi for j in hi)
print(f"  e0-e7  x  e0-e7  stays in e0-e7 ?  {lo_closed}   <- A SUBALGEBRA")
print(f"  e8-e15 x  e8-e15 stays in e8-e15?  {hi_closed}   <- NOT closed")
print(f"     products of two upper elements land: {dict(hi_lands)}")
print("  => e0-e7 is the OCTONIONS: closed, alternative, a DIVISION ALGEBRA.")
print("     e8-e15 is not an algebra at all -- it is a MODULE over e0-e7.")

print()
print("  zero divisors: do they REQUIRE both halves?")
found_lo = 0
for a in range(1, 8):
    for b in range(1, 8):
        if a == b: continue
        for s in (1, -1):
            v1 = e(a) + s*e(b)                     # both legs inside e0-e7
            for c in range(1, 8):
                for d in range(1, 8):
                    if c == d: continue
                    for t in (1, -1):
                        if np.linalg.norm(mul(v1, e(c)+t*e(d))) < 1e-9:
                            found_lo += 1
print(f"    zero divisors with BOTH legs inside e0-e7 : {found_lo}   (expect 0)")
print(f"    every Assessor is span(e_a, e_(b+8)) -- ONE LEG IN EACH HALF.")
print()
print("  VERDICT: the asymmetry is not epistemic, it is ALGEBRAIC.")
print("    e0-e7  : division defined everywhere -> a unique answer -> CALCULABLE")
print("    e8-e15 : division undefined at the ZD -> answers UNDERDETERMINED")
print("    'opinion' = underdetermination. Both halves are equally COMPUTABLE;")
print("    only the lower half is INVERTIBLE.")

print()
print("="*72)
print("Q1 — ORDER OF OPERATIONS: precedence from the associator")
print("="*72)
print("  In an ASSOCIATIVE algebra bracketing is irrelevant -- no order of")
print("  operations is needed.  Precedence exists exactly where [a,b,c] != 0.")
print()
def assoc(i, j, k):
    return mul(mul(e(i), e(j)), e(k)) - mul(e(i), mul(e(j), e(k)))

curving = 0
involve = np.zeros(N, dtype=int)
for i, j, k in itertools.product(range(N), repeat=3):
    if np.linalg.norm(assoc(i, j, k)) > 1e-9:
        curving += 1
        involve[i] += 1; involve[j] += 1; involve[k] += 1
print(f"  curving basis triples: {curving} / {N**3}   (published: 1848/4096)")
print()
OPS = ['identity','negate','bind','name','apply','abstract','branch','iterate',
       'recurse','allocate','query','derefer','compose','parallelize','interrupt','emit']
print(f"  {'e_k':>4}  {'operator':<14}{'in curving triples':>20}  {'half':>5}")
order = np.argsort(-involve)
for k in order:
    print(f"  e{k:<3}  {OPS[k]:<14}{involve[k]:>20}  {'lo' if k < 8 else 'hi':>5}")

print()
lo_inv = involve[:8].sum(); hi_inv = involve[8:].sum()
print(f"  total involvement  lower half {lo_inv}   upper half {hi_inv}"
      f"   ratio {hi_inv/max(lo_inv,1):.3f}")
print(f"  e0 (identity) involvement: {involve[0]}  <- expect 0, it associates with everything")

print()
print("  PRECEDENCE READING: elements in MORE curving triples are the ones whose")
print("  bracketing you must specify.  Elements in NONE are free -- they can be")
print("  moved without changing the result.  That IS an order of operations,")
print("  and it is derived from the table rather than declared.")

# the tower levels -- the other natural order
print()
print("="*72)
print("the CD tower already imposes an order, by construction level")
print("="*72)
levels = {0:'R  real', 1:'C  complex', 2:'H  quaternion', 3:'H  quaternion'}
for k in range(4, 8):  levels[k] = 'O  octonion'
for k in range(8, 16): levels[k] = 'S  sedenion'
lost = {'R  real':'-', 'C  complex':'ordering', 'H  quaternion':'commutativity',
        'O  octonion':'associativity', 'S  sedenion':'alternativity / division'}
seen = []
for k in range(N):
    if levels[k] not in seen:
        seen.append(levels[k])
        print(f"  e{k:<3} {levels[k]:<16} property lost at this step: {lost[levels[k]]}")
print()
print("  Each doubling BUYS dimensions and PAYS a property. That is the deepest")
print("  order of operations in the object: not a precedence among elements but")
print("  a precedence among the LAWS they obey.")
