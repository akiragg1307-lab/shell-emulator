"""Ядро эмулятора: разбор строки и выполнение команды."""

from shell_emulator.commands import COMMANDS
from shell_emulator.parser import ParseError, parse_line
from shell_emulator.result import Result
from shell_emulator.vfs import Vfs

DEFAULT_VFS_NAME = "vfs"
DEFAULT_PROMPT = "$ "
TITLE_PREFIX = "Эмулятор оболочки"


class Shell:
    """Состояние сеанса эмулятора и выполнение введённых команд."""

    def __init__(self, vfs_name=DEFAULT_VFS_NAME, prompt=DEFAULT_PROMPT,
                 vfs=None):
        """Создать сеанс с именем VFS, приглашением и самой VFS.

        Если ``vfs`` не задана, используется пустая VFS в памяти.
        """
        self.vfs_name = vfs_name
        self.prompt = prompt
        self.vfs = vfs if vfs is not None else Vfs()
        self.cwd = self.vfs.root

    @property
    def title(self):
        """Заголовок окна, содержащий имя VFS."""
        return f"{TITLE_PREFIX} — {self.vfs_name}"

    def execute(self, line):
        """Выполнить строку и вернуть ``Result``.

        Пустая строка ничего не делает. Ошибки разбора и неизвестные
        команды возвращаются как ``Result`` с заполненным ``error``.
        """
        try:
            words = parse_line(line)
        except ParseError as exc:
            return Result(error=f"ошибка разбора: {exc}")
        if not words:
            return Result()
        name, args = words[0], words[1:]
        handler = COMMANDS.get(name)
        if handler is None:
            return Result(error=f"{name}: команда не найдена")
        return handler(self, args)
