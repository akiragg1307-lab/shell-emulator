#!/bin/sh
# Этап 5: ошибки chown (после каждой ошибки закройте окно)
cd "$(dirname "$0")/.." || exit 1
for name in path args group; do
    ./run.sh --vfs examples/vfs/deep \
        --script "examples/scripts/stage5_error_$name.emu"
done
