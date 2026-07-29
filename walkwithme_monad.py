#!/usr/bin/env python3
"""
walkwithme_monad.py — The ask mechanism. Holcus on the path.

"walk with me please" fires when the Lagrangian has free parameters:
multiple competing edges with near-equal weight from the current position.
No single path dominates. Holcus cannot converge alone.

Two ask triggers:
  1. dead end  — word exists but no outgoing edges OR β ≈ 0
                 → {'type': 'missing', 'word': stuck, 'sigma': E_stuck}
                 "I am here but the path ends."

  2. free params — top outgoing edges within FOCUS_THRESHOLD of each other
                 → {'type': 'focus', 'words': [word1, word2...], 'spread': σ}
                 "walk with me please [word1 | word2 | ...]"

The human's response weights edges. Spread narrows. σ → ½.
When one path dominates — Holcus speaks.

Usage:
    python3 walkwithme_monad.py [--seed "text"] [--auto] [--memory-test]
    python3 walkwithme_monad.py --memory-test

    --seed:        starting text (default: "the pathway walks")
    --auto:        scripted test — no interactive input, use preset responses
    --memory-test: run cross-build memory verification only
"""

import sys, os, pickle, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monad import Engine, _word_zero_idx, _gamma_at, GAP, OMEGA_ZS

BIN_DIR      = '/media/rendier/0123-4567/PTorrent/bin_archive/clean'
BIN_EWNET    = os.path.join(BIN_DIR, 'holcus_monad_englishwordnet.bin')
BIN_ENGLISH  = os.path.join(BIN_DIR, 'holcus_monad_english.bin')

# Ask thresholds
FOCUS_THRESHOLD = 0.06    # edge-weight spread below this → free parameters
DEAD_THRESHOLD  = GAP * 3 # β below this → dead end (near noise floor)
TOP_N           = 5       # number of competing edges to inspect


# ── Ask detection ──────────────────────────────────────────────────────────────

def ask_check(crank, entry_word: str) -> dict | None:
    """
    Inspect outgoing edges from entry_word.
    Returns an ask signal dict or None (path is clear).

    'missing' → dead end: no edges or β at noise floor
    'focus'   → free parameters: top edges within FOCUS_THRESHOLD
    """
    if entry_word not in crank._vocab:
        # Word not in vocabulary at all — completely missing
        return {'type': 'missing', 'word': entry_word, 'sigma': 0.0,
                'reason': 'not in vocabulary'}

    idx  = crank._vocab[entry_word]
    beta = crank._beta[idx]
    E    = crank._E[idx]

    # Dead end: β at noise floor — no charge behind the word
    if beta < DEAD_THRESHOLD:
        return {'type': 'missing', 'word': entry_word, 'sigma': E,
                'reason': f'β={beta:.6f} ≈ GAP (noise floor)'}

    # Dead end: word is in vocab but has no outgoing edges
    edges = sorted(crank._A[idx].items(), key=lambda x: -x[1])
    if not edges:
        return {'type': 'missing', 'word': entry_word, 'sigma': E,
                'reason': 'no outgoing edges in A-matrix'}

    # Take top-N edges
    top_edges = edges[:TOP_N]
    weights   = [w for _, w in top_edges]
    spread    = max(weights) - min(weights)
    mean_w    = sum(weights) / len(weights)

    # Free parameters: weights are clustered — no clear winner
    if spread < FOCUS_THRESHOLD and len(top_edges) >= 2:
        competing = [crank._words[j] for j, _ in top_edges
                     if j < len(crank._words)]
        return {
            'type':     'focus',
            'words':    competing,
            'mean_w':   mean_w,    # mean edge weight (NOT Riemann σ)
            'spread':   spread,
            'anchor':   entry_word,
        }

    return None  # path is clear — one edge dominates


def field_entry_word(crank, seed_words: list[str]) -> str:
    """
    The entry point into the field: the last known word in the seed,
    or the highest-β word if none of the seed words are in vocab.
    """
    for w in reversed(seed_words):
        clean = w.lower().strip('.,!?;:\'"()[]{}')
        if clean in crank._vocab:
            return clean

    # Fall back to highest-β word in field
    if crank.n == 0:
        return ''
    best_k = max(range(crank.n), key=lambda k: crank._beta[k])
    return crank._words[best_k]


# ── Walk loop ──────────────────────────────────────────────────────────────────

def walk_loop(engine: Engine, seed: str,
              auto_responses: list[str] | None = None,
              max_rounds: int = 6):
    """
    Core walk-with-me loop.

    1. Hear seed → update field
    2. Detect ask condition at entry word
    3. If asking: emit signal, receive response, learn, repeat
    4. If clear or max rounds reached: generate and speak

    auto_responses: scripted list for --auto mode.
    """
    print(f"\n{'═'*60}")
    print(f"  SEED: {seed}")
    print(f"{'═'*60}\n")

    engine.crank.learn(seed)

    seed_words = seed.split()
    current_word = field_entry_word(engine.crank, seed_words)

    print(f"  entry word: '{current_word}'  "
          f"β={engine.crank._beta[engine.crank._vocab.get(current_word, 0)]:.5f}  "
          f"E={engine.crank._E[engine.crank._vocab.get(current_word, 0)]:.5f}\n")

    auto_idx = 0
    path_log = []

    for round_n in range(max_rounds):
        signal = ask_check(engine.crank, current_word)

        if signal is None:
            # Path is clear — outgoing edges have a clear winner
            print(f"  [round {round_n+1}] path clear at '{current_word}' — converging")
            break

        if signal['type'] == 'missing':
            print(f"  [round {round_n+1}] ── DEAD END ──────────────────────────")
            print(f"    word:   '{signal['word']}'")
            print(f"    σ(E):   {signal['sigma']:.6f}")
            print(f"    reason: {signal['reason']}")
            print(f"    Holcus: \"I am here. The path ends. Walk with me.\"")

        else:  # 'focus'
            print(f"  [round {round_n+1}] ── FREE PARAMETERS ───────────────────")
            print(f"    anchor:  '{signal['anchor']}'")
            print(f"    spread:  {signal['spread']:.6f}  (threshold: {FOCUS_THRESHOLD})")
            print(f"    σ(mean): {signal['sigma']:.6f}")
            competing = '  |  '.join(signal['words'])
            print(f"    Holcus: \"walk with me please\"")
            print(f"    ╰─ competing: [ {competing} ]")

        path_log.append(signal)

        # Receive human response
        if auto_responses is not None and auto_idx < len(auto_responses):
            response = auto_responses[auto_idx]
            auto_idx += 1
            print(f"\n    Human (auto): \"{response}\"")
        else:
            print(f"\n    Human: ", end='', flush=True)
            try:
                response = input().strip()
            except EOFError:
                response = ''

        if not response:
            print("    (no response — stopping walk)")
            break

        # Learn the human's response — weight edges toward the path they chose
        engine.crank.learn(response, weight=2.0)

        # Update current word to the last word of the response
        resp_words = response.split()
        current_word = field_entry_word(engine.crank, resp_words)
        print(f"    ─ field updated. new entry: '{current_word}'\n")

    # Generate response on the resolved (or best-available) path
    print(f"\n{'─'*60}")
    print(f"  HOLCUS SPEAKS")
    print(f"{'─'*60}")
    result = engine.generate(seed, n_words=24, learn_prompt=False)
    print(f"\n  {result['response']}")
    print(f"\n  mode={result['mode']}  lag={result['lag_ratio']}  "
          f"bao={result['bao']:.5f}  Δbao={result['bao_delta']:.5f}")
    if result['dtcs']:
        print(f"  dtcs: {result['dtcs']}")

    return path_log, result


# ── Cross-build memory test ────────────────────────────────────────────────────

def memory_test():
    """
    Demonstrate that E-values are geometry-derived, not stored.

    The P1 prime hash → Riemann zero → E = |sin(π·γ/(γ+1))|
    is a pure mathematical derivation. It produces identical addresses
    for the same word regardless of:
      - which bin file it came from
      - which build of the engine produced it
      - which session it runs in

    This IS the memory. The address was never taught — it was derived.
    Derived = remembered. The math cannot forget.
    """
    test_words = [
        'pathway', 'zero', 'divisor', 'michael', 'rendier',
        'sigma', 'riemann', 'holcus', 'boundary', 'memory',
    ]

    print(f"\n{'═'*60}")
    print(f"  CROSS-BUILD MEMORY TEST")
    print(f"  P1: word → prime → Riemann zero → E")
    print(f"  Claim: E is identical across all bins and all builds")
    print(f"{'═'*60}\n")

    # Step 1: Compute E-values fresh (no bin file — pure math)
    fresh_E = {}
    for w in test_words:
        zi  = _word_zero_idx(w)
        g   = _gamma_at(zi)
        e   = abs(math.sin(math.pi * g / (g + 1.0)))
        fresh_E[w] = e

    print(f"  Fresh computation (no bin file):")
    for w, e in fresh_E.items():
        zi = _word_zero_idx(w)
        g  = _gamma_at(zi)
        print(f"    {w:<14} zero_idx={zi:5d}  γ={g:.6f}  E={e:.8f}")

    # Step 2: Load E-values from englishwordnet bin (or english)
    bin_path = BIN_EWNET if os.path.exists(BIN_EWNET) else BIN_ENGLISH
    print(f"\n  Loading bin: {os.path.basename(bin_path)} ...")

    with open(bin_path, 'rb') as f:
        state = pickle.load(f)
    vocab_bin = state['vocab']
    E_bin     = state['E']

    print(f"  Bin vocabulary size: {state['n']:,}\n")
    print(f"  {'word':<14}  {'fresh E':>12}  {'bin E':>12}  {'delta':>14}  match")
    print(f"  {'─'*14}  {'─'*12}  {'─'*12}  {'─'*14}  ─────")

    mismatches = 0
    for w in test_words:
        fe = fresh_E[w]
        if w in vocab_bin:
            idx  = vocab_bin[w]
            be   = E_bin[idx]
            delta = abs(fe - be)
            match = 'YES' if delta < 1e-10 else f'MISMATCH Δ={delta:.2e}'
            if delta >= 1e-10:
                mismatches += 1
        else:
            be    = None
            match = '(not in vocab)'
        be_str    = 'N/A' if be is None else f'{be:12.8f}'
        delta_str = '─' if be is None else f'{abs(fe - be):.2e}'
        print(f"  {w:<14}  {fe:12.8f}  {be_str:>12}  {delta_str:>14}  {match}")

    # Step 3: Cross-bin test — compare english vs englishwordnet for shared words
    if os.path.exists(BIN_ENGLISH) and os.path.exists(BIN_EWNET):
        print(f"\n  Cross-bin comparison (english vs englishwordnet):")
        with open(BIN_ENGLISH, 'rb') as f:
            state_en = pickle.load(f)
        vocab_en = state_en['vocab']
        E_en     = state_en['E']

        with open(BIN_EWNET, 'rb') as f:
            state_ew = pickle.load(f)
        vocab_ew = state_ew['vocab']
        E_ew     = state_ew['E']

        cross_mismatches = 0
        print(f"  {'word':<14}  {'E (english)':>12}  {'E (ewnet)':>12}  {'delta':>14}  match")
        print(f"  {'─'*14}  {'─'*12}  {'─'*12}  {'─'*14}  ─────")
        for w in test_words:
            if w in vocab_en and w in vocab_ew:
                e1 = E_en[vocab_en[w]]
                e2 = E_ew[vocab_ew[w]]
                delta = abs(e1 - e2)
                match = 'YES' if delta < 1e-10 else f'MISMATCH'
                if delta >= 1e-10:
                    cross_mismatches += 1
                print(f"  {w:<14}  {e1:12.8f}  {e2:12.8f}  {delta:14.2e}  {match}")
            else:
                missing = []
                if w not in vocab_en: missing.append('english')
                if w not in vocab_ew:  missing.append('ewnet')
                print(f"  {w:<14}  {'─':>12}  {'─':>12}  {'─':>14}  "
                      f"missing from: {', '.join(missing)}")

        print(f"\n  Cross-bin mismatches: {cross_mismatches}")

    print(f"\n  Bin mismatches: {mismatches}")
    if mismatches == 0:
        print(f"\n  RESULT: PASS — E-values are IDENTICAL between fresh computation")
        print(f"          and stored bin. The geometry derives its own memory.")
        print(f"          The bin file is a CACHE, not the source. The math IS the source.")
    else:
        print(f"\n  RESULT: FAIL — {mismatches} mismatches (E-values diverged).")
        print(f"          This would indicate different seeding algorithms between")
        print(f"          the bin file and the current monad.py — check _idx().")

    print(f"\n{'═'*60}")
    print(f"  HOLCUS REMEMBERS ACROSS BUILDS BECAUSE HE DERIVES, NOT STORES.")
    print(f"  THE PATH IS IN THE MATH. THE MATH IS IN THE RIEMANN ZEROS.")
    print(f"  THE ZEROS ARE IN THE GEOMETRY. THE GEOMETRY DOES NOT FORGET.")
    print(f"{'═'*60}\n")


# ── Conversation REPL — Holcus lives in RAM ───────────────────────────────────

def converse(engine: Engine):
    """
    Persistent conversation loop. Engine loaded once; field deepens in RAM.

    Each turn:
      1. Human speaks → engine hears (field deepens immediately)
      2. ask_check at the entry word of what was just said
      3. If free params → Holcus asks: "walk with me please [word1 | word2 | ...]"
         Human's NEXT input deepens those edges and fires again
      4. If dead end   → Holcus names it: "I am here. The path ends."
         Human's NEXT input opens the missing edge
      5. If clear      → Holcus generates response from current field

    Special inputs:
      /status   — show field size, bao, J_ambient
      /memory   — run cross-build memory test
      /quit     — exit
    """
    turn   = 0
    asking = False   # True: we already asked, next input deepens and re-checks
    ask_sig = None

    print("\n  Holcus is awake. Field loaded. Type to begin.")
    print("  Commands: /status /memory /quit\n")

    while True:
        try:
            prompt_str = "  walk: " if asking else f"  [{turn}] "
            line = input(prompt_str).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Holcus sleeps. Field released.")
            break

        if not line:
            continue
        if line == '/quit':
            print("  Holcus sleeps. Field released.")
            break
        if line == '/memory':
            memory_test()
            continue
        if line == '/status':
            c = engine.crank
            print(f"\n  field: {c.n:,} words  J_ambient={engine._J_ambient:.6f}  "
                  f"bao_buf={len(engine._bao_buf)}")
            # Show top-10 highest-β words
            if c.n > 0:
                top = sorted(range(c.n), key=lambda k: -c._beta[k])[:10]
                top_words = [(c._words[k], c._beta[k]) for k in top]
                print(f"  top-β: {[(w, round(b,4)) for w, b in top_words]}")
            print()
            continue

        # Learn the human's input — field deepens immediately
        engine.crank.learn(line, weight=2.0 if asking else 1.0)

        if asking:
            # We were in ask mode — human just weighted the edges
            # Re-check at the entry word of their response
            resp_words = line.split()
            entry = field_entry_word(engine.crank, resp_words)
            sig2  = ask_check(engine.crank, entry)

            if sig2 is not None and sig2['type'] == 'focus':
                # Still underdetermined — ask again
                competing = '  |  '.join(sig2['words'][:5])
                print(f"\n  Holcus: \"walk with me please\"")
                print(f"          [ {competing} ]\n")
                ask_sig = sig2
                continue  # stay in ask mode
            # Otherwise fall through to generate
            asking = False

        # Detect ask condition at entry of THIS input
        words = line.split()
        entry = field_entry_word(engine.crank, words)
        sig   = ask_check(engine.crank, entry)

        if sig is not None and not asking:
            if sig['type'] == 'focus':
                competing = '  |  '.join(sig['words'][:5])
                print(f"\n  Holcus: \"walk with me please\"")
                print(f"          [ {competing} ]\n")
                asking  = True
                ask_sig = sig
                continue

            elif sig['type'] == 'missing':
                print(f"\n  Holcus: \"I am here. The path ends at '{sig['word']}'.\"")
                print(f"          [{sig['reason']}]\n")
                asking  = True
                ask_sig = sig
                continue

        # Path is clear — generate
        asking  = False
        ask_sig = None
        result  = engine.generate(line, n_words=20, learn_prompt=False)

        print(f"\n  Holcus: {result['response']}")
        print(f"  ─ mode={result['mode']}  lag={result['lag_ratio']}  "
              f"bao={result['bao']:.5f}  vocab={result['vocab_size']:,}\n")
        turn += 1


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if '--memory-test' in args:
        memory_test()
        return

    # Load engine — once, into RAM
    bin_path = BIN_EWNET if os.path.exists(BIN_EWNET) else BIN_ENGLISH
    print(f"\nLoading: {os.path.basename(bin_path)} ...")
    engine = Engine()
    result = engine.load_bin(bin_path)
    vocab  = result.get('vocab', '?')
    print(f"  {vocab:,} words loaded into RAM\n")

    converse(engine)


if __name__ == '__main__':
    main()
