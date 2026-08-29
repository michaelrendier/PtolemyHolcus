#!/usr/bin/env python3
"""
bootstrap.py — the canonical, project-first Monad build.

Every Monad, no matter who builds it, starts PROJECT FLUENT: the ContextPlease
engineering corpus (the primers, TODOs, and every repo's wiki / README / docs
prose — the entire engineering structure) is ingested FIRST and always. Only
then are the general-language bins and any user additions folded in. The result
is a Monad that can talk about its own functionality in both code-shape and
English before it has learned anything else.

  python3 bootstrap.py                 project-fluent build (project + general language)
  python3 bootstrap.py --project-only  the ContextPlease engineering corpus ONLY
  python3 bootstrap.py --add DIR ...   also ingest user prose trees (repeatable)
  python3 bootstrap.py --pack          also produce PtolC/monad3_c.bin for ptol.c
  python3 bootstrap.py --override      replace an existing bin of a DIFFERENT
                                       structure (backs it up first)

SAFETY: an existing ~/.ptolemy/monad.bin that was NOT produced by this
bootstrap (no marker, wrong kind, or a different SPEC_VERSION) is left
untouched — the build refuses and tells you to pass --override. --override
backs the old file up to monad.bin.bak-<timestamp> before writing.
"""
import argparse
import hashlib
import json
import os
import pickle
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(os.path.dirname(HERE), "corpus")
PTOL = os.path.expanduser("~/.ptolemy")
OUT = os.path.join(PTOL, "monad.bin")

SPEC_VERSION = 1
KIND = "project-fluent"

# repo-relative fallbacks so this runs from a fresh clone of either repo
THEPLACE = "/home/rendier/Projects/ThePlace"
for cand in (THEPLACE, os.path.join(THEPLACE, "VAPMIP")):
    if cand not in sys.path:
        sys.path.insert(0, cand)

# the project-fluency core — always built, always folded, in this order
PROJECT_FACTORS = ["monad_engineering.bin", "monad_war.bin", "monad_repos.bin"]
# general language — folded unless --project-only
GENERAL_FACTORS = ["monad_english.bin", "monad_foundations.bin", "monad_meaning.bin",
                   "monad_mathematics.bin", "monad_physics.bin",
                   "monad_python.bin", "monad_c.bin"]
WEIGHT = {"monad_engineering.bin": 1.2, "monad_war.bin": 1.2}   # project bins weigh more


def sh(*a):
    print("  $", " ".join(a))
    subprocess.run(a, check=True, cwd=HERE)


def sha_files(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        if os.path.exists(p):
            with open(p, "rb") as f:
                while (b := f.read(1 << 20)):
                    h.update(b)
    return h.hexdigest()


def ensure_project_bins():
    """(Re)build the three project factor bins from the ContextPlease corpuses."""
    print("── PROJECT FIRST — ingesting the ContextPlease engineering corpus ──")
    ca = os.path.join(CORPUS, "corpus_all.txt")
    cr = os.path.join(CORPUS, "corpus_repos.txt")
    if not (os.path.exists(ca) and os.path.exists(cr)):
        sys.exit(f"missing corpuses in {CORPUS} — run corpus_strip.py / corpus_repos.py first")
    # engineering + war + repos, via the ingest scripts (idempotent — they
    # rebuild the named bin from scratch each run)
    sh(sys.executable, "ingest.py")          # corpus_all.txt  -> monad_engineering.bin
    sh(sys.executable, "ingest_war.py")      # prime-directive primers -> monad_war.bin
    sh(sys.executable, "corpus_repos.py", "--ingest")   # corpus_repos.txt -> monad_repos.bin
    return sha_files([ca, cr])


def ingest_user_tree(path, n):
    """Strip + learn a user prose tree into monad_user_<n>.bin."""
    from corpus_strip import strip_file
    from VAPMIP.monad import Engine
    import glob
    e = Engine()
    files = []
    for ext in ("*.md", "*.txt", "*.rst"):
        files += glob.glob(os.path.join(path, "**", ext), recursive=True)
    total = 0
    for f in sorted(set(files)):
        blob = strip_file(f)
        for para in (p for p in blob.split("\n") if p.strip()):
            total += e.crank.learn(para, weight=1.0)
    ub = os.path.join(PTOL, f"monad_user_{n}.bin")
    e.save_session(ub)
    print(f"  + user tree {path}: {len(files)} files, {total:,} words -> {os.path.basename(ub)}")
    return os.path.basename(ub)


def _load(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def merge(factor_names, project_sha, user_bins):
    from build_monad_bin import _sha, _stats
    order = factor_names
    Uv, Uw, Ub, UE, Ua, UA = {}, [], [], [], [], []
    prov = []
    for name in order:
        p = os.path.join(PTOL, name)
        if not os.path.exists(p):
            print(f"  - {name}: MISSING, skipped")
            continue
        st = _load(p)
        w = WEIGHT.get(name, 1.0)
        words, beta = st["words"], st.get("beta", [])
        E, age, A = st.get("E", []), st.get("age", [0.0] * len(words)), st.get("A", [])
        remap = {}
        for old, word in enumerate(words):
            if word not in Uv:
                Uv[word] = len(Uw); Uw.append(word)
                Ub.append(min((beta[old] if old < len(beta) else 0.0) * w, 1.0))
                UE.append(E[old] if old < len(E) else 0.0)
                Ua.append(age[old] if old < len(age) else 0.0)
                UA.append({})
            else:
                k = Uv[word]
                if old < len(beta):
                    Ub[k] = min(Ub[k] + beta[old] * w, 1.0)
            remap[old] = Uv[word]
        for s_old, edges in enumerate(A):
            ns = remap.get(s_old)
            if ns is None:
                continue
            for d_old, wt in edges.items():
                nd = remap.get(d_old)
                if nd is None or nd == ns:
                    continue
                UA[ns][nd] = min(UA[ns].get(nd, 0.0) + wt * w, 1.0)
        prov.append({"bin": name, "weight": w, "sha256": _sha(p),
                     "project": name in PROJECT_FACTORS or name in user_bins,
                     **_stats(st)})
        print(f"  + {name:24} w={w:<4} vocab={len(Uw):>7,} edges={sum(len(d) for d in UA):>9,}")
    state = {
        "version": "monad.bin/merged", "vocab": Uv, "words": Uw, "beta": Ub,
        "E": UE, "A": UA, "age": Ua, "n": len(Uw), "psi_prev": [0.0] * 16,
        "word_count": len(Uw), "correction_mask": {}, "fire_count": [0] * len(Uw),
        "stratum": [0] * len(Uw), "_provenance": prov,
        "_built": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_bootstrap": {
            "kind": KIND, "spec_version": SPEC_VERSION,
            "project_corpus_sha256": project_sha,
            "project_first": True,
            "project_factors": [p for p in PROJECT_FACTORS + user_bins],
        },
    }
    return state


def safety_check(path, override):
    """Return True if it is safe to write `path`."""
    if not os.path.exists(path):
        return True
    try:
        old = _load(path)
        bs = old.get("_bootstrap") or {}
    except Exception:
        bs = {}
    same = bs.get("kind") == KIND and bs.get("spec_version") == SPEC_VERSION
    if same:
        print(f"  existing {os.path.basename(path)} is a compatible project-fluent "
              f"build (spec v{SPEC_VERSION}) — refreshing in place.")
        return True
    if override:
        bak = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, bak)
        print(f"  --override: existing {os.path.basename(path)} "
              f"(kind={bs.get('kind')!r} spec={bs.get('spec_version')!r}) "
              f"backed up to {os.path.basename(bak)}")
        return True
    print(f"\n  REFUSING to overwrite {path}")
    print(f"    it was not produced by this bootstrap "
          f"(kind={bs.get('kind')!r}, spec_version={bs.get('spec_version')!r}).")
    print(f"    pass --override to replace it (the old file is backed up first).")
    return False


def pack_c(override):
    """Produce PtolC/monad3_c.bin from the merged monad.bin (see SPEC.md §5)."""
    ptolc = os.path.join(THEPLACE, "VAPMIP", "PtolC")
    target = os.path.join(ptolc, "monad3_c.bin")
    if os.path.exists(target) and not override:
        with open(target, "rb") as f:
            magic = f.read(8)
        if magic != b"MONAD3C\x00":
            print(f"  REFUSING to overwrite {target}: unexpected magic {magic!r}. "
                  f"pass --override.")
            return
    if os.path.exists(target):
        shutil.copy2(target, f"{target}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    sys.path.insert(0, os.path.join(THEPLACE, "VAPMIP"))
    import monad_combine as mc
    cm = mc.CombinedMonad(
        english=mc._meio.read(OUT, use_cache=False),
        wordnet=mc.read_boxkite_c(), phonetic=mc.read_phonetic(),
        path=os.path.join(ptolc, "monad3.bin"))
    mc.write(cm, os.path.join(ptolc, "monad3.bin"))
    mc.write_c(cm, target)
    print(f"  packed {target}  ({os.path.getsize(target):,} B)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-only", action="store_true")
    ap.add_argument("--add", action="append", default=[], metavar="DIR")
    ap.add_argument("--pack", action="store_true")
    ap.add_argument("--override", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    project_sha = ensure_project_bins()

    user_bins = []
    for i, d in enumerate(a.add):
        user_bins.append(ingest_user_tree(d, i))

    factors = list(PROJECT_FACTORS)
    if not a.project_only:
        factors += GENERAL_FACTORS
    factors += user_bins

    print("\n── MERGE (project factors first) ──")
    state = merge(factors, project_sha, user_bins)

    if not safety_check(a.out, a.override):
        sys.exit(2)

    with open(a.out, "wb") as f:
        pickle.dump(state, f, protocol=4)
    n = state["n"]; edges = sum(len(d) for d in state["A"])
    print(f"\n  wrote {a.out}  ({os.path.getsize(a.out):,} B)")
    print(f"  {KIND} spec v{SPEC_VERSION}  ·  {n:,} words  ·  {edges:,} edges")
    proj = [p['bin'] for p in state['_provenance'] if p['project']]
    print(f"  project-first factors: {', '.join(proj)}")

    man = {"generated": state["_built"], "bootstrap": state["_bootstrap"],
           "factors": state["_provenance"]}
    with open(os.path.join(os.path.dirname(HERE), "manifest.json"), "w") as f:
        json.dump(man, f, indent=2)

    if a.pack:
        print("\n── PACK for ptol.c ──")
        pack_c(a.override)


if __name__ == "__main__":
    main()
