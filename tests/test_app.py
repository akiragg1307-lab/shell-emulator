"""Тесты запуска стартового скрипта и отладочного вывода."""

import os
import tempfile
import unittest

from shell_emulator.app import create_shell, make_startup, run_startup_script
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
        path = self.make_script("pwd\n")
        self.assertTrue(run_startup_script(self.window, path))
        texts = self.window.texts()
        self.assertEqual(texts[0], "$ pwd")
        self.assertEqual(texts[1], "/")

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


EXAMPLE_VFS = os.path.join(os.path.dirname(__file__), os.pardir, "examples",
                           "vfs", "minimal")


class CreateShellTest(unittest.TestCase):
    """Проверки создания сеанса с VFS."""

    def test_loads_vfs_from_directory(self):
        """VFS загружается в память из каталога --vfs."""
        shell, errors = create_shell(Config(vfs_path=EXAMPLE_VFS))
        self.assertEqual(errors, [])
        self.assertIn("hello.txt", shell.vfs.root.children)
        self.assertIn("minimal", shell.title)

    def test_without_vfs_is_empty(self):
        """Без --vfs используется пустая VFS."""
        shell, errors = create_shell(Config())
        self.assertEqual((errors, shell.vfs.root.children), ([], {}))

    def test_missing_directory_reports_error(self):
        """Ошибка загрузки возвращается сообщением, VFS пустая."""
        shell, errors = create_shell(Config(vfs_path="no/such/dir"))
        self.assertEqual(len(errors), 1)
        self.assertIn("no/such/dir", errors[0])
        self.assertEqual(shell.vfs.root.children, {})

    def test_startup_shows_errors(self):
        """Ошибки запуска выводятся в окне с тегом ошибки."""
        window = FakeWindow()
        make_startup(Config(), ["[vfs] ошибка: тест"])(window)
        self.assertIn(("[vfs] ошибка: тест", TAG_ERROR), window.lines)


if __name__ == "__main__":
    unittest.main()
