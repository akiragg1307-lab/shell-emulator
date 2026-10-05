#!/bin/sh
# Этап 4: все режимы команд ls, cd, tree, tac на VFS deep
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --vfs examples/vfs/deep --script examples/scripts/stage4_all.emu
