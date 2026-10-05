#!/bin/sh
# Этап 3: VFS «several» из каталога, проверка всех команд и vfs-save
cd "$(dirname "$0")/.." || exit 1
rm -rf out/vfs-copy
exec ./run.sh --vfs examples/vfs/several --script examples/scripts/stage3_all.emu
