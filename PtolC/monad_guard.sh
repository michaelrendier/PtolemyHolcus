#!/bin/bash
# monad_guard.sh — protect an installed monad3_c.bin from being clobbered by a
# differently-structured build. Called by the ptol.c build/install step before
# it copies a new monad3_c.bin next to the binary.
#
#   monad_guard.sh <candidate monad3_c.bin> <installed path>
#
# Refuses (exit 3) if the installed file exists, is a valid MONAD3C store, and
# the candidate's stamped spec differs — UNLESS PTOL_MONAD_OVERRIDE=1, in which
# case the installed file is backed up and replaced.
set -euo pipefail
CAND="${1:?candidate monad3_c.bin}"
DEST="${2:?installed path}"
MAGIC='MONAD3C'

stamp() { head -c 12 "$1" 2>/dev/null | tr -d '\0'; }   # magic(8) + version(u32) prefix

if [ ! -f "$DEST" ]; then
    cp "$CAND" "$DEST"; echo "monad_guard: installed (no prior store)"; exit 0
fi
if [ "$(head -c 7 "$DEST")" != "$MAGIC" ]; then
    if [ "${PTOL_MONAD_OVERRIDE:-0}" = "1" ]; then
        cp "$DEST" "$DEST.bak-$(date +%Y%m%d-%H%M%S)"; cp "$CAND" "$DEST"
        echo "monad_guard: OVERRIDE — non-MONAD3C file backed up and replaced"; exit 0
    fi
    echo "monad_guard: REFUSING — $DEST is not a MONAD3C store. Set PTOL_MONAD_OVERRIDE=1 to replace." >&2
    exit 3
fi
if [ "$(stamp "$CAND")" = "$(stamp "$DEST")" ]; then
    cp "$CAND" "$DEST"; echo "monad_guard: same spec — refreshed in place"; exit 0
fi
if [ "${PTOL_MONAD_OVERRIDE:-0}" = "1" ]; then
    cp "$DEST" "$DEST.bak-$(date +%Y%m%d-%H%M%S)"; cp "$CAND" "$DEST"
    echo "monad_guard: OVERRIDE — spec changed; old store backed up and replaced"; exit 0
fi
echo "monad_guard: REFUSING — installed store has a different spec stamp than the candidate." >&2
echo "             the existing monad would be mutilated by this build structure." >&2
echo "             Set PTOL_MONAD_OVERRIDE=1 to replace it (a backup is made first)." >&2
exit 3
