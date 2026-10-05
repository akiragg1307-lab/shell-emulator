"""Команды эмулятора.

Каждая команда — функция ``(shell, args) -> Result``, где ``args`` —
список аргументов без имени команды. На этапе 1 ``ls`` и ``cd`` являются
заглушками: они выводят своё имя и полученные аргументы. Команда
``vfs-save`` сохраняет состояние VFS на диск.
"""

from shell_emulator.result import Result
from shell_emulator.vfs import VfsError, save_vfs

SINGLE_ARGUMENT = 1


def _stub(name, args):
    """Сформировать вывод команды-заглушки: имя и аргументы."""
    return Result(output=f"команда: {name}, аргументы: {args!r}")


def cmd_ls(shell, args):
    """Заглушка команды ls."""
    return _stub("ls", args)


def cmd_cd(shell, args):
    """Заглушка команды cd."""
    return _stub("cd", args)


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
    "exit": cmd_exit,
    "vfs-save": cmd_vfs_save,
}
