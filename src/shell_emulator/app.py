"""Сборка приложения: настройки, отладочный вывод и стартовый скрипт."""

from shell_emulator.config import debug_lines, parse_args
from shell_emulator.script import ScriptError, load_script, run_script
from shell_emulator.shell import Shell
from shell_emulator.tags import TAG_DEBUG, TAG_ERROR
from shell_emulator.vfs import VfsError, load_vfs


def run_startup_script(window, path):
    """Выполнить стартовый скрипт ``path`` в окне ``window``.

    Ввод и вывод команд показываются как диалог с пользователем.
    Об ошибке чтения или выполнения скрипта сообщается в окне.
    """
    try:
        lines = load_script(path)
    except ScriptError as exc:
        window.write(f"[скрипт] ошибка: {exc}", TAG_ERROR)
        return False

    def report(text):
        """Вывести сообщение об ошибке скрипта."""
        window.write(text, TAG_ERROR)

    return run_script(lines, window.run_command, report)


def create_shell(config):
    """Создать сеанс эмулятора и загрузить VFS в память.

    Возвращает пару (сеанс, список сообщений об ошибках). Если VFS не
    удалось загрузить, работа продолжается с пустой VFS.
    """
    vfs = None
    errors = []
    if config.vfs_path:
        try:
            vfs = load_vfs(config.vfs_path)
        except VfsError as exc:
            errors.append(f"[vfs] ошибка: {exc}")
    shell = Shell(config.vfs_name, config.prompt, vfs)
    return shell, errors


def make_startup(config, errors=()):
    """Создать обработчик, вызываемый после открытия окна.

    ``errors`` — сообщения об ошибках запуска, которые нужно показать.
    """

    def startup(window):
        """Показать отладочный вывод, ошибки запуска и выполнить скрипт."""
        for line in debug_lines(config):
            window.write(line, TAG_DEBUG)
        for message in errors:
            window.write(message, TAG_ERROR)
        if config.script_path:
            run_startup_script(window, config.script_path)

    return startup


def main(argv=None):
    """Разобрать параметры и запустить эмулятор."""
    from shell_emulator.gui import run_gui

    config = parse_args(argv)
    shell, errors = create_shell(config)
    run_gui(shell, make_startup(config, errors))
