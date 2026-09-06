#!/usr/bin/env bash
# datasets/fetch.sh — reproducible re-download of the grammar corpora that
# feed monad_sentences.bin.  The corpora themselves are .gitignored (see
# ../.gitignore); this script + README.md are the tracked provenance.
#
# Run from anywhere:  bash datasets/fetch.sh
set -euo pipefail
cd "$(dirname "$0")"

clone() {  # name  url  keep-glob...
  local name="$1" url="$2"; shift 2
  if [ -d "$name" ]; then echo "  $name exists — skip (rm -rf to refresh)"; return; fi
  echo "  cloning $name"
  git clone --depth 1 -q "$url" "$name"
  ( cd "$name"; git rev-parse --short HEAD > .COMMIT; rm -rf .git )
}

clone UD_English-EWT  https://github.com/UniversalDependencies/UD_English-EWT
clone UD_English-GUM  https://github.com/UniversalDependencies/UD_English-GUM
clone verbnet         https://github.com/cu-clear/verbnet
clone propbank-frames https://github.com/propbank/propbank-frames

# trim to payload only
for d in UD_English-EWT UD_English-GUM; do
  [ -d "$d" ] && find "$d" -mindepth 1 -maxdepth 1 \
    ! -name 'en_*-ud-*.conllu' ! -name 'README.md' ! -name 'LICENSE.txt' ! -name '.COMMIT' \
    -exec rm -rf {} +
done
[ -d verbnet ] && ( cd verbnet && find . -mindepth 1 -maxdepth 1 \
  ! -name 'verbnet3.4' ! -name 'README.md' ! -name '.COMMIT' -exec rm -rf {} + )
[ -d propbank-frames ] && ( cd propbank-frames && find . -mindepth 1 -maxdepth 1 \
  ! -name 'frames' ! -name 'dtds' ! -name 'LICENSE' ! -name 'README.md' ! -name '.COMMIT' -exec rm -rf {} + )

echo
echo "FrameNet 1.7 and the Penn Treebank are NOT fetched here:"
echo "  FrameNet  — ICSI licence, register at framenet.icsi.berkeley.edu"
echo "              (or: nltk.download('framenet_v17') for the redistributable subset)"
echo "  Penn TB   — LDC licence, paid.  Free 10% WSJ sample: nltk.download('treebank')"
echo
du -sh ./*/
