#!/usr/bin/env bash
# Launch or toggle the Control Center.
# Usage: launch.sh [--page overview|wifi|bluetooth] [--show|--toggle]
set -euo pipefail

# gtk4-layer-shell must be loaded before libwayland-client. The Python entry
# point also re-execs itself if this variable is missing.
export LD_PRELOAD="/usr/lib/libgtk4-layer-shell.so${LD_PRELOAD:+ $LD_PRELOAD}"

exec python3 "$HOME/.config/control-center/main.py" "$@"
