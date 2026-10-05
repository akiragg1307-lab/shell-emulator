"""Параметры командной строки эмулятора."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional

from shell_emulator.shell import DEFAULT_PROMPT, DEFAULT_VFS_NAME

NOT_SET = "(не задан)"


@dataclass(frozen=True)
class Config:
    """Настройки эмулятора, заданные пользователем.

    vfs_path: путь к физическому расположению VFS;
    prompt: приглашение к вводу в REPL;
    script_path: путь к стартовому скрипту.
    """

    vfs_path: Optional[str] = None
    prompt: str = DEFAULT_PROMPT
    script_path: Optional[str] = None

    @property
    def vfs_name(self):
        """Имя VFS для заголовка окна (последний элемент пути)."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        name = os.path.basename(os.path.normpath(self.vfs_path))
        return name or DEFAULT_VFS_NAME


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell_emulator",
        description="Эмулятор оболочки UNIX-подобной ОС с GUI.",
    )
    parser.add_argument(
        "--vfs", metavar="ПУТЬ",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--prompt", metavar="ТЕКСТ", default=DEFAULT_PROMPT,
        help="приглашение к вводу в REPL (по умолчанию %(default)r)",
    )
    parser.add_argument(
        "--script", metavar="ПУТЬ",
        help="путь к стартовому скрипту с командами эмулятора",
    )
    return parser


def parse_args(argv=None):
    """Разобрать список параметров ``argv`` и вернуть ``Config``."""
    namespace = build_parser().parse_args(argv)
    return Config(
        vfs_path=namespace.vfs,
        prompt=namespace.prompt,
        script_path=namespace.script,
    )


def debug_lines(config):
    """Вернуть строки отладочного вывода всех заданных параметров."""
    return [
        f"[отладка] vfs: {config.vfs_path or NOT_SET}",
        f"[отладка] prompt: {config.prompt!r}",
        f"[отладка] script: {config.script_path or NOT_SET}",
    ]
