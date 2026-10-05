"""Тесты стартового скрипта."""

import os
import tempfile
import unittest

from shell_emulator.script import (ScriptError, is_executable, load_script,
                                   run_script)
from shell_emulator.shell import Shell


class RunScriptTest(unittest.TestCase):
    """Проверки выполнения строк скрипта."""

    def setUp(self):
        """Подготовить сеанс и накопители вывода."""
        self.shell = Shell()
        self.executed = []
        self.reports = []

    def run_line(self, line):
        """Выполнить строку, запомнив её."""
        self.executed.append(line)
        return self.shell.execute(line)

    def run_lines(self, lines):
        """Запустить скрипт и вернуть признак успеха."""
        return run_script(lines, self.run_line, self.reports.append)

    def test_all_commands_executed(self):
        """Корректный скрипт выполняется целиком."""
        self.assertTrue(self.run_lines(["ls", "pwd"]))
        self.assertEqual(self.executed, ["ls", "pwd"])
        self.assertEqual(self.reports, [])

    def test_stops_on_first_error(self):
        """Выполнение останавливается на первой ошибке."""
        ok = self.run_lines(["ls", "bad", "cd /a"])
        self.assertFalse(ok)
        self.assertEqual(self.executed, ["ls", "bad"])

    def test_error_report_has_line_number(self):
        """В сообщении об ошибке указан номер строки скрипта."""
        self.run_lines(["ls", "", "bad cmd"])
        self.assertEqual(len(self.reports), 1)
        self.assertIn("строке 3", self.reports[0])
        self.assertIn("bad cmd", self.reports[0])

    def test_blank_and_comment_lines_skipped(self):
        """Пустые строки и комментарии не выполняются."""
        self.run_lines(["", "# комментарий", "  ", "ls"])
        self.assertEqual(self.executed, ["ls"])

    def test_exit_stops_script(self):
        """Команда exit прекращает выполнение скрипта без ошибки."""
        self.assertTrue(self.run_lines(["ls", "exit", "cd /a"]))
        self.assertEqual(self.executed, ["ls", "exit"])

    def test_is_executable(self):
        """Проверка признака исполняемой строки."""
        self.assertTrue(is_executable("  ls"))
        self.assertFalse(is_executable("   "))
        self.assertFalse(is_executable("  # ls"))


class LoadScriptTest(unittest.TestCase):
    """Проверки чтения файла скрипта."""

    def write_script(self, data):
        """Создать временный файл скрипта с байтами ``data``."""
        handle = tempfile.NamedTemporaryFile(delete=False)
        handle.write(data)
        handle.close()
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def test_load_lines(self):
        """Строки читаются в порядке следования."""
        path = self.write_script("ls\ncd /a\n".encode("utf-8"))
        self.assertEqual(load_script(path), ["ls", "cd /a"])

    def test_bom_is_ignored(self):
        """Метка порядка байтов UTF-8 не попадает в первую команду."""
        path = self.write_script(b"\xef\xbb\xbfls\n")
        self.assertEqual(load_script(path), ["ls"])

    def test_missing_file(self):
        """Отсутствующий файл — ScriptError."""
        with self.assertRaises(ScriptError):
            load_script("no/such/script.emu")

    def test_invalid_encoding(self):
        """Файл не в UTF-8 — ScriptError."""
        path = self.write_script(b"\xff\xfe\x00bad")
        with self.assertRaises(ScriptError):
            load_script(path)


if __name__ == "__main__":
    unittest.main()
