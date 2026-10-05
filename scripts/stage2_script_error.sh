#!/bin/sh
# Этап 2: стартовый скрипт с ошибкой (остановка и сообщение)
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --script examples/scripts/stage2_error.emu
