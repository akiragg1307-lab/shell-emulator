"""Тесты ядра эмулятора на этапе 1 (заглушки и exit)."""

import unittest

from shell_emulator.shell import Shell


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


if __name__ == "__main__":
    unittest.main()
