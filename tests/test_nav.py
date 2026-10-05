"""Тесты команд навигации ls, cd и pwd."""

import os
import unittest

from shell_emulator.nav_commands import parse_options
from shell_emulator.shell import Shell
from shell_emulator.vfs import FileNode, load_vfs

DEEP = os.path.join(os.path.dirname(__file__), os.pardir, "examples", "vfs",
                    "deep")


class NavTestCase(unittest.TestCase):
    """Базовый класс: сеанс с глубокой тестовой VFS."""

    def setUp(self):
        """Загрузить глубокую VFS и добавить скрытый файл."""
        vfs = load_vfs(DEEP)
        vfs.root.add(FileNode(".hidden", b"h"))
        self.shell = Shell(vfs=vfs)

    def run_cmd(self, line):
        """Выполнить команду и вернуть ``Result``."""
        return self.shell.execute(line)

    def out(self, line):
        """Выполнить команду и вернуть вывод по строкам."""
        return self.run_cmd(line).output.splitlines()


class LsTest(NavTestCase):
    """Проверки команды ls."""

    def test_root_listing_sorted_without_hidden(self):
        """ls показывает элементы по алфавиту, скрытые не показывает."""
        self.assertEqual(self.out("ls"), ["docs", "root.txt", "src"])

    def test_all_shows_hidden(self):
        """ls -a показывает и скрытые файлы."""
        self.assertIn(".hidden", self.out("ls -a"))

    def test_long_format(self):
        """ls -l показывает тип, владельца и размер."""
        lines = self.out("ls -l docs")
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("-"))
        self.assertTrue(any(line.startswith("d root") for line in lines))
        self.assertIn("index.txt", lines[0])

    def test_combined_options(self):
        """Опции можно объединять: ls -la."""
        lines = self.out("ls -la")
        self.assertTrue(any(".hidden" in line for line in lines))

    def test_relative_and_absolute_paths(self):
        """ls работает с относительным и абсолютным путём."""
        self.assertEqual(self.out("ls docs/work"),
                         ["2026", "plan.txt"])
        self.assertEqual(self.out("ls /docs/work/2026/q3"), ["summary.txt"])

    def test_file_argument(self):
        """ls для файла выводит его имя."""
        self.assertEqual(self.out("ls root.txt"), ["root.txt"])

    def test_multiple_paths_have_headers(self):
        """При нескольких путях выводятся заголовки."""
        lines = self.out("ls docs/personal src/app")
        self.assertEqual(lines[0], "docs/personal:")
        self.assertIn("src/app:", lines)

    def test_missing_path(self):
        """Несуществующий путь — ошибка, остальные пути выводятся."""
        result = self.run_cmd("ls nope docs/personal")
        self.assertFalse(result.ok)
        self.assertIn("nope", result.error)
        self.assertIn("notes.txt", result.output)

    def test_unknown_option(self):
        """Неизвестная опция — ошибка."""
        result = self.run_cmd("ls -z")
        self.assertFalse(result.ok)
        self.assertIn("'z'", result.error)

    def test_parse_options(self):
        """parse_options разделяет опции и операнды."""
        self.assertEqual(parse_options(["-la", "x", "-"]),
                         ({"l", "a"}, ["x", "-"]))
        with self.assertRaises(ValueError):
            parse_options(["-q"])


class CdPwdTest(NavTestCase):
    """Проверки команд cd и pwd."""

    def test_pwd_in_root(self):
        """В начале работы текущий каталог — корень."""
        self.assertEqual(self.run_cmd("pwd").output, "/")

    def test_cd_relative_then_ls(self):
        """После cd ls работает относительно нового каталога."""
        self.assertTrue(self.run_cmd("cd docs/work").ok)
        self.assertEqual(self.run_cmd("pwd").output, "/docs/work")
        self.assertEqual(self.out("ls"), ["2026", "plan.txt"])

    def test_cd_absolute_and_parent(self):
        """cd поддерживает абсолютные пути и .."""
        self.run_cmd("cd /docs/work/2026/q3")
        self.assertEqual(self.run_cmd("pwd").output, "/docs/work/2026/q3")
        self.run_cmd("cd ../..")
        self.assertEqual(self.run_cmd("pwd").output, "/docs/work")

    def test_cd_without_arguments_goes_to_root(self):
        """cd без аргументов возвращает в корень."""
        self.run_cmd("cd src/app")
        self.run_cmd("cd")
        self.assertEqual(self.run_cmd("pwd").output, "/")

    def test_cd_to_missing_directory(self):
        """cd в несуществующий каталог — ошибка, каталог не меняется."""
        result = self.run_cmd("cd nope")
        self.assertFalse(result.ok)
        self.assertIn("nope", result.error)
        self.assertEqual(self.run_cmd("pwd").output, "/")

    def test_cd_to_file(self):
        """cd в файл — ошибка."""
        result = self.run_cmd("cd root.txt")
        self.assertFalse(result.ok)
        self.assertIn("Не каталог", result.error)

    def test_cd_too_many_arguments(self):
        """cd с двумя аргументами — ошибка."""
        self.assertFalse(self.run_cmd("cd docs src").ok)

    def test_pwd_with_arguments(self):
        """pwd с аргументами — ошибка."""
        self.assertFalse(self.run_cmd("pwd x").ok)

    def test_ls_without_path_uses_current_directory(self):
        """ls без пути показывает текущий каталог."""
        self.run_cmd("cd src")
        self.assertEqual(self.out("ls"), ["app"])


if __name__ == "__main__":
    unittest.main()
