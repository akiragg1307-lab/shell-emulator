"""Стартовый скрипт: чтение файла и последовательное выполнение команд."""

COMMENT_PREFIX = "#"
FIRST_LINE_NUMBER = 1
ENCODING = "utf-8-sig"


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def load_script(path):
    """Прочитать стартовый скрипт и вернуть список его строк.

    При невозможности прочитать файл выбрасывается ``ScriptError``.
    """
    try:
        with open(path, encoding=ENCODING) as handle:
            return handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise ScriptError(f"не удалось прочитать скрипт {path}: {exc}")


def is_executable(line):
    """Вернуть True, если строка содержит команду (не пустая, не #)."""
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(COMMENT_PREFIX)


def run_script(lines, run_line, report):
    """Выполнить строки скрипта до первой ошибки.

    run_line(line) выполняет строку (показывая ввод и вывод) и
    возвращает ``Result``; report(text) сообщает об ошибке скрипта.
    Пустые строки и строки, начинающиеся с ``#``, пропускаются.
    Возвращает True, если все команды выполнены без ошибок.
    """
    numbered = enumerate(lines, FIRST_LINE_NUMBER)
    for number, line in numbered:
        if not is_executable(line):
            continue
        result = run_line(line)
        if not result.ok:
            report(f"[скрипт] остановлен: ошибка в строке {number}: {line}")
            return False
        if result.exit_requested:
            return True
    return True
