"""Команды навигации по VFS: ``ls``, ``cd`` и ``pwd``."""

from shell_emulator.paths import absolute_path, resolve_path
from shell_emulator.result import Result
from shell_emulator.vfs import VfsError

HIDDEN_PREFIX = "."
OPTION_PREFIX = "-"
KNOWN_OPTIONS = "la"
DIR_SIZE_LABEL = "-"
SINGLE = 1


def parse_options(args, known=KNOWN_OPTIONS):
    """Отделить опции (``-l``, ``-a``, ``-la``) от остальных аргументов.

    ``known`` — строка допустимых букв опций. Возвращает пару (множество
    опций, список операндов). Для неизвестной опции выбрасывается
    ``ValueError`` с её символом.
    """
    options = set()
    operands = []
    for arg in args:
        if arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX:
            for letter in arg[len(OPTION_PREFIX):]:
                if letter not in known:
                    raise ValueError(letter)
                options.add(letter)
        else:
            operands.append(arg)
    return options, operands


def format_entry(node, long_format):
    """Сформировать строку ``ls`` для элемента VFS."""
    if not long_format:
        return node.name
    kind = "d" if node.is_dir else "-"
    size = DIR_SIZE_LABEL if node.is_dir else node.size
    return f"{kind} {node.owner:<8} {size:>6} {node.name}"


def list_node(node, options):
    """Вернуть строки содержимого каталога или самого файла."""
    long_format = "l" in options
    if not node.is_dir:
        return [format_entry(node, long_format)]
    children = node.sorted_children()
    if "a" not in options:
        children = [c for c in children
                    if not c.name.startswith(HIDDEN_PREFIX)]
    return [format_entry(child, long_format) for child in children]


def cmd_ls(shell, args):
    """Показать содержимое каталогов: ``ls [-l] [-a] [путь...]``."""
    try:
        options, operands = parse_options(args)
    except ValueError as exc:
        return Result(error=f"ls: неверная опция -- '{exc}'")
    lines = []
    errors = []
    for path in operands or [absolute_path(shell.cwd)]:
        try:
            node = resolve_path(shell.vfs, shell.cwd, path)
        except VfsError as exc:
            errors.append(f"ls: невозможно получить доступ к '{path}': {exc}")
            continue
        if len(operands) > SINGLE:
            lines.append(f"{path}:")
        lines.extend(list_node(node, options))
    return Result(output="\n".join(lines), error="\n".join(errors))


def cmd_cd(shell, args):
    """Сменить текущий каталог: ``cd [путь]`` (без пути — корень)."""
    if len(args) > SINGLE:
        return Result(error="cd: слишком много аргументов")
    if not args:
        shell.cwd = shell.vfs.root
        return Result()
    try:
        node = resolve_path(shell.vfs, shell.cwd, args[0])
    except VfsError as exc:
        return Result(error=f"cd: {args[0]}: {exc}")
    if not node.is_dir:
        return Result(error=f"cd: {args[0]}: Не каталог")
    shell.cwd = node
    return Result()


def cmd_pwd(shell, args):
    """Вывести абсолютный путь текущего каталога."""
    if args:
        return Result(error="pwd: слишком много аргументов")
    return Result(output=absolute_path(shell.cwd))
