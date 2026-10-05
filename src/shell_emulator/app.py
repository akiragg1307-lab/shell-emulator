"""Сборка приложения: настройки, отладочный вывод и стартовый скрипт."""

from shell_emulator.config import debug_lines, parse_args
from shell_emulator.gui import TAG_DEBUG, TAG_ERROR, run_gui
from shell_emulator.script import ScriptError, load_script, run_script
from shell_emulator.shell import Shell


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


def make_startup(config):
    """Создать обработчик, вызываемый после открытия окна."""

    def startup(window):
        """Показать отладочный вывод параметров и запустить скрипт."""
        for line in debug_lines(config):
            window.write(line, TAG_DEBUG)
        if config.script_path:
            run_startup_script(window, config.script_path)

    return startup


def main(argv=None):
    """Разобрать параметры и запустить эмулятор."""
    config = parse_args(argv)
    shell = Shell(vfs_name=config.vfs_name, prompt=config.prompt)
    run_gui(shell, make_startup(config))
