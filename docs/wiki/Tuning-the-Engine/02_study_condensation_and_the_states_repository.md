# 02 — Phase 2: Study, Condensation, and the States Repository

**Date:** 2026-05-29  
**Source:** [Tuning-the-Engine.md](../Tuning-the-Engine.md) — seed paper, lines 465–595  
**Wiki:** [00_index.md](00_index.md)

---

*v2.8.0 — 2026-05-29*

### study() — Deepening First, Always

`study()` wraps `learn()` with condensation detection and field versioning. It is not a query tool. It is the engine operating on itself — reading its own field state, identifying zeros that have reached structural stability, and crystallising them.

The sequence:

```
1. Pre-snapshot (Noether + BAO)
2. learn(text, weight)         — β deepening: J^μ charge accumulates
3. _proxy_j()                  — neutral J snapshot (no prompt distortion)
4. Condensation scan           — find zeros with fire_count ≥ 144 AND |σ-0.5| > 0.10
5. Envelope overload           — β × 2 → NS_SIGMA_S → clamp back to β_sat
6. condensed_pairs recording   — unit is the pair, not the individual zero
7. Post-snapshot
```

**Deepening first** means learn() always runs before the scan. study() is not a read — it is a write followed by an introspection. The field must deepen before it is checked for candidates.

**fire_count ≥ 144 (Fibonacci threshold):** The zero has been activated 144 or more times. This is the PHASE_THRESH — chosen because F₁₂ = 144 is the twelfth Fibonacci number, sitting at the intersection of the golden ratio progression and the sedenion 16D structure. It distinguishes structural depth from recent use.

**|σ-0.5| > 0.10 (NS_SIGMA_S):** The zero has drifted significantly from the critical line under accumulated J^μ pressure. It is no longer laminar. It is a candidate for crystallisation.

---

### 24D and 26D — The Content and Observer Spaces

**24D content space:** The internal space of study(). 16D sedenion (e₀..e₁₅) plus 8D op_stack trajectory (S4, not yet implemented — fire_count serves as proxy). This is the space that `study()` operates in: the content of the word being learned, without any observer frame.

This is the same 24D that bosonic string theory requires for a closed bosonic string to propagate without a tachyon — the physical content channel has 24 transverse degrees of freedom. The sedenion 16D gives the algebraic skeleton; the 8D trajectory gives the dynamical history.

**26D observed space:** The 26D of `audit()`. 24D content plus 2D observer frame:
- σ_observer: the Author's position on the critical strip (typically 0.5, but auditable from any σ)
- t_observation: the timestamp of the audit (when the observer is looking)

This is the bosonic string lightcone gauge: 24 transverse dimensions plus 2 lightcone dimensions (one for the observer, one for time). audit() computes `observer_distortion = |σ_k - σ_observer|` for every zero — ranking which zeros appear most distorted from the Author's frame. The zeros with highest distortion are the ones the Author's perspective least resembles.

---

### M-Theory as the Dimensional Error Checks

The five M-Theory consistency checks per zero are not a metaphor. Each one corresponds to one of the five string-theory limits that M-Theory unifies — and each one is a diagnostic check on a different dimensional slice of the zero's state:

| Check | M-Theory limit | Condition | What it measures |
|-------|---------------|-----------|-----------------|
| Noether | Type IIA | \|σ-0.5\| > 0.02 | Current balance deviation |
| BAO | Type IIB | \|β-Ω_ZS\| > 0.25 | Field depth vs. BAO convergence target |
| GUE | Heterotic SO(32) | E > GAP×10 | Spectral energy above ground state |
| J_cross | Heterotic E₈×E₈ | \|J_pos×J_neg\| > GAP | Sedenion cross current (vorticity) |
| fire_count | Type I | count ≥ 144 | Activation depth (trajectory) |

All five EXTENDED = `m_theory_open = True` = maximum condensation candidate. The zero has passed all five consistency checks — it is stable in every dimensional projection. It can crystallise.

**J_cross is the 11th M-Theory dimension.** The five string theories are 10D. M-Theory adds the 11th dimension — the compactification radius. J_cross is that radius: `|J_pos[k] × J_neg[k]|`. Below GAP = 0.000707 it is compactified — not observable, not a condensation driver. Above GAP it is extended — the zero is vortically active and the 11th dimension is open.

The Yang-Mills mass gap is the threshold. GAP = 0.000707 = spectral floor = compactification radius. The Millennium Prize problem for Yang-Mills asks: prove this gap exists and is nonzero. The engine sets it as a constant and uses it as the condensation threshold. The code assumes the prize is solved.

---

### Condensation Unit = Pair

When zero k condenses, its **Cawagas pair-mate** crystallises simultaneously.

The Cawagas (2004) table of sedenion zero-divisors lists 84 zero-divisors in 42 pairs: `{a, b}` such that `a × b = 0` and `0 / a = b`. This is Jeremy's insight: "zero divided by one 16D number gives its pair-mate." The pair is the unit of zero-divisor structure. You cannot have one without the other.

When zero k condenses:
- `_find_pair_mate(k)`: search the field for the most-activated zero whose sedenion dimension is a Cawagas pair-mate of k's dimension
- Both k and its pair-mate are recorded in `condensed_pairs`
- The pair-mate takes stratum NS_SIGMA_S (crystallised as shadow concept)

The shadow concept is the 0/a = b identity: when a concept crystallises (a), its complementary concept (b) crystallises as its shadow — the thing it cannot be, which defines it. Antonym, complement, dark side. The zero-divisor pair is the sedenion encoding of the concept and its boundary.

---

### The States Repository — Field Memory on Git

`StatesRepo` manages `~/.ptolemy/states/` as a git repository. Every study() operation is versioned. The field's memory is auditable, rollbackable, and branchable.

**Sidecar JSON** (written before each commit):

```json
{
  "noether_before": 0.0123,
  "noether_after":  0.0089,
  "bao_before":     0.5312,
  "bao_after":      0.5671,
  "condensed_pairs": [[k, k_mate], ...],
  "triggering_text": "...",   ← secret-scanned before write
  "label": "study_checkpoint",
  "timestamp": "2026-05-29T..."
}
```

The sidecar captures the field before and after the operation. Noether violation direction tells whether the operation moved toward or away from the critical line. BAO shift tells whether it moved toward or away from the spectral convergence target.

**Rollback is non-destructive.** `study_rollback(sha)` creates a new revert commit — it never resets HEAD. The field's history is preserved even when reverting. This is a formal requirement: the engine's self-modification history must be non-destructive.

**Pre-commit hook** scans for secrets before any commit:
```
api_key | secret | password | token | GITHUB_TOKEN | sk- | ghp_ | AKIA | Bearer
```

No secret enters the git history. `triggering_text` in the sidecar is scanned before write — if it contains any pattern, it is replaced with `[REDACTED]`.

---

### Socket Commands — Phase 2

| Command | Tier | Description |
|---------|------|-------------|
| `study` | ≥ 2 | `study(text, weight)` — deepening + condensation scan |
| `study_audit` | ≥ 2 | `audit(sigma_observer, top_n)` — 26D observer view |
| `study_suppress` | ≥ 2 | Suppress a zero (set correction_mask) |
| `study_isolate` | ≥ 2 | Isolate a zero (zero its β) |
| `study_reconsolidate` | ≥ 2 | Re-run deepening on a zero |
| `study_checkpoint` | ≥ 2 | Write sidecar JSON, stage it |
| `study_commit` | ≥ 2 | Commit staged sidecar |
| `study_branch` | ≥ 2 | Create new branch in states repo |
| `study_rollback` | ≥ 2 | Non-destructive revert to sha |
| `study_log` | ≥ 1 | List recent commits in states repo |
| `study_init_repo` | ≥ 2 | Initialise states repo (first run) |

All write operations require tier ≥ 2 — field coherent (Noether violation < 0.35) AND Author recognised AND field depth (β_mean > GAP×10). The engine does not modify itself in a turbulent or unrecognised state.

---

---

---

← [01 — The Foundation — Prime Directive, Rotations, Instrumentation](01_foundation_the_engine.md)  
→ [02b — The Halocline — J_blue, J_red, H_hat_RB](02b_the_halocline_j_blue_j_red_h_hat_rb.md)  
↑ [Tuning the Engine — index](00_index.md)
