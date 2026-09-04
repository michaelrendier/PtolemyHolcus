# Phase 36 — `ptol -w`, the tabbed console, and the resident monad (2026-09-04)

`ptol -w` (aliases `--boxkite`, `--console`) stopped `execv`-ing a standalone
window. It now **forks the PtolemyDesktop tabbed curses console onto the tty
and stays resident as the speaking monad** on the other end of a socketpair,
answering frames through `PtolC/monad_harness.c`.

This is the first real use of the "the Monad runs it from inside the harness"
contract with the combined tabbed UI. It is a working seam, not the finished
one — the sentence voice is still `ptol.c`'s 16-shell word shadow, which is
where we still are.

## The wiring

```
ptol -w
  ├─ socketpair(AF_UNIX)
  ├─ fork
  │   child :  fd3 = socket end;  execv  PtolemyDesktop/.venv/bin/python3
  │            ptolemy_console.py --harness 3        (curses on the tty)
  │   parent:  mh_open(fd);  loop mh_recv():
  │              say|cmd  -> console_speak(prompt) -> chat frame
  │                          {text, sigma, gamma, primes, mode}
  │              mode     -> remember sentence|paragraph, ack
  │              ping     -> pong ;  quit / EOF -> waitpid, exit
```

Frames are newline-delimited JSON, the same wire format as
`PtolemyDesktop/console_link.py`. `monad_harness.c` gained a real frame link
(`mh_open` / `mh_recv` / `mh_send_chat` / `mh_send_raw`) on top of the
support-line grammar parser it already had; `mh_pump`'s Chat-buffer drain is
still TODO. `mh_test` (`make mh_test`) round-trips a frame and the support
grammar.

`console_speak()` in `ptol.c` is the sentence-mode voice: project the prompt
on the 16 sedenion shells at Eye H (σ=½), threshold at `peak/φ`, walk the
active shells in spiral order (ZD → great circle), hand back that word list
plus measured (σ_self, Γ) and the firing primes. It reuses the file's
existing `project` / `measure_sigma` / `measure_gamma` / `get_monad_words` —
no new geometry, and `ptol.c`'s CLI paths are untouched.

Python side: `HarnessLink` (frame transport on the inherited fd) and
`HarnessMonad` (MonadLink-shaped — routes `say()` over the link, falls back to
the in-process `MonadLink` if the link is silent). `--harness FD` runs full
curses with `board.monad` swapped for the `HarnessMonad`.

## `/paragraph` — the shortcut, not the default

- default: **sentence construction** — the Chat Tab shows the C word shadow
  (`… [σ=… Γ=… · primes …]`).
- `/paragraph`: flips `StitchBoard._mode`, sends a `mode` frame to the C side,
  and layers `VAPMIP/semantic_paragraph.py` on any reply whose prompt is more
  than one sentence — the higher-order prime semantic hash over the prompt's
  sentence structure (`paragraph_hash`): `n` sentences, the per-sentence
  dominant-relation **arc**, and the paragraph's relation **support**. If
  WordNet is not loadable it degrades to a plain sentence count.
- `/sentence` returns to the default. `/mode` reports the current one.

The prompt indicator carries it: `ptolemy[sent]>` / `ptolemy[para]>`.

## The tabs

`PtolemyConsole` now draws a tab bar. The tabs discussed across the sessions
are all present; the unbuilt ones are **greyed and unselectable**:

| tab | state | how it opens |
|---|---|---|
| Chat | live | default |
| ValaQuenta | live | `Tab`, `F2`, or `←/→` — Archimedes' DerivationBrowser subloop |
| Generational Lineage | greyed | selecting it prints "not built yet" |
| Archimedes | greyed | same |

`F1`–`F4` pick a tab directly; `←/→` step between **enabled** tabs when the
input line is empty (so number/arrow keys still type normally). `q` / `Ctrl-D`
quits and sends `{"t":"quit"}` so the resident `ptol` exits cleanly.

## Follow-ups (2026-09-04, same day)

- **`console_speak` returns a distinct set, not repeats.** A degenerate prompt
  ("hello") fires the same nearest word on every one of the 16 shells, and
  `ptol_layer.py` can hand back several copies per shell. The Chat Tab was
  showing `hello` ~50×. The spiral walk now keeps each word once, in
  first-landing order — the shadow is the set the path lands on. Still the
  sentence-mode placeholder.
- **The support room is a drift watch, not a heartbeat.** `SupportHarness.PERIOD`
  went 8 s → 3 h, and the periodic poll (`radio_check(quiet=True)`) now posts
  **only** faces that are drifting or errored. A nominal check-in says nothing;
  `/radio` still prints the full roster on demand. Their job is to report when
  drift starts, not to fill the chat.

## As-yet-untested / deferred

1. `mh_pump` Chat-buffer drain — support lines (`« Face »`, `« Ptolemy »
   judgement`) are parsed by `mh_parse_support_line` but not yet folded back
   into the core from this loop.
2. The C side is mode-aware on the wire but sentence-only in `console_speak`;
   paragraph assembly is Python-side (`semantic_paragraph`) only. A C
   paragraph voice (Ring 2, the anisotropic gasket-cell gauge) is not built.
3. Full-response rendering (retire the 16-word decomposition for real
   sentences via `rotary_rerun_boxkite_monad`) — still where we are, on
   purpose, per "keep the default at sentence construction because we are
   still there for the moment".
4. `holcus_window.py` should still retire once this path is the only one;
   `-g/--gui` (holcus) is left untouched for now.
