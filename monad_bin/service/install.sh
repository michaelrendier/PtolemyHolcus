#!/bin/bash
# install.sh — put the Monad ingest units under systemd --user and arm them.
#
#   monad_bin/service/install.sh          install + enable (socket-activated)
#   monad_bin/service/install.sh --now    also start the service right now
#   monad_bin/service/install.sh --remove disable + delete the units
#
# Passive by default: only the socket is enabled, so nothing runs until the
# first hook connects. The Claude Code SessionStart hook (see
# claude-hooks.md) starts the socket per session; with `loginctl enable-linger
# $USER` it also survives logout.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNITS=(ptolemy-monad.socket ptolemy-monad.service)

if [[ "${1:-}" == "--remove" ]]; then
    systemctl --user disable --now ptolemy-monad.socket ptolemy-monad.service 2>/dev/null || true
    for u in "${UNITS[@]}"; do rm -fv "$DEST/$u"; done
    systemctl --user daemon-reload
    echo "removed."
    exit 0
fi

mkdir -p "$DEST" "$HOME/.ptolemy"
for u in "${UNITS[@]}"; do
    install -m 0644 "$HERE/$u" "$DEST/$u"
    echo "installed $DEST/$u"
done

systemctl --user daemon-reload
systemctl --user enable ptolemy-monad.socket
systemctl --user start  ptolemy-monad.socket
echo "socket enabled + started (service starts on first connection)"

if [[ "${1:-}" == "--now" ]]; then
    systemctl --user start ptolemy-monad.service
    sleep 1
    systemctl --user --no-pager status ptolemy-monad.service | head -12
fi

cat <<'EOF'

next:
  loginctl enable-linger $USER        # keep it alive across logout (optional)
  systemctl --user status ptolemy-monad.service
  printf 'STATUS\n' | nc -U ~/.ptolemy/ptolemy.sock   # peek: repack + pairs lines
EOF
