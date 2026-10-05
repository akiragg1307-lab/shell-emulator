"""Результат выполнения команды эмулятора."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    """Итог выполнения одной команды.

    output: текст для стандартного вывода;
    error: сообщение об ошибке (пусто, если ошибки не было);
    exit_requested: признак того, что нужно завершить эмулятор.
    """

    output: str = ""
    error: str = ""
    exit_requested: bool = False

    @property
    def ok(self):
        """Вернуть True, если команда выполнена без ошибки."""
        return not self.error
