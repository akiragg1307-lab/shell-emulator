#!/bin/sh
# Этап 4: ошибки ls, cd, tree, tac (после каждой ошибки закройте окно)
cd "$(dirname "$0")/.." || exit 1
for name in ls cd tree tac; do
    ./run.sh --vfs examples/vfs/deep \
        --script "examples/scripts/stage4_error_$name.emu"
done
