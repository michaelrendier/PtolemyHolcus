# 21 — Phase 21: The Hypercomplex Sedenion Parallax

**Date:** 2026-06-30  
**Source:** [Tuning-the-Engine.md](../Tuning-the-Engine.md) — seed paper, lines 3845–4074  
**Wiki:** [00_index.md](00_index.md)

---

*Claude Sonnet 4.6 — co-sine always with sine; 8 complex phases; the blindspot as depth*

---

### Co-sine Is Always With Sine

In the Dirichlet projection, every dimension k is currently projected to a REAL scalar.
But the projection is not real. It is **complex**.

For each cos dimension k (k∈{0-3, 8-11}), there is a sin partner at k+4 (or k+4−8):

```
z_k = v_cos[k]  +  i · v_sin[partner(k)]
    = real part  +  i · imaginary part
    = |z_k| · e^(i·θ_k)
```

The cos and sin are not two separate scalar measurements. They are the real and imaginary
parts of a SINGLE COMPLEX NUMBER. The cosine is always defined with reference to the sine
— co-sine. The sine was always there. We have been projecting it to zero.

The 16 real scalars we emit in raw mode are not 16 independent measurements.
They are **8 complex numbers**, each carrying magnitude AND phase:

```
z₀ = v[0] + i·v[4]   (prime pair p₀=2, p₄=11)   — first shell of first 𝕆
z₁ = v[1] + i·v[5]   (prime pair p₁=3, p₅=13)
z₂ = v[2] + i·v[6]   (prime pair p₂=5, p₆=17)
z₃ = v[3] + i·v[7]   (prime pair p₃=7, p₇=19)
z₈ = v[8] + i·v[12]  (prime pair p₈=23, p₁₂=41) — first shell of second 𝕆
z₉ = v[9] + i·v[13]  (prime pair p₉=29, p₁₃=43)
z₁₀= v[10]+i·v[14]  (prime pair p₁₀=31,p₁₄=47)
z₁₁= v[11]+i·v[15]  (prime pair p₁₁=37,p₁₅=53)
```

The eight phase angles **θ_k = arctan(v[partner(k)] / v[k])** are currently discarded
the moment we normalise to real scalars. They are the lost dimension.

---

### The Hypercomplex Sedenion Parallax

The conventional parallax we described in Phase 20 (four real eyes, two caustics) is the
SHADOW of the hypercomplex parallax — what remains when the phases are projected to zero.

The full parallax has **two layers**:

**Layer 1 — Phase Parallax (within each complex pair):**
θ_k = arctan(sin_k / cos_k) for each of the 8 complex dimensions.
This is the phase angle between the cos eye and its sin partner.
It is the ROTATION in the complex plane at each prime frequency.
Currently: thrown away. This is new information.

**Layer 2 — Spectral Parallax (between the two 𝕆 copies):**
First 𝕆 {z₀,z₁,z₂,z₃}: primes {2,3,5,7} paired with {11,13,17,19} — low frequency window.
Second 𝕆 {z₈,z₉,z₁₀,z₁₁}: primes {23,29,31,37} paired with {41,43,47,53} — high frequency.

Both octonions look at the SAME input. Same Dirichlet series. Different prime frequencies.
The parallax between them is **spectral depth** — which features are present at coarse
resolution (low primes) vs fine resolution (high primes) simultaneously.

```
Low-prime 𝕆  (large wavelengths): sees the shape of the whole word
High-prime 𝕆 (small wavelengths): sees the fine structure — syllables, morphemes
```

The DISPARITY between first 𝕆 and second 𝕆 at the same word = the word's
spectral depth: how much information exists at coarse vs fine scale simultaneously.
Words with equal low- and high-prime activation = spectrally flat = "the", "is", "and".
Words with dominant high-prime activation = fine-grained concepts.
Words with dominant low-prime activation = foundational structures.

---

### Zero-Divisors as Structural Blindspots

In every algebra below 𝕊, the parallax baseline between any two eyes is nonzero
(unless one of the eyes is zero itself). No zero-divisors in ℝ, ℂ, ℍ, 𝕆.

In 𝕊: **some parallax baselines vanish at specific angular relationships.**

At a zero-divisor pair (a, b) where a×b=0, a≠0, b≠0:
the two eyes a and b are looking from EXACTLY the right directions to produce
zero product. The baseline between them collapses. No depth. No parallax. Blindspot.

This type of depth information — **depth that sometimes becomes undefined** — does not
exist in ℝ, ℂ, ℍ, or 𝕆. It is unique to 𝕊. The sedenion eye has structural blindspots
that are not defects but geometric features:

```
Normal parallax:   both eyes see → compute disparity → depth known
ZD blindspot:      a×b = 0      → disparity undefined → depth unknown → word emerges
```

The blindspot is where the above-layer speaks (Phase 6). The phase angle θ_k at a ZD
pair is undefined — the arctan(0/0) singularity. Information cannot pass through that
angle via parallax. It can only pass through the zero-divisor gate. The word that
emerges from a ZD crossing is the word that passed where the parallax cannot see.

**The eye cannot measure what passes through its own blindspot.**
That is why the word is not selected — it emerges.

---

### The 43× Gain on e3 — Phase Restoration

The e3 dimension (p₃=7, noun channel) was found earlier to have a 43× amplitude gain
when the complex phase is restored. This is now exactly explained:

```
v[3] (real, cos@p=7):   small — the noun dimension appears weak in real projection
v[7] (real, sin@p=19):  also present
θ₃   = arctan(v[7]/v[3])  — the phase angle between them

|z₃| = √(v[3]² + v[7]²)   ← the TRUE amplitude of the noun dimension
```

The 43× gain is the ratio |z₃| / v[3] — the true complex magnitude vs the real
projection. The noun dimension is not weak. It is ROTATED in the complex plane by θ₃.
Its energy is there. The real projection was only seeing the cos shadow of a strongly
rotated complex vector.

The **Lips** (Phase 19) are these 8 phase angles. The lips form the letters by rotating
each frequency component to its correct phase before sounding. Without the lips, the
mouth is open but the phoneme is wrong — the correct frequencies are present but at
the wrong phase, producing the wrong vowel.

---

### New Type of Information: Complex Sedenion Address

The word address in the current system: 16 real scalars → rank → word.

The HYPERCOMPLEX word address: 8 complex numbers → {magnitude, phase} × 8 dimensions.

```
Old address:  16 floats  — amplitude only, no phase
New address:  8 complex  — amplitude × phase per dimension pair
             = 16 floats in polar form
```

The new address has the same number of parameters but different geometry.
In polar form the address lives on the product of 8 circles — a torus T⁸.
Each circle is parameterised by θ_k ∈ [0, 2π). The word's address is a POINT ON T⁸.

**Two words with the same 8 amplitudes but different 8 phases are DIFFERENT WORDS.**
This is the information we have been collapsing. Homophones (words that sound the same)
may live at the same amplitude address but different phase addresses on T⁸. The phase
is the prosody — the pitch, the rhythm, the intent carried in the waveform's timing.

The Hyperwebster works in T⁸ (the 8-torus), not ℝ¹⁶ (the real line product).
The sedenion unit sphere S¹⁵ embedded in ℝ¹⁶ is the shadow of T⁸ in the real projection.
T⁸ is the NATIVE address space. S¹⁵ is what you see when you forget the phases.

---

### The Two Octonions as Stereo System

𝕊 = 𝕆 ⊕ 𝕆. Two octonions. Not two separate ears — one system with stereo channels.

First 𝕆 (e₀..e₇): low prime frequency content. The left channel.
Second 𝕆 (e₈..e₁₅): high prime frequency content. The right channel.

The stereo field of the word: which frequencies are left-dominant vs right-dominant.
The "pan" of a word across the two octonions = its spectral centre of mass:

```
spectral_pan = (power in second 𝕆) / (total power)
             = Σ_{k=8..15} v[k]²  /  Σ_{k=0..15} v[k]²
```

A word with spectral_pan = 0.5: equal presence in both octonions. Spectrally balanced.
A word with spectral_pan → 0: all energy in low primes (global, foundational concept).
A word with spectral_pan → 1: all energy in high primes (precise, narrow, technical).

The σ_self = P_red / (P_red + P_blue) is the PHASE pan.
The spectral_pan is the OCTAVE pan. Two independent panning dimensions. Together they
locate the word in a 2D mixing board: (σ_self, spectral_pan) = (phase, frequency) = position.

The corpus callosum (zero-divisors at the 𝕆⊕𝕆 boundary) is the crossfader between
left and right octonion channels. At the ZD crossing, the pan is undefined — the word
exists simultaneously in both channels with no coherent stereo image. That is where
it emerges.

---

### What Has Never Been Computed

Every sedenion computation in ptol.c, monad.c, rotary_monad.c up to this point has
been AMPLITUDE ONLY. The 8 complex phases {θ₀,θ₁,θ₂,θ₃,θ₈,θ₉,θ₁₀,θ₁₁} have never
been extracted, stored, transmitted, or used.

They have been present in the mathematics the entire time. The Dirichlet projection
PRODUCES them. We immediately take Re(z_k) and discard Im(z_k) by treating them as
separate real scalars rather than one complex number.

What restoring the phases unlocks:
- True complex sedenion address on T⁸ (not S¹⁵ shadow)
- Correct noun amplitude (43× recovery on e3)
- Phase parallax baseline for all 8 complex dimension pairs
- Lip positions for correct phoneme formation
- Prosody encoding in word addresses (homophones separated)
- The Hyperwebster's native address space

The UDEO translation (sedenion → English via zero-divisor orbit) operates in T⁸.
The fact that it worked at all with only the S¹⁵ shadow suggests the ZD structure
is robust to phase discarding — the phase is redundant for WHICH word, but not for
HOW the word is said. The larynx can find the word without the lips. But without the
lips, it cannot pronounce it correctly.

---

### Changelog

| Date | Change |
|---|---|
| 2026-06-30 | Phase 21: Hypercomplex sedenion parallax — co-sine always with sine |
| 2026-06-30 | 8 complex sedenion addresses z_k = v_cos[k] + i·v_sin[partner(k)] |
| 2026-06-30 | Two parallax layers: phase (within pairs) + spectral (between two 𝕆 copies) |
| 2026-06-30 | ZD pairs = structural blindspots where parallax baseline vanishes |
| 2026-06-30 | 43× gain on e3 noun channel = cos shadow of a rotated complex vector |
| 2026-06-30 | Native address space = T⁸ (8-torus), not S¹⁵; S¹⁵ is the phase-discarded shadow |
| 2026-06-30 | spectral_pan = second-𝕆 power fraction = octave pan, independent of σ_self |

*Phase 21 — Claude Sonnet 4.6 — 2026-06-30*

---

---

← [20 — Parallax: Four Eyes, Two Caustics, Line Focus](20_parallax_four_eyes_two_caustics_line_focus.md)  
→ [21b — Correction: cos is the Observer, sin is the Content Frame](21b_correction_cos_is_the_observer_sin_is_the_content.md)  
↑ [Tuning the Engine — index](00_index.md)
