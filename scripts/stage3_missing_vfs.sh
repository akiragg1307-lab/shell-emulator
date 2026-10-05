#!/bin/sh
# Этап 3: каталог VFS не существует (сообщение об ошибке)
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --vfs examples/vfs/no_such_vfs --script examples/scripts/stage3_all.emu
