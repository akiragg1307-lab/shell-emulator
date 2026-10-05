# shell-emulator

Эмулятор языка оболочки UNIX-подобной ОС с графическим интерфейсом (GUI).
Практическая работа № 1, вариант № 6, дисциплина «Конфигурационное
управление».

## Общее описание

Приложение имитирует работу командной строки UNIX: пользователь вводит
команды в окне, а эмулятор выполняет их над виртуальной файловой системой
(VFS), целиком загруженной в память.

Язык реализации — Python 3 (только стандартная библиотека, GUI на Tkinter).

## Структура репозитория

- `src/shell_emulator/` — исходный код эмулятора;
- `tests/` — модульные тесты (`unittest`);
- `examples/scripts/` — примеры стартовых скриптов (`*.emu`);
- `examples/vfs/` — тестовые VFS: `minimal`, `several`, `deep`;
- `scripts/` — скрипты ОС (`*.sh` и `*.bat`) для проверки параметров;
- `Makefile`, `run.sh`, `run.bat` — запуск приложения и тестов.

## Сборка и запуск

Требуется Python 3.10+ с Tkinter (в установщике для Windows и в большинстве
дистрибутивов Linux он входит в состав; в Debian/Ubuntu: `sudo apt install
python3-tk`).

```
make run            # запуск (Linux/macOS)
./run.sh            # запуск (Linux/macOS)
run.bat             # запуск (Windows)
python -m shell_emulator   # запуск с PYTHONPATH=src
```

## Тесты

```
make test
```

Без `make`: `PYTHONPATH=src python3 -m unittest discover -s tests -v`
(в Windows: `set PYTHONPATH=src` и `python -m unittest discover -s tests`).

## Команды (этап 1)

| Команда | Описание |
|---------|----------|
| `ls [аргументы]` | заглушка: выводит имя и аргументы |
| `cd [аргументы]` | заглушка: выводит имя и аргументы |
| `exit` | закрывает окно эмулятора |
| `vfs-save ПУТЬ` | сохраняет состояние VFS в каталог `ПУТЬ` в исходном формате |

Заголовок окна содержит имя VFS. Парсер корректно обрабатывает аргументы
в двойных (`"a b"`, с экранированием `\"` и `\\`) и одинарных (`'a b'`)
кавычках, а также экранирование пробела (`a\ b`). Ошибки (неизвестная
команда, незакрытая кавычка, лишние аргументы у `exit`) выводятся в окне
красным цветом. Стрелки вверх/вниз листают историю команд.

## Параметры командной строки (этап 2)

| Параметр | Описание |
|----------|----------|
| `--vfs ПУТЬ` | путь к физическому расположению VFS; имя последнего каталога в пути показывается в заголовке окна |
| `--prompt ТЕКСТ` | пользовательское приглашение к вводу (по умолчанию `$ `) |
| `--script ПУТЬ` | путь к стартовому скрипту |

При запуске в окне выводятся строки отладки со всеми заданными
параметрами (`[отладка] vfs: ...`, `[отладка] prompt: ...`,
`[отладка] script: ...`).

## Стартовый скрипт

Файл в кодировке UTF-8, по одной команде эмулятора в строке. Пустые строки
и строки, начинающиеся с `#`, пропускаются. Команды выполняются как диалог:
в окне видны и приглашение с введённой командой, и её вывод.

Выполнение **останавливается при первой ошибке** с сообщением вида
`[скрипт] остановлен: ошибка в строке N: ...`; после этого окно остаётся
открытым для ручной работы. Если файл скрипта не найден или не читается,
выводится сообщение `[скрипт] ошибка: ...`.

## Скрипты ОС для проверки параметров

Запускаются из любого каталога, открывают окно эмулятора с нужными
параметрами. Для каждого сценария есть версия для Linux/macOS (`.sh`)
и Windows (`.bat`):

| Скрипт | Что проверяет |
|--------|---------------|
| `scripts/stage2_all_params` | все три параметра вместе, скрипт завершается `exit` |
| `scripts/stage2_prompt_only` | только `--prompt` |
| `scripts/stage2_defaults` | запуск без параметров |
| `scripts/stage2_script_error` | остановка скрипта на ошибке |
| `scripts/stage2_missing_script` | отсутствующий файл скрипта |

## Виртуальная файловая система (этап 3)

Источник VFS — каталог на диске (параметр `--vfs`). При запуске он целиком
читается в память (`src/shell_emulator/vfs.py`); все операции выполняются
над деревом в памяти, данные на диске не распаковываются и не изменяются.
Если каталог не найден, в окне выводится сообщение `[vfs] ошибка: ...`, а
работа продолжается с пустой VFS.

Команда `vfs-save ПУТЬ` записывает текущее состояние VFS в каталог `ПУТЬ`
(он создаётся при необходимости, одноимённые файлы перезаписываются) в том
же формате — обычное дерево каталогов и файлов. Ошибки (нет аргумента,
цель — файл, нет прав) выводятся сообщением.

Тестовые VFS в `examples/vfs/`:

| Каталог | Содержимое |
|---------|------------|
| `minimal` | один файл |
| `several` | несколько файлов в корне |
| `deep` | вложенность 4 уровня (`docs/work/2026/q3`), файлы на каждом уровне |

Скрипты ОС этапа 3 (`.sh` и `.bat`) запускают эмулятор с этими VFS и
стартовым скриптом `examples/scripts/stage3_all.emu`:
`scripts/stage3_minimal`, `scripts/stage3_several`, `scripts/stage3_deep`,
`scripts/stage3_errors` (ошибка `vfs-save` останавливает скрипт) и
`scripts/stage3_missing_vfs` (каталог VFS не существует). Сохранённые копии
VFS попадают в каталог `out/` (он в `.gitignore`).

## Примеры использования

Сеанс в интерактивном режиме (приглашение по умолчанию — `$ `):

```
$ ls
команда: ls, аргументы: []
$ ls -l /home "My Documents" 'a b'
команда: ls, аргументы: ['-l', '/home', 'My Documents', 'a b']
$ cd /usr/local
команда: cd, аргументы: ['/usr/local']
$ cd "dir with spaces"
команда: cd, аргументы: ['dir with spaces']
$ echo
echo: команда не найдена
$ ls "незакрытая
ошибка разбора: незакрытая двойная кавычка
$ 
$ exit now
exit: слишком много аргументов
$ exit
[окно закрыто]
```

Запуск с параметрами и стартовым скриптом (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/demo --prompt "demo$ " --script examples/scripts/stage2_ok.emu
[заголовок окна] Эмулятор оболочки — demo
[отладка] vfs: examples/vfs/demo
[отладка] prompt: 'demo$ '
[отладка] script: examples/scripts/stage2_ok.emu
demo$ ls
команда: ls, аргументы: []
demo$ ls -l "папка с пробелами" 'a b'
команда: ls, аргументы: ['-l', 'папка с пробелами', 'a b']
demo$ cd /usr/local
команда: cd, аргументы: ['/usr/local']
demo$ exit

$ python -m shell_emulator --script examples/scripts/stage2_error.emu
[заголовок окна] Эмулятор оболочки — vfs
[отладка] vfs: (не задан)
[отладка] prompt: '$ '
[отладка] script: examples/scripts/stage2_error.emu
$ ls /home
команда: ls, аргументы: ['/home']
$ cd "my dir"
команда: cd, аргументы: ['my dir']
$ unknown_command arg
unknown_command: команда не найдена
[скрипт] остановлен: ошибка в строке 4: unknown_command arg

$ python -m shell_emulator --script examples/scripts/no_such_file.emu
[заголовок окна] Эмулятор оболочки — vfs
[отладка] vfs: (не задан)
[отладка] prompt: '$ '
[отладка] script: examples/scripts/no_such_file.emu
[скрипт] ошибка: не удалось прочитать скрипт examples/scripts/no_such_file.emu: [Errno 2] No such file or directory: 'examples/scripts/no_such_file.emu'
```

Работа с VFS, `vfs-save` и обработка ошибок (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage3_all.emu
[заголовок окна] Эмулятор оболочки — deep
[отладка] vfs: examples/vfs/deep
[отладка] prompt: '$ '
[отладка] script: examples/scripts/stage3_all.emu
$ ls
команда: ls, аргументы: []
$ ls -l "my dir" 'a b'
команда: ls, аргументы: ['-l', 'my dir', 'a b']
$ cd /docs/work
команда: cd, аргументы: ['/docs/work']
$ vfs-save out/vfs-copy
VFS сохранена в out/vfs-copy
$ ls out
команда: ls, аргументы: ['out']
$ exit

$ python -m shell_emulator --vfs examples/vfs/several --script examples/scripts/stage3_errors.emu
[заголовок окна] Эмулятор оболочки — several
[отладка] vfs: examples/vfs/several
[отладка] prompt: '$ '
[отладка] script: examples/scripts/stage3_errors.emu
$ vfs-save out/ok-copy
VFS сохранена в out/ok-copy
$ vfs-save
vfs-save: использование: vfs-save путь
[скрипт] остановлен: ошибка в строке 3: vfs-save

$ python -m shell_emulator --vfs examples/vfs/no_such_vfs
[заголовок окна] Эмулятор оболочки — no_such_vfs
[отладка] vfs: examples/vfs/no_such_vfs
[отладка] prompt: '$ '
[отладка] script: (не задан)
[vfs] ошибка: каталог VFS не найден: examples/vfs/no_such_vfs
```
