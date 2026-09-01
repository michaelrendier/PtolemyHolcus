"""
monad_bus.py — the language-blind Monad backend + the threading/memory governor.

Two things live here, both imported by `harness.py` and by the python monad
(`rotary_rerun_boxkite_monad.RotaryBoxKiteMonad`):

  1. MonadBackend — the harness is BLIND to whether the Monad is the C binary
     (the `ptolemy` daemon) or the python object. `load_monad(prefer)` picks
     one, or a NullMonadBackend (warn, never fault), and REPORTS which.

  2. ResourceGovernor — Ptolemy is the one doing threading management, so
     memory management falls out of it: admission control on a per-job RAM
     estimate against a fixed ceiling. Cody's rule of thumb:

         CEILING = MemTotal + min(SwapTotal, MemTotal // 2)

     ("the general peak of a computer's ability to not get bogged down
     treating a file like RAM is to make swap about half the RAM"). A job is
     admitted only if a thread slot is free AND committed RAM + its estimate
     stays under CEILING AND committed bandwidth + its cost stays under the
     available link. Jobs that don't fit WAIT in their priority tier — they
     never die. The GC does the rest, once admission keeps the peak bounded.

Nothing here raises on a missing connection. That is the standing rule.
"""
from __future__ import annotations

import gc
import os
import socket
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════
#  ResourceGovernor — threading admission, memory falls out of it
# ═══════════════════════════════════════════════════════════════════════════

def _meminfo() -> Dict[str, int]:
    """/proc/meminfo in BYTES. Falls back to conservative defaults off-Linux."""
    out: Dict[str, int] = {}
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                k, _, rest = line.partition(':')
                out[k.strip()] = int(rest.strip().split()[0]) * 1024
    except OSError:
        pass
    out.setdefault('MemTotal', 2 * 1024 ** 3)
    out.setdefault('MemAvailable', out['MemTotal'] // 2)
    out.setdefault('SwapTotal', 0)
    out.setdefault('SwapFree', 0)
    return out


# tiers mirror PtolBus's rotary semaphore: 0 system, 1 user, 2+ autonomous
TIER_SYSTEM, TIER_USER, TIER_AUTO = 0, 1, 2


@dataclass
class Job:
    """A unit of routed work with its cost estimate. `ram_peak` is the
    resident bytes the job is expected to peak at (for a fetch+parse:
    content_length x parse_blowup; a streamed download is ~O(1))."""
    name: str
    tier: int = TIER_USER
    ram_peak: int = 0
    bw_cost: float = 0.0            # bytes/sec of link the job will consume
    _admitted_at: float = 0.0


class ResourceGovernor:
    """Threading bus + memory manager in one object. Thread-safe."""

    def __init__(self, max_slots: Optional[int] = None,
                 bw_cap: Optional[float] = None,
                 swap_rule: bool = True) -> None:
        mi = _meminfo()
        self._mi0 = mi
        if swap_rule:
            self.CEILING = mi['MemTotal'] + min(mi['SwapTotal'], mi['MemTotal'] // 2)
        else:
            self.CEILING = mi['MemTotal'] + mi['SwapTotal']
        self.max_slots = int(max_slots or os.environ.get(
            'PTOL_MAX_SLOTS', os.cpu_count() or 4))
        self.bw_cap = float(bw_cap or os.environ.get(
            'PTOL_BW_CAP', 50 * 1024 * 1024))     # 50 MB/s default link estimate
        self._cv = threading.Condition()
        self._running: Dict[int, Job] = {}
        self._seq = 0

    # ── live view ────────────────────────────────────────────────────────
    def mem_live(self) -> Tuple[int, int]:
        mi = _meminfo()
        return mi['MemAvailable'], mi['SwapFree']

    def _committed_ram(self) -> int:
        return sum(j.ram_peak for j in self._running.values())

    def _committed_bw(self) -> float:
        return sum(j.bw_cost for j in self._running.values())

    def bw_avail(self) -> float:
        return max(0.0, self.bw_cap - self._committed_bw())

    def headroom_ok(self, est_bytes: int) -> bool:
        """Standalone check for the BARE monad: would `est_bytes` of new
        resident work keep us under CEILING and off the live floor?"""
        with self._cv:
            if self._committed_ram() + est_bytes > self.CEILING:
                return False
        avail, swapfree = self.mem_live()
        return (avail + swapfree - est_bytes) > (128 * 1024 * 1024)   # 128 MB floor

    # ── admission ────────────────────────────────────────────────────────
    def admit(self, job: Job) -> bool:
        """Non-blocking: is there room for `job` RIGHT NOW? (slots ∧ RAM ∧ bw)"""
        with self._cv:
            return self._admit_locked(job)

    def _admit_locked(self, job: Job) -> bool:
        if len(self._running) >= self.max_slots:
            return False
        if self._committed_ram() + job.ram_peak > self.CEILING:
            return False
        if self._committed_bw() + job.bw_cost > self.bw_cap:
            return False
        return True

    @contextmanager
    def guard(self, job: Job, block: bool = True, timeout: Optional[float] = None):
        """Run a routed job under admission control. Blocks (by tier: lower
        tier wakes first) until it fits, unless block=False, then raises
        TimeoutError only if an explicit timeout elapses. Frees the slot and
        gc.collect()s on exit — the manager never frees memory itself, it
        just stops admitting work that would blow the ceiling."""
        deadline = None if timeout is None else time.time() + timeout
        with self._cv:
            while not self._admit_locked(job):
                if not block:
                    raise RuntimeError(f"governor: no room for {job.name!r} "
                                       f"(running={len(self._running)}/{self.max_slots}, "
                                       f"ram={self._committed_ram()}/{self.CEILING})")
                wait = None if deadline is None else max(0.0, deadline - time.time())
                if wait == 0.0:
                    raise TimeoutError(f"governor: {job.name!r} waited out {timeout}s")
                # crude tier fairness: higher tiers back off a touch longer
                self._cv.wait(timeout=(wait if wait is not None else 0.25 + 0.1 * job.tier))
                if wait is not None:
                    deadline = deadline  # loop re-checks
            self._seq += 1
            key = self._seq
            job._admitted_at = time.time()
            self._running[key] = job
        try:
            yield job
        finally:
            with self._cv:
                self._running.pop(key, None)
                self._cv.notify_all()
            gc.collect()

    # ── reporting ────────────────────────────────────────────────────────
    def snapshot(self) -> Dict[str, Any]:
        with self._cv:
            avail, swapfree = self.mem_live()
            return {
                'ceiling_bytes': self.CEILING,
                'ceiling_gib': round(self.CEILING / 1024 ** 3, 2),
                'mem_total_gib': round(self._mi0['MemTotal'] / 1024 ** 3, 2),
                'swap_total_gib': round(self._mi0['SwapTotal'] / 1024 ** 3, 2),
                'live_headroom_gib': round((avail + swapfree) / 1024 ** 3, 2),
                'max_slots': self.max_slots,
                'running': len(self._running),
                'committed_ram_mib': round(self._committed_ram() / 1024 ** 2, 1),
                'bw_cap_mibps': round(self.bw_cap / 1024 ** 2, 1),
                'bw_avail_mibps': round(self.bw_avail() / 1024 ** 2, 1),
                'jobs': [j.name for j in self._running.values()],
            }


# ═══════════════════════════════════════════════════════════════════════════
#  MonadBackend — the harness is blind to C-vs-python
# ═══════════════════════════════════════════════════════════════════════════

class MonadBackend:
    name = 'abstract'

    def alive(self) -> bool: ...
    def learn(self, text: str, w_sem: float = 1.0,
              w_ctx: Optional[float] = None) -> int: ...
    def persist(self) -> bool: ...


class NullMonadBackend(MonadBackend):
    """No monad reachable. Every call is a no-op. Warn once, never fault."""
    name = 'null'

    def __init__(self, log: Optional[Callable[[str], None]] = None) -> None:
        if log:
            log("monad_bus: no Monad backend available — ingest is a no-op "
                "(warning, not a fault; boot continues)")

    def alive(self) -> bool:
        return False

    def learn(self, text: str, w_sem: float = 1.0,
              w_ctx: Optional[float] = None) -> int:
        return 0

    def persist(self) -> bool:
        return False


class CMonadBackend(MonadBackend):
    """The C binary — the `ptolemy` daemon. Ingest is a framed OBSERVE line
    on the FIFO (spool fallback), exactly as the Claude Code hooks do it.
    Persistence is the daemon's own repack; not ours."""
    name = 'c:ptolemy-daemon'

    def __init__(self, fifo: str, sock: str, spool: str) -> None:
        self.fifo, self.sock, self.spool = fifo, sock, spool

    def alive(self) -> bool:
        try:
            fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
            os.close(fd)
            return True
        except OSError:
            pass
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.25)
            s.connect(self.sock)
            s.close()
            return True
        except OSError:
            return False

    def learn(self, text: str, w_sem: float = 1.0,
              w_ctx: Optional[float] = None, cls: str = 'web') -> int:
        sents = [ln.strip() for ln in text.replace('\r', ' ').split('\n')
                 if ln.strip()] or [text.strip()]
        msg = (f"{cls}\n" + "\n".join(sents) + "\n.\n").encode('utf-8', 'replace')
        try:
            fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
            try:
                os.write(fd, msg)
            finally:
                os.close(fd)
            return len(text.split())
        except OSError:
            try:
                os.makedirs(os.path.dirname(self.spool), exist_ok=True)
                with open(self.spool, 'a', encoding='utf-8') as f:
                    f.write(msg.decode('utf-8', 'replace'))
                return len(text.split())
            except OSError:
                return 0

    def persist(self) -> bool:
        return False


class PyMonadBackend(MonadBackend):
    """The python monad — RotaryBoxKiteMonad (or any duck-compatible object).
    Ingest goes through `monad_english_io.hear` on its combined store, or a
    `.crank.learn` if that is what it exposes."""

    def __init__(self, monad_obj: Any) -> None:
        self._m = monad_obj
        self.name = f"python:{type(monad_obj).__name__}"

    def alive(self) -> bool:
        return self._m is not None

    def learn(self, text: str, w_sem: float = 1.0,
              w_ctx: Optional[float] = None) -> int:
        m = self._m
        store = getattr(m, 'store', None)
        if store is not None:
            try:
                from monad_english_io import hear
                hear(getattr(store, 'english', store), text, echo=0)
                return len(text.split())
            except Exception:
                pass
        crank = getattr(m, 'crank', None)
        if crank is not None and hasattr(crank, 'learn'):
            try:
                return crank.learn(text, weight=w_sem,
                                   w_ctx=(w_ctx if w_ctx is not None else w_sem))
            except TypeError:
                return crank.learn(text, weight=w_sem)
        return 0

    def persist(self) -> bool:
        for meth in ('checkpoint', 'persist', 'save'):
            fn = getattr(self._m, meth, None)
            if callable(fn):
                try:
                    fn()
                    return True
                except Exception:
                    return False
        return False


def load_monad(prefer: str = 'auto',
               fifo: Optional[str] = None,
               sock: Optional[str] = None,
               spool: Optional[str] = None,
               log: Optional[Callable[[str], None]] = None
               ) -> Tuple[MonadBackend, Dict[str, Any]]:
    """Pick a backend at `prefer` ∈ {'auto','c','python'} and REPORT.
    'auto' = the C daemon if reachable, else the python monad, else Null.
    Never raises — an unreachable backend is a warning and a NullMonadBackend."""
    fifo = fifo or os.path.expanduser('~/.ptolemy/monad.observe.fifo')
    sock = sock or os.path.expanduser('~/.ptolemy/ptolemy.sock')
    spool = spool or os.path.expanduser('~/.ptolemy/observe.spool')

    def _try_c() -> Optional[MonadBackend]:
        b = CMonadBackend(fifo, sock, spool)
        return b if b.alive() else None

    def _try_py() -> Optional[MonadBackend]:
        try:
            import importlib
            mod = importlib.import_module('rotary_rerun_boxkite_monad')
            return PyMonadBackend(mod.RotaryBoxKiteMonad())
        except Exception as e:      # noqa: BLE001 — any failure → warn + Null
            if log:
                log(f"monad_bus: python monad unavailable ({e})")
            return None

    order = {'auto': ('c', 'python'), 'c': ('c',),
             'python': ('python',), 'py': ('python',)}.get(prefer, ('c', 'python'))
    for kind in order:
        be = _try_c() if kind == 'c' else _try_py()
        if be is not None:
            rpt = {'chosen': be.name, 'why': f'prefer={prefer}', 'alive': be.alive()}
            if log:
                log(f"monad_bus: backend = {be.name} (prefer={prefer})")
            return be, rpt

    be = NullMonadBackend(log=log)
    return be, {'chosen': 'null',
                'why': f'prefer={prefer}, none reachable', 'alive': False}
