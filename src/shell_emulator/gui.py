"""Графический интерфейс эмулятора на Tkinter."""

import tkinter as tk
from tkinter import scrolledtext

FONT = ("Consolas", 11)
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
PROMPT_COLOR = "#6a9955"
ERROR_COLOR = "#f48771"
PADDING = 4
TAG_PROMPT = "prompt"
TAG_ERROR = "error"


class ShellWindow:
    """Окно эмулятора: область вывода и строка ввода с приглашением."""

    def __init__(self, root, shell):
        """Создать окно в корневом виджете ``root`` для сеанса ``shell``."""
        self.root = root
        self.shell = shell
        self.history = []
        self.history_pos = 0
        root.title(shell.title)
        self._build_output()
        self._build_input()
        self.entry.focus_set()

    def _build_output(self):
        """Создать область вывода (только для чтения)."""
        self.output = scrolledtext.ScrolledText(
            self.root, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND, wrap=tk.WORD, state=tk.DISABLED,
        )
        self.output.tag_configure(TAG_PROMPT, foreground=PROMPT_COLOR)
        self.output.tag_configure(TAG_ERROR, foreground=ERROR_COLOR)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _build_input(self):
        """Создать строку ввода с приглашением и привязки клавиш."""
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X)
        self.prompt_label = tk.Label(
            frame, text=self.shell.prompt, font=FONT, bg=BACKGROUND,
            fg=PROMPT_COLOR,
        )
        self.prompt_label.pack(side=tk.LEFT, padx=PADDING)
        self.entry = tk.Entry(
            frame, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND, relief=tk.FLAT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=PADDING)
        self.entry.bind("<Return>", self._on_return)
        self.entry.bind("<Up>", self._on_history_up)
        self.entry.bind("<Down>", self._on_history_down)

    def write(self, text, tag=None):
        """Добавить строку текста в область вывода."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def run_command(self, line):
        """Показать введённую строку, выполнить её и вывести результат.

        Возвращает ``Result`` выполненной команды.
        """
        self.write(self.shell.prompt + line, TAG_PROMPT)
        result = self.shell.execute(line)
        if result.output:
            self.write(result.output)
        if result.error:
            self.write(result.error, TAG_ERROR)
        if result.exit_requested:
            self.root.destroy()
        return result

    def _on_return(self, _event):
        """Обработать нажатие Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        self.run_command(line)

    def _show_history(self):
        """Поместить в строку ввода запись истории по текущей позиции."""
        self.entry.delete(0, tk.END)
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])

    def _on_history_up(self, _event):
        """Показать предыдущую команду из истории."""
        if self.history_pos:
            self.history_pos -= 1
            self._show_history()

    def _on_history_down(self, _event):
        """Показать следующую команду из истории."""
        if self.history_pos < len(self.history):
            self.history_pos += 1
            self._show_history()


def run_gui(shell):
    """Открыть окно эмулятора и запустить главный цикл."""
    root = tk.Tk()
    ShellWindow(root, shell)
    root.mainloop()
