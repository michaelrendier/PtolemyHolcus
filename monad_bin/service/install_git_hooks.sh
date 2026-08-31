#!/bin/bash
# install_git_hooks.sh — point every ThePlace repo's post-commit at the
# shared Monad doc-ingest hook.
#
#   install_git_hooks.sh                every git repo under ~/Projects/ThePlace
#   install_git_hooks.sh PATH ...       only these repos
#   install_git_hooks.sh --remove       unset core.hooksPath in those repos
#
# Uses per-repo `git config core.hooksPath` so nothing is copied into
# .git/hooks and the hook updates in place when this file changes. A repo
# that already has a custom hooksPath is reported and skipped.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HOOKS_DIR="$HERE/git-hooks"
ROOT="${THEPLACE:-$HOME/Projects/ThePlace}"

chmod +x "$HOOKS_DIR/post-commit"

remove=0
[[ "${1:-}" == "--remove" ]] && { remove=1; shift; }

if [[ $# -gt 0 ]]; then
    mapfile -t repos < <(for p in "$@"; do echo "$p"; done)
else
    mapfile -t repos < <(find "$ROOT" -maxdepth 3 -type d -name .git -printf '%h\n' | sort)
fi

for repo in "${repos[@]}"; do
    [[ -d "$repo/.git" ]] || { echo "skip (not a repo): $repo"; continue; }
    cur="$(git -C "$repo" config --local --get core.hooksPath || true)"
    if [[ $remove -eq 1 ]]; then
        if [[ "$cur" == "$HOOKS_DIR" ]]; then
            git -C "$repo" config --local --unset core.hooksPath
            echo "unset:  $repo"
        else
            echo "left as-is ($cur): $repo"
        fi
        continue
    fi
    if [[ -n "$cur" && "$cur" != "$HOOKS_DIR" ]]; then
        echo "SKIP (custom hooksPath '$cur'): $repo"
        continue
    fi
    git -C "$repo" config --local core.hooksPath "$HOOKS_DIR"
    echo "wired:  $repo"
done

echo
echo "shared post-commit: $HOOKS_DIR/post-commit"
echo "test: touch a README in a wired repo, commit, then"
echo "  printf 'STATUS\\n' | nc -U ~/.ptolemy/ptolemy.sock | grep -E 'repack|pairs'"
