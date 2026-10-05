"""Тесты параметров командной строки."""

import unittest

from shell_emulator.config import Config, debug_lines, parse_args
from shell_emulator.shell import DEFAULT_PROMPT, DEFAULT_VFS_NAME


class ParseArgsTest(unittest.TestCase):
    """Проверки разбора параметров и отладочного вывода."""

    def test_defaults(self):
        """Без параметров используются значения по умолчанию."""
        config = parse_args([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.script_path)
        self.assertEqual(config.prompt, DEFAULT_PROMPT)

    def test_all_parameters(self):
        """Все три параметра разбираются."""
        config = parse_args(
            ["--vfs", "data/vfs", "--prompt", "me> ", "--script", "a.emu"]
        )
        self.assertEqual(config.vfs_path, "data/vfs")
        self.assertEqual(config.prompt, "me> ")
        self.assertEqual(config.script_path, "a.emu")

    def test_unknown_parameter_exits(self):
        """Неизвестный параметр приводит к завершению с ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--unknown"])

    def test_vfs_name_from_path(self):
        """Имя VFS — последний элемент пути, в том числе со слешем."""
        self.assertEqual(Config(vfs_path="a/b/vfs1").vfs_name, "vfs1")
        self.assertEqual(Config(vfs_path="a/b/vfs2/").vfs_name, "vfs2")

    def test_vfs_name_default(self):
        """Без пути используется имя VFS по умолчанию."""
        self.assertEqual(Config().vfs_name, DEFAULT_VFS_NAME)

    def test_debug_lines_show_all_parameters(self):
        """Отладочный вывод содержит все заданные параметры."""
        config = Config("data/vfs", "me> ", "a.emu")
        text = "\n".join(debug_lines(config))
        for expected in ("data/vfs", "me> ", "a.emu"):
            self.assertIn(expected, text)

    def test_debug_lines_for_unset_parameters(self):
        """Незаданные параметры помечаются в отладочном выводе."""
        text = "\n".join(debug_lines(Config()))
        self.assertIn("не задан", text)


if __name__ == "__main__":
    unittest.main()
