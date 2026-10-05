"""Команды, изменяющие состояние VFS в памяти: ``chown``."""

from shell_emulator.nav_commands import parse_options
from shell_emulator.paths import resolve_path
from shell_emulator.result import Result
from shell_emulator.vfs import VfsError

CHOWN_OPTIONS = "R"
GROUP_SEPARATOR = ":"
MIN_OPERANDS = 2


def set_owner(node, owner, recursive):
    """Назначить владельца элементу ``node``.

    При ``recursive`` владелец назначается и всем вложенным элементам.
    """
    node.owner = owner
    if recursive and node.is_dir:
        for child in node.children.values():
            set_owner(child, owner, recursive)


def check_owner(owner):
    """Проверить имя владельца; при ошибке выбрасывается ``ValueError``."""
    if GROUP_SEPARATOR in owner:
        raise ValueError("группы не поддерживаются")
    if not owner.strip():
        raise ValueError("неверное имя владельца")


def cmd_chown(shell, args):
    """Сменить владельца: ``chown [-R] владелец путь...``.

    Изменение выполняется только в памяти; на диск оно попадёт лишь
    в виде структуры каталога при ``vfs-save`` (владельцы там не хранятся).
    """
    try:
        options, operands = parse_options(args, CHOWN_OPTIONS)
    except ValueError as exc:
        return Result(error=f"chown: неверная опция -- '{exc}'")
    if len(operands) < MIN_OPERANDS:
        return Result(error="chown: пропущен операнд\n"
                      "использование: chown [-R] владелец путь...")
    owner, paths = operands[0], operands[1:]
    try:
        check_owner(owner)
    except ValueError as exc:
        return Result(error=f"chown: {exc}: '{owner}'")
    errors = []
    for path in paths:
        try:
            node = resolve_path(shell.vfs, shell.cwd, path)
        except VfsError as exc:
            errors.append(
                f"chown: невозможно получить доступ к '{path}': {exc}")
            continue
        set_owner(node, owner, CHOWN_OPTIONS in options)
    return Result(error="\n".join(errors))
