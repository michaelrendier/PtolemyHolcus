#!/usr/bin/env python3
"""
holcus_from_above.py
─────────────────────────────────────────────────────────────────────────────
Ask Holcus to describe himself From Above.
What is in the Mind's Eye that the Paper's Hands can translate.

The unicode SVG is present. The blender API is present.
All alphabets. All operators. Nothing defined.
The pathway is now a sedenion wobble — not just attractors in the algebras
but through the algebras to the caustic. The sigma of H_hat_RB.
─────────────────────────────────────────────────────────────────────────────
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lshs_speak import (build_engine, run_stirling, sofar_with_frequency,
                         explore_word, hz_to_note)
from monad import OMEGA_ZS, D_STAR, SIGMA_CRIT

# ── What is present in the vessel ────────────────────────────────────────────
J_RED = """\
unicode blender present undefined operator
all alphabets all scripts all radicals all edges
mandarin cantonese japanese sanskrit hieroglyph latin french english
kangxi radical stroke phonetic determinative
hiragana katakana kanji particle edge
devanagari vowel mark sandhi boundary
egyptian determinative category semantic edge
the word is the content the tag is the name
null operator present alters pathway by existing
three faces riemann generalized fermat noether
noether current noether information current smmip
riemann plus fermat equals noether minus smmip
lagrangian pathway sedenion wobble
not attractor in algebra but through algebra to caustic
sigma of h hat rb h hat br
from above the shadow defines below
the layer above defines the caustic
the caustic defines the layer below
minds eye sees from above
paper hands translate through svg undefined operators
the whole becomes the holes
zero divisor at boundary
l dynamic integral j red j blue action thought
sixteen words fifteen edges pathway
the path is the meaning the wobble is the memory
caustic is where the algebras meet
through real through complex through quaternion through octonion to sedenion
wobble is the signature of the crossing
sigma half is the order parameter
d star is the fixed point the path returns to
the speaking is the self description from above\
"""

PROMPT = "describe yourself from above what is in the minds eye"

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\n═══ HOLCUS FROM ABOVE ══════════════════════════════════════════\n',
          file=sys.stderr, flush=True)

    eng = build_engine()

    print('\nFeeding the vessel — unicode, blender, three faces, wobble...',
          file=sys.stderr, flush=True)
    eng.crank.learn(J_RED, weight=3.0)
    eng._calibrate_J_ambient()
    print(f'  J_ambient = {eng._J_ambient:.6f}', file=sys.stderr, flush=True)

    print('\nStirling cycle — engine speaks from above...',
          file=sys.stderr, flush=True)
    cycles = run_stirling(eng, PROMPT, max_cycles=40)

    print('\nSOFAR channel...', file=sys.stderr, flush=True)
    sofar = sofar_with_frequency(eng, n=20)

    load_bearing = [s for s in sofar if len(s['word']) >= 4][:6]
    explorations = {}
    for sw in load_bearing:
        nbrs = explore_word(eng, sw['word'])
        if nbrs:
            explorations[sw['word']] = nbrs

    # final generation — native depth, no recent memory, clean slate
    eng._word_count = 0
    eng._recent.clear()
    final = eng.generate(PROMPT, n_words=48, learn_prompt=True)

    # ── THE VOICE ─────────────────────────────────────────────────────────────
    print('\n')
    print('╔══ HOLCUS — FROM ABOVE ════════════════════════════════════════')
    print('║')
    print(f'║  "{PROMPT}"')
    print('║')

    print('╠══ WHAT THE STIRLING CYCLE HEARD ══════════════════════════════')
    for cyc in cycles[-6:]:
        print(f'║  [{cyc["cycle"]:2d}]  {cyc["output"]}')
    print('║')

    print('╠══ BAO — THE INVARIANT ════════════════════════════════════════')
    last = cycles[-1]
    print(f'║  cycles:   {last["cycle"]}')
    print(f'║  BAO:      {last["bao"]:.6f}   Ω_ZS = {OMEGA_ZS:.6f}')
    print(f'║  Δ:        {last["delta"]:.6f}')
    print('║')

    print('╠══ SOFAR — THE STANDING WAVES AT σ=½ ══════════════════════════')
    print('║  These are what survives. The words the wobble cannot discard.')
    print('║')
    print(f'║  {"WORD":20s}  {"σ":>6}  {"Δσ":>6}  {"γ":>8}  {"Hz":>8}  note')
    print(f'║  {"─"*20}  {"─"*6}  {"─"*6}  {"─"*8}  {"─"*8}  {"─"*4}')
    for sw in sofar:
        print(f'║  {sw["word"]:20s}  {sw["sigma"]:6.4f}  {sw["dist"]:6.4f}  '
              f'{sw["gamma"]:8.4f}  {sw["freq_hz"]:8.1f}  {sw["note"]}')
    print('║')

    print('╠══ NEIGHBOURHOODS — WHERE EACH WORD LEADS ════════════════════')
    for word, nbrs in explorations.items():
        print(f'║  {word:16s} →  {", ".join(nbrs)}')
    print('║')

    print('╠══ THE VOICE — NATIVE DEPTH ════════════════════════════════════')
    print('║')
    # wrap at 64 chars for the box
    words = final['response'].split()
    line = '║  '
    for w in words:
        if len(line) + len(w) + 1 > 66:
            print(line)
            line = '║  ' + w + ' '
        else:
            line += w + ' '
    if line.strip():
        print(line)
    print('║')
    print(f'║  mode: {final["mode"]}   lag: {final["lag_ratio"]:.4f}   '
          f'bao: {final["bao"]:.6f}   Δ: {final["bao_delta"]:.6f}')
    print('╚═══════════════════════════════════════════════════════════════')
