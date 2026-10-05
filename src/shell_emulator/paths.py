"""Работа с путями VFS: разрешение относительных и абсолютных путей."""

from shell_emulator.vfs import VfsError

SEPARATOR = "/"
CURRENT = "."
PARENT = ".."
NO_SUCH_PATH = "Нет такого файла или каталога"
NOT_A_DIRECTORY = "Не каталог"


def _step(node, part):
    """Перейти из каталога ``node`` в элемент ``part`` (с ``.`` и ``..``)."""
    if part in ("", CURRENT):
        return node
    if part == PARENT:
        return node.parent if node.parent is not None else node
    if not node.is_dir:
        raise VfsError(NOT_A_DIRECTORY)
    if part not in node.children:
        raise VfsError(NO_SUCH_PATH)
    return node.children[part]


def resolve_path(vfs, cwd, path):
    """Найти элемент VFS по пути ``path`` относительно каталога ``cwd``.

    Путь, начинающийся с ``/``, считается абсолютным. Поддерживаются
    ``.``, ``..`` и повторяющиеся разделители. Если путь заканчивается
    разделителем, он должен указывать на каталог. При ошибке выбрасывается
    ``VfsError`` с текстом причины.
    """
    node = vfs.root if path.startswith(SEPARATOR) else cwd
    for part in path.split(SEPARATOR):
        node = _step(node, part)
    if path.endswith(SEPARATOR) and not node.is_dir:
        raise VfsError(NOT_A_DIRECTORY)
    return node


def absolute_path(node):
    """Вернуть абсолютный путь элемента VFS (корень — ``/``)."""
    parts = []
    while node.parent is not None:
        parts.append(node.name)
        node = node.parent
    return SEPARATOR + SEPARATOR.join(reversed(parts))
