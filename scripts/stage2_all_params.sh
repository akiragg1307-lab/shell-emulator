#!/bin/sh
# Этап 2: все параметры сразу (скрипт завершается командой exit)
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --vfs examples/vfs/demo --prompt "demo$ " --script examples/scripts/stage2_ok.emu
