#!/bin/sh
# Этап 5: все режимы chown (изменения только в памяти) на VFS deep
cd "$(dirname "$0")/.." || exit 1
rm -rf out/stage5-copy
exec ./run.sh --vfs examples/vfs/deep --script examples/scripts/stage5_all.emu
