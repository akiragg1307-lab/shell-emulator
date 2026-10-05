"""Тесты парсера строки команды."""

import unittest

from shell_emulator.parser import ParseError, parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки функции parse_line."""

    def test_empty_line(self):
        """Пустая строка и пробелы дают пустой список."""
        self.assertEqual(parse_line(""), [])
        self.assertEqual(parse_line("   \t "), [])

    def test_plain_arguments(self):
        """Аргументы без кавычек делятся по пробелам."""
        self.assertEqual(parse_line("ls  -l   /home"), ["ls", "-l", "/home"])

    def test_double_quotes_keep_spaces(self):
        """Пробелы в двойных кавычках сохраняются."""
        self.assertEqual(parse_line('ls "my dir" x'), ["ls", "my dir", "x"])

    def test_single_quotes_are_literal(self):
        """В одинарных кавычках экранирование не действует."""
        self.assertEqual(parse_line(r"echo 'a\b c'"), ["echo", r"a\b c"])

    def test_adjacent_parts_are_joined(self):
        """Соседние части без пробела склеиваются в один аргумент."""
        self.assertEqual(parse_line("a\"b c\"d'e f'"), ["ab cde f"])

    def test_empty_quoted_argument(self):
        """Пустые кавычки дают пустой аргумент."""
        self.assertEqual(parse_line('a "" b'), ["a", "", "b"])

    def test_escapes(self):
        """Экранирование работает вне кавычек и внутри двойных."""
        self.assertEqual(parse_line(r"a\ b"), ["a b"])
        self.assertEqual(parse_line(r'"q\"r\\s"'), ['q"r\\s'])

    def test_backslash_before_other_char_in_double_quotes(self):
        """Обратная косая черта перед обычным символом остаётся."""
        self.assertEqual(parse_line(r'"a\nb"'), [r"a\nb"])

    def test_unclosed_double_quote(self):
        """Незакрытая двойная кавычка — ошибка."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')

    def test_unclosed_single_quote(self):
        """Незакрытая одинарная кавычка — ошибка."""
        with self.assertRaises(ParseError):
            parse_line("ls 'abc")

    def test_trailing_backslash(self):
        """Обратная косая черта в конце строки — ошибка."""
        with self.assertRaises(ParseError):
            parse_line("ls \\")


if __name__ == "__main__":
    unittest.main()
