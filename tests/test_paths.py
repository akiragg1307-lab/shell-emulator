"""Тесты разрешения путей VFS."""

import unittest

from shell_emulator.paths import absolute_path, resolve_path
from shell_emulator.vfs import DirNode, FileNode, Vfs, VfsError


class PathsTest(unittest.TestCase):
    """Проверки resolve_path и absolute_path на небольшом дереве."""

    def setUp(self):
        """Построить дерево /a/b/c.txt, /a/x.txt, /top.txt."""
        self.vfs = Vfs()
        root = self.vfs.root
        self.a = root.add(DirNode("a"))
        self.b = self.a.add(DirNode("b"))
        self.c = self.b.add(FileNode("c.txt", b"c"))
        self.x = self.a.add(FileNode("x.txt", b"x"))
        self.top = root.add(FileNode("top.txt", b"t"))

    def resolve(self, path, cwd=None):
        """Разрешить путь относительно ``cwd`` (по умолчанию корня)."""
        return resolve_path(self.vfs, cwd or self.vfs.root, path)

    def test_absolute_path(self):
        """Абсолютный путь не зависит от текущего каталога."""
        self.assertIs(self.resolve("/a/b/c.txt", self.b), self.c)

    def test_relative_path(self):
        """Относительный путь считается от текущего каталога."""
        self.assertIs(self.resolve("b/c.txt", self.a), self.c)

    def test_dot_and_dotdot(self):
        """Поддерживаются . и .. в произвольных местах."""
        self.assertIs(self.resolve("./b/../x.txt", self.a), self.x)
        self.assertIs(self.resolve("../..", self.b), self.vfs.root)

    def test_dotdot_at_root_stays_in_root(self):
        """Выше корня подняться нельзя."""
        self.assertIs(self.resolve("/../.."), self.vfs.root)

    def test_repeated_and_trailing_separators(self):
        """Лишние и завершающие разделители допустимы для каталогов."""
        self.assertIs(self.resolve("//a///b/"), self.b)

    def test_empty_path_is_current_directory(self):
        """Пустой путь означает текущий каталог."""
        self.assertIs(self.resolve("", self.a), self.a)

    def test_missing_path(self):
        """Несуществующий элемент — VfsError."""
        with self.assertRaises(VfsError):
            self.resolve("/a/nope")

    def test_through_file_is_error(self):
        """Путь «через» файл — ошибка."""
        with self.assertRaises(VfsError):
            self.resolve("/top.txt/inner")

    def test_trailing_slash_on_file_is_error(self):
        """Завершающий разделитель после файла — ошибка."""
        with self.assertRaises(VfsError):
            self.resolve("/top.txt/")

    def test_absolute_path_of_nodes(self):
        """Абсолютные пути узлов строятся от корня."""
        self.assertEqual(absolute_path(self.vfs.root), "/")
        self.assertEqual(absolute_path(self.b), "/a/b")
        self.assertEqual(absolute_path(self.c), "/a/b/c.txt")


if __name__ == "__main__":
    unittest.main()
