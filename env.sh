#!/usr/bin/env bash
# env.sh — activate the VAPMIP analysis environment.
#
#   source env.sh          # activate
#   ./env.sh check         # verify the stack imports
#
# WHY A VENV (2026-08-15):
#   Same reason as BulletCluster/env.sh: the system Python has a numpy in
#   ~/.local shadowing the apt numpy, and every apt-built C extension is still
#   linked against the older ABI. pip refuses to fix it in place (PEP 668,
#   externally managed). So the engine's Python side runs in THIS venv.
#
#   The C monad (monad.c -> ptolemy-monad, `make`) is unaffected — it links
#   nothing from Python. _sedenion is pure Python and lives in engines/.
#
#   Test protocol stands: prototype in this venv's python3, port to the C
#   monad only on a significant result.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"

if [ "$1" = "check" ]; then
    "$VENV/bin/python" - <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
mods = ['numpy','scipy','matplotlib','sympy','mpmath','nltk',
        'PIL','PyQt5','pyaudio','html2text','ebooklib','odf']
bad = 0
for m in mods:
    try:
        mod = __import__(m)
        print(f"  OK    {m:<12} {getattr(mod,'__version__','?')}")
    except Exception as ex:
        bad += 1
        print(f"  FAIL  {m:<12} {type(ex).__name__}: {str(ex)[:60]}")
print("\nall good" if not bad else f"\n{bad} broken")
PY
    exit 0
fi

if [ ! -d "$VENV" ]; then
    echo "no venv at $VENV — create with:"
    echo "  python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt"
    return 1 2>/dev/null || exit 1
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
export PYTHONPATH="$HERE:$HERE/engines${PYTHONPATH:+:$PYTHONPATH}"
echo "VAPMIP env active — $(python --version), $VENV"
