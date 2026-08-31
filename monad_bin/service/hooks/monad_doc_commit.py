#!/usr/bin/env python3
"""
monad_doc_commit.py — git POST-commit hook: feed committed documentation
into the Monad as the 'document' class.

Runs AFTER the commit succeeds (never pre-commit, never on push), so it can
neither block nor fail a commit. Looks at the files the just-made commit
touched, keeps the documentation among them — wiki pages, READMEs, papers,
anything under docs/ — reads each, prose-sanitises it with
harness.strip_to_prose (same protocol as the conversation hook: fenced
code, tables, box-drawing, notation-dense lines dropped; the words for the
maths are expected to come from the calculator's narration, not raw
glyphs), and writes it non-blocking to the ingest FIFO, or the spool if the
daemon is away.

Install: point every ThePlace repo at the shared hook —
    monad_bin/service/install_git_hooks.sh
which sets core.hooksPath so this file is the post-commit hook everywhere.
"""
import os
import subprocess
import sys

_VAPMIP = os.environ.get(
    'MONAD_HARNESS_DIR',
    os.path.expanduser('~/Projects/ThePlace/VAPMIP'))
if _VAPMIP not in sys.path:
    sys.path.insert(0, _VAPMIP)

# what counts as documentation
_DOC_EXT = ('.md', '.rst', '.txt', '.tex', '.org')
_DOC_DIR_HINT = ('/docs/', '/wiki/', '/doc/', '/papers/', '/paper/')
_DOC_NAME_HINT = ('readme', 'changelog', 'paper', 'addendum', 'wiki',
                  'primer', 'notes')
# never ingest these even if they match above
_SKIP = ('license', 'licence', 'copying', 'authors', 'contributors',
         'code_of_conduct', 'third_party', 'vendor/', 'node_modules/')


def _is_doc(path):
    p = path.lower()
    if any(s in p for s in _SKIP):
        return False
    if not p.endswith(_DOC_EXT):
        return False
    base = os.path.basename(p)
    return (any(h in p for h in _DOC_DIR_HINT)
            or any(h in base for h in _DOC_NAME_HINT)
            or p.endswith(('.md', '.rst')))   # md/rst anywhere is prose enough


def _committed_files():
    try:
        # --root so the very first commit in a repo still lists its files;
        # --diff-filter=d drops deletions (nothing to read).
        out = subprocess.check_output(
            ['git', 'show', '--pretty=format:', '--name-only',
             '--diff-filter=d', '--root', 'HEAD'],
            text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    try:
        root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        root = '.'
    return [os.path.join(root, f.strip()) for f in out.splitlines() if f.strip()]


def _emit(msg, fifo, spool):
    data = msg.encode('utf-8', 'replace')
    try:
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
        try:
            if os.write(fd, data) == len(data):
                return True
        finally:
            os.close(fd)
    except OSError:
        pass
    try:
        os.makedirs(os.path.dirname(spool), exist_ok=True)
        with open(spool, 'a', encoding='utf-8') as f:
            f.write(msg)
        return True
    except OSError:
        return False


def main():
    docs = [p for p in _committed_files() if _is_doc(p) and os.path.exists(p)]
    if not docs:
        return
    try:
        from harness import (strip_to_prose, _sentences,
                             OBSERVE_FIFO, OBSERVE_SPOOL)
    except Exception:
        return
    sent = 0
    for path in docs:
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                body = f.read()
        except OSError:
            continue
        prose = strip_to_prose(body)
        if not prose.strip():
            continue
        msg = "document\n" + "\n".join(_sentences(prose)) + "\n.\n"
        if _emit(msg, OBSERVE_FIFO, OBSERVE_SPOOL):
            sent += 1
    if sent and not os.environ.get('MONAD_DOC_QUIET'):
        sys.stderr.write(f"[monad] fed {sent} committed doc(s) to the field\n")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
