"""Verify what 0_RB says the boundary IS: det(L_a)=0 and the {4,8,4} eigensplit.

0_RB claims, at a zero-divisor a:
    lambda = 0      x4   null space      -- gravity (ABSENT)
    lambda = +-i    x8   imaginary pair  -- three quantum forces
    lambda = +-i.r2 x4   scaled pair     -- Sigma_RB channel
Checked here from the Cayley-Dickson table, not assumed.
"""
import numpy as np

def cd_mul(x, y):
    """Cayley-Dickson product, dimension = len(x), power of two."""
    n = len(x)
    if n == 1:
        return np.array([x[0]*y[0]])
    h = n // 2
    a, b = x[:h], x[h:]
    c, d = y[:h], y[h:]
    def conj(v):
        w = v.copy(); w[1:] = -w[1:]; return w
    # (a,b)(c,d) = (ac - d*b , a*d + c b)   -- conjugate on the starred term
    left  = cd_mul(a, c) - cd_mul(conj(d), b)
    right = cd_mul(conj(a), d) + cd_mul(c, b)
    return np.concatenate([left, right])

N = 16
def e(k):
    v = np.zeros(N); v[k] = 1.0; return v

def L(a):
    """left-multiplication matrix: column k is a * e_k"""
    return np.column_stack([cd_mul(a, e(k)) for k in range(N)])

print("="*70)
print("sanity: is the algebra right?")
print("="*70)
# octonion subalgebra must be a division algebra; sedenions must not be
prod = cd_mul(e(1), e(1))
print(f"  e1*e1 = {prod[0]:+.0f} (expect -1)")
assoc = cd_mul(cd_mul(e(1), e(2)), e(4)) - cd_mul(e(1), cd_mul(e(2), e(4)))
print(f"  associator [e1,e2,e4] norm = {np.linalg.norm(assoc):.3f}  (octonions: nonzero)")

print()
print("="*70)
print("the ASSESSOR: span(e_a, e_{b+8}), a,b in 1..7, a != b")
print("="*70)
a_i, b_i = 1, 2
A1 = e(a_i) + e(b_i+8)          # a diagonal of the assessor plane
A2 = e(a_i) - e(b_i+8)
print(f"  a = e{a_i} + e{b_i+8}     b = e{a_i} - e{b_i+8}")
print(f"  a*b norm = {np.linalg.norm(cd_mul(A1, A2)):.2e}   <- ZERO DIVISOR" )
print(f"  |a| = {np.linalg.norm(A1):.4f}   |b| = {np.linalg.norm(A2):.4f}   (both nonzero)")

print()
print("="*70)
print("det(L_a) at the zero divisor")
print("="*70)
La = L(A1)
print(f"  det(L_a) = {np.linalg.det(La):.3e}")
print(f"  rank     = {np.linalg.matrix_rank(La, tol=1e-9)} / 16")
print(f"  nullity  = {16 - np.linalg.matrix_rank(La, tol=1e-9)}")

print()
print("="*70)
print("EIGENVALUES of L_a  -- 0_RB predicts {4 zero, 8 at +-i.s, 4 at +-i.s.sqrt2}")
print("="*70)
w = np.linalg.eigvals(La)
mag = np.abs(w)
uniq = []
for m in sorted(mag):
    if not uniq or abs(m - uniq[-1][0]) > 1e-6:
        uniq.append([m, 1])
    else:
        uniq[-1][1] += 1
print(f"{'|lambda|':>12}{'multiplicity':>15}{'ratio to smallest nonzero':>28}")
nz = [u for u in uniq if u[0] > 1e-9]
base = nz[0][0] if nz else 1.0
for m, c in uniq:
    r = '-' if m < 1e-9 else f"{m/base:.6f}"
    print(f"{m:>12.6f}{c:>15}{r:>28}")

print()
print(f"  sqrt(2) = {np.sqrt(2):.6f}")
print(f"  purely imaginary? max|Re(lambda)| = {np.abs(w.real).max():.2e}")

print()
print("="*70)
print("VERDICT")
print("="*70)
mults = [c for m, c in uniq]
print(f"  multiplicity pattern (by |lambda|, ascending): {mults}")
zero_mult = next((c for m, c in uniq if m < 1e-9), 0)
print(f"  null space dimension : {zero_mult}")
print(f"  0_RB claims          : 4")
print(f"  MATCH" if zero_mult == 4 else f"  ** MISMATCH **")
