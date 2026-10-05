"""Команды эмулятора.

Каждая команда — функция ``(shell, args) -> Result``, где ``args`` —
список аргументов без имени команды. На этапе 1 ``ls`` и ``cd`` являются
заглушками: они выводят своё имя и полученные аргументы.
"""

from shell_emulator.result import Result


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


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
