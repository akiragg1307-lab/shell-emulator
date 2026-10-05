#!/bin/sh
# Этап 3: ошибка команды vfs-save останавливает стартовый скрипт
cd "$(dirname "$0")/.." || exit 1
rm -rf out/ok-copy
exec ./run.sh --vfs examples/vfs/several --script examples/scripts/stage3_errors.emu
