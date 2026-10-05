"""Разбор строки команды на аргументы с учётом кавычек.

Поддерживаются:
- пробельные символы как разделители аргументов;
- двойные кавычки (внутри допустимы экранирования ``\\"`` и ``\\\\``);
- одинарные кавычки (содержимое берётся буквально);
- экранирование символа обратной косой чертой вне кавычек;
- пустой аргумент в кавычках (``""``).
"""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
ESCAPE = "\\"
DOUBLE_QUOTE_ESCAPABLE = (DOUBLE_QUOTE, ESCAPE)
NEXT_CHAR = 1
NOT_FOUND = -1


class ParseError(Exception):
    """Ошибка разбора строки команды."""


def _read_single_quoted(line, pos):
    """Прочитать текст в одинарных кавычках.

    ``pos`` указывает на символ после открывающей кавычки. Возвращает
    пару (текст, позиция после закрывающей кавычки).
    """
    end = line.find(SINGLE_QUOTE, pos)
    if end == NOT_FOUND:
        raise ParseError("незакрытая одинарная кавычка")
    return line[pos:end], end + NEXT_CHAR


def _read_double_quoted(line, pos):
    """Прочитать текст в двойных кавычках с поддержкой экранирования."""
    chars = []
    while pos < len(line):
        char = line[pos]
        if char == DOUBLE_QUOTE:
            return "".join(chars), pos + NEXT_CHAR
        follows = pos + NEXT_CHAR < len(line)
        if char == ESCAPE and follows:
            if line[pos + NEXT_CHAR] in DOUBLE_QUOTE_ESCAPABLE:
                pos += NEXT_CHAR
                char = line[pos]
        chars.append(char)
        pos += NEXT_CHAR
    raise ParseError("незакрытая двойная кавычка")


def _read_escaped(line, pos):
    """Прочитать символ, экранированный обратной косой чертой."""
    if pos >= len(line):
        raise ParseError("обратная косая черта в конце строки")
    return line[pos], pos + NEXT_CHAR


_QUOTE_READERS = {
    SINGLE_QUOTE: _read_single_quoted,
    DOUBLE_QUOTE: _read_double_quoted,
    ESCAPE: _read_escaped,
}


def parse_line(line):
    """Разобрать строку на список аргументов.

    Первый элемент результата — имя команды. Для пустой строки
    возвращается пустой список. При некорректных кавычках выбрасывается
    ``ParseError``.
    """
    args = []
    current = []
    in_token = False
    pos = 0
    while pos < len(line):
        char = line[pos]
        if char.isspace():
            if in_token:
                args.append("".join(current))
                current = []
                in_token = False
            pos += NEXT_CHAR
        elif char in _QUOTE_READERS:
            text, pos = _QUOTE_READERS[char](line, pos + NEXT_CHAR)
            current.append(text)
            in_token = True
        else:
            current.append(char)
            in_token = True
            pos += NEXT_CHAR
    if in_token:
        args.append("".join(current))
    return args
