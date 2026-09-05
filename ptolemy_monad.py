#!/usr/bin/env python3
"""
ptolemy_monad.py — the next Monad: built to USE the harness (VAPMIP/harness.py),
not the reverse. harness.attach_monad(monad) already existed; this is the
first Monad that actually calls harness.reach() / harness.present() for
anything outside itself, rather than a diagnostic script standing in for it.

Cody, 2026-08-25 — the design brief this file implements, point by point:

  "the monad is the roots of the tree, and the leaves are both the input
  and output words." — process_input() reads INPUT leaves (sentence_context.
  build_sentence_context) to build the root context; response construction
  walks back OUT from that same root to new OUTPUT leaves
  (sentence_context.nearest_synsets over a neighborhood pool). One tree,
  read both directions — not two separate mechanisms.

  "an input picks the direction that the monad will travel in its
  intention" — infer_direction() reads the sentence root's DOMINANT
  relation (which of the 19 WordNet relation types contributed the most
  weight) and maps it to a coarse processing direction (classify/decompose/
  situate/...). Set once per input as self.intent, exactly the "direction"
  language.

  "Mind's Eye and Paper's Hands on different threads that can communicate
  back and forth as a human mind does when it talks to itself" — two real
  daemon threads (_eye_loop, _hands_loop), each with its own queue.Queue,
  exchanging ExchangeEntry messages for up to MAX_ROUNDS before settling.
  Not simulated in one function — an actual cross-thread round trip, same
  shape as ptol.c's R_hat (Eye, live sigma_self, updateable) / B_hat =
  R_hat^dagger (Hands, 1-sigma_self, non-updateable): Eye proposes and
  revises; Hands only ever confirms or critiques, never authors a draft.

  "include the KVM in the monad...stub the KVM functions" — MonadKVM below,
  intentionally not wired to PyQt6 (Cody, 2026-08-24: KVM is a basic
  Monad-native sense/actuator, not a harness-reachable Face tool — it lives
  directly on the Monad, not behind toolset_registry).

  "if you stumble across a functionality the harness should have...add
  that to the harness" — harness.present() (a viewport-or-stdout output
  call) was added to harness.py while building this file, for exactly
  that reason; see its docstring there.

Python only, on purpose ("test it all with the python version so we can
have easy importing into the harness for now") — a C rewrite is future
work once the harness is doing enough rendering/data work to need it.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from sentence_context import (
    SentenceBoxKite, build_sentence_context, neighborhood_corpus, nearest_synsets,
)
from wordnet_boxkite import RELATION_METHODS


# ── input picks the direction ────────────────────────────────────────────
# Coarse mapping from "which WordNet relation dominates the sentence root"
# to a processing direction. Not claimed to be a complete taxonomy of
# intention — a first, honest pass, same spirit as spelling_code's
# "PROVISIONAL" flag in wordnet_boxkite.py.

DIRECTION_BY_DOMINANT_RELATION: Dict[str, str] = {
    'hypernyms':          'classify',       # what kind of thing is this
    'instance_hypernyms':  'classify',
    'hyponyms':            'enumerate',     # what are its kinds
    'instance_hyponyms':   'enumerate',
    'part_meronyms':       'decompose',     # what is it made of
    'substance_meronyms':  'decompose',
    'member_meronyms':     'decompose',
    'part_holonyms':       'situate',       # what is it part of
    'substance_holonyms':  'situate',
    'member_holonyms':     'situate',
    'attributes':          'characterize',
    'causes':               'explain',
    'entailments':          'imply',
    'also_sees':            'associate',
    'similar_tos':          'compare',
    'verb_groups':          'compare',
    'topic_domains':        'contextualize',
    'region_domains':       'localize',
    'usage_domains':        'register',
}


# hyponyms/hypernyms measure taxonomy BRANCHING, not what the sentence is
# ABOUT — nearly every noun has WordNet subtypes, so raw-count argmax over
# the full 19-dim root almost always lands here (measured 2026-09-04: 9/10
# varied test sentences came back 'enumerate'). context_hash_v2.code_omega()
# and semantic_paragraph's grammar already exclude this same channel for the
# same reason; infer_direction did not. Prefer the richer, rarer signal —
# causes/similar_tos/topic_domains/etc — when one fired at all; branching
# stays the FALLBACK direction, not the default one.
_BRANCHING = frozenset({'hypernyms', 'instance_hypernyms',
                        'hyponyms', 'instance_hyponyms'})


def infer_direction(root_vector: List[int]) -> str:
    """The dominant nonzero dimension of the sentence root picks the
    direction. No dominant signal (all-zero root — an input with no
    resolvable WordNet content) returns 'observe', not an error: a valid
    direction, just an uncommitted one."""
    if not any(root_vector):
        return 'observe'
    non_branch = [(i, c) for i, c in enumerate(root_vector)
                  if c and RELATION_METHODS[i] not in _BRANCHING]
    if non_branch:
        idx = max(non_branch, key=lambda ic: ic[1])[0]
    else:
        idx = max(range(len(root_vector)), key=lambda i: root_vector[i])
    return DIRECTION_BY_DOMINANT_RELATION.get(RELATION_METHODS[idx], 'observe')


# ── the redundancy layer, built into the Mind's Eye ─────────────────────
class MindsEyeRepass:
    """The sedenion window's RECURSIVE repass -- redundancy, built into
    the Mind's Eye.

    Structure: 16-word FRAMES, a 15-edge spanning tree per frame (the
    Recaman backward arcs), the step incremented once per word. Slot 0 of
    each frame is e0 -- the anchor, owns no edge, the reference the arcs
    hang off. The recursion factor is the number of frames.

    This is the RECURSIVE repass (one scale), NOT the fractal one -- each
    frame becoming a word at the next scale (sentence -> paragraph ->
    chapter), nested self-similarly, is later.

    Runs ABOVE and OUTSIDE the one-shot selection: it sees the whole draft
    while the construction walk sees only its current slot, and
    SIMULTANEOUSLY GUIDES construction -- each step recommends the next
    Recaman BACKWARD move (return to an earlier word, deepen it: affix ->
    modifier -> clause as the global step grows) rather than pushing
    forward. Forced forward only when a frame is fully refined.

    Guarantee shape: injective by construction (a slot is not re-refined
    within one cycle); coverage is best-effort and unrefined slots are
    REPORTED, never hidden. A second, independent view of the draft -- if
    the selection drifts, the repass is the parallel route (mesh, not
    star)."""

    FRAME = 16

    def __init__(self, slots: List[str]):
        self.slots = list(slots)              # chosen words, reading order
        self.visited: set = set()             # slot idxs refined this cycle
        self.refined: Dict[int, List[str]] = {}
        self.step = 1                         # GLOBAL Recaman step: +1/word, never resets
        self.passes = 0
        self._last_in_frame: Dict[int, int] = {}   # frame idx -> last refined slot

    def _frames(self):
        return [(s, min(s + self.FRAME, len(self.slots)))
                for s in range(0, len(self.slots), self.FRAME)]

    def _target(self):
        """Earliest slot that is not its frame's e0 anchor, still bare,
        and unvisited this cycle. (None, None) -> forced forward."""
        for start, end in self._frames():
            for i in range(start, end):
                if i == start:
                    continue                 # e0 owns no edge
                if i not in self.visited and i not in self.refined:
                    return i, start
        return None, None

    def guidance(self) -> Dict[str, Any]:
        """One repass step -- the recommendation construction consumes."""
        self.passes += 1
        i, anchor = self._target()
        if i is None:
            return {'action': 'stop', 'passes': self.passes,
                    'reason': 'every frame refined -- forced forward'}
        fidx = anchor // self.FRAME
        # the Recaman backward arc: from slot i to the previous refined
        # slot in its frame, or to e0 if this is the frame's first arc
        back = self._last_in_frame.get(fidx, anchor)
        tier = ('affix' if self.step <= 2 else
                'modifier' if self.step <= 5 else 'clause')
        self.visited.add(i)
        self._last_in_frame[fidx] = i
        self.step += 1
        return {'action': 'refine', 'slot': i, 'word': self.slots[i],
                'edge': (back, i), 'anchor': self.slots[anchor],
                'operator': tier, 'step': self.step - 1, 'frame': fidx,
                'passes': self.passes,
                'reason': (f'frame {fidx} arc: slot {i} ({self.slots[i]}) '
                           f'-> {self.slots[back]}')}

    def record(self, slot: int, op: str) -> None:
        self.refined.setdefault(slot, []).append(op)

    def coverage(self) -> Dict[str, Any]:
        anchors = {start for start, _ in self._frames()}
        bare = [self.slots[i] for i in range(len(self.slots))
                if i not in self.refined and i not in anchors]
        return {'refined': {self.slots[k]: v for k, v in self.refined.items()},
                'unrefined': bare,               # bare NON-anchor slots only
                'anchors': [self.slots[i] for i in sorted(anchors)],  # e0s, bare by design
                'passes': self.passes, 'frames': len(self._frames()),
                'complete': not bare}            # every edge-bearing slot refined


# ── KVM — stub only, deliberately ────────────────────────────────────────

class MonadKVM:
    """Cody, 2026-08-25: "include the KVM in the monad...it doesn't need
    full wiring in yet since we are not playing with the pyqt6 version of
    software yet." Every call here returns a plain not-ok dict rather than
    raising — a caller can check ['ok'] the same way it would check a
    FaceResult, without needing a try/except just to probe availability.
    Real wiring (PtolemyDesktop's KVM.py / Tesla) is deferred until the
    desktop environment work resumes."""

    def watch_cursor(self, *args, **kwargs) -> Dict[str, Any]:
        return {'ok': False, 'error': 'KVM.watch_cursor not wired yet — '
                'stub, PyQt6 desktop integration pending'}

    def read_screen_region(self, *args, **kwargs) -> Dict[str, Any]:
        return {'ok': False, 'error': 'KVM.read_screen_region not wired yet — '
                'stub, PyQt6 desktop integration pending'}

    def move_cursor(self, *args, **kwargs) -> Dict[str, Any]:
        return {'ok': False, 'error': 'KVM.move_cursor not wired yet — '
                'stub, PyQt6 desktop integration pending'}


# ── the Eye/Hands exchange record ────────────────────────────────────────

@dataclass
class ExchangeEntry:
    sender: str    # 'eye' | 'hands'
    kind: str      # 'draft' | 'confirm' | 'critique'
    payload: Dict[str, Any]


@dataclass
class MonadResponse:
    text: str
    direction: str
    root_vector: List[int]
    leaves_in: List[Dict[str, Any]]
    leaves_out: List[Dict[str, Any]]
    exchange_log: List[ExchangeEntry] = field(default_factory=list)
    repass: Dict[str, Any] = field(default_factory=dict)   # Mind's Eye redundancy


# ── the Monad ─────────────────────────────────────────────────────────────

class PtolemyMonad:
    """Roots of the tree. Attach a Harness (harness.attach_monad(self) on
    the harness side, or pass one in here) and this Monad will reach OUT
    through it for anything beyond its own sentence-context/deliberation
    core — never talks to a Face, an engine, or a repo's tools.py
    directly, per harness.py's own standing rule."""

    MAX_ROUNDS = 3    # bounded self-talk — Eye/Hands settle or time out, never spin
    # the Recaman repass is bounded per-call by slot count (see _eye_repass);
    # the frame width is MindsEyeRepass.FRAME (= 16), the per-frame edge
    # budget is 15.

    def __init__(self, harness: Optional[Any] = None):
        self.harness = harness
        self.kvm = MonadKVM()
        self.intent: Optional[str] = None   # set per input — the "direction"

        self._eye_q: "queue.Queue" = queue.Queue()
        self._hands_q: "queue.Queue" = queue.Queue()
        self._stop = threading.Event()
        self._eye_thread = threading.Thread(target=self._eye_loop, daemon=True,
                                            name='monad-eye')
        self._hands_thread = threading.Thread(target=self._hands_loop, daemon=True,
                                              name='monad-hands')
        self._eye_thread.start()
        self._hands_thread.start()

    def attach_harness(self, harness: Any) -> None:
        self.harness = harness

    def shutdown(self) -> None:
        self._stop.set()
        self._eye_q.put(None)
        self._hands_q.put(None)
        self._eye_thread.join(timeout=2)
        self._hands_thread.join(timeout=2)

    # ── Mind's Eye: R_hat at live sigma_self — drafts, updateable ──────────

    def _eye_loop(self) -> None:
        while not self._stop.is_set():
            task = self._eye_q.get()
            if task is None:
                break
            kind, payload, reply_q = task
            if kind == 'deliberate':
                reply_q.put(ExchangeEntry('eye', 'draft', self._eye_draft(payload)))
            elif kind == 'reconsider':
                reply_q.put(ExchangeEntry('eye', 'draft', self._eye_revise(payload)))
            elif kind == 'repass':
                reply_q.put(ExchangeEntry('eye', 'repass', self._eye_repass(payload)))

    def _eye_draft(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        direction = infer_direction(ctx['root_vector'])
        pool = neighborhood_corpus(ctx['leaves_in'])
        return {'direction': direction, 'pool': pool, 'max_per_relation': 5}

    def _eye_revise(self, note: Dict[str, Any]) -> Dict[str, Any]:
        # Hands rejected the first draft as too thin — widen the search.
        ctx = note['ctx']
        wider = note['draft']['max_per_relation'] + 5
        pool = neighborhood_corpus(ctx['leaves_in'], max_per_relation=wider)
        return {'direction': note['draft']['direction'], 'pool': pool,
                'max_per_relation': wider}

    def _eye_repass(self, note: Dict[str, Any]) -> Dict[str, Any]:
        """Built-in: the Mind's Eye repasses its own chosen words. Runs
        bounded guided Recaman backward steps over the selected slots and
        returns (guidance trace, coverage report). Guidance steers the
        deepening; the trace is the redundant second view. Actually
        applying each nuance (inflect via monad_grammar.bin / attach a
        modifier from the basin) is the constructor's consumer step —
        flagged, not done here."""
        slots = note.get('slots') or []
        me = MindsEyeRepass(slots)
        # can't do more refinements than slots; +frames for the per-frame
        # 'stop' steps, +1 slack.
        max_iters = len(slots) + (len(slots) // MindsEyeRepass.FRAME) + 2
        trace: List[Dict[str, Any]] = []
        for _ in range(max_iters):
            g = me.guidance()
            trace.append(g)
            if g['action'] == 'stop':
                break
            me.record(g['slot'], g['operator'])
        return {'guidance': trace, 'coverage': me.coverage()}

    # ── Paper's Hands: B_hat = R_hat^dagger at 1-sigma_self — reviews only,
    # never authors a draft, non-updateable ────────────────────────────────

    def _hands_loop(self) -> None:
        while not self._stop.is_set():
            task = self._hands_q.get()
            if task is None:
                break
            kind, payload, reply_q = task
            if kind == 'review':
                reply_q.put(self._hands_review(payload))

    def _hands_review(self, note: Dict[str, Any]) -> ExchangeEntry:
        draft = note['draft']
        if len(draft['pool']) < 3:
            return ExchangeEntry('hands', 'critique',
                                 {'reason': 'candidate pool too thin', 'draft': draft})
        return ExchangeEntry('hands', 'confirm', {'draft': draft})

    # ── the actual cross-thread round trip ──────────────────────────────────

    def _deliberate(self, ctx: Dict[str, Any]) -> Tuple[Dict[str, Any], List[ExchangeEntry]]:
        log: List[ExchangeEntry] = []
        reply_eye: "queue.Queue" = queue.Queue()
        reply_hands: "queue.Queue" = queue.Queue()

        self._eye_q.put(('deliberate', ctx, reply_eye))
        entry = reply_eye.get()
        log.append(entry)
        draft = entry.payload

        for _ in range(self.MAX_ROUNDS):
            self._hands_q.put(('review', {'draft': draft}, reply_hands))
            verdict = reply_hands.get()
            log.append(verdict)
            if verdict.kind == 'confirm':
                draft = verdict.payload['draft']
                break
            self._eye_q.put(('reconsider', {'draft': verdict.payload['draft'],
                                            'ctx': ctx}, reply_eye))
            entry = reply_eye.get()
            log.append(entry)
            draft = entry.payload
        return draft, log

    # ── the one public entry point ──────────────────────────────────────────

    def process_input(self, text: str, user_id: str = 'default') -> MonadResponse:
        """INPUT leaves -> root (understanding) -> deliberate (Eye/Hands,
        cross-thread) -> OUTPUT leaves (communication). The harness is
        reached for context-buffer bookkeeping and for presenting the
        result, if one is attached — never required, always optional."""
        ctx = build_sentence_context(text)
        self.intent = infer_direction(ctx.root_vector)

        if self.harness is not None:
            buf = self.harness.context_buffer(user_id)
            if buf is not None and hasattr(buf, 'record'):
                buf.record(text)   # duck-typed — real CyclicContextBuffer shape

        draft, log = self._deliberate({'leaves_in': ctx.leaves,
                                       'root_vector': ctx.root_vector})
        pool = draft['pool']
        out_synsets = nearest_synsets(ctx.root_vector, pool,
                                      top_k=min(5, len(pool))) if pool else []
        leaves_out = [{'word': (s.lemma_names()[0] if s.lemma_names() else s.name()),
                       'synset': s.name(), 'distance': d} for d, s in out_synsets]

        response_words = [l['word'].replace('_', ' ') for l in leaves_out]
        response_text = ' '.join(response_words) if response_words else '(no candidates found)'

        # Mind's Eye redundancy: repass the chosen words (Recaman backward
        # steps) ABOVE and OUTSIDE the one-shot selection above, guiding
        # where nuance (affix / modifier / clause) should be added.
        reply_repass: "queue.Queue" = queue.Queue()
        self._eye_q.put(('repass', {'slots': response_words}, reply_repass))
        repass = reply_repass.get().payload
        log.append(ExchangeEntry('eye', 'repass',
                                 {'coverage': repass['coverage']}))

        response = MonadResponse(text=response_text, direction=self.intent,
                                 root_vector=ctx.root_vector, leaves_in=ctx.leaves,
                                 leaves_out=leaves_out, exchange_log=log,
                                 repass=repass)

        if self.harness is not None:
            self.harness.present(response_text, kind='monad_response', center='hands')

        return response


# ── smoke test — real Harness, real Monad, real WordNet, no mocks ─────────
if __name__ == '__main__':
    from harness import Harness, FaceResult

    h = Harness()
    monad = PtolemyMonad(harness=h)
    h.attach_monad(monad)

    print('=== process_input, direction inference, Eye/Hands exchange ===')
    for sentence in (
        'the volcano formed a mountain of cinder and ash',
        'she deposited her savings in the reserve account',
        'the engine contains sixteen distinct operators',
    ):
        print(f'\n  input: {sentence!r}')
        resp = monad.process_input(sentence, user_id='cody')
        print(f'    direction (intent): {resp.direction}')
        print(f'    root_vector (nonzero via leaves_in): '
              f'{ {RELATION_METHODS[i]: c for i, c in enumerate(resp.root_vector) if c} }')
        print(f'    leaves_in : {[l["word"] + "/" + l["synset"].name() for l in resp.leaves_in]}')
        out_desc = [f'{l["word"]}/{l["synset"]}(L1={l["distance"]})' for l in resp.leaves_out]
        print(f'    leaves_out: {out_desc}')
        print(f'    exchange_log: {[(e.sender, e.kind) for e in resp.exchange_log]}')
        print(f'    response text: {resp.text!r}')
        cov = resp.repass.get('coverage', {})
        print(f"    mind's-eye repass: {cov.get('passes')} passes, "
              f"refined {list(cov.get('refined', {}))}, "
              f"unrefined {cov.get('unrefined')}, complete={cov.get('complete')}")

    assert monad.intent is not None
    assert all(isinstance(e, ExchangeEntry) for r in [resp] for e in r.exchange_log)
    assert any(e.kind == 'confirm' for e in resp.exchange_log)   # Hands settled
    assert resp.exchange_log[-1].kind == 'repass'                # Eye repassed last
    assert 'coverage' in resp.repass and 'guidance' in resp.repass

    print('\n=== KVM — stubbed, not wired, does not raise ===')
    kvm_result = monad.kvm.watch_cursor()
    print(f'  watch_cursor(): {kvm_result}')
    assert kvm_result['ok'] is False and 'not wired yet' in kvm_result['error']

    print('\n=== harness.present() actually received the last response ===')
    last_present = [r for r in h.call_log if r.data == resp.text]
    assert last_present, 'monad.process_input did not reach harness.present()'
    print(f'  handled_by={last_present[-1].handled_by}  center={last_present[-1].center}')

    print('\n=== an empty / no-WordNet-content input takes the observe direction ===')
    resp_empty = monad.process_input('xyzzy plugh qux', user_id='cody')
    assert resp_empty.direction == 'observe', resp_empty.direction
    print(f'  direction: {resp_empty.direction}  (no resolvable synsets — correct fallback)')

    monad.shutdown()
    print('\nptolemy_monad.py: smoke test passed. Eye/Hands threads joined cleanly.')
