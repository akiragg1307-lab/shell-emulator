"""Тесты команд tree и tac."""

import os
import unittest

from shell_emulator.shell import Shell
from shell_emulator.vfs import DirNode, FileNode, Vfs, load_vfs

EXAMPLES = os.path.join(os.path.dirname(__file__), os.pardir, "examples",
                        "vfs")
EXPECTED_DEEP_TREE = """.
├── docs
│   ├── index.txt
│   ├── personal
│   │   └── notes.txt
│   └── work
│       ├── 2026
│       │   ├── q3
│       │   │   └── summary.txt
│       │   └── report.txt
│       └── plan.txt
├── root.txt
└── src
    └── app
        ├── main.py
        └── utils
            └── helpers.py

каталогов: 8, файлов: 8"""


def shell_for(name):
    """Создать сеанс с тестовой VFS ``name``."""
    return Shell(vfs=load_vfs(os.path.join(EXAMPLES, name)))


class TreeTest(unittest.TestCase):
    """Проверки команды tree."""

    def test_full_tree(self):
        """tree рисует всё дерево и считает каталоги и файлы."""
        result = shell_for("deep").execute("tree")
        self.assertEqual(result.output, EXPECTED_DEEP_TREE)

    def test_subdirectory(self):
        """tree для подкаталога использует его как корень."""
        result = shell_for("deep").execute("tree docs/personal")
        self.assertEqual(result.output.splitlines()[:2],
                         ["docs/personal", "└── notes.txt"])
        self.assertIn("каталогов: 0, файлов: 1", result.output)

    def test_current_directory(self):
        """Без аргументов tree показывает текущий каталог."""
        shell = shell_for("deep")
        shell.execute("cd src/app")
        lines = shell.execute("tree").output.splitlines()
        self.assertEqual(lines[0], ".")
        self.assertIn("├── main.py", lines)

    def test_empty_directory(self):
        """Пустой каталог даёт нулевые счётчики."""
        result = Shell(vfs=Vfs()).execute("tree")
        self.assertEqual(result.output, ".\n\nкаталогов: 0, файлов: 0")

    def test_hidden_files(self):
        """Скрытые файлы показываются только с -a."""
        vfs = Vfs()
        vfs.root.add(DirNode(".git")).add(FileNode("cfg", b""))
        shell = Shell(vfs=vfs)
        self.assertNotIn(".git", shell.execute("tree").output)
        self.assertIn(".git", shell.execute("tree -a").output)

    def test_errors(self):
        """Ошибки: нет пути, файл вместо каталога, опция, аргументы."""
        shell = shell_for("deep")
        for line in ("tree nope", "tree root.txt", "tree -x",
                     "tree docs src"):
            self.assertFalse(shell.execute(line).ok, line)


class TacTest(unittest.TestCase):
    """Проверки команды tac."""

    def setUp(self):
        """Создать сеанс с VFS из нескольких файлов."""
        self.shell = shell_for("several")

    def test_reverses_lines(self):
        """tac выводит строки файла в обратном порядке."""
        result = self.shell.execute("tac lines.txt")
        self.assertEqual(result.output,
                         "Третья строка\nВторая строка\nПервая строка")

    def test_multiple_files(self):
        """Несколько файлов обрабатываются по очереди."""
        result = self.shell.execute("tac lines.txt people.csv")
        self.assertEqual(result.output.splitlines()[3], "Борис,22")

    def test_file_without_trailing_newline(self):
        """Файл без завершающего перевода строки обрабатывается."""
        self.shell.vfs.root.add(FileNode("x.txt", b"a\nb"))
        self.assertEqual(self.shell.execute("tac x.txt").output, "b\na")

    def test_empty_file(self):
        """Пустой файл даёт пустой вывод без ошибки."""
        self.shell.vfs.root.add(FileNode("empty", b""))
        result = self.shell.execute("tac empty")
        self.assertEqual((result.output, result.error), ("", ""))

    def test_invalid_utf8_is_replaced(self):
        """Некорректные байты UTF-8 не приводят к падению."""
        self.shell.vfs.root.add(FileNode("bin", b"ok\n\xff\n"))
        self.assertTrue(self.shell.execute("tac bin").ok)

    def test_path_with_directory(self):
        """tac работает с путями внутри каталогов."""
        shell = shell_for("deep")
        result = shell.execute("tac docs/work/2026/q3/summary.txt")
        self.assertEqual(result.output.splitlines()[0], "в работе")

    def test_errors(self):
        """Ошибки: нет операнда, нет файла, каталог."""
        self.assertFalse(self.shell.execute("tac").ok)
        self.assertFalse(self.shell.execute("tac missing").ok)
        result = Shell(vfs=load_vfs(os.path.join(EXAMPLES, "deep"))
                       ).execute("tac docs")
        self.assertIn("Это каталог", result.error)

    def test_partial_failure_keeps_output(self):
        """Ошибка одного файла не отменяет вывод остальных."""
        result = self.shell.execute("tac missing todo.txt")
        self.assertFalse(result.ok)
        self.assertIn("Сделать коммит", result.output)


if __name__ == "__main__":
    unittest.main()
