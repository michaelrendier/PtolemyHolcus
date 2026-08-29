#!/usr/bin/env python3
"""
build_monad_bin.py — the single Monad brain, decomposed and rebuildable.

The C monad (ptol.c) reads ONE store. This script folds every domain factor
bin into one `monad.bin` that is BOTH the vocabulary (word -> Horner/prime/γ
address) AND the knowledge store (β-field + E + A-matrix co-occurrence
topology). Every word keeps its deterministic address, so the union is
collision-free and order-independent — the same `monad.bin` is produced from
the same factor set every time.

  test    : load each factor bin standalone, report stats + a generate() smoke
  merge   : additive union of all factor bins -> monad.bin
  verify  : load the merged monad.bin, report, generate()
  manifest: (re)write manifest.json describing the factor set

Factor bins live in ~/.ptolemy/ (built by corpus ingestion). GitHub can't hold
a 60 MB merged bin as a release asset comfortably, but each factor bin is
< 100 MB and uploads fine — ship the factors + this script, rebuild on-box.

Usage:
  python3 build_monad_bin.py test
  python3 build_monad_bin.py merge   [--out ~/.ptolemy/monad.bin] [--weight-map name=w,...]
  python3 build_monad_bin.py verify  [--bin ~/.ptolemy/monad.bin]
  python3 build_monad_bin.py manifest
"""
import argparse
import hashlib
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from VAPMIP.monad import Engine  # noqa: E402


def _speak_text(out):
    if isinstance(out, str):
        return out
    if isinstance(out, dict):
        for k in ("text", "response", "output", "speak", "sentence", "words"):
            v = out.get(k)
            if isinstance(v, str) and v.strip():
                return v
            if isinstance(v, (list, tuple)) and v:
                return " ".join(w[0] if isinstance(w, (list, tuple)) else str(w) for w in v)
        return str({k: out[k] for k in list(out)[:3]})
    if isinstance(out, (list, tuple)):
        return " ".join(w[0] if isinstance(w, (list, tuple)) else str(w) for w in out)
    return repr(out)[:120]

PTOL = os.path.expanduser("~/.ptolemy")
HERE = os.path.dirname(os.path.abspath(__file__))

# The factor set, in fold order. english first (largest base vocab), then the
# domain specialisations, then the project's own corpora. weight scales the
# contribution of that bin's β and edges into the union.
FACTORS = [
    ("monad_english.bin",      1.0),
    ("monad_foundations.bin",  1.0),
    ("monad_meaning.bin",      1.0),
    ("monad_mathematics.bin",  1.0),
    ("monad_physics.bin",      1.0),
    ("monad_python.bin",       1.0),
    ("monad_c.bin",            1.0),
    ("monad_engineering.bin",  1.2),   # this project's own detailed self-description
    ("monad_war.bin",          1.2),   # the prime-directive conversations + Caesar corpus
]
OUT_DEFAULT = os.path.join(PTOL, "monad.bin")


def _load_state(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def _sha(path, n=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while (b := f.read(n)):
            h.update(b)
    return h.hexdigest()


def _stats(state):
    beta = state.get("beta", [])
    A = state.get("A", [])
    return {
        "vocab": state.get("n", len(state.get("words", []))),
        "edges": sum(len(d) for d in A),
        "beta_mean": (sum(beta) / len(beta)) if beta else 0.0,
        "beta_gt_half": sum(1 for b in beta if b > 0.5),
    }


def cmd_test(_args):
    print("=" * 70)
    print("  FACTOR BIN TEST — each store standalone in VAPMIP.monad")
    print("=" * 70)
    for name, _w in FACTORS:
        p = os.path.join(PTOL, name)
        if not os.path.exists(p):
            print(f"  {name:26} MISSING")
            continue
        e = Engine()
        t0 = time.time()
        e.load_bin(p)
        st = _stats({"n": e.crank.n, "words": e.crank._words,
                     "beta": e.crank._beta, "A": e.crank._A})
        # generate() smoke — a neutral prompt, short
        try:
            out = e.generate("the shape of the", n_words=12, learn_prompt=False)
            speak = _speak_text(out)
        except Exception as exc:
            speak = f"(generate error: {exc})"
        dt = time.time() - t0
        print(f"  {name:26} vocab={st['vocab']:>7,}  edges={st['edges']:>9,}  "
              f"β̄={st['beta_mean']:.4f}  ({dt:.1f}s)")
        print(f"       speak: {speak[:110]}")
    print()


def cmd_merge(args):
    weights = dict((n, w) for n, w in FACTORS)
    if args.weight_map:
        for kv in args.weight_map.split(","):
            k, v = kv.split("=")
            weights[k if k.endswith(".bin") else k + ".bin"] = float(v)

    print("=" * 70)
    print("  MERGE — additive union of the factor set -> monad.bin")
    print("=" * 70)
    U_vocab, U_words, U_beta, U_E, U_age, U_A = {}, [], [], [], [], []
    provenance = []
    for name, _w in FACTORS:
        w = weights[name]
        p = os.path.join(PTOL, name)
        if not os.path.exists(p):
            print(f"  {name:26} MISSING — skipped")
            continue
        st = _load_state(p)
        words = st["words"]
        beta = st.get("beta", [])
        E = st.get("E", [])
        age = st.get("age", [0.0] * len(words))
        A = st.get("A", [])
        remap = {}
        for old, word in enumerate(words):
            if word not in U_vocab:
                new = len(U_words)
                U_vocab[word] = new
                U_words.append(word)
                U_beta.append(min(beta[old] * w if old < len(beta) else 0.0, 1.0))
                U_E.append(E[old] if old < len(E) else 0.0)
                U_age.append(age[old] if old < len(age) else 0.0)
                U_A.append({})
            else:
                new = U_vocab[word]
                if old < len(beta):
                    U_beta[new] = min(U_beta[new] + beta[old] * w, 1.0)
            remap[old] = new
        for old_src, edges in enumerate(A):
            ns = remap.get(old_src)
            if ns is None:
                continue
            for old_dst, wt in edges.items():
                nd = remap.get(old_dst)
                if nd is None or nd == ns:
                    continue
                U_A[ns][nd] = min(U_A[ns].get(nd, 0.0) + wt * w, 1.0)
        s = _stats(st)
        provenance.append({"bin": name, "weight": w, "sha256": _sha(p),
                           "vocab": s["vocab"], "edges": s["edges"]})
        print(f"  + {name:24} w={w:<4}  running vocab={len(U_words):>7,}  "
              f"edges={sum(len(d) for d in U_A):>9,}")

    state = {
        "version": "monad.bin/merged",
        "vocab": U_vocab, "words": U_words, "beta": U_beta, "E": U_E,
        "A": U_A, "age": U_age, "n": len(U_words),
        "psi_prev": [0.0] * 16, "word_count": sum(1 for _ in U_words),
        "correction_mask": {}, "fire_count": [0] * len(U_words),
        "stratum": [0] * len(U_words),
        "_provenance": provenance, "_built": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with open(args.out, "wb") as f:
        pickle.dump(state, f, protocol=4)
    print(f"\n  wrote {args.out}  ({os.path.getsize(args.out):,} B)")
    print(f"  vocab {len(U_words):,}   edges {sum(len(d) for d in U_A):,}   "
          f"β>0.5: {sum(1 for b in U_beta if b > 0.5):,}")
    cmd_manifest(args, provenance=provenance, out_bin=args.out)


def cmd_verify(args):
    e = Engine()
    e.load_bin(args.bin)
    st = _stats({"n": e.crank.n, "words": e.crank._words,
                 "beta": e.crank._beta, "A": e.crank._A})
    print(f"  {args.bin}")
    print(f"  vocab {st['vocab']:,}   edges {st['edges']:,}   "
          f"β̄ {st['beta_mean']:.4f}   β>0.5 {st['beta_gt_half']:,}")
    for pr in ("the shape of the", "riemann zeta", "the monad speaks",
               "prime directive", "add scale sign"):
        try:
            out = e.generate(pr, n_words=14, learn_prompt=False)
            speak = _speak_text(out)
        except Exception as exc:
            speak = f"(error: {exc})"
        print(f"    «{pr}» → {speak}")


def cmd_manifest(args, provenance=None, out_bin=None):
    out_bin = out_bin or getattr(args, "out", OUT_DEFAULT)
    if provenance is None:
        provenance = []
        for name, w in FACTORS:
            p = os.path.join(PTOL, name)
            if os.path.exists(p):
                provenance.append({"bin": name, "weight": w,
                                   "sha256": _sha(p),
                                   "bytes": os.path.getsize(p)})
    man = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "target": os.path.basename(out_bin),
        "note": "monad.bin = union(factor bins). Vocabulary AND knowledge "
                "store. Every word address is deterministic (Horner→prime→γ), "
                "so the union is order-independent and reproducible. Rebuild "
                "on-box: python3 build_monad_bin.py merge",
        "factors": provenance,
    }
    mp = os.path.join(HERE, "manifest.json")
    with open(mp, "w") as f:
        json.dump(man, f, indent=2)
    print(f"  manifest: {mp}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("test").set_defaults(fn=cmd_test)
    m = sub.add_parser("merge")
    m.add_argument("--out", default=OUT_DEFAULT)
    m.add_argument("--weight-map", default="")
    m.set_defaults(fn=cmd_merge)
    v = sub.add_parser("verify")
    v.add_argument("--bin", default=OUT_DEFAULT)
    v.set_defaults(fn=cmd_verify)
    mn = sub.add_parser("manifest")
    mn.add_argument("--out", default=OUT_DEFAULT)
    mn.set_defaults(fn=cmd_manifest)
    a = ap.parse_args()
    a.fn(a)
