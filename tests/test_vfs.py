"""Тесты виртуальной файловой системы."""

import filecmp
import os
import tempfile
import unittest

from shell_emulator.vfs import (DirNode, FileNode, Vfs, VfsError, load_vfs,
                                save_vfs)

EXAMPLES = os.path.join(os.path.dirname(__file__), os.pardir, "examples",
                        "vfs")
DEEP_LEVELS = 3


def example(name):
    """Вернуть путь к примеру VFS ``name``."""
    return os.path.join(EXAMPLES, name)


def same_tree(left, right):
    """Вернуть True, если каталоги полностью совпадают по содержимому."""
    cmp = filecmp.dircmp(left, right)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _match, mismatch, errors = filecmp.cmpfiles(
        left, right, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(os.path.join(left, sub), os.path.join(right, sub))
               for sub in cmp.common_dirs)


def depth(node):
    """Вернуть глубину вложенности каталогов под ``node``."""
    dirs = [child for child in node.children.values() if child.is_dir]
    return 1 + max((depth(child) for child in dirs), default=0)


class LoadVfsTest(unittest.TestCase):
    """Проверки загрузки VFS из каталога."""

    def test_minimal(self):
        """Минимальная VFS содержит один файл."""
        vfs = load_vfs(example("minimal"))
        self.assertEqual(list(vfs.root.children), ["hello.txt"])
        self.assertIn("Привет".encode("utf-8"),
                      vfs.root.children["hello.txt"].data)

    def test_several_files(self):
        """VFS с несколькими файлами загружает их все."""
        vfs = load_vfs(example("several"))
        self.assertEqual(len(vfs.walk_files()), len(os.listdir(
            example("several"))))

    def test_deep_structure(self):
        """В глубокой VFS не менее трёх уровней каталогов."""
        vfs = load_vfs(example("deep"))
        self.assertGreaterEqual(depth(vfs.root) - 1, DEEP_LEVELS)
        q3 = vfs.root.children["docs"].children["work"].children["2026"]
        self.assertIn("summary.txt", q3.children["q3"].children)

    def test_parent_links(self):
        """У каждого элемента задан родитель."""
        vfs = load_vfs(example("deep"))
        for node in vfs.walk_files():
            self.assertIsNotNone(node.parent)
            self.assertIs(node.parent.children[node.name], node)

    def test_default_owner(self):
        """Владелец по умолчанию — root."""
        vfs = load_vfs(example("minimal"))
        self.assertEqual(vfs.root.children["hello.txt"].owner, "root")

    def test_missing_directory(self):
        """Несуществующий каталог — VfsError."""
        with self.assertRaises(VfsError):
            load_vfs(example("no_such_vfs"))

    def test_file_instead_of_directory(self):
        """Путь к файлу вместо каталога — VfsError."""
        with self.assertRaises(VfsError):
            load_vfs(os.path.join(example("minimal"), "hello.txt"))

    def test_memory_changes_do_not_touch_disk(self):
        """Изменения в памяти не затрагивают исходный каталог."""
        path = os.path.join(example("minimal"), "hello.txt")
        with open(path, "rb") as handle:
            before = handle.read()
        vfs = load_vfs(example("minimal"))
        vfs.root.children["hello.txt"].data = b"changed"
        vfs.root.add(FileNode("new.txt", b"x"))
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), before)
        self.assertEqual(os.listdir(example("minimal")), ["hello.txt"])


class SaveVfsTest(unittest.TestCase):
    """Проверки сохранения VFS на диск."""

    def setUp(self):
        """Создать временный каталог для сохранения."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name

    def test_roundtrip_is_identical(self):
        """Загрузка и сохранение дают побайтно идентичный каталог."""
        for name in ("minimal", "several", "deep"):
            target = os.path.join(self.tmp, name)
            save_vfs(load_vfs(example(name)), target)
            self.assertTrue(same_tree(example(name), target), name)

    def test_saves_changes(self):
        """Изменения, сделанные в памяти, попадают на диск."""
        vfs = load_vfs(example("minimal"))
        folder = vfs.root.add(DirNode("sub"))
        folder.add(FileNode("a.txt", b"data"))
        target = os.path.join(self.tmp, "out")
        save_vfs(vfs, target)
        with open(os.path.join(target, "sub", "a.txt"), "rb") as handle:
            self.assertEqual(handle.read(), b"data")

    def test_empty_vfs(self):
        """Пустая VFS сохраняется как пустой каталог."""
        target = os.path.join(self.tmp, "empty")
        save_vfs(Vfs(), target)
        self.assertEqual(os.listdir(target), [])

    def test_target_is_file(self):
        """Если цель — файл, сохранение завершается ошибкой."""
        target = os.path.join(self.tmp, "file")
        with open(target, "w", encoding="utf-8") as handle:
            handle.write("x")
        with self.assertRaises(VfsError):
            save_vfs(Vfs(), target)


if __name__ == "__main__":
    unittest.main()
