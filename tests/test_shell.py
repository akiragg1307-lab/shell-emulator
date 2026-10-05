"""Тесты ядра эмулятора на этапе 1 (заглушки и exit)."""

import os
import tempfile
import unittest

from shell_emulator.shell import Shell
from shell_emulator.vfs import DirNode, FileNode, Vfs


class ShellStubsTest(unittest.TestCase):
    """Проверки выполнения команд-заглушек и обработки ошибок."""

    def setUp(self):
        """Создать новый сеанс для каждого теста."""
        self.shell = Shell()

    def test_title_contains_vfs_name(self):
        """Заголовок окна содержит имя VFS."""
        shell = Shell(vfs_name="my_vfs")
        self.assertIn("my_vfs", shell.title)

    def test_ls_prints_name_and_arguments(self):
        """ls выводит своё имя и аргументы."""
        result = self.shell.execute("ls -l /tmp")
        self.assertTrue(result.ok)
        self.assertIn("ls", result.output)
        self.assertIn("['-l', '/tmp']", result.output)

    def test_cd_prints_name_and_arguments(self):
        """cd выводит своё имя и аргументы."""
        result = self.shell.execute("cd /a")
        self.assertIn("cd", result.output)
        self.assertIn("['/a']", result.output)

    def test_quoted_argument_is_single(self):
        """Аргумент в кавычках передаётся как один."""
        result = self.shell.execute('ls "dir with spaces" b')
        self.assertIn("['dir with spaces', 'b']", result.output)

    def test_empty_line_is_ignored(self):
        """Пустая строка не даёт ни вывода, ни ошибки."""
        result = self.shell.execute("   ")
        self.assertEqual((result.output, result.error), ("", ""))

    def test_unknown_command(self):
        """Неизвестная команда возвращает ошибку."""
        result = self.shell.execute("foo bar")
        self.assertFalse(result.ok)
        self.assertIn("foo", result.error)

    def test_parse_error_is_reported(self):
        """Ошибка разбора кавычек возвращается как ошибка команды."""
        result = self.shell.execute('ls "abc')
        self.assertFalse(result.ok)
        self.assertIn("кавычка", result.error)

    def test_exit_requests_shutdown(self):
        """exit запрашивает завершение работы."""
        self.assertTrue(self.shell.execute("exit").exit_requested)

    def test_exit_with_arguments_is_error(self):
        """exit с аргументами — ошибка, завершения нет."""
        result = self.shell.execute("exit now")
        self.assertFalse(result.ok)
        self.assertFalse(result.exit_requested)


class VfsSaveCommandTest(unittest.TestCase):
    """Проверки команды vfs-save."""

    def setUp(self):
        """Создать сеанс с небольшой VFS и временный каталог."""
        vfs = Vfs()
        folder = vfs.root.add(DirNode("dir"))
        folder.add(FileNode("a.txt", b"abc"))
        self.shell = Shell(vfs=vfs)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name

    def test_saves_to_disk(self):
        """vfs-save записывает дерево VFS в указанный каталог."""
        target = os.path.join(self.tmp, "my out")
        result = self.shell.execute(f'vfs-save "{target}"')
        self.assertTrue(result.ok)
        path = os.path.join(target, "dir", "a.txt")
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), b"abc")

    def test_requires_one_argument(self):
        """Без аргумента или с лишними аргументами — ошибка."""
        self.assertFalse(self.shell.execute("vfs-save").ok)
        self.assertFalse(self.shell.execute("vfs-save a b").ok)

    def test_target_is_file(self):
        """Если путь указывает на файл, команда сообщает об ошибке."""
        target = os.path.join(self.tmp, "file")
        with open(target, "w", encoding="utf-8") as handle:
            handle.write("x")
        result = self.shell.execute(f'vfs-save "{target}"')
        self.assertFalse(result.ok)
        self.assertIn("vfs-save", result.error)


if __name__ == "__main__":
    unittest.main()
