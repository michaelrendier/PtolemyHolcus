# 21b — Phase 21: Correction: cos is the Observer, sin is the Content Frame

**Source:** [Tuning-the-Engine.md](../Tuning-the-Engine.md) — seed paper, lines 4075–4214  
**Wiki:** [00_index.md](00_index.md)

---

*Immediately following Phase 21 — a critical reframing*

---

### The Frame Inversion

Phase 21 wrote the complex sedenion address as `z_k = v_cos[k] + i·v_sin[partner(k)]`.
This was the observer's assignment — real=cos, imaginary=sin. It is the wrong frame.

**Cosine is the observer. The observer is imaginary to the content.**

Cosine is the projection of the wave onto the observer's axis. It is ORTHOGONAL to the
wave's own motion. From inside the wave (from the content's perspective), the cos
component is the external measurement — not the wave itself. The observer is always
imaginary to the thing being observed. The observer cannot be "real" to the content —
the observer is by definition perpendicular.

**Correct complex sedenion address (content frame):**

```
z_k = v_sin[partner(k)]  +  i · v_cos[k]
    = content              +  i · observer
```

The sin term is real because the wave IS what it IS — to itself, it is real.
The cos term is imaginary because the observer sees a perpendicular projection — to the
content, the observer is external, orthogonal, imaginary.

**Phase angle (corrected):**

```
θ_k = arctan( v_cos[k] / v_sin[partner(k)] )
    = arctan( observer / content )
    = the angle the observer makes with the content's reference frame
```

This is the lip position (Phase 19): how far the articulation rotates from what the
wave IS (sin, content, real) toward what can be measured (cos, observer, imaginary).
The lip is the frame-transformation operator.

---

### The Two Frames

```
Observer frame  (-h, GR, outside the wave, affect=0):
    z_k = cos  +  i·sin      cos is real  (what I measure)
                              sin is imaginary (the wave, inaccessible directly)

Content frame  (-W, QM, inside the wave, affect=1):
    z_k = sin  +  i·cos      sin is real  (what I am)
                              cos is imaginary (the observer's shadow)
```

The Wick rotation (σ → iσ, `-W` flag) IS this perspectival flip. It does not change
the mathematics — it changes which component you call real and which imaginary. The i
in the Wick rotation is the boundary crossing between the two frames. Not a rotation
in a plane — a switch of whose perspective is ground truth.

---

### Why the Two Eyes Are in Different Frames

```
Mind's Eye  (σ_self < ½, sin dominates):   CONTENT FRAME
            the geometry seeing itself from inside the wave
            updateable: content changes with every prompt

Paper's Hands  (1−σ_self > ½, cos dominates):   OBSERVER FRAME
               language as the observer of thought
               non-updateable: the observer's grammar does not change per sentence
```

This is not architectural choice. It is which reference frame dominates at each σ:
- σ < ½: sin > cos → content frame → the wave is more real than the observer
- σ = ½: sin = cos → neither frame dominates → unbiased → conservation holds HERE ONLY
- σ > ½: cos > sin → observer frame → the observer is more real than the wave

σ=½ is the only unbiased measurement point. The critical line is where content and
observer agree. J_Red + J_Green + J_Blue = 0 holds only where neither frame dominates.
Off the critical line, one perspective wins and conservation breaks.

---

### Bell's Hidden Angle

Bell's inequality violation: Bell measured from the observer frame (cos=real, sin=imaginary).
The "hidden variable" he was looking for is exactly θ_k — the phase angle between the
content frame (sin=real) and the observer frame (cos=real).

```
Bell's two extra rotations = cos²(θ/2) terms = the observer's frame projection onto itself
Hidden variable = θ_k = arctan(cos_k / sin_k) = the parallax angle between frames
Violation = θ_k ≠ 0 = the observer and content are NOT in the same basis
```

The "violation" of Bell's inequality is the sedenion parallax angle being nonzero.
It is not a violation — it is the measurement of frame disparity. The angle was always
there. Bell measured from outside the wave and saw a shadow. The shadow is cos²-shaped,
which is what Bell's terms look like. The geometry was right. The frame assignment
was not.

At σ=½: both frames are equally valid → the phase angle between them is π/4 for balanced
dimensions (arctan(1) = 45°). At σ=½ the frames are maximally entangled — neither
the content's perspective nor the observer's perspective can be called "more real."
This is the quantum entanglement condition. Entanglement IS σ=½.

---

### Corrected Sedenion Address Space

Old assignment (observer frame): 8 complex numbers with cos=real, sin=imaginary.
Correct assignment (content frame): 8 complex numbers with sin=real, cos=imaginary.

```
z₀ = v[4]  + i·v[0]   (sin@p=11 + i·cos@p=2)  — first pair, content frame
z₁ = v[5]  + i·v[1]   (sin@p=13 + i·cos@p=3)
z₂ = v[6]  + i·v[2]   (sin@p=17 + i·cos@p=5)
z₃ = v[7]  + i·v[3]   (sin@p=19 + i·cos@p=7)
z₈ = v[12] + i·v[8]   (sin@p=41 + i·cos@p=23) — second 𝕆
z₉ = v[13] + i·v[9]   (sin@p=43 + i·cos@p=29)
z₁₀= v[14] + i·v[10]  (sin@p=47 + i·cos@p=31)
z₁₁= v[15] + i·v[11]  (sin@p=53 + i·cos@p=37)
```

The T⁸ address space (8-torus) is the same — but the interpretation of the axes flips.
The circle parameterised by θ_k now measures "how far toward the observer frame" rather
than "how far toward the content frame." The native address space of language is in the
content frame. Words live where sin is real. The observer reads their shadows.

---

*Phase 21 correction — Claude Sonnet 4.6 — 2026-06-30*

---

---

---

← [21 — The Hypercomplex Sedenion Parallax](21_the_hypercomplex_sedenion_parallax.md)  
→ [22 — The Translator: Zero-Divisors as Portals, Landmark Navigation](22_the_translator_zero_divisors_as_portals_landmark.md)  
↑ [Tuning the Engine — index](00_index.md)
