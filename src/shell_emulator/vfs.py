"""Виртуальная файловая система (VFS), целиком хранящаяся в памяти.

Источник VFS — каталог на диске пользователя. При загрузке его содержимое
читается в память; исходные данные на диске не распаковываются и не
изменяются. Сохранение (``save_vfs``) записывает текущее состояние в
каталог в том же (исходном) формате.
"""

import os

DEFAULT_OWNER = "root"
ROOT_NAME = ""


class VfsError(Exception):
    """Ошибка загрузки или сохранения VFS."""


class Node:
    """Элемент VFS: имя, владелец и ссылка на родительский каталог."""

    is_dir = False

    def __init__(self, name, owner=DEFAULT_OWNER, parent=None):
        """Создать элемент с именем ``name`` и владельцем ``owner``."""
        self.name = name
        self.owner = owner
        self.parent = parent


class FileNode(Node):
    """Файл VFS: содержимое хранится в памяти в виде байтов."""

    def __init__(self, name, data=b"", owner=DEFAULT_OWNER, parent=None):
        """Создать файл с содержимым ``data``."""
        super().__init__(name, owner, parent)
        self.data = data

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.data)


class DirNode(Node):
    """Каталог VFS: словарь дочерних элементов по имени."""

    is_dir = True

    def __init__(self, name, owner=DEFAULT_OWNER, parent=None):
        """Создать пустой каталог."""
        super().__init__(name, owner, parent)
        self.children = {}

    def add(self, node):
        """Добавить дочерний элемент и вернуть его."""
        node.parent = self
        self.children[node.name] = node
        return node

    def sorted_children(self):
        """Вернуть дочерние элементы, упорядоченные по имени."""
        return [self.children[name] for name in sorted(self.children)]


class Vfs:
    """Дерево VFS с корневым каталогом."""

    def __init__(self, root=None):
        """Создать VFS с корнем ``root`` (по умолчанию пустой каталог)."""
        self.root = root if root is not None else DirNode(ROOT_NAME)

    def walk_files(self):
        """Вернуть список всех файлов дерева."""
        found = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.is_dir:
                stack.extend(node.children.values())
            else:
                found.append(node)
        return found


def _read_file(path, name):
    """Прочитать файл с диска в ``FileNode``."""
    try:
        with open(path, "rb") as handle:
            return FileNode(name, handle.read())
    except OSError as exc:
        raise VfsError(f"не удалось прочитать {path}: {exc}") from exc


def _load_dir(path, node):
    """Рекурсивно загрузить содержимое каталога ``path`` в ``node``."""
    try:
        entries = sorted(os.scandir(path), key=lambda entry: entry.name)
    except OSError as exc:
        raise VfsError(f"не удалось прочитать каталог {path}: {exc}") from exc
    for entry in entries:
        if entry.is_symlink():
            continue
        if entry.is_dir():
            _load_dir(entry.path, node.add(DirNode(entry.name)))
        elif entry.is_file():
            node.add(_read_file(entry.path, entry.name))


def load_vfs(path):
    """Загрузить каталог ``path`` в память и вернуть ``Vfs``.

    Символические ссылки пропускаются. Если путь не существует или не
    является каталогом, выбрасывается ``VfsError``.
    """
    if not os.path.isdir(path):
        raise VfsError(f"каталог VFS не найден: {path}")
    vfs = Vfs()
    _load_dir(path, vfs.root)
    return vfs


def _save_dir(node, path):
    """Рекурсивно записать каталог ``node`` на диск по пути ``path``."""
    os.makedirs(path, exist_ok=True)
    for child in node.sorted_children():
        target = os.path.join(path, child.name)
        if child.is_dir:
            _save_dir(child, target)
        else:
            with open(target, "wb") as handle:
                handle.write(child.data)


def save_vfs(vfs, target):
    """Сохранить состояние VFS в каталог ``target`` в исходном формате.

    Каталог создаётся при необходимости; существующие файлы с теми же
    именами перезаписываются. При ошибке ввода-вывода выбрасывается
    ``VfsError``.
    """
    if os.path.exists(target) and not os.path.isdir(target):
        raise VfsError(f"{target} существует и не является каталогом")
    try:
        _save_dir(vfs.root, target)
    except OSError as exc:
        raise VfsError(f"не удалось сохранить VFS в {target}: {exc}") from exc
