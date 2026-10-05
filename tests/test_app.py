"""Тесты запуска стартового скрипта и отладочного вывода."""

import os
import tempfile
import unittest

from shell_emulator.app import make_startup, run_startup_script
from shell_emulator.config import Config
from shell_emulator.shell import Shell
from shell_emulator.tags import TAG_DEBUG, TAG_ERROR


class FakeWindow:
    """Упрощённое окно: запоминает выведенные строки."""

    def __init__(self):
        """Создать окно с новым сеансом эмулятора."""
        self.shell = Shell()
        self.lines = []

    def write(self, text, tag=None):
        """Запомнить выведенный текст и его тег."""
        self.lines.append((text, tag))

    def run_command(self, line):
        """Показать ввод, выполнить команду и показать результат."""
        self.write(self.shell.prompt + line)
        result = self.shell.execute(line)
        if result.output:
            self.write(result.output)
        if result.error:
            self.write(result.error, TAG_ERROR)
        return result

    def texts(self):
        """Вернуть только тексты выведенных строк."""
        return [text for text, _tag in self.lines]


class StartupScriptTest(unittest.TestCase):
    """Проверки выполнения скрипта в окне."""

    def setUp(self):
        """Создать окно."""
        self.window = FakeWindow()

    def make_script(self, text):
        """Создать временный скрипт с текстом ``text``."""
        handle = tempfile.NamedTemporaryFile(
            "w", delete=False, encoding="utf-8", suffix=".emu"
        )
        handle.write(text)
        handle.close()
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def test_input_and_output_are_shown(self):
        """В окне видны и ввод, и вывод команд скрипта."""
        path = self.make_script("ls a\n")
        self.assertTrue(run_startup_script(self.window, path))
        texts = self.window.texts()
        self.assertEqual(texts[0], "$ ls a")
        self.assertIn("['a']", texts[1])

    def test_error_stops_script_and_is_reported(self):
        """После ошибки скрипт останавливается и выводится сообщение."""
        path = self.make_script("ls\nbad\ncd x\n")
        self.assertFalse(run_startup_script(self.window, path))
        self.assertNotIn("$ cd x", self.window.texts())
        text, tag = self.window.lines[-1]
        self.assertEqual(tag, TAG_ERROR)
        self.assertIn("строке 2", text)

    def test_missing_script_is_reported(self):
        """Отсутствующий скрипт даёт сообщение об ошибке."""
        self.assertFalse(run_startup_script(self.window, "none.emu"))
        text, tag = self.window.lines[-1]
        self.assertEqual(tag, TAG_ERROR)
        self.assertIn("none.emu", text)

    def test_startup_prints_debug_parameters(self):
        """Обработчик запуска печатает все параметры отладочным тегом."""
        config = Config("data/vfs", "me> ", None)
        make_startup(config)(self.window)
        debug = [t for t, tag in self.window.lines if tag == TAG_DEBUG]
        joined = "\n".join(debug)
        self.assertIn("data/vfs", joined)
        self.assertIn("me> ", joined)

    def test_startup_runs_script_after_debug(self):
        """Скрипт выполняется после отладочного вывода."""
        path = self.make_script("ls\n")
        make_startup(Config(script_path=path))(self.window)
        self.assertEqual(self.window.lines[0][1], TAG_DEBUG)
        self.assertIn("$ ls", self.window.texts())


if __name__ == "__main__":
    unittest.main()
