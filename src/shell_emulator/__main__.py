"""Точка входа: ``python -m shell_emulator``."""

from shell_emulator.gui import run_gui
from shell_emulator.shell import Shell


def main():
    """Создать сеанс эмулятора и запустить графический интерфейс."""
    run_gui(Shell())


if __name__ == "__main__":
    main()
