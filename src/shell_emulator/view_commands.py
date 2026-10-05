"""Команды просмотра содержимого VFS: ``tree`` и ``tac``."""

from shell_emulator.nav_commands import (HIDDEN_PREFIX, SINGLE, parse_options)
from shell_emulator.paths import resolve_path
from shell_emulator.result import Result
from shell_emulator.vfs import VfsError

TREE_OPTIONS = "a"
BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
BLANK = "    "
ROOT_LABEL = "."
DECODE_ERRORS = "replace"


def visible_children(node, show_hidden):
    """Вернуть дочерние элементы каталога, скрыв точечные при необходимости."""
    children = node.sorted_children()
    if show_hidden:
        return children
    return [c for c in children if not c.name.startswith(HIDDEN_PREFIX)]


def tree_lines(node, show_hidden, prefix="", counts=None):
    """Построить строки дерева каталога ``node``.

    ``counts`` — словарь со счётчиками ``dirs`` и ``files``, который
    пополняется по мере обхода. Возвращает список строк.
    """
    counts = counts if counts is not None else {"dirs": 0, "files": 0}
    lines = []
    children = visible_children(node, show_hidden)
    for index, child in enumerate(children):
        last = index == len(children) - SINGLE
        lines.append(prefix + (LAST_BRANCH if last else BRANCH) + child.name)
        if child.is_dir:
            counts["dirs"] += SINGLE
            extension = BLANK if last else PIPE
            lines.extend(tree_lines(child, show_hidden, prefix + extension,
                                    counts))
        else:
            counts["files"] += SINGLE
    return lines


def cmd_tree(shell, args):
    """Показать дерево каталога: ``tree [-a] [путь]``."""
    try:
        options, operands = parse_options(args, TREE_OPTIONS)
    except ValueError as exc:
        return Result(error=f"tree: неверная опция -- '{exc}'")
    if len(operands) > SINGLE:
        return Result(error="tree: слишком много аргументов")
    path = operands[0] if operands else ROOT_LABEL
    try:
        node = resolve_path(shell.vfs, shell.cwd, path)
    except VfsError as exc:
        return Result(error=f"tree: {path}: {exc}")
    if not node.is_dir:
        return Result(error=f"tree: {path}: Не каталог")
    counts = {"dirs": 0, "files": 0}
    lines = [path] + tree_lines(node, TREE_OPTIONS in options, "", counts)
    lines.append("")
    lines.append(f"каталогов: {counts['dirs']}, файлов: {counts['files']}")
    return Result(output="\n".join(lines))


def tac_file(shell, path):
    """Вернуть строки файла ``path`` в обратном порядке.

    При ошибке выбрасывается ``VfsError``.
    """
    node = resolve_path(shell.vfs, shell.cwd, path)
    if node.is_dir:
        raise VfsError("Это каталог")
    text = node.data.decode("utf-8", errors=DECODE_ERRORS)
    return list(reversed(text.splitlines()))


def cmd_tac(shell, args):
    """Вывести строки файлов в обратном порядке: ``tac файл...``."""
    if not args:
        return Result(error="tac: пропущен операнд")
    lines = []
    errors = []
    for path in args:
        try:
            lines.extend(tac_file(shell, path))
        except VfsError as exc:
            errors.append(f"tac: {path}: {exc}")
    return Result(output="\n".join(lines), error="\n".join(errors))
