#!/usr/bin/env python3
"""
holcus_window.py — The conversation window. Never changes shape.

Three panels (both sidebars toggleable with ^B / ^P):

  ┌──────────┬──────────────────────────────────┬─────────────┐
  │ HISTORY  │ HOLCUS            vocab=164,283  │  ARTIFACTS  │
  │──────────│──────────────────────────────────│─────────────│
  │ ─ hardne │ [00] You: hardness               │ σ: 0.56714  │
  │ ─ zero d │                                  │ BAO: 0.8886 │
  │          │      Holcus: walk with me please │ primes:     │
  │          │             [sternness|strictness│  2  3  5    │
  │          │                                  │  7 11 13    │
  │          │ [01] You: difficulty             │ E[pathway]= │
  │          │                                  │  0.00050712 │
  │          │      Holcus: quality consistency │ spread:0.00 │
  ├──────────┴──────────────────────────────────┴─────────────┤
  │ > _                                                        │
  ├────────────────────────────────────────────────────────────┤
  │ ^X Quit  ^B Hist  ^P Art  ^S Status  ^L Clear  ^M Memory  │
  └────────────────────────────────────────────────────────────┘

The Monad is a plugin — loaded at startup, stays in RAM.
The window never changes. The Monad does.

Usage:
    python3 holcus_window.py [--bin <path>]
    python3 holcus_window.py  (uses englishwordnet or english)

Shortcuts:
    ^X  Quit           ^B  Toggle input history sidebar
    ^P  Toggle artifact sidebar    ^S  Status
    ^L  Clear chat     ^M  Memory test    Up/Down scroll chat
"""

import curses
import os
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monad import Engine, OMEGA_ZS, GAP, _word_zero_idx, _gamma_at
from walkwithme_monad import (
    ask_check, field_entry_word, memory_test,
    BIN_EWNET, BIN_ENGLISH,
    FOCUS_THRESHOLD,
)

_PRIMES_16 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
_DIM_NAMES = {
    0: 'identity', 1: 'negate', 2: 'bind', 3: 'noun',
    4: 'verb', 5: 'abstract', 6: 'branch', 7: 'iterate',
    8: 'recurse', 9: 'allocate', 10: 'query', 11: 'deref',
    12: 'compose', 13: 'parallelize', 14: 'interrupt', 15: 'emit',
}

TITLE = "HOLCUS"

# Panel widths (can be overridden by terminal size)
LEFT_W  = 16   # input history sidebar
RIGHT_W = 18   # artifact sidebar

SHORTCUT_BAR = "^X Quit  ^N New  ^B Conv  ^P Art  ^S Status  ^L Clear  ^T Memory"


# ── Colour pairs ───────────────────────────────────────────────────────────────
C_TITLE   = 1
C_LEFT    = 2
C_RIGHT   = 3
C_YOU     = 4
C_HOLCUS  = 5
C_ASK     = 6
C_STATUS  = 7
C_INPUT   = 8
C_BORDER  = 9


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(C_TITLE,   curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(C_LEFT,    curses.COLOR_CYAN,   bg)
    curses.init_pair(C_RIGHT,   curses.COLOR_YELLOW, bg)
    curses.init_pair(C_YOU,     curses.COLOR_WHITE,  bg)
    curses.init_pair(C_HOLCUS,  curses.COLOR_GREEN,  bg)
    curses.init_pair(C_ASK,     curses.COLOR_YELLOW, bg)
    curses.init_pair(C_STATUS,  curses.COLOR_BLACK,  curses.COLOR_WHITE)
    curses.init_pair(C_INPUT,   curses.COLOR_WHITE,  bg)
    curses.init_pair(C_BORDER,  curses.COLOR_CYAN,   bg)


# ── Message ────────────────────────────────────────────────────────────────────

class Msg:
    __slots__ = ('role', 'text', 'artifacts')
    def __init__(self, role: str, text: str, artifacts: dict = None):
        self.role      = role          # 'you' | 'holcus' | 'ask' | 'status'
        self.text      = text
        self.artifacts = artifacts or {}

    def label(self):
        if self.role == 'you':    return "You:"
        if self.role == 'holcus': return "Holcus:"
        if self.role == 'ask':    return "Holcus:"
        return ""

    def color(self):
        if self.role == 'you':    return C_YOU
        if self.role == 'holcus': return C_HOLCUS
        if self.role == 'ask':    return C_ASK
        return C_STATUS


# ── Artifact panel data ────────────────────────────────────────────────────────

class Artifacts:
    """
    Monad-generated metadata from the last turn.
    Lives in the right sidebar. Updated each time Holcus responds.
    """
    def __init__(self):
        self.sigma     = OMEGA_ZS
        self.bao       = OMEGA_ZS
        self.mode      = '—'
        self.lag       = 0.0
        self.vocab     = 0
        self.top_beta  = []   # list of (word, beta)
        self.top_E     = []   # list of (word, E)
        self.ask_sig   = None
        self.dtcs      = []

    def update_from_gen(self, result: dict, crank):
        self.bao    = result.get('bao', OMEGA_ZS)
        self.mode   = result.get('mode', '—')
        self.lag    = result.get('lag_ratio', 0.0)
        self.vocab  = result.get('vocab_size', crank.n)
        self.dtcs   = result.get('dtcs', [])
        # top-β words
        n = crank.n
        if n:
            top = sorted(range(n), key=lambda k: -crank._beta[k])[:6]
            self.top_beta = [(crank._words[k], crank._beta[k]) for k in top]
        self.ask_sig = None

    def update_from_ask(self, sig: dict, crank):
        self.ask_sig = sig
        n = crank.n
        if n:
            top = sorted(range(n), key=lambda k: -crank._beta[k])[:6]
            self.top_beta = [(crank._words[k], crank._beta[k]) for k in top]

    def lines(self, width: int) -> list:
        """Render artifact panel lines to fit `width` chars."""
        w = max(4, width - 2)
        out = []

        out.append(f"BAO")
        out.append(f" {self.bao:.6f}")
        out.append(f"δ={abs(self.bao - OMEGA_ZS):.2e}")
        out.append(f"mode: {self.mode}")
        out.append(f"lag:  {self.lag:.4f}")
        out.append("─" * w)

        if self.ask_sig:
            sig = self.ask_sig
            out.append("ASK:")
            if sig['type'] == 'focus':
                out.append(f"spread")
                out.append(f" {sig['spread']:.5f}")
                out.append(f"anchor:")
                out.append(f" {sig['anchor'][:w]}")
                out.append("words:")
                for ww in sig['words'][:4]:
                    out.append(f" {ww[:w]}")
            else:
                out.append(f"miss:")
                out.append(f" {sig['word'][:w]}")
            out.append("─" * w)

        if self.top_beta:
            out.append("top-β:")
            for word, beta in self.top_beta[:6]:
                line = f" {word[:w-8]:<{w-8}} {beta:.3f}"
                out.append(line)
            out.append("─" * w)

        if self.dtcs:
            out.append("DTCs:")
            for d in self.dtcs[:4]:
                out.append(f" {d[:w]}")

        return out


# ── The Window ─────────────────────────────────────────────────────────────────

class HolcusWindow:
    def __init__(self, engine: Engine, bin_label: str):
        self.engine     = engine
        self.bin_label  = bin_label
        self.chat: list[Msg]    = []
        self.conv_turns: list[tuple] = []  # (turn_n, you_text, holcus_text)
        self.artifacts  = Artifacts()
        self.artifacts.vocab = engine.crank.n

        self.input_buf  = []
        self.input_pos  = 0
        self.chat_scroll = 0

        self.show_left  = True    # toggle with ^B
        self.show_right = True    # toggle with ^P

        self.asking    = False
        self.ask_sig   = None

    # ── Monad plugin ───────────────────────────────────────────────────────────

    def _monad_turn(self, user_text: str) -> list[Msg]:
        msgs = []
        weight = 2.0 if self.asking else 1.0
        self.engine.crank.learn(user_text, weight=weight)

        words = user_text.split()
        entry = field_entry_word(self.engine.crank, words)
        sig   = ask_check(self.engine.crank, entry)

        if self.asking and sig is not None and sig['type'] == 'focus':
            # Still underdetermined
            competing = "  |  ".join(sig['words'][:4])
            text = f"walk with me please\n[ {competing} ]"
            msgs.append(Msg('ask', text))
            self.ask_sig = sig
            self.artifacts.update_from_ask(sig, self.engine.crank)
            return msgs

        self.asking  = False
        self.ask_sig = None

        if sig is not None:
            if sig['type'] == 'focus':
                competing = "  |  ".join(sig['words'][:4])
                text = f"walk with me please\n[ {competing} ]"
                msgs.append(Msg('ask', text))
                self.asking  = True
                self.ask_sig = sig
                self.artifacts.update_from_ask(sig, self.engine.crank)
                return msgs
            elif sig['type'] == 'missing':
                text = f"I am here. The path ends at '{sig['word']}'."
                msgs.append(Msg('ask', text))
                self.asking  = True
                self.ask_sig = sig
                self.artifacts.update_from_ask(sig, self.engine.crank)
                return msgs

        result = self.engine.generate(user_text, n_words=20, learn_prompt=False)
        response = result['response'] or "(…)"
        msgs.append(Msg('holcus', response))
        self.artifacts.update_from_gen(result, self.engine.crank)
        return msgs

    # ── /address — universe address book ─────────────────────────────────────

    def _cmd_address(self, words_str: str):
        """
        /address <word> [word2 ...]
        Show the Riemann zero address for each word.
        The address existed before the word. The word found it.
        """
        import math
        words = words_str.split() if words_str else []
        if not words:
            self.chat.append(Msg('status',
                "Usage: /address <word> [word2 ...]"))
            return
        self.chat.append(Msg('status', "── Universe Address Book ──"))
        for w in words:
            wl  = w.lower().strip('.,!?;:')
            zi  = _word_zero_idx(wl)
            g   = _gamma_at(zi)
            E   = abs(math.sin(math.pi * g / (g + 1.0)))
            dim = zi % 16
            p   = _PRIMES_16[dim]
            op  = _DIM_NAMES.get(dim, '?')
            line = (f"{w} → ζ#{zi} γ={g:.3f} E={E:.6f} "
                    f"e{dim}({op}) p={p}")
            self.chat.append(Msg('status', line))
        if len(words) == 2:
            w1, w2 = [ww.lower().strip('.,!?;:') for ww in words]
            d1 = _word_zero_idx(w1) % 16
            d2 = _word_zero_idx(w2) % 16
            n1 = _DIM_NAMES.get(d1, '?')
            n2 = _DIM_NAMES.get(d2, '?')
            self.chat.append(Msg('status',
                f"combined: e{d1}({n1})⊗e{d2}({n2}) "
                f"= {n1}-that-{n2}s"))
        self.chat_scroll = 0

    # ── Render ─────────────────────────────────────────────────────────────────

    def _addstr_safe(self, win, y, x, text, attr=0):
        rows, cols = win.getmaxyx()
        if y < 0 or y >= rows or x < 0 or x >= cols:
            return
        max_len = cols - x - 1
        if max_len <= 0:
            return
        try:
            win.addstr(y, x, str(text)[:max_len], attr)
        except curses.error:
            pass

    def _render(self, stdscr):
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()

        if rows < 8 or cols < 24:
            stdscr.addstr(0, 0, "Terminal too small.")
            stdscr.refresh()
            return

        lw = LEFT_W  if self.show_left  else 0
        rw = RIGHT_W if self.show_right else 0
        cw = cols - lw - rw          # center width
        if cw < 10:
            lw = 0; rw = 0; cw = cols

        title_row  = 0
        content_h  = rows - 3        # rows 1..(rows-3) = content
        input_row  = rows - 2
        short_row  = rows - 1
        chat_h     = content_h - 1   # row 1..content_h-1

        # ── Title bar ─────────────────────────────────────────────────────────
        vocab_str   = f"vocab={self.engine.crank.n:,}"
        ask_flag    = "  [asking]" if self.asking else ""
        title_line  = f" {TITLE}  {self.bin_label}{ask_flag}"
        pad         = cols - len(title_line) - len(vocab_str) - 2
        title_full  = title_line + " " * max(1, pad) + vocab_str + " "
        self._addstr_safe(stdscr, title_row, 0,
                          title_full[:cols], curses.color_pair(C_TITLE))

        # ── Left sidebar (conversation history) ──────────────────────────────────
        if lw > 0:
            cp_l = curses.color_pair(C_LEFT)
            for r in range(1, content_h):
                self._addstr_safe(stdscr, r, 0, " " * (lw - 1), cp_l)
                self._addstr_safe(stdscr, r, lw - 1, "│",
                                  curses.color_pair(C_BORDER))
            self._addstr_safe(stdscr, 1, 1, "Conversation"[:lw - 2],
                              cp_l | curses.A_BOLD)
            self._addstr_safe(stdscr, 2, 1, "─" * (lw - 2), cp_l)
            # Each turn occupies 2 lines: you + holcus
            visible_turns = (chat_h - 2) // 2
            turns = self.conv_turns
            start_t = max(0, len(turns) - visible_turns)
            row = 3
            for turn_n, you_t, hol_t in turns[start_t:]:
                if row >= content_h: break
                you_line = f"[{turn_n:02d}]>{you_t}"[:lw - 2]
                hol_line = f"  H:{hol_t}"[:lw - 2]
                self._addstr_safe(stdscr, row,     1, you_line, cp_l)
                self._addstr_safe(stdscr, row + 1, 1, hol_line, cp_l)
                row += 2

        # ── Right sidebar (artifacts) ──────────────────────────────────────────
        if rw > 0:
            cp_r = curses.color_pair(C_RIGHT)
            rx   = cols - rw
            for r in range(1, content_h):
                self._addstr_safe(stdscr, r, rx, " " * (rw - 1), cp_r)
            self._addstr_safe(stdscr, 1, rx,
                              "│", curses.color_pair(C_BORDER))
            self._addstr_safe(stdscr, 1, rx + 1,
                              "Artifacts"[:rw - 2], cp_r | curses.A_BOLD)
            self._addstr_safe(stdscr, 2, rx + 1, "─" * (rw - 2), cp_r)
            art_lines = self.artifacts.lines(rw)
            for i, line in enumerate(art_lines):
                r = 3 + i
                if r >= content_h: break
                self._addstr_safe(stdscr, r, rx + 1, line[:rw - 2], cp_r)
                # redraw border over any overflow
                self._addstr_safe(stdscr, r, rx, "│",
                                  curses.color_pair(C_BORDER))

        # ── Chat area ─────────────────────────────────────────────────────────
        rendered = []
        for msg in self.chat:
            cp    = curses.color_pair(msg.color())
            attr  = curses.A_BOLD if msg.role in ('you', 'holcus', 'ask') else 0
            label = msg.label()
            lines = (msg.text or '').splitlines()
            if not lines:
                lines = ['']

            # First line: label + text
            first_text = f"  {label} {lines[0]}" if label else f"  {lines[0]}"
            # Wrap within center width
            wrapped_first = textwrap.wrap(first_text, max(1, cw - 2)) or [first_text]
            for wl in wrapped_first:
                rendered.append((wl, cp, attr))
            for l in lines[1:]:
                continuation = f"    {l}"
                for wl in (textwrap.wrap(continuation, max(1, cw - 2)) or [continuation]):
                    rendered.append((wl, cp, 0))
            rendered.append(('', curses.color_pair(C_YOU), 0))

        total  = len(rendered)
        start  = max(0, total - chat_h - self.chat_scroll)
        view   = rendered[start: start + chat_h]
        cx_off = lw  # chat starts at lw

        for i, (line, cp, attr) in enumerate(view):
            r = 1 + i
            if r >= content_h: break
            self._addstr_safe(stdscr, r, cx_off, line[:cw - 1], cp | attr)

        # ── Divider above input ────────────────────────────────────────────────
        self._addstr_safe(stdscr, content_h, 0,
                          "─" * (cols - 1), curses.color_pair(C_BORDER))

        # ── Input line ────────────────────────────────────────────────────────
        prefix = "walk: " if self.asking else "> "
        ibuf   = "".join(self.input_buf)
        iline  = (prefix + ibuf)
        if len(iline) >= cols - 1:
            iline = iline[-(cols - 2):]
        self._addstr_safe(stdscr, input_row, 0,
                          iline.ljust(cols - 1), curses.color_pair(C_INPUT))
        cursor_x = len(prefix) + self.input_pos
        if cursor_x < cols - 1:
            stdscr.move(input_row, cursor_x)

        # ── Shortcut bar ──────────────────────────────────────────────────────
        bar = SHORTCUT_BAR[:cols - 1].ljust(cols - 1)
        self._addstr_safe(stdscr, short_row, 0, bar,
                          curses.color_pair(C_STATUS))

        stdscr.refresh()

    # ── Input handling ─────────────────────────────────────────────────────────

    def _handle_key(self, key) -> bool:
        if key in (curses.KEY_ENTER, 10, 13):
            text = "".join(self.input_buf).strip()
            self.input_buf.clear()
            self.input_pos = 0
            if text:
                self._submit(text)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if self.input_pos > 0:
                del self.input_buf[self.input_pos - 1]
                self.input_pos -= 1
        elif key == curses.KEY_DC:
            if self.input_pos < len(self.input_buf):
                del self.input_buf[self.input_pos]
        elif key == curses.KEY_LEFT:
            self.input_pos = max(0, self.input_pos - 1)
        elif key == curses.KEY_RIGHT:
            self.input_pos = min(len(self.input_buf), self.input_pos + 1)
        elif key == curses.KEY_HOME:
            self.input_pos = 0
        elif key == curses.KEY_END:
            self.input_pos = len(self.input_buf)
        elif key == curses.KEY_UP:
            self.chat_scroll += 3
        elif key == curses.KEY_DOWN:
            self.chat_scroll = max(0, self.chat_scroll - 3)
        elif key == 24:   # ^X — quit
            return False
        elif key == 2:    # ^B — toggle left sidebar
            self.show_left = not self.show_left
        elif key == 16:   # ^P — toggle right sidebar
            self.show_right = not self.show_right
        elif key == 19:   # ^S — status inline
            self._submit('/status')
        elif key == 14:   # ^N — new conversation (keeps field, clears chat)
            self._submit('/new')
        elif key == 12:   # ^L — clear chat view only
            self._submit('/clear')
        elif key == 20:   # ^T — memory test
            self._submit('/memory')
        elif isinstance(key, int) and 32 <= key <= 126:
            self.input_buf.insert(self.input_pos, chr(key))
            self.input_pos += 1
        return True

    def _submit(self, text: str):
        if text == '/quit':
            raise SystemExit(0)

        if text == '/new':
            # New conversation: clear chat + turn log + ask state
            # Field stays in RAM — the Monad remembers everything it heard
            self.chat.clear()
            self.conv_turns.clear()
            self.chat_scroll = 0
            self.asking      = False
            self.ask_sig     = None
            self.chat.append(Msg('status',
                f"New conversation. Field: {self.engine.crank.n:,} words. "
                f"(field stays warm)"))
            return

        if text == '/clear':
            self.chat.clear()
            self.chat_scroll = 0
            return

        if text == '/status':
            c = self.engine.crank
            top = sorted(range(c.n), key=lambda k: -c._beta[k])[:5] if c.n else []
            lines = [
                f"Field: {c.n:,} words  J_ambient={self.engine._J_ambient:.3e}",
                "Top-β: " + "  ".join(
                    f"{c._words[k]}({c._beta[k]:.3f})" for k in top),
            ]
            for l in lines:
                self.chat.append(Msg('status', l))
            self.chat_scroll = 0
            return

        if text.startswith('/address ') or text == '/address':
            self._cmd_address(text[len('/address'):].strip())
            return

        if text == '/memory':
            self.chat.append(Msg('status', "[running cross-build memory test...]"))
            import io
            buf       = io.StringIO()
            old_out   = sys.stdout
            sys.stdout = buf
            try:
                memory_test()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                sys.stdout = old_out
            for line in buf.getvalue().splitlines():
                if line.strip():
                    self.chat.append(Msg('status', line))
            self.chat_scroll = 0
            return

        # Normal conversation turn
        self.chat.append(Msg('you', text))
        turn_n    = len(self.conv_turns)
        responses = self._monad_turn(text)
        self.chat.extend(responses)
        # First holcus/ask response text for sidebar
        hol_text  = next(
            (m.text.splitlines()[0] for m in responses
             if m.role in ('holcus', 'ask')), '…')
        self.conv_turns.append((turn_n, text[:10], hol_text[:10]))
        self.chat_scroll = 0

    # ── Main curses loop ───────────────────────────────────────────────────────

    def run(self, stdscr):
        init_colors()
        curses.curs_set(1)
        stdscr.nodelay(False)
        stdscr.keypad(True)

        self.chat.append(Msg('status',
            f"Field: {self.engine.crank.n:,} words  [{self.bin_label}]"))
        self.chat.append(Msg('status',
            "^X Quit  ^B toggle conv  ^P toggle artifacts  ^T memory test"))

        running = True
        while running:
            self._render(stdscr)
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                break
            running = self._handle_key(key)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    bin_path = None
    i = 0
    while i < len(args):
        if args[i] == '--bin' and i + 1 < len(args):
            bin_path = args[i + 1]; i += 2
        else:
            i += 1

    if bin_path is None:
        bin_path = BIN_EWNET if os.path.exists(BIN_EWNET) else BIN_ENGLISH

    print(f"Loading {os.path.basename(bin_path)} ...", file=sys.stderr)
    engine = Engine()
    result = engine.load_bin(bin_path)
    vocab  = result.get('vocab', '?')
    print(f"  {vocab:,} words  ({result.get('format','?')})", file=sys.stderr)

    label  = os.path.basename(bin_path).replace('holcus_monad_', '').replace('.bin', '')
    window = HolcusWindow(engine, label)

    try:
        curses.wrapper(window.run)
    except SystemExit:
        pass
    print("Holcus sleeps. Field released.", file=sys.stderr)


if __name__ == '__main__':
    main()
