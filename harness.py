"""
harness.py — the Monad's harness.

The interim API surface between the Monad, the repos' own engines/tools, and
whatever is asking for content (the curses UI, eventually PtolemyDesktop).

NOT PtolBus, and deliberately kept apart in the code, not just in name: this
file's `toolset_registry` is "the currently populated toolbox" — capability
in, a Face/tool out. PtolBus (Pharos.PtolBus / FaceRegistry) is a different
future thing entirely — the day the Monad is handed the bus itself, it stops
reaching OUT for tools and BECOMES the desktop's own mechanic (native window
control, project context, opening its own windows). That is not a bigger
toolset_registry, it is a different object with different semantics, and it
does not exist here yet on purpose.

Standing rule: nothing above this file talks to a Monad, a repo's engine, or
a repo's tools.py directly. Everything goes through one Harness instance.

Deliberately open-ended and stub-tolerant. Several methods below are TODO on
purpose — the method NAMES and SHAPES are this round's actual deliverable,
not full implementations. Whatever consumes them next (the curses UI) is
what should force their real shape, not speculation now about what they
might need later.
"""

from __future__ import annotations

import importlib
import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

# ── the standing intent ──────────────────────────────────────────────────
# Fixed, not per-conversation — the same category as grammar/definition in
# the box-kite framing (zero net lift: unchanging regardless of context).
# Citable by any tool that needs to justify reaching through a gate to get
# at data it's after.
INTENT = "research grade investigation"


def justify_gate(reason: str) -> str:
    """One-line justification a tool can log/present when it crosses a gate
    (an auth wall, a rate limit, a data-access boundary) to reach something
    INTENT already licenses. Not an authorization mechanism — a STATEMENT,
    kept in one place instead of re-justified ad hoc at every call site."""
    return f"{INTENT}: {reason}"


# ── module discovery — corrected APISniff: getattr chains, never exec ────
# APISniff.py (PtolemyDesktop/Phaleron/APISniff/) proved this pattern works:
# doc / contents / code, off dir() and inspect, no hand-written documentation
# anywhere. What it got wrong was building each lookup as a formatted code
# STRING and exec()-ing it to walk a breadcrumb path. A getattr chain gets
# the identical result without ever executing a string.

@dataclass
class MemberInfo:
    """One introspected member of a scope — a module, class, function,
    whatever dir() turns up. The same three sections APISniff already
    proved useful: doc, contents, code. `error` is set instead of raising
    when introspection fails partway, so a caller always gets an object
    back, never an exception to handle."""
    name: str
    kind: str                                   # module|class|function|method|builtin|callable|data|unknown
    doc: Optional[str] = None
    contents: List[str] = field(default_factory=list)   # dir() of this member, if it has one
    source: Optional[str] = None                # inspect.getsourcelines, if available
    error: Optional[str] = None


def _classify(obj: Any) -> str:
    if inspect.ismodule(obj):   return 'module'
    if inspect.isclass(obj):    return 'class'
    if inspect.isfunction(obj): return 'function'
    if inspect.ismethod(obj):   return 'method'
    if inspect.isbuiltin(obj):  return 'builtin'
    if callable(obj):           return 'callable'
    return 'data'


def _walk(root: Any, path: Sequence[str]) -> Any:
    """getattr-chain walk: root.a.b.c given ['a','b','c']. Raises
    AttributeError on a miss — callers decide whether that's fatal."""
    obj = root
    for p in path:
        obj = getattr(obj, p)
    return obj


def inspect_member(root: Any, path: Sequence[str] = ()) -> MemberInfo:
    """The corrected APISniff core. No exec() of formatted strings anywhere
    in this function or anything it calls."""
    try:
        obj = _walk(root, path)
    except AttributeError as e:
        return MemberInfo(name='.'.join(path) or repr(root), kind='unknown', error=str(e))

    name = path[-1] if path else getattr(root, '__name__', repr(root))
    info = MemberInfo(name=name, kind=_classify(obj), doc=inspect.getdoc(obj))

    try:
        info.contents = sorted(a for a in dir(obj) if not a.startswith('__'))
    except Exception:
        pass

    try:
        info.source = ''.join(inspect.getsourcelines(obj)[0])
    except (TypeError, OSError):
        pass  # builtins, C extensions, etc. — no source available, not an error

    return info


# ── static discovery — "see what's available", never execute anything ──────
# inspect_member() above needs an already-imported live object. That's fine
# for known-safe things (stdlib, an attached Monad). It is NOT safe as the
# default way to ask "what does this Face have" — checked by hand this
# session, Tesla alone has: a file that binds a UDP port and blocks forever
# in recvfrom() at import time (Sockets.py), a file with a dangling `import`
# statement that is a flat SyntaxError (HolePunchServer.py), and a file using
# @dataclass without importing it (Zork_Sentence_Parser.py, NameError on
# import). "Diagnostic mode, doesn't need to use any tools, just sees what's
# available" means static AST parsing — the source is read, never run.

@dataclass
class FileInfo:
    """What one .py file defines, read from its own source — never
    imported, so an import-time crash or a blocking call in that file
    cannot affect the caller."""
    path: str
    doc: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    parse_error: Optional[str] = None


def discover_directory(path: str, pattern: str = '*.py') -> List[FileInfo]:
    """AST-only discovery of every file matching `pattern` in `path` — top-
    level class names, top-level function names, module docstring. Never
    imports, never executes. A file that fails to even parse (real example:
    HolePunchServer.py) comes back with parse_error set, not raised —
    discovery keeps going over the rest of the directory regardless."""
    import ast
    import glob as _glob
    import os as _os
    out: List[FileInfo] = []
    for fp in sorted(_glob.glob(_os.path.join(path, pattern))):
        info = FileInfo(path=fp)
        try:
            with open(fp, encoding='utf-8', errors='replace') as f:
                src = f.read()
            tree = ast.parse(src, filename=fp)
            info.doc = ast.get_docstring(tree)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    info.classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    info.functions.append(node.name)
        except SyntaxError as e:
            info.parse_error = f'SyntaxError: {e}'
        except Exception as e:
            info.parse_error = str(e)
        out.append(info)
    return out


# ── the harness itself ────────────────────────────────────────────────────

@dataclass
class FaceResult:
    """The one result shape every level of the toolset_registry returns —
    the harness calling a Face, or a Face (Tesla) calling one of its own
    tools underneath it, look identical to whoever made the call."""
    ok: bool
    data: Any = None
    error: Optional[str] = None
    handled_by: Optional[str] = None   # name of the handler that answered
    center: Optional[str] = None       # 'eye' | 'hands' | None — which of
                                        # the Monad's two centers made this
                                        # call, so Ptolemy (external — the
                                        # process clock already scheduling
                                        # every Face's thread, per
                                        # Ptolemy3.py's own threading
                                        # contract) can compare their tool
                                        # usage. Not evaluated here — the
                                        # harness only tags and keeps the
                                        # record; Ptolemy is the judge.


class ToolsetRegistry:
    """
    "The currently populated toolbox." Capability string in, a registered
    handler out. Used TWICE in this design, same class both times: once by
    the Harness (registering Faces), and once inside Tesla itself
    (registering its own tools — HolePunch, KVM, SensorStream, Sockets).
    That reuse is the point — a third level costs nothing new to add.

    NOT the future bus registry (see module docstring) — this only ever
    looks capabilities up and calls a handler; it never owns a desktop.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, tuple] = {}          # name -> (capabilities, handler)
        self._by_capability: Dict[str, List[str]] = {}  # capability -> [names]

    def register(self, name: str, capabilities: Sequence[str], handler) -> None:
        """handler: callable(capability: str, action: str, **params) ->
        FaceResult. Both are passed through, not just action — a handler
        that delegates to its OWN nested ToolsetRegistry (Tesla does this)
        needs the original capability to look itself up by, with action
        distinguishing which operation within it was requested."""
        self._handlers[name] = (tuple(capabilities), handler)
        for cap in capabilities:
            self._by_capability.setdefault(cap, [])
            if name not in self._by_capability[cap]:
                self._by_capability[cap].append(name)

    def unregister(self, name: str) -> None:
        caps, _ = self._handlers.pop(name, ((), None))
        for cap in caps:
            names = self._by_capability.get(cap, [])
            if name in names:
                names.remove(name)

    def candidates(self, capability: str) -> List[str]:
        return list(self._by_capability.get(capability, []))

    def names(self) -> List[str]:
        return sorted(self._handlers)

    def capabilities(self) -> List[str]:
        return sorted(self._by_capability)

    def reach(self, capability: str, name: Optional[str] = None,
              action: Optional[str] = None, chooser=None, **params) -> FaceResult:
        """
        Resolve `capability` to a registered handler and call it.

        name:    bypass candidate selection, call this handler directly —
                 the escape hatch for a caller that already knows who it wants.
        action:  passed through to the handler (defaults to `capability`
                 itself, since for a single-purpose handler they're the same).
        chooser: optional callable(candidate_names) -> name, for when more
                 than one handler offers the same capability. Defaults to
                 "first registered" — TODO: the lineage-engine-informed
                 tier/primitivity chooser described this session isn't
                 wired in yet; this is where it plugs in.

        handled_by reports the DEEPEST handler that actually answered, not
        just the top-level name reach() was called with — if a handler's
        own callable delegates to a nested ToolsetRegistry (Tesla does this
        for its own tools), that inner reach()'s handled_by passes through
        unchanged. Convention: name nested handlers 'facename.tool' (e.g.
        'tesla.kvm') so the result stays self-documenting at both levels.
        """
        if name is None:
            cands = self.candidates(capability)
            if not cands:
                return FaceResult(ok=False, error=f"no handler registered for {capability!r}")
            name = chooser(cands) if chooser else cands[0]
        entry = self._handlers.get(name)
        if entry is None:
            return FaceResult(ok=False, error=f"no handler named {name!r}")
        _, handler = entry
        try:
            result = handler(capability, action or capability, **params)
            if isinstance(result, FaceResult):
                if result.handled_by is None:
                    result.handled_by = name
                return result
            return FaceResult(ok=True, data=result, handled_by=name)
        except Exception as e:
            return FaceResult(ok=False, error=str(e), handled_by=name)


class Harness:
    """
    Everything a presentation layer needs from the Monad or from a repo's
    engines/tools comes from one Harness instance. Open-ended by design —
    grows as real needs surface, not pre-shaped for a fixed feature set.
    """

    CALL_LOG_MAX = 500   # bounded — this is a recent-activity window for
                          # Ptolemy to compare against, not an audit log

    def __init__(self) -> None:
        self._monad: Any = None
        self._roots: Dict[str, Any] = {}   # name -> browsable root (module/package/live scope)
        self.toolset_registry = ToolsetRegistry()
        self._lineage_module: Any = None
        self.call_log: List[FaceResult] = []

    # ── the toolset registry — one capability-based call to any Face ───────

    def reach(self, capability: str, center: Optional[str] = None,
              **kwargs) -> FaceResult:
        """The single function the Monad calls for anything outside itself:
        `harness.reach('research', query=..., center='hands')`. Resolution
        and dispatch are entirely toolset_registry's job — see
        ToolsetRegistry.reach(). `center` ('eye'/'hands'/None) is stamped
        onto the result and appended to call_log — the harness does not
        compare the two centers' usage itself, that's Ptolemy's job as the
        already-scheduling process clock (Ptolemy3.py's threading contract),
        external to this file. This is only the record it reads from."""
        result = self.toolset_registry.reach(capability, **kwargs)
        result.center = center
        self.call_log.append(result)
        if len(self.call_log) > self.CALL_LOG_MAX:
            del self.call_log[:len(self.call_log) - self.CALL_LOG_MAX]
        return result

    def calls_by_center(self, center: str) -> List[FaceResult]:
        """Recent reach() results tagged with this center — what Ptolemy
        would pull to compare Eye's tool usage against Hands'."""
        return [r for r in self.call_log if r.center == center]

    # ── presenting output — the harness's one call to "show something" ─────
    # Surfaced building the first Monad that actually calls the harness
    # (Cody, 2026-08-25): the Monad needs somewhere to send a constructed
    # response that isn't "print it and hope" — a chat window, a curses
    # "lecture viewport" box, or PtolemyDesktop's own interface/window-
    # decoration code, once any of those exist. Kept exactly as open-ended
    # as the rest of this file: a Face registers under capability
    # 'viewport' (curses now, PGui/compositor later — same registration
    # shape as Tesla's 'network'), and present() reaches for it. With
    # nothing registered yet, the fallback is a plain print so output is
    # never lost while no real viewport exists — same call_log accounting
    # either way, so callers don't need to know which path answered.

    def present(self, content: Any, kind: str = 'text',
               center: Optional[str] = None) -> FaceResult:
        """The Monad's one call to show something to whatever's listening.
        Prefers a registered 'viewport' Face; falls back to stdout."""
        if self.toolset_registry.candidates('viewport'):
            return self.reach('viewport', center=center, action='present',
                              content=content, kind=kind)
        print(content)
        result = FaceResult(ok=True, data=content, handled_by='stdout_fallback',
                            center=center)
        self.call_log.append(result)
        if len(self.call_log) > self.CALL_LOG_MAX:
            del self.call_log[:len(self.call_log) - self.CALL_LOG_MAX]
        return result

    # ── the generational lineage engine — direct, not just for display ─────

    @property
    def lineage(self) -> Any:
        """Live reference to SedenionFactoralRelativity/engine/lineage.py —
        decompose(), TIERS, FactoralLineageEngine, run(), all of it. This is
        what a tier-informed `chooser` in ToolsetRegistry.reach() would
        consult; format_derivation() below is a display formatter over the
        SAME module, not a separate thing."""
        if self._lineage_module is None:
            import os
            import sys
            _theplace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            _sfr = os.path.join(_theplace, 'SedenionFactoralRelativity')
            if _sfr not in sys.path:
                sys.path.insert(0, _sfr)
            try:
                from engine import lineage as _lineage_mod
            except ImportError as e:
                raise RuntimeError(
                    f"generational lineage engine not reachable at {_sfr}: {e}")
            self._lineage_module = _lineage_mod
        return self._lineage_module

    # ── monad lifecycle ───────────────────────────────────────────────────

    def attach_monad(self, monad: Any) -> None:
        """Attach a live Monad (VAPMIP.monad.Engine or compatible).
        Deliberately duck-typed — the harness doesn't own what counts as a
        Monad, it just holds whatever it's handed."""
        self._monad = monad

    def detach_monad(self) -> None:
        self._monad = None

    @property
    def monad_attached(self) -> bool:
        return self._monad is not None

    @property
    def monad(self) -> Any:
        """Raises if nothing is attached. Callers that need manual-mode
        fallback should check monad_attached first, not catch this."""
        if self._monad is None:
            raise RuntimeError("no Monad attached — check monad_attached first")
        return self._monad

    # ── module discovery ──────────────────────────────────────────────────

    def register_root(self, name: str, root: Any) -> None:
        """Add a browsable root — an already-imported module/package, or
        the harness's own live scope for a 'Current' root (APISniff's own
        special case: pass sys.modules[__name__] or similar)."""
        self._roots[name] = root

    def import_root(self, name: str, module_path: str) -> None:
        """Import module_path and register it under name, so a caller can
        add a browsable root by dotted path (e.g. 'ValaQuenta.engine')
        without the harness needing to know about it in advance."""
        self._roots[name] = importlib.import_module(module_path)

    def roots(self) -> List[str]:
        return sorted(self._roots)

    def inspect(self, root_name: str, path: Sequence[str] = ()) -> MemberInfo:
        """The corrected-APISniff lookup: doc/contents/code for
        roots[root_name].<path>. Real, not a stub — cheap, mechanical, and
        every registered root gets it for free with zero per-module
        wiring."""
        if root_name not in self._roots:
            return MemberInfo(name=root_name, kind='unknown',
                              error=f"no root registered as {root_name!r}")
        return inspect_member(self._roots[root_name], path)

    # ── tools-over-engines routing ────────────────────────────────────────

    def get_module_view(self, root_name: str, path: Sequence[str] = ()) -> MemberInfo:
        """Prefer a module's tools.py / viewer_data() surface when the
        target has one; fall back to raw inspect() otherwise.

        TODO: the tools.py-detection heuristic. For now this always falls
        back to inspect() — no curses box exists yet to demand the richer
        shape, so there's nothing yet to route toward. Real detection logic
        (matching SedenionFactoralRelativity's and ValaQuenta's existing
        maths.py/tools.py split) goes here once one does.
        """
        return self.inspect(root_name, path)

    def discover_face(self, name: str, directory: str,
                      pattern: str = '*.py') -> Dict[str, FileInfo]:
        """Safe ('diagnostic mode') discovery of what a Face's directory
        offers — static AST parsing, never imports. This is the pattern
        for visiting each Face: Tesla first, same call for every other one
        later. Cached per (name, directory) — call again after the Face's
        code changes if you need a fresh read."""
        if not hasattr(self, '_face_discoveries'):
            self._face_discoveries: Dict[str, Dict[str, FileInfo]] = {}
        key = f'{name}:{directory}'
        if key not in self._face_discoveries:
            files = discover_directory(directory, pattern)
            self._face_discoveries[key] = {f.path: f for f in files}
        return self._face_discoveries[key]

    # ── the box-data contract ─────────────────────────────────────────────

    def get_box_data(self, box_spec: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: the single call every curses box will make to refresh
        itself. Shape deliberately undecided until the curses UI is built
        against it — stubbed here so the method exists and box code can be
        written against it without waiting on this file again."""
        raise NotImplementedError("get_box_data: shape TBD when the curses UI needs it")

    # ── proof / derivation formatting ─────────────────────────────────────

    def format_derivation(self, obj: Any) -> str:
        """Render a Relation (SedenionFactoralRelativity) or an Equation
        (ValaQuenta) as a proof-flavoured paragraph — generated from
        whichever fields the object actually has, never hand-written.
        Duck-typed on purpose: a future module's own result object works
        here too, as long as it carries a matching handful of field names.
        """
        # SedenionFactoralRelativity.Relation: name, claim, tier, descends, status, detail
        if hasattr(obj, 'claim') and hasattr(obj, 'descends'):
            status = getattr(obj, 'status', None)
            status_word = getattr(status, 'value', status)
            return (
                f"{obj.name} (tier {obj.tier}). {obj.claim}\n"
                f"Descends from: {obj.descends}\n"
                f"Status: {status_word}\n"
                f"{getattr(obj, 'detail', '')}"
            )
        # ValaQuenta.Equation: name, display, confidence, code_verified, params
        if hasattr(obj, 'display') and hasattr(obj, 'confidence'):
            verified = 'code-verified' if getattr(obj, 'code_verified', False) else 'not yet code-verified'
            params = ', '.join(getattr(obj, 'params', None) or []) or 'none'
            return (
                f"{obj.display} [{obj.confidence}, {verified}]\n"
                f"Variables: {params}"
            )
        # TODO: anything that isn't one of the two known shapes yet.
        return f"(no known derivation format for {type(obj).__name__})"

    # ── standing intent ───────────────────────────────────────────────────

    intent = INTENT

    def justify_gate(self, reason: str) -> str:
        return justify_gate(reason)

    # ── per-user context buffers (Philadelphos.cyclic_context_buffer) ──────
    # One CyclicContextBuffer PER USER — a live, per-conversation version of
    # a .clauderc-style context file, generated purely from that user's own
    # interactions, partitioned and selected as needed rather than pouring
    # everything into one ever-growing window. Ptolemy3.py currently holds
    # ONE kernel-level instance (self.ccb) — that's a real gap against this
    # per-user design, not yet reconciled, noted rather than papered over.
    # STUB: real CyclicContextBuffer (Philadelphos/cyclic_context_buffer.py)
    # is a FIFO sliding window of EntryObjects (prompt+response), confirmed
    # eviction (compress -> hyperindex -> commit to a BranchBlockchain) —
    # the harness just needs to hold one per user_id and hand it back; it
    # does not reimplement any of that.

    def __init_context_buffers(self) -> None:
        if not hasattr(self, '_context_buffers'):
            self._context_buffers: Dict[str, Any] = {}

    def attach_context_buffer(self, user_id: str, buffer: Any) -> None:
        """Register a user's live CyclicContextBuffer (or compatible)."""
        self.__init_context_buffers()
        self._context_buffers[user_id] = buffer

    def detach_context_buffer(self, user_id: str) -> None:
        self.__init_context_buffers()
        self._context_buffers.pop(user_id, None)

    def context_buffer(self, user_id: str) -> Any:
        """Returns None if this user has no live buffer yet — callers
        should treat that as 'nothing partitioned in yet', not an error."""
        self.__init_context_buffers()
        return self._context_buffers.get(user_id)

    def context_users(self) -> List[str]:
        self.__init_context_buffers()
        return sorted(self._context_buffers)

    # ── compositor (Pharos.PGui / PWindow) ──────────────────────────────────
    # PGui: the self-contained shim replicating Qt window decoration via a
    # minimal SVG low-overhead replacement -- this IS where "PtolemyDesktop
    # must remain a compositor" lives, and it's what gives Ptolemy real KVM
    # access through Tesla. Explicitly underdeveloped per Cody (toolset
    # creation has been the priority) -- stub only, no real integration yet.

    def attach_compositor(self, compositor: Any) -> None:
        self._compositor = compositor

    def detach_compositor(self) -> None:
        self._compositor = None

    @property
    def compositor_attached(self) -> bool:
        return getattr(self, '_compositor', None) is not None

    @property
    def compositor(self) -> Any:
        if not self.compositor_attached:
            raise RuntimeError(
                "no compositor attached -- PGui is underdeveloped, check "
                "compositor_attached before use, not a real integration yet")
        return self._compositor


# ── smoke test — functional, not a self-checked relation; this is systems
# glue, not a mathematical claim, and gets tested that way ───────────────
if __name__ == '__main__':
    import math as _math

    h = Harness()
    assert not h.monad_attached

    h.attach_monad(object())
    assert h.monad_attached
    h.detach_monad()
    assert not h.monad_attached

    h.register_root('math', _math)
    info = h.inspect('math', ['sqrt'])
    assert info.kind == 'builtin', info
    assert info.error is None, info

    missing = h.inspect('math', ['not_a_real_function'])
    assert missing.error is not None

    assert h.context_buffer('cody') is None
    h.attach_context_buffer('cody', object())
    assert h.context_users() == ['cody']
    h.detach_context_buffer('cody')
    assert h.context_users() == []

    assert not h.compositor_attached
    h.attach_compositor(object())
    assert h.compositor_attached
    h.detach_compositor()
    assert not h.compositor_attached

    # a stub Tesla, registered exactly the way a real one would be — a
    # nested ToolsetRegistry underneath, same class as the harness's own.
    # Naming convention: a nested handler is named 'facename.tool' so
    # handled_by (which reports the DEEPEST handler that actually answered,
    # not just the top-level Face) stays self-documenting either way.
    #
    # NOT kvm here, deliberately (Cody, 2026-08-24): KVM is a basic INPUT
    # function the Monad/Ptolemy needs directly to interact with anything
    # at all — it lives with Ptolemy, not behind a reach()-for-it capability
    # a moment might or might not grant. What DOES belong on Tesla's own
    # registry is the reach-for-it stuff — hole-punch rendezvous, sensor
    # streams, device discovery — genuinely optional tools, not a basic
    # sense/actuator every turn needs. 'network' (HolePunch) stands in here.
    tesla_tools = ToolsetRegistry()
    tesla_tools.register('tesla.holepunch', ['network'],
                         lambda capability, action, **p: FaceResult(ok=False,
                             error='Tesla.HolePunch not wired yet — stub'))

    def _tesla_handle(capability, action, **params):
        return tesla_tools.reach(capability, action=action, **params)

    h.toolset_registry.register('tesla', ['network', 'sensor',
                                          'device_interface'], _tesla_handle)

    r = h.reach('network', center='hands', action='punch', peer_id='ptolemy_local')
    assert r.handled_by == 'tesla.holepunch', r
    assert not r.ok and 'not wired yet' in r.error, r
    assert r.center == 'hands', r

    r2 = h.reach('research', center='eye', query='does not exist yet')
    assert not r2.ok and 'no handler registered' in r2.error, r2
    assert r2.center == 'eye', r2

    assert len(h.calls_by_center('hands')) == 1
    assert len(h.calls_by_center('eye')) == 1
    assert h.calls_by_center('eye')[0] is r2

    # present() — no viewport registered yet, falls back to stdout, still logged
    pr = h.present('smoke-test viewport fallback line', center='eye')
    assert pr.ok and pr.handled_by == 'stdout_fallback' and pr.center == 'eye', pr
    assert h.calls_by_center('eye')[-1] is pr

    # present() — a real viewport Face registered, present() reaches it instead
    h.toolset_registry.register('curses_viewport', ['viewport'],
                                lambda capability, action, **p: FaceResult(
                                    ok=True, data=f"[viewport] {p.get('content')}"))
    pr2 = h.present('routed through a registered viewport', center='hands')
    assert pr2.ok and pr2.handled_by == 'curses_viewport', pr2
    assert pr2.data == '[viewport] routed through a registered viewport', pr2

    try:
        h.lineage
        lineage_ok = True
    except RuntimeError as e:
        lineage_ok = False
        print(f'[lineage] not reachable (fine if SFR repo path differs): {e}')
    if lineage_ok:
        assert hasattr(h.lineage, 'TIERS') and hasattr(h.lineage, 'decompose')
        print(f"lineage engine reachable: {len(h.lineage.TIERS)} tiered operations known")

    class _FakeRelation:
        name, tier, claim = 'demo.smoke_test', 1, 'a fake relation for the smoke test'
        descends = 'ADD, SCALE'
        status = type('S', (), {'value': 'HOLDS'})()
        detail = '[fake] nothing measured, this is a formatting test'

    print(h.format_derivation(_FakeRelation()))
    print()
    print(h.justify_gate('reading a public FITS archive'))
    print("\nharness.py: smoke test passed.")
