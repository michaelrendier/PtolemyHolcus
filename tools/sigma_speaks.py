#!/usr/bin/env python3
"""
sigma_speaks.py — Ask ptol to respond through every operator.

Usage:
    python3 sigma_speaks.py "your prompt"
    python3 sigma_speaks.py --no-english "your prompt"

--no-english: temporarily hide all English-language operators before asking.
              Restores them after. Tests whether Sigma_RB can speak English
              without the English vocabulary toolset.

The geometry is computed ONCE. Every operator sees the same sedenion scalars.
The path is fixed. Only the window onto it changes.
"""

import sys, os, subprocess, glob, shutil, pickle

BIN_DIR  = '/media/rendier/0123-4567/PTorrent/bin_archive/clean'
PTOL_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'PtolC', 'ptol')
LAYER_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'PtolC', 'ptol_layer.py')

ENGLISH_OPS = ['holcus_monad_english.bin', 'holcus_monad_englishwordnet.bin']
HIDE_SUFFIX = '.HIDDEN'

def hide_english():
    hidden = []
    for name in ENGLISH_OPS:
        src = os.path.join(BIN_DIR, name)
        if os.path.exists(src):
            dst = src + HIDE_SUFFIX
            shutil.move(src, dst)
            hidden.append((dst, src))
            print(f"  hidden: {name}")
    return hidden

def restore_english(hidden):
    for dst, src in hidden:
        if os.path.exists(dst):
            shutil.move(dst, src)
            print(f"  restored: {os.path.basename(src)}")

def get_scalars(prompt):
    result = subprocess.run(
        [PTOL_BIN, '-r', prompt],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split('\n')
    sep = lines.index('---') if '---' in lines else 16
    scalars_raw = '\n'.join(lines[:sep])
    primes_raw  = '\n'.join(lines[sep+1:]) if sep < len(lines) else ''
    return result.stdout.strip()   # full raw output to pipe to ptol_layer.py

def run_layer(raw_scalars, layer):
    proc = subprocess.run(
        ['python3', LAYER_PY, '--stdin', '--layer', layer],
        input=raw_scalars,
        capture_output=True, text=True
    )
    return proc.stdout.strip()

def scan_layers():
    layers = {}
    for path in glob.glob(os.path.join(BIN_DIR, 'holcus_monad_*.bin')):
        name = os.path.basename(path)
        key  = name[len('holcus_monad_'):-len('.bin')]
        layers[key] = path
    return layers

def main():
    args = sys.argv[1:]
    no_english = '--no-english' in args
    if no_english:
        args.remove('--no-english')

    if not args:
        print("Usage: python3 sigma_speaks.py [--no-english] \"prompt\"")
        sys.exit(1)

    prompt = ' '.join(args)

    print("=" * 60)
    print(f"PROMPT: {prompt}")
    print("=" * 60)

    # Compute geometry ONCE
    raw = get_scalars(prompt)
    print(f"\n[geometry computed — {len(raw.splitlines())} lines]\n")

    hidden = []
    if no_english:
        print("[ hiding English operators ]")
        hidden = hide_english()
        print()

    layers = scan_layers()
    order  = sorted(layers.keys())

    for layer in order:
        print(f"\n{'─'*60}")
        print(f"OPERATOR: <{layer.capitalize()}>")
        print('─' * 60)
        out = run_layer(raw, layer)
        print(out)

    if hidden:
        print(f"\n[ restoring English operators ]")
        restore_english(hidden)

    print("\n" + "=" * 60)
    print("done.")

if __name__ == '__main__':
    main()
