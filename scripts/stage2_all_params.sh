#!/bin/sh
# Этап 2: все параметры сразу (окно остаётся открытым после скрипта)
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --vfs examples/vfs/several --prompt "demo$ " --script examples/scripts/stage2_ok.emu
