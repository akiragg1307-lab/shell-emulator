"""Тесты команды chown."""

import os
import tempfile
import unittest

from shell_emulator.shell import Shell
from shell_emulator.vfs import load_vfs

DEEP = os.path.join(os.path.dirname(__file__), os.pardir, "examples", "vfs",
                    "deep")


class ChownTest(unittest.TestCase):
    """Проверки смены владельца в памяти."""

    def setUp(self):
        """Создать сеанс с глубокой VFS."""
        self.shell = Shell(vfs=load_vfs(DEEP))

    def owner_of(self, path):
        """Вернуть владельца элемента по пути (через ls -l)."""
        line = self.shell.execute(f"ls -l {path}").output.splitlines()[0]
        return line.split()[1]

    def test_change_file_owner(self):
        """chown меняет владельца файла, что видно в ls -l."""
        self.assertEqual(self.owner_of("root.txt"), "root")
        self.assertTrue(self.shell.execute("chown alice root.txt").ok)
        self.assertEqual(self.owner_of("root.txt"), "alice")

    def test_change_directory_owner_not_recursive(self):
        """Без -R владелец вложенных элементов не меняется."""
        self.shell.execute("chown bob docs")
        node = self.shell.vfs.root.children["docs"]
        self.assertEqual(node.owner, "bob")
        self.assertEqual(node.children["index.txt"].owner, "root")

    def test_recursive(self):
        """С -R владелец меняется у всего поддерева."""
        self.shell.execute("chown -R carol docs/work")
        for path in ("docs/work", "docs/work/plan.txt",
                     "docs/work/2026/q3/summary.txt"):
            node = self.shell.vfs.root
            for part in path.split("/"):
                node = node.children[part]
            self.assertEqual(node.owner, "carol", path)
        self.assertEqual(self.owner_of("docs/index.txt"), "root")

    def test_multiple_paths_and_relative(self):
        """Несколько путей и относительные пути обрабатываются."""
        self.shell.execute("cd docs")
        self.shell.execute("chown dave index.txt personal")
        self.assertEqual(self.owner_of("index.txt"), "dave")
        docs = self.shell.vfs.root.children["docs"]
        self.assertEqual(docs.owner, "root")
        self.assertEqual(docs.children["personal"].owner, "dave")

    def test_missing_path_does_not_stop_others(self):
        """Ошибка одного пути не отменяет смену владельца у других."""
        result = self.shell.execute("chown eve nope root.txt")
        self.assertFalse(result.ok)
        self.assertIn("nope", result.error)
        self.assertEqual(self.owner_of("root.txt"), "eve")

    def test_argument_errors(self):
        """Нет операндов, неверная опция, группа, пустой владелец."""
        for line in ("chown", "chown alice", "chown -x a root.txt",
                     "chown a:b root.txt", 'chown " " root.txt'):
            self.assertFalse(self.shell.execute(line).ok, line)

    def test_disk_is_not_modified(self):
        """Смена владельца не затрагивает исходный каталог на диске."""
        before = sorted(os.listdir(DEEP))
        self.shell.execute("chown -R mallory /")
        self.assertEqual(sorted(os.listdir(DEEP)), before)

    def test_vfs_save_keeps_structure_after_chown(self):
        """vfs-save после chown сохраняет структуру и содержимое."""
        self.shell.execute("chown -R x /")
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "copy")
            self.assertTrue(self.shell.execute(f'vfs-save "{target}"').ok)
            with open(os.path.join(target, "root.txt"), "rb") as copy:
                with open(os.path.join(DEEP, "root.txt"), "rb") as source:
                    self.assertEqual(copy.read(), source.read())


if __name__ == "__main__":
    unittest.main()
