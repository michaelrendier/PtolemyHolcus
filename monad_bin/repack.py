#!/usr/bin/env python3
"""
repack.py — fold the journal into the packed monad3_c.bin.

The daemon's input-size repack timer (a leaky integrator that fires at the
knee of its charge curve — see PtolC/daemon.c) spawns this, and so does the
harness's persist() path. It is the ONE serializer for the packed store, so
a daemon-triggered fold and a harness-triggered fold are byte-identical
(the pack invariant).

    python3 repack.py [--journal ~/.ptolemy/monad.bin]
                      [--out    VAPMIP/PtolC/monad3_c.bin]
                      [--guard  VAPMIP/PtolC/monad_guard.sh]   (default: on)
                      [--no-guard]

Reads the merged journal pickle, rebuilds the packed MONAD3C file via
monad_combine.write_c into a temp path, then hands it to monad_guard.sh
(which refuses a spec-stamp mismatch unless PTOL_MONAD_OVERRIDE=1, backing
up first) before an atomic rename into place.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_VAPMIP = os.path.dirname(_HERE)
if _VAPMIP not in sys.path:
    sys.path.insert(0, _VAPMIP)

DEFAULT_JOURNAL = os.path.expanduser('~/.ptolemy/monad.bin')
DEFAULT_OUT = os.path.join(_VAPMIP, 'PtolC', 'monad3_c.bin')
DEFAULT_GUARD = os.path.join(_VAPMIP, 'PtolC', 'monad_guard.sh')


def repack(journal: str = DEFAULT_JOURNAL, out: str = DEFAULT_OUT,
           guard: str | None = DEFAULT_GUARD) -> str:
    """Fold `journal` → packed `out`. Returns the path written. Raises on a
    missing journal or a guard refusal."""
    import monad_combine as mc

    if not os.path.exists(journal):
        raise FileNotFoundError(f"journal not found: {journal}")

    t0 = time.time()
    cm = mc.read(journal) if journal.endswith(('.bin', '.pkl')) and \
        _is_combined(journal) else _combined_from_english(mc, journal)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(out), suffix='.monad3c.tmp')
    os.close(fd)
    try:
        cm.path = tmp
        mc.write_c(cm, tmp)          # the one serializer

        if guard and os.path.exists(guard):
            r = subprocess.run(['bash', guard, tmp, out],
                               capture_output=True, text=True)
            sys.stderr.write(r.stdout + r.stderr)
            if r.returncode != 0:
                raise RuntimeError(
                    f"monad_guard.sh refused the repack (exit {r.returncode}); "
                    "set PTOL_MONAD_OVERRIDE=1 to replace a spec-mismatched store")
            # guard copied tmp → out itself
        else:
            os.replace(tmp, out)     # atomic, no guard configured

        # write_c also drops monad3c.h next to tmp — move it beside out
        tmp_h = os.path.join(os.path.dirname(tmp), 'monad3c.h')
        out_h = os.path.join(os.path.dirname(out), 'monad3c.h')
        if os.path.exists(tmp_h) and os.path.abspath(tmp_h) != os.path.abspath(out_h):
            os.replace(tmp_h, out_h)
    finally:
        for p in (tmp, os.path.join(os.path.dirname(tmp), 'monad3c.h')):
            if os.path.exists(p):
                try:
                    os.unlink(p)
                except OSError:
                    pass

    dt = time.time() - t0
    sz = os.path.getsize(out)
    sys.stderr.write(f"repack: {out}  ({sz:,} B, {dt:.1f}s)\n")
    return out


def _is_combined(path: str) -> bool:
    try:
        import pickle
        with open(path, 'rb') as f:
            head = pickle.load(f)
        return isinstance(head, dict) and head.get('magic') == 'MONAD3'
    except Exception:
        return False


def _combined_from_english(mc, journal: str):
    """The journal is a bare english/merged store (monad.bin), not a
    CombinedMonad — wrap it with the current wordnet + phonetic tables."""
    import monad_english_io as meio
    eng = meio.read(journal, use_cache=False)
    return mc.CombinedMonad(english=eng, wordnet=mc.read_boxkite_c(),
                            phonetic=mc.read_phonetic(), path=journal)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--journal', default=DEFAULT_JOURNAL)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--guard', default=DEFAULT_GUARD)
    ap.add_argument('--no-guard', action='store_true')
    a = ap.parse_args()
    try:
        repack(a.journal, a.out, None if a.no_guard else a.guard)
    except Exception as e:
        sys.stderr.write(f"repack: FAILED — {e}\n")
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
