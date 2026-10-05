#!/bin/sh
# Этап 2: несуществующий стартовый скрипт (сообщение об ошибке)
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --script examples/scripts/no_such_file.emu
