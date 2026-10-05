"""Тесты окна эмулятора с подменой Tkinter (без графического дисплея)."""

import importlib
import sys
import unittest
from unittest import mock

from shell_emulator.shell import Shell


class ShellWindowTest(unittest.TestCase):
    """Проверки логики окна на макете библиотеки Tkinter."""

    def setUp(self):
        """Подменить Tkinter макетом и создать окно."""
        fake_tk = mock.MagicMock()
        modules = {"tkinter": fake_tk,
                   "tkinter.scrolledtext": fake_tk.scrolledtext}
        patcher = mock.patch.dict(sys.modules, modules)
        patcher.start()
        self.addCleanup(patcher.stop)
        gui = importlib.import_module("shell_emulator.gui")
        self.gui = importlib.reload(gui)
        self.addCleanup(importlib.reload, self.gui)
        self.root = mock.MagicMock()
        self.window = self.gui.ShellWindow(self.root, Shell("demo", "> "))
        self.window.write = mock.MagicMock()

    def written(self):
        """Вернуть список строк, выведенных в окно."""
        return [call.args[0] for call in self.window.write.call_args_list]

    def test_title_has_vfs_name(self):
        """Заголовок окна содержит имя VFS."""
        self.root.title.assert_called_once()
        self.assertIn("demo", self.root.title.call_args.args[0])

    def test_command_is_echoed_with_prompt(self):
        """Введённая строка выводится вместе с приглашением."""
        self.window.run_command("ls a")
        self.assertEqual(self.written()[0], "> ls a")
        self.assertIn("ls: невозможно получить доступ", self.written()[1])

    def test_error_is_written_with_error_tag(self):
        """Ошибка выводится с тегом ошибки."""
        self.window.run_command("nope")
        self.window.write.assert_any_call(mock.ANY, self.gui.TAG_ERROR)

    def test_exit_closes_window(self):
        """Команда exit закрывает окно."""
        self.window.run_command("exit")
        self.root.destroy.assert_called_once()

    def test_history_navigation(self):
        """Стрелки вверх и вниз листают историю команд."""
        self.window.history = ["one", "two"]
        self.window.history_pos = 2
        self.window._on_history_up(None)
        self.window.entry.insert.assert_called_with(0, "two")
        self.window._on_history_up(None)
        self.window.entry.insert.assert_called_with(0, "one")
        self.window._on_history_down(None)
        self.window.entry.insert.assert_called_with(0, "two")


if __name__ == "__main__":
    unittest.main()
