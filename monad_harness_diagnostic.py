#!/usr/bin/env python3
"""
monad_harness_diagnostic.py — a real Monad, attached to a real Harness,
running Tesla in diagnostic mode: see what's there, use nothing.

This is the template call for visiting every other Face later (Callimachus,
Phaleron, Anaximander, ...) — same registration shape, different directory.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monad import Engine  # noqa: E402  — the real Monad, not a stub
from harness import Harness, FaceResult  # noqa: E402

TESLA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'PtolemyDesktop', 'Tesla')


def tesla_diagnostic_handler(capability, action, **params):
    """Registered under 'diagnostic' — reports what Tesla's directory
    offers via static discovery. Never imports Tesla's own files, so
    Sockets.py's blocking bind, HolePunchServer.py's SyntaxError, and
    Zork_Sentence_Parser.py's missing import cannot affect this call."""
    files = params['harness'].discover_face('tesla', TESLA_DIR)
    summary = []
    for path, info in files.items():
        base = os.path.basename(path)
        if info.parse_error:
            summary.append(f'  {base:32s} UNREADABLE — {info.parse_error}')
        else:
            classes = ', '.join(info.classes) or '(none)'
            summary.append(f'  {base:32s} classes: {classes}')
    return FaceResult(ok=True, data={'files': files, 'summary': summary})


def main():
    print('=== building a real Monad ===')
    monad = Engine()
    print(f'  Engine created, version={monad.version}, vocab={monad.crank.n}')

    print('\n=== attaching it to a real Harness ===')
    harness = Harness()
    harness.attach_monad(monad)
    print(f'  monad_attached={harness.monad_attached}')

    print('\n=== registering Tesla, diagnostic mode only ===')
    harness.toolset_registry.register(
        'tesla', ['network', 'sensor', 'device_interface', 'diagnostic'],
        lambda capability, action, **p: tesla_diagnostic_handler(
            capability, action, harness=harness, **p))

    print(f'  Tesla directory: {TESLA_DIR}')
    print(f'  exists: {os.path.isdir(TESLA_DIR)}')

    print('\n=== the Monad reaches for Tesla, capability=diagnostic ===')
    result = harness.reach('diagnostic', center='hands', action='list')

    print(f'\n  ok={result.ok}  handled_by={result.handled_by}  center={result.center}')
    print(f'  files discovered: {len(result.data["files"])}')
    print()
    for line in result.data['summary']:
        print(line)

    print(f'\n  call_log length: {len(harness.call_log)}')
    print(f'  calls by Paper\'s Hands so far: {len(harness.calls_by_center("hands"))}')

    print('\nNo Tesla tool was imported, connected to, or used. Diagnostic only.')


if __name__ == '__main__':
    main()
