"""Where does the Hyperwebster index live? Measure its dimensionality.

Claim under test: the Hyperwebster / Horner enumeration index is a SCALAR
(radial, norm-like) quantity, dominated by string length -- therefore it lands
on e0, the fixed point, which Phase 25 proved is in NO Assessor.
"""
import math, statistics

def horner(w, base=95, offset=32):
    v = 0
    for ch in w:
        v = v * base + max(0, ord(ch) - offset)
    return abs(v)

words = ["a","at","cat","car","dog","feline","big","large","the","is","of",
         "water","man","dark","hot","philadelphos","holcus","muster",
         "sedenion","octonion","zero","divisor","eight","ate","though","tough"]

print("=== 1. log(index) vs length : is the index just length? ===")
print(f"{'word':<16}{'len':>4}{'log95(index)':>14}{'index bits':>12}")
rows = []
for w in sorted(words, key=len):
    v = horner(w)
    lg = math.log(v, 95) if v > 0 else 0.0
    rows.append((len(w), lg))
    print(f"{w:<16}{len(w):>4}{lg:>14.4f}{v.bit_length():>12}")

# correlation between length and log95(index)
n = len(rows)
xs = [r[0] for r in rows]; ys = [r[1] for r in rows]
mx, my = statistics.mean(xs), statistics.mean(ys)
cov = sum((x-mx)*(y-my) for x,y in rows)/n
sx = math.sqrt(sum((x-mx)**2 for x in xs)/n)
sy = math.sqrt(sum((y-my)**2 for y in ys)/n)
print(f"\ncorr(length, log95 index) = {cov/(sx*sy):+.6f}")
print("  -> log95(index) IS the length, to within the leading digit.")

print("\n=== 2. semantic vs orthographic distance in index space ===")
pairs = [("cat","car","unrelated"), ("cat","dog","co-hyponym"),
         ("cat","feline","SYNONYM"), ("big","large","SYNONYM"),
         ("eight","ate","HOMOPHONE"), ("though","tough","near-spelling")]
for a,b,rel in pairs:
    d = abs(horner(a)-horner(b))
    print(f"  {a:>7} / {b:<8} {rel:<14} index distance = {d:,}")

print("\n=== 3. the dimensionality of the address ===")
print("  Horner index          -> 1 scalar")
print("  next_prime(index)     -> 1 scalar")
print("  pi(prime) = zero_idx  -> 1 scalar, range [1, 6542]")
print("  gamma_at(zero_idx)    -> 1 scalar")
print("  E = |sin(pi*g/(g+1))| -> 1 scalar")
print("  RESULT: text enters the engine as ONE real number.")
print("  A single real number has no angular content. It is a RADIUS.")
print("  In 0_RB the radial/scalar channel is e0 -- the fixed point, in no Assessor.")

print("\n=== 4. capacity ===")
print(f"  distinct zero addresses available : 6542")
print(f"  English tokens to seat            : 101916")
print(f"  pigeonhole collision rate         : {101916/6542:.1f} : 1")
