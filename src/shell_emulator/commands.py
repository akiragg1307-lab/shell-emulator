"""Команды эмулятора.

Каждая команда — функция ``(shell, args) -> Result``, где ``args`` —
список аргументов без имени команды. Здесь собраны реестр команд и
служебные команды ``exit`` и ``vfs-save``; остальные команды находятся в
отдельных модулях.
"""

from shell_emulator.nav_commands import cmd_cd, cmd_ls, cmd_pwd
from shell_emulator.owner_commands import cmd_chown
from shell_emulator.result import Result
from shell_emulator.vfs import VfsError, save_vfs
from shell_emulator.view_commands import cmd_tac, cmd_tree

SINGLE_ARGUMENT = 1


def cmd_exit(shell, args):
    """Завершить работу эмулятора."""
    if args:
        return Result(error="exit: слишком много аргументов")
    return Result(exit_requested=True)


def cmd_vfs_save(shell, args):
    """Сохранить состояние VFS на диск: ``vfs-save путь``."""
    if len(args) != SINGLE_ARGUMENT:
        return Result(error="vfs-save: использование: vfs-save путь")
    try:
        save_vfs(shell.vfs, args[0])
    except VfsError as exc:
        return Result(error=f"vfs-save: {exc}")
    return Result(output=f"VFS сохранена в {args[0]}")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "tree": cmd_tree,
    "tac": cmd_tac,
    "chown": cmd_chown,
    "exit": cmd_exit,
    "vfs-save": cmd_vfs_save,
}
