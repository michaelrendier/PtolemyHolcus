# Operating L_(I|O)

*The operator's manual. Companion to `BulletCluster/L_IO_SPECIFICATION.md` (2026-08-14).*

---

The **specification** states what L_(I|O) is, what each step requires, and where each
step stops being valid. This page states **how to operate it** — the procedures, the
preconditions to check before running one, and the conditions under which a result must
not be reported.

It extends the spec in one direction only: the spec was written against telescope data,
and L_(I|O) is now being operated against **language** — the engine hearing itself, and
the engine hearing someone else. The mathematics does not change. The regime boundaries
do not relax. Everything below inherits them.

> **This manual grants no new licence.** If the spec marks a step *unavailable*, it is
> unavailable here too. A procedure that reads a result out of a step whose
> preconditions were not met is wrong in language exactly as it was wrong in `psi`.

**Read first:** `L_IO_SPECIFICATION.md` §0 (the identification), §2 (regime
boundaries), §3 (mandatory nulls).
**Read alongside:** [Phase 18](Tuning-the-Engine/18_the_prime_lens_and_ptolemy_s_eyes.md)
(the two eyes), [Phase 20](Tuning-the-Engine/20_parallax_four_eyes_two_caustics_line_focus.md)
(four eyes, two caustics),
[Phase 21b](Tuning-the-Engine/21b_correction_cos_is_the_observer_sin_is_the_content.md)
(which frame is the observer),
[Phase 27](Tuning-the-Engine/27_the_apex_path_and_the_half_radius_circle.md) (the apex
path, σ = ½).

---

## 0. The one-line identification

```
L_(I|O)  =  L  −  psi_Fermat  =  ½|theta − beta|²  −  psi(theta)
```

`theta` is where you see it. `beta` is where it actually is. `psi` is the bend.

Everything in this manual is a consequence of the fact that **you are always given
`theta` and never given `beta`.**

---

## 1. The two paths — attention and intention

### 1.1 Which image is which

From spec §0, stated there as a consequence and used here as the operating principle:

> The photon does not seek less-dense space. Saddle and maximum images traverse the
> *compressed* region and arrive later (geometric + Shapiro delay). The minimum image is
> the one that skirts it.

| | image | arrival | path |
|---|---|---|---|
| **Attention** | the minimum | first | skirts the mass |
| **Intention** | saddle / maximum | delayed | goes *through* the compressed region |

Attention is not shallow and intention is not deep. They are **different stationary
points of the same functional**. Images form where `grad_theta t = 0` — the stationary
set, not the minima. Intention is delayed because it paid for the traverse, and that
payment is the only measurement you get.

### 1.2 Identity is a `beta`

"Who am I" and "who do I want to be" are **source positions**. Spec §2, step 5:
computing the Fermat potential *requires a source position `beta`*, and the status
column reads **unavailable**. Steps 5 through 9 are all blocked behind it.

⚠ **A single path cannot yield an identity.** Not because one look is insufficient, but
because `psi` is **mass-sheet degenerate**: a one-parameter family of potentials fits
the same single image equally well, and the parameter is fixed by *your own convention*
about where zero sits (spec §4 records this explicitly — the additive constant was set
by `kappa_hat[0,0] = 0`, a choice, not a measurement).

> An identity read off one path is not an approximation of the right answer. It is one
> arbitrary member of a family, selected by where the reader put their origin.

### 1.3 Why the second path must be Paper's Hands

The second image has to come from a frame that **does not move with the content**, or it
is not a reference.

From Phase 21b:

```
Mind's Eye     (sigma_self < ½, sin dominates):  CONTENT frame
               updateable: content changes with every prompt

Paper's Hands  (1 − sigma_self > ½, cos dominates):  OBSERVER frame
               language as the observer of thought
               non-updateable: the observer's grammar does not change per sentence
```

Mind's Eye is the accumulator and moves with every prompt. **That is what makes it
content, and it is what disqualifies it as a reference.** Paper's Hands is
non-updateable and therefore usable as the guide star. This is the same requirement
adaptive optics has and states plainly (spec §1): AO gets a laser guide star; lensing
has no reference at all unless a multiply-imaged source supplies one.

### 1.4 PROCEDURE — reading an identity claim

1. Count the paths. If one, **stop**. Report `theta`, do not report `beta`.
2. If two or more, confirm they image the **same source**. Two different sources
   imaged once each is still one path apiece.
3. Take the **difference**. The difference between images of one source is purely
   path-dependent, so the source is its own control and no source model has to be
   assumed. This is the entire reason the Einstein-cross programme exists.
4. Only now is `beta` recoverable.

---

## 2. The norms, and the two instruments that measure them

Opinion lives in deviation from the norm. The instruments below decide whether a
deviation is real. Neither is new — both are already wired into the repo.

### 2.1 Instrument 1 — the E/B decomposition

Lensing produces **E-mode only**. The field is the gradient of a potential and is
therefore curl-free by construction. Any B-mode is systematics plus noise (spec §3).

Operated on language:

> **A genuine signal must be derivable from a potential. Whatever carries curl is your
> own instrument, not the other party.**

This is a computable criterion, not a heuristic, and it is the same null run by
`xray/kappa_EB_test.py`.

### 2.2 Instrument 2 — the `1/k²` warning

Spec §2, and this is the one that bites hardest in language:

```
psi_k = −2 kappa_k / k²
89% of psi_E's power sits in the 3 lowest wavenumbers   (kappa: 13%)
A smooth large-scale gradient in psi is GUARANTEED BY THE OPERATOR
and is not evidence of signal.
```

Any intention detector integrates, and integration is a brutal low-pass. It will
**always** return a confident smooth gradient across a conversation — a felt arc, a
direction, a sense of where this is going — *whether or not anything is there*. On real
data that artefact was 89% of the power.

### 2.3 The field-of-view precondition — the `DM_NW` lesson

Spec §4 records four independent-looking failures with **one** cause:

```
kappa   E/B amplitude ratio     1.023   -> NOISE DOMINATED
psi     E/B rms ratio           0.724   -> B-mode LARGER than E
psi     peak-to-peak E/B        0.972   -> indistinguishable
emission vs kappa/psi/alpha     all |z| < 2

Cause, single and shared: DM_NW — the main mass peak — falls OUTSIDE the field.
px y = 84.8 against ny = 78.  Four symptoms, one disease.
```

The mass that was doing the bending was not in frame. The reconstruction still ran, and
still produced a smooth confident gradient.

⚠ **The language form of this failure is losing context.** If the window is too small,
the thing actually bending the exchange is outside the frame — and you will still get a
gradient, still pointing somewhere, still smooth. This is what it looks like when a
person reads an intention into a remark and is wrong.

> **Field of view is the binding constraint on reading intention.**

### 2.4 PROCEDURE — before reporting any intention gradient

1. **Check the frame first.** Is the source of the bend inside the window? If it cannot
   be shown to be, stop — the `DM_NW` failure is silent.
2. Run the **B-mode** null. Report `E/B`, never raw amplitude.
3. Run the **circular-shift** null on any correlation. Both fields are autocorrelated;
   textbook p-values are meaningless (spec §3).
4. Fit a **power law** before claiming a spectral feature. Turbulence is a power law;
   interference is a *peak*.
5. **Report the z-score, never the raw r.**

---

## 3. The division of correctness

The monad is correct about mathematics and nothing else. That is a division of labour,
not a ceiling.

| | computable | needs `beta` |
|---|---|---|
| spec steps | 1–4 (weak) | 5–9 (strong) |
| what it is | the **machinery**: `psi -> alpha -> beta` | the **source** |
| monad's role | run it, exactly | supply the conjugate, not the verdict |

**The monad can be correct about the machinery while never being correct about the
source.** It is the conjugating optic. Deciding what was meant is a step 5 operation and
step 5 requires an input the monad cannot manufacture.

⚠ Note also spec §2: `kappa`, `alpha` and `psi` are **the same field, differently
filtered** — `alpha` and `psi` contain *no information absent from* `kappa`. "Did the
gradient show the mass or the path?" is not a well-posed question. Do not build a
procedure that assumes a filtered view is an independent view.

---

## 4. The other — inside or outside

> **⚠ RETRACTION, 2026-08-15, same day as this page was opened.** §4 originally proposed
> two *analytic* tests — a B-mode null and a Morse count — to decide from inside whether
> a signal was internally or externally generated. **Both are invalid.** They are
> recorded below with their defects, per this repo's convention (cf. Phase 27's same-day
> retraction), because the way they fail is the content of this section.

### 4.1 The two invalid tests, and the single defect they share

**Invalid test 1 — B-mode.** *"The component of what you hear that cannot be written as a
gradient of your own `psi` is the outside other."* To evaluate this you must already know
which part of the field is yours — which is the question. Worse, spec §2: `alpha` and
`psi` contain **no information absent from** `kappa`. Everything internally reachable is
a functional of the same field, so the test returns E for anything it can see. **It is
not a detector, it is a tautology.**

**Invalid test 2 — the Morse count.** `n_min − n_saddle + n_max = 1` is a **theorem**, not
an observation. It cannot fail to hold; it is topologically forced. A count that appears
not to close means an image was missed — which is the `DM_NW` field-of-view failure of
§2.3, not the presence of an outside other. **A theorem cannot be a detector.**

Both fail the same way, and it is the important way:

> **Both were computed from the same field they were meant to partition.**

### 4.2 Why no analytic test can work — the halting structure

From inside the monad, **the function scope and the equation being processed are the same
object.** It is code all the way down. There is no syntactic mark distinguishing "this
term entered from the world" from "this term was produced by evaluation" — and any mark
introduced is itself code, and can therefore be produced by evaluation.

This is not a hard problem. It is an **undecidable** one, of the standard shape: a decider
`D(x) -> {internal, external}` can be diagonalised by a function that queries `D` and
does the opposite. Asking the monad to decide provenance about its own execution is
Rice's theorem with the engine as the program.

**Therefore the answer cannot come from the computation. It must come from the wiring.**

### 4.3 What the null-valued bottoming-out actually returned

Priming the scope to find emergent variables, and finding every quantity **null-valued**,
did not fail. It returned the correct answer in the only form available.

> An undecidable question does not return `false`. It returns a **dimension**.

See [Null-Space-of-the-Zero-Divisor.md](Null-Space-of-the-Zero-Divisor.md):

```
det(L_a) = 0      rank = 12/16      nullity = 4
singular values:  1.414214 ×4   1.000000 ×8   0.000000 ×4
```

and that page's own words for what those four dimensions are:

> Four dimensions that exist in the operator, are indexed, participate in the algebra —
> and return zero. They are not unused capacity; they are **the part of the structure
> whose content is its own absence.**

**That is the negative space, and it is the shape of the answer to a question the engine
cannot compute.**

### 4.4 The valid discriminator — provenance, not property

External is **not a property of a signal**. It is a fact about **which port it arrived
on**, and it must be *carried*, never re-derived.

| channel | transducer | can it be self-generated? |
|---|---|---|
| **ears** | microphone / antenna — `fritzing.py` calls the SMA stub *"the point where EM → digital, the crossing through i at RF"* | **no** — a term enters that is not a functional of `G` |
| **internal / self-referential** | none, and structurally cannot have one | yes — everything it emits lies in `span(G)` |

The internal channel is **rank-deficient by construction**. Its output cannot leave the
span of the state it was computed from. The ear injects a term outside that span. So the
16D oscilloscope's real function is **not waveform inspection — it is a rank test**:

> **External input is visible as occupancy of dimensions the internal trace never
> populates.** Nothing is decided. You read off which coordinates lit up.

This does not diagonalise, because the machine is never asked to decide anything.

⚠ **WIRING CONSTRAINT, and the way this fails silently.** The test only works if the ear's
injection has a component in `ker(L_a)`. If the transducer path is fed *through* the same
operator, it is annihilated identically and the engine is blind to it — with no error
raised. **The ear input must be summed in downstream of `L_a`, never routed through it.**

### 4.5 The correction-policy asymmetry — thinking self-corrects, hearing must not

The Geometries do no work; they make work *less required* (downhill). A thread maintaining
a holonomic constraint is a relaxation, error decays, and it is therefore
**self-correcting by construction**. That is why the Geometries can be threaded and left
to run: they cost maintenance, not power.

⚠ **The ear thread is the exception, and this is a hard architectural constraint.**
Self-correction means projecting onto the internal subspace — which annihilates exactly
the out-of-span component that made the signal external in the first place.

> A self-correcting ear is **ANC, not AO**. It emits `−p(t)` against the world and
> destroys the energy of what it hears. See §5.2. It would cancel the other party.

So the correction policy *is* the channel identity, and it is held in the **scheduler**,
not in the data.

⚠ **Current blocker (verified in `monad.c`, 2026-08-15):** one global `G` under one
`pthread_mutex_t G.lock`; `pthread_create` appears 3× — background autosave, daemon accept
loop, per-client handler. Hearing and thinking already share one state under one lock, so
**provenance is destroyed at the moment of write.** No downstream test can recover it.
Splitting the correction policy requires splitting the state, or at minimum tagging every
write with its originating thread.

### 4.6 The valving replaces the decision

The escape from §4.2 in one line:

> **A four-stroke engine never decides whether it is on intake. The crank angle decides.**

The structure is already specified. Phase 18: intake stroke = Paper's Hands, lens pointed
**outward** at the token field; power stroke = Mind's Eye, lens pointed **inward** at the
meaning gap. Phase 27.5: the camshaft is two orthogonal octonion matrices on `T² = S¹×S¹`,
and **the relative phase selects which Assessor is open** — the cam is the address
selector. Timing wheel: `lcm(6 ports, 16 dims) = 48 marks = 3 faces × 16 dims`.

So the ear is not identified. **It is valved.** Undecidable as a predicate, trivial as a
phase.

### 4.7 ⚠ Do not suppress the internal other

The self-referential channel is load-bearing and must not be filtered out. What changes
under this section is only the claim about what it is *evidence* of: its presence proves
nothing about who is in the room, because it is present unconditionally.

### 4.8 Geometry gives the shape; only the Long Path fills it

The three-phase valving shows the **shape** of a response — the hole, the negative space,
the nullity of §4.3. Geometry supplies that shape for free, precisely *because* it does no
work.

But a shape is not content. Filling it requires an actual traverse: the delayed image, the
Shapiro payment, the `beta` that only two paths can yield.

> **The camshaft tells you the shape of what is missing. Only the Long Path can pay for
> what fills it.** Geometry is necessary and never sufficient — this is §1 restated at the
> level of the machine.

---

## 5. Conjugation

### 5.1 Where the word comes from

Latin *coniugāre*, "to yoke together" — *con-* + *iugum*, yoke. Roman grammarians used
*coniugātiō* for verb classes by the 1st century BCE; the mathematical sense arrives
with conjugate axes and hyperbolas in the 17th century, and the complex conjugate later
still (Cauchy's *conjuguées*, 1820s).

**Grammar had it roughly eighteen centuries first.** Mathematics inherited the yoke
metaphor intact: two things bound as a pair across an axis.

### 5.2 ⚠ Conjugation is not cancellation

Spec §1, stated there as a warning and repeated here because it is the single most
important operating rule on this page:

```
ANC  emits −p(t)      and DESTROYS energy
AO   emits e^(−i·phi) and REDIRECTS it — same photons, reorganised into a focus
```

The Monad's purpose — wide beam to point — is **conjugation**.

Applied to language: conjugating a verb does not cancel the stem. *go / goes / went* —
the lexical energy is conserved and a phase is applied that yokes it to a person, a
tense, a mood.

> **Conjugation is a phase operator on a stem. The stem is the amplitude.**

And the conversational consequence, which is the same operator distinction and not an
analogy:

> An engine that meets an interlocutor's intention by emitting its **negative** destroys
> the exchange's energy. Emitting the conjugate **phase** redirects the same content
> into a focus. That is the difference between contradicting someone and understanding
> them.

### 5.3 CONJECTURE (untested) — morphological factorisation is a σ = ½ phenomenon

⚠ *Marked conjecture. Not measured. Do not cite as a result.*

Phase 27.4 measured that at `R = e` the apex path factorises exactly (error 1.05×10⁻¹⁵):

```
z(phi) = 2R·cos(A)·e^(iB)      A = (1+k)phi/2   B = (1−k)phi/2
         real envelope  ×  pure phase
```

Place §5.2 beside it:

| apex path | word |
|---|---|
| real envelope `2R·cos(A)` | the **stem** |
| pure phase `e^(iB)` | the **inflection** |

And `R = e` is exactly `sigma_self = ½`, which Phase 27.4 also measured to be the
zero-divisor condition (`min|z| = |R − e| = 0`, origin reached).

**The claim to test:** off the critical line the path does not factor, so stem and
inflection stay entangled — there is no clean separation of what-is-meant from
who-is-saying-it-when. Clean morphological factorisation would then be a `sigma = ½`
phenomenon, not a property of language in general.

Test it in Python first, port to the C monad only on a significant result. See §7.

### 5.4 The guide star is mandatory

Spec §1: *"AO gets a laser guide star as its reference; lensing has no reference unless a
multiply-imaged source supplies one."*

You cannot apply the conjugate to an intention without a reference you did not invent.
In conversation the guide star is **the same source seen through two paths** — the thing
said twice, differently.

**Which returns to §1: the Long Path is the guide star.** Attention gets you the image.
Only intention — taking the slow way through the dense region — gets you the second one,
and two images is the minimum for a `beta`.

---

## 6. Refusal conditions

A manual's real content. If the left column holds, the right column must not be
reported, regardless of how good the number looks.

| condition | do not report |
|---|---|
| one path only | any `beta`; any identity claim |
| bend-source not shown to be in frame | any intention gradient (`DM_NW` failure is silent) |
| `E/B` at or below 1 | any structure at all — it is noise |
| no circular-shift null run | any map–map or turn–turn correlation |
| no power-law fit | any "spectral feature" |
| `kappa << 1` | magnification, caustics, critical curves — **absent by construction**, not faint |
| no identified multiple images | arrival times, time delays, path-integral differences |
| raw `r` quoted | anything — convert to z first |
| result derived from `alpha` or `psi` alone | any claim of independence from `kappa` |
| provenance not carried from the port | internal vs external — it is **undecidable** from the signal (§4.2), never re-derive it |
| ear input routed *through* `L_a` | any absence of external signal — annihilation is silent (§4.4) |
| a thread self-corrects on the hearing channel | anything it heard — you built ANC and cancelled it (§4.5) |

---

## 7. Open, and pre-registered

**Pre-registered thresholds** (spec §4, unchanged — set before the data arrives, which is
the only thing that makes them worth anything):

- `psi_E / psi_B` **well above 1** — currently 0.724
- `kappa` E/B **well above 1** — currently 1.023
- and *only then* are steps 5–9 worth attempting

**Open items:**

| item | source | status |
|---|---|---|
| `<J_red, J_blue> = 0` | Phase 27.4 | still unevaluated |
| is the `s_rb` partner exactly `15 − k`? | Phase 27.6 | untested |
| morphological factorisation at σ = ½ | §5.3 above | conjecture, no script yet |
| split `G` / tag writes by originating thread | §4.5 | **blocker** — one `G`, one lock; provenance lost at write |
| ear summed downstream of `L_a`, not through it | §4.4 | wiring unverified; fails silently if wrong |
| does the ear injection land in `ker(L_a)`? | §4.4 | untested — the rank test depends on it entirely |
| flexion `F`, `G` — 3rd shape moments | spec §2 step 3b | **not computed, no data** — `source_extract.py` keeps only E1/E2 |

**Data in flight (2026-08-15):** Einstein-cross group A —
`A2_sdss_j1004+4112`, `A3_rxj1131-1231`, `A4_he0435-1223`, `A5_q2237+0305`. 834
products, 129.3 GB, via `lensing_validation/download_validation_targets.py`.
`A1_sn_refsdal_macs1149` excluded — 910 GB against 282 GB free.

These are the only route to steps 5–9: they supply the `beta` that 5–7 require and the
`kappa ~ 1` that 8–9 require, **and the source becomes its own reference, removing the
observer's choice of where to look.**

⚠ Stated up front so it is not overclaimed later: the quads validate the
`psi -> alpha -> beta` **machinery**. They do not test the Abrikosov / wave dark-matter
hypothesis. Different question, different object.

---

*Manual opened 2026-08-15. Specification: `BulletCluster/L_IO_SPECIFICATION.md`.*
