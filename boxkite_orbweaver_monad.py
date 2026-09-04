#!/usr/bin/env python3
"""boxkite_orbweaver_monad.py — the spider-web composition cycle, on top of
the rotary box-kite Monad.  UNTESTED — this file is the test bench.

Cody, 2026-09-03:

  One box-kite traversal = one SENTENCE = one RADIUS.  WordNet's job ends
  at the sentence (rings of box-kites = sentences).  ABOVE the sentence is
  a different organiser: the orb-weaver web-construction cycle.

    STRUCTURE   anchor -> bridge -> frame -> hub(= zero-divisor reframe)
                -> radii (one per section axis, one through-line each)
    SCAFFOLD    the centre->out spiral: the outline, `reach` loops deep,
                `reach` set by SCALE (paragraph / section / chapter)
    CAPTURE     the out->in spiral: the prose, one arc = one paragraph,
                each unit ending on the CONNECTIVE that names the next
                move on the web
    FRUSTRATION when context flow is turbulent (>= 3 near-equal relations)
                the spiral reverses along a strut — a `however` pivot + an
                aciniform recap, then jump radius; the return steps
                interdigitate the outbound steps

The heavy WordNet sentence layer (`rotary_rerun_boxkite_monad`) is loaded
lazily and only when `weave_via()` is used.  The default `weave()` path is
decoupled: it takes a light word list + a 19-slot relation vector (or
sniffs a crude one from the text) so the web cycle itself is fast to test.

Paragraph *construction* is meant to move into monad3_c.bin and paragraph
*usage* into the granular .bin files — that redesign happens AFTER this
test.  The connective lexicon and block frames live here for now, scoped
as a template layer, not a claimed NLG system.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from monad import cam_encode
from rotary_rerun_monad import (
    BoxKite, BoxKiteUnavailable, MindsEye, PapersHands,
    Ledger, Relation, Status, Fault,
)
from ptolemy_monad import infer_direction

# ── sentence templates — copied from rotary_rerun_boxkite_monad so this
#    file does not drag in its heavy import chain just to fill a frame. ───
_SENTENCE_TEMPLATES: Dict[str, str] = {
    "classify": "this is a kind of {0}.",
    "enumerate": "it includes {0}, {1}, and {2}.",
    "decompose": "it is made of {0} and {1}.",
    "situate": "it is part of {0}.",
    "characterize": "it is marked by {0}.",
    "explain": "it happens because of {0}.",
    "imply": "it leads to {0}.",
    "associate": "it relates to {0}.",
    "compare": "it resembles {0}.",
    "contextualize": "it belongs to the domain of {0}.",
    "localize": "it is found in {0}.",
    "register": "it is used in {0}.",
    "observe": "{0}.",
}


def assemble_sentence(direction: str, words_out: List[str]) -> str:
    if not words_out:
        return "(no candidates found)"
    tmpl = _SENTENCE_TEMPLATES.get(direction, "{0}.")
    fillers = list(words_out)
    while len(fillers) < tmpl.count("{"):
        fillers.append(fillers[-1])
    return tmpl.format(*fillers[:tmpl.count("{")])


# ── the connective lexicon — segue words, each a silk operator and a move
#    on the web.  ~closed class (Halliday & Hasan / PDTB); a starter slice.
_CONNECTIVES: Dict[str, List[str]] = {
    "throughline": ["because", "therefore", "thus", "hence", "so", "it follows that"],
    "elaborate":   ["specifically", "more precisely", "in detail", "that is",
                    "in other words"],
    "exemplify":   ["for example", "for instance", "consider", "namely"],
    "wrap":        ["in sum", "on the whole", "overall", "in short", "to summarise"],
    "lateral":     ["and", "also", "moreover", "next", "similarly", "likewise"],
    "reverse":     ["but", "however", "yet", "that said", "conversely",
                    "on the other hand"],
    "return":      ["as established", "recall that", "to return to", "as noted"],
    "scope":       ["with respect to", "as for", "turning to"],
    "signpost":    ["we return to this below", "more on this later",
                    "setting this aside for now"],
}
# radial move on the web per connective class:
#   +1 outward, -1 inward, 0 lateral (next spoke), "pivot" = frustrated reversal
_SPIRAL_MOVE: Dict[str, Any] = {
    "throughline": +1, "elaborate": +1, "exemplify": +1,
    "wrap": -1, "return": -1, "lateral": 0, "reverse": "pivot",
    "scope": 0, "signpost": 0,
}

# genre = a field configuration: which blocks, in what order, how deep.
_GENRE: Dict[str, Dict[str, Any]] = {
    "paper":    {"blocks": ["bridge", "frame", "body", "wrap"], "reach_cap": 4},
    "report":   {"blocks": ["bridge", "body", "wrap"],          "reach_cap": 3},
    "memo":     {"blocks": ["bridge", "body"],                  "reach_cap": 2},
    "tutorial": {"blocks": ["frame", "body"],                   "reach_cap": 4},
    "note":     {"blocks": ["body"],                            "reach_cap": 1},
}
_DEPTH_NAME = {1: "paragraph", 2: "section", 3: "chapter", 4: "part"}

# 19 WordNet relation slots -> a coarse direction, for the sniffed vector.
# (rotary_rerun_boxkite uses ptolemy_monad.infer_direction on the real
# 19-vector; the sniffer below only needs enough spread to rank axes.)
_STOP = set("a an the of to in on and or is are was were be been it its this "
            "that these those with for as at by from into over under".split())


@dataclass
class Radius:
    direction: str
    text: str
    struts: List[int] = field(default_factory=list)


@dataclass
class Block:
    kind: str                       # bridge | scope | paragraph | pivot | wrap
    depth: int
    radius: Optional[str]
    text: str
    connective_out: str = ""
    move: Any = 0


@dataclass
class Document:
    genre: str
    scale: float
    reach: int
    turbulent: bool
    bridge: str
    frame: str
    radii: List[Radius]
    scaffold: List[str]
    blocks: List[Block]
    ledger_rows: List[Relation] = field(default_factory=list)

    def render(self) -> str:
        L = [f"[{self.genre}  scale={self.scale}  reach={self.reach}"
             f"  {'turbulent' if self.turbulent else 'laminar'}"
             f"  radii={len(self.radii)}  blocks={len(self.blocks)}]",
             f"BRIDGE: {self.bridge}",
             f"FRAME : {self.frame}", "SCAFFOLD (centre->out):"]
        L += [f"    {s}" for s in self.scaffold]
        L.append("CAPTURE (out->in):")
        for b in self.blocks:
            tag = b.kind + (f"/{b.radius}" if b.radius else "")
            L.append(f"    ·d{b.depth} {tag}: {b.text}"
                     + (f"   -> [{b.connective_out}]" if b.connective_out else ""))
        return "\n".join(L)


class OrbWeaverMonad:
    """The web-construction cycle.  Holds its own MindsEye / PapersHands /
    BoxKite (fast to build); the heavy WordNet Monad is optional."""

    def __init__(self) -> None:
        self._eye = MindsEye()
        self._hands = PapersHands()
        try:
            self.box_kite: Optional[BoxKite] = BoxKite.between(self._eye, self._hands)
            self._kite_error: Optional[str] = None
        except BoxKiteUnavailable as exc:
            self.box_kite = None
            self._kite_error = str(exc)

    # ── helpers ──────────────────────────────────────────────────────────
    def _struts(self, text: str) -> List[int]:
        if self.box_kite is None:
            return []
        try:
            return sorted(self._eye.lit_struts(cam_encode(text)))
        except Exception:                                          # noqa: BLE001
            return []

    @staticmethod
    def _sniff(text: str) -> Tuple[List[str], List[int]]:
        """A crude word list + 19-slot relation vector from the raw text —
        enough to rank section axes without loading WordNet."""
        toks = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]+", text)]
        content = [w for w in toks if w not in _STOP and len(w) > 2]
        # dedupe, keep order
        seen: set = set()
        words = [w for w in content if not (w in seen or seen.add(w))]
        rv = [0] * 19
        # spread counts across slots by a stable hash of each content word
        for w in content:
            rv[hash(w) % 19] += 1
        if not any(rv):
            rv[12] = 1                                    # 'observe' fallback slot
        return (words or ["it"]), rv

    def _ranked_directions(self, rv: List[int], k: int) -> List[str]:
        v = list(rv)
        out: List[str] = []
        for _ in range(max(1, k)):
            if not any(v):
                break
            try:
                d = infer_direction(v)
            except Exception:                                     # noqa: BLE001
                d = "observe"
            if d not in out:
                out.append(d)
            v[max(range(len(v)), key=lambda i: v[i])] = 0
        return out or ["observe"]

    @staticmethod
    def _turbulence(rv: List[int]) -> Tuple[bool, int]:
        if not any(rv):
            return False, 0
        m = max(rv)
        peaks = sum(1 for c in rv if c >= 0.5 * m and c > 0)
        return peaks >= 3, peaks

    @staticmethod
    def _reach(scale: float, genre: str) -> int:
        cap = _GENRE.get(genre, _GENRE["paper"])["reach_cap"]
        try:
            from GenerationalLineage.engine import line_descend       # noqa: PLC0415
            g = line_descend("scale", float(max(scale, 1e-6)), chart=True)["charts"]
            rung = g["discrete"].get("generation")
            if isinstance(rung, int):
                return max(1, min(cap, rung + 1))
        except Exception:                                            # noqa: BLE001
            pass
        return max(1, min(cap, int(round(scale))))

    def _conn(self, cls: str, rng: random.Random) -> Tuple[str, Any]:
        return rng.choice(_CONNECTIVES.get(cls, ["and"])), _SPIRAL_MOVE.get(cls, 0)

    # ── the cycle ────────────────────────────────────────────────────────
    def weave(self, text: str, scale: float = 2.0, genre: str = "paper",
              words: Optional[List[str]] = None,
              root_vector: Optional[List[int]] = None,
              seed: int = 20260903) -> Document:
        rng = random.Random(seed)
        if words is None or root_vector is None:
            words, root_vector = self._sniff(text)
        rv = list(root_vector)
        turbulent, peaks = self._turbulence(rv)
        reach = self._reach(scale, genre)
        gblocks = _GENRE.get(genre, _GENRE["paper"])["blocks"]

        # STRUCTURE ---------------------------------------------------------
        bridge = assemble_sentence("contextualize", words)
        frame_s = assemble_sentence("situate", words)
        n_axes = max(1, min(reach + 1, len(words)))
        dirs = self._ranked_directions(rv, n_axes)
        radii = [Radius(d, assemble_sentence(d, words),
                        self._struts(assemble_sentence(d, words))) for d in dirs]

        # SCAFFOLD SPIRAL (centre -> out) ---------------------------------
        scaffold: List[str] = []
        for depth in range(1, reach + 1):
            dn = _DEPTH_NAME.get(depth, f"d{depth}")
            for r in radii:
                scaffold.append(f"[{dn}] {r.direction}: {r.text}")

        # CAPTURE SPIRAL (out -> in) ------------------------------------
        blocks: List[Block] = []
        if "bridge" in gblocks:
            blocks.append(Block("bridge", 0, None, bridge,
                                *self._conn("throughline", rng)))
        if "frame" in gblocks:
            blocks.append(Block("scope", 0, None, frame_s, *self._conn("scope", rng)))

        for depth in range(reach, 0, -1):
            dn = _DEPTH_NAME.get(depth, f"level {depth}")
            for pos, r in enumerate(radii):
                cw, mv = self._conn("elaborate", rng)
                blocks.append(Block("paragraph", depth, r.direction,
                                    f"{cw.capitalize()}, {r.text[:-1]} at the "
                                    f"{dn} level.", cw, mv))
                if len(words) > pos + 1:
                    hw, hm = self._conn("exemplify", rng)
                    blocks.append(Block("paragraph", depth, r.direction,
                                        f"{hw.capitalize()}: {words[pos + 1]}.",
                                        hw, hm))
                # FRUSTRATION: turbulent -> reverse along the strut, recap,
                # jump spoke.  The return step sits next to the outbound
                # step (same depth, adjacent radius) — interdigitated.
                if turbulent and depth == reach and pos < len(radii) - 1:
                    rw, rm = self._conn("reverse", rng)
                    blocks.append(Block("pivot", depth, r.direction,
                                        f"{rw.capitalize()}, the {r.direction} axis "
                                        f"only carries so far here.", rw, rm))
                    ww, wm = self._conn("wrap", rng)
                    blocks.append(Block("wrap", depth, r.direction,
                                        f"{ww.capitalize()}, {r.text[:-1]} — carried "
                                        f"back to the hub.", ww, wm))
        if "wrap" in gblocks:
            ww, wm = self._conn("wrap", rng)
            blocks.append(Block("wrap", 0, None, f"{ww.capitalize()}, {bridge[:-1]}.",
                                ww, wm))

        rows = self._measure(radii, blocks, turbulent, peaks, rng)
        return Document(genre=genre, scale=scale, reach=reach, turbulent=turbulent,
                        bridge=bridge, frame=frame_s, radii=radii,
                        scaffold=scaffold, blocks=blocks, ledger_rows=rows)

    def weave_via(self, rbk_monad: Any, text: str, **kw) -> Document:
        """Heavy path: use a fully-built RotaryBoxKiteMonad for the real
        WordNet sentence layer, then weave.  Not exercised in __main__."""
        enc = rbk_monad.process_input(text)
        return self.weave(text, words=enc.words_out or None,
                          root_vector=list(enc.root_vector), **kw)

    # ── measurement (UNTESTED — new model, tiny n) ──────────────────────
    def _measure(self, radii: List[Radius], blocks: List[Block],
                 turbulent: bool, peaks: int, rng: random.Random) -> List[Relation]:
        rows: List[Relation] = []
        para = [b for b in blocks if b.kind == "paragraph" and b.radius]
        if self.box_kite is not None and para and len(radii) > 1:
            by_dir = {r.direction: set(r.struts) for r in radii}
            real = [len(set(self._struts(b.text)) & by_dir.get(b.radius, set()))
                    for b in para]
            ctrl = []
            for b in para:
                other = rng.choice([d for d in by_dir if d != b.radius]
                                   or list(by_dir))
                ctrl.append(len(set(self._struts(b.text)) & by_dir[other]))
            rmean = sum(real) / len(real)
            cmean = sum(ctrl) / len(ctrl)
            rows.append(Relation(
                name="orbweaver.paragraph_hangs_on_its_radius",
                claim="a capture-spiral paragraph shares more box-kite struts "
                      "with its own radius than with another radius",
                status=Status.UNTESTED,
                expected="real_mean > ctrl_mean",
                observed=f"{rmean:.3f} vs {cmean:.3f}  (n={len(para)})",
                detail="new model, tiny n — direction only",
                group="spider-web-composition"))
        else:
            rows.append(Relation(
                name="orbweaver.paragraph_hangs_on_its_radius",
                claim="capture-spiral paragraph <-> its radius strut overlap",
                status=Status.UNTESTED, fault=Fault.NONE,
                detail=f"BoxKite/para unavailable: {self._kite_error}",
                group="spider-web-composition"))
        rows.append(Relation(
            name="orbweaver.frustration_on_turbulence",
            claim="turbulent context flow (>=3 near-equal relations) triggers "
                  "spiral reversals (pivot + aciniform recap)",
            status=Status.UNTESTED,
            observed=f"turbulent={turbulent}  n_peaks={peaks}  "
                     f"pivots={sum(1 for b in blocks if b.kind == 'pivot')}",
            detail="mechanism wired; not validated against read-back",
            group="spider-web-composition"))
        return rows


if __name__ == "__main__":
    m = OrbWeaverMonad()
    ledger = Ledger()
    print(f"BoxKite {'sig ' + str(m.box_kite.signature) + '  ' + str(m.box_kite.n_struts) + ' struts' if m.box_kite else 'UNAVAILABLE: ' + str(m._kite_error)}")

    cases = [
        ("the engine contains sixteen distinct operators that fold into a "
         "single algebra", 2.0, "paper"),
        ("she deposited her savings in the reserve account", 1.0, "note"),
        ("the volcano formed a mountain of cinder ash lava rock and time "
         "under pressure and heat", 3.0, "report"),
    ]
    for text, scale, genre in cases:
        print(f"\n{'=' * 72}\ninput: {text!r}\n       scale={scale} genre={genre}")
        doc = m.weave(text, scale=scale, genre=genre)
        print(doc.render())
        for r in doc.ledger_rows:
            ledger.add(r)

    print(f"\n{'=' * 72}")
    for i in range(len(ledger)):
        print(ledger.at(i))
    print(f"\n{len(ledger)} relations   {ledger.count(Status.HOLDS)} hold   "
          f"{ledger.count(Status.VIOLATED)} FAULT   "
          f"{ledger.count(Status.UNTESTED)} untested")
    print("\nboxkite_orbweaver_monad.py: run complete.")
