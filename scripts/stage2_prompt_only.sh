#!/bin/sh
# Этап 2: только пользовательское приглашение к вводу
cd "$(dirname "$0")/.." || exit 1
exec ./run.sh --prompt "user@emu> "
