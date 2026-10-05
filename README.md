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

## Команды

| Команда | Описание |
|---------|----------|
| `ls [-l] [-a] [путь...]` | содержимое каталога; `-l` — подробно, `-a` — со скрытыми (`.имя`) |
| `cd [путь]` | смена текущего каталога (абсолютные и относительные пути, `.`, `..`); без аргумента — корень VFS |
| `pwd` | абсолютный путь текущего каталога |
| `tree [-a] [путь]` | дерево каталогов и файлов с итогом `каталогов: N, файлов: M` |
| `tac файл...` | строки файлов в обратном порядке |
| `chown [-R] ВЛАДЕЛЕЦ ПУТЬ...` | смена владельца файлов и каталогов (только в памяти); `-R` — рекурсивно |
| `vfs-save ПУТЬ` | сохраняет состояние VFS в каталог `ПУТЬ` в исходном формате |
| `exit` | закрывает окно эмулятора |

Для `ls -l` выводятся тип (`d` или `-`), владелец, размер и имя; при нескольких
путях `ls` печатает заголовки `путь:`. Ошибки выводятся в стиле UNIX (`ls: невозможно получить доступ к 'x':
Нет такого файла или каталога`, `cd: x: Не каталог`, `tac: x: Это каталог`).
Если команда получила несколько путей и часть из них недоступна, вывод
доступных путей не отменяется.

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
| `scripts/stage2_all_params` | все три параметра вместе |
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

## Скрипты ОС этапа 4

`scripts/stage4_all` запускает эмулятор на VFS `deep` и стартовый скрипт
`examples/scripts/stage4_all.emu` со всеми режимами `ls`, `cd`, `tree`,
`tac`. `scripts/stage4_errors` по очереди запускает четыре скрипта с
ошибками (`stage4_error_ls|cd|tree|tac.emu`); после каждой ошибки скрипт
останавливается, окно нужно закрыть вручную.

## Изменение владельца (этап 5)

`chown [-R] ВЛАДЕЛЕЦ ПУТЬ...` меняет владельца элементов VFS; результат
виден в `ls -l`. Изменение выполняется **только в памяти**: каталог на
диске не затрагивается, а при `vfs-save` сохраняется структура и
содержимое (в формате «каталог на диске» владельцев хранить негде).
Группы (`владелец:группа`) не поддерживаются и дают ошибку; ошибка по
одному из путей не отменяет смену владельца для остальных.

Скрипты ОС: `scripts/stage5_all` (все режимы, `examples/scripts/
stage5_all.emu`) и `scripts/stage5_errors` (три сценария с ошибками
`stage5_error_path|args|group.emu`).

## Примеры использования

Сеанс в интерактивном режиме на VFS `several` (приглашение по умолчанию — `$ `):

```
$ ls
README.md
lines.txt
people.csv
todo.txt
$ ls -l "." '/'
.:
- root         83 README.md
- root         78 lines.txt
- root         48 people.csv
- root        112 todo.txt
/:
- root         83 README.md
- root         78 lines.txt
- root         48 people.csv
- root        112 todo.txt
$ cd "dir with spaces"
cd: dir with spaces: Нет такого файла или каталога
$ ls "дерево
ошибка разбора: незакрытая двойная кавычка
$ echo
echo: команда не найдена
$ 
$ exit now
exit: слишком много аргументов
$ exit
[окно закрыто]
```

Запуск с параметрами и стартовым скриптом (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/several --prompt "demo$ " --script examples/scripts/stage2_ok.emu
[заголовок окна] Эмулятор оболочки — several
[отладка] vfs: examples/vfs/several
[отладка] prompt: 'demo$'
[отладка] script: examples/scripts/stage2_ok.emu
demo$pwd
/
demo$ls
README.md
lines.txt
people.csv
todo.txt
demo$ls -l "." '/'
.:
- root         83 README.md
- root         78 lines.txt
- root         48 people.csv
- root        112 todo.txt
/:
- root         83 README.md
- root         78 lines.txt
- root         48 people.csv
- root        112 todo.txt
demo$cd "/"

$ python -m shell_emulator --script examples/scripts/stage2_error.emu
[заголовок окна] Эмулятор оболочки — vfs
[отладка] vfs: (не задан)
[отладка] prompt: '$ '
[отладка] script: examples/scripts/stage2_error.emu
$ pwd
/
$ ls "."
$ unknown_command arg
unknown_command: команда не найдена
[скрипт] остановлен: ошибка в строке 4: unknown_command arg

$ python -m shell_emulator --script examples/scripts/no_such_file.emu
[заголовок окна] Эмулятор оболочки — vfs
[отладка] vfs: (не задан)
[отладка] prompt: '$ '
[отладка] script: examples/scripts/no_such_file.emu
[скрипт] ошибка: не удалось прочитать скрипт examples/scripts/no_such_file.emu: No such file or directory
```

Работа с VFS, `vfs-save` и обработка ошибок (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage3_all.emu
[заголовок окна] Эмулятор оболочки — deep
[отладка] vfs: examples/vfs/deep
[отладка] prompt: '$ '
[отладка] script: examples/scripts/stage3_all.emu
$ pwd
/
$ ls
docs
root.txt
src
$ ls -l
d root          - docs
- root         26 root.txt
d root          - src
$ cd "/"
$ tree
.
├── docs
│   ├── index.txt
│   ├── personal
│   │   └── notes.txt
│   └── work
│       ├── 2026
│       │   ├── q3
│       │   │   └── summary.txt
│       │   └── report.txt
│       └── plan.txt
├── root.txt
└── src
    └── app
        ├── main.py
        └── utils
            └── helpers.py

каталогов: 8, файлов: 8
$ vfs-save out/vfs-copy
VFS сохранена в out/vfs-copy

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

Все режимы команд этапа 4 (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage4_all.emu
[заголовок окна] Эмулятор оболочки — deep
[отладка] vfs: examples/vfs/deep
[отладка] prompt: '$ '
[отладка] script: examples/scripts/stage4_all.emu
$ pwd
/
$ ls
docs
root.txt
src
$ ls -l
d root          - docs
- root         26 root.txt
d root          - src
$ ls -a
docs
root.txt
src
$ ls -l docs/work
d root          - 2026
- root         83 plan.txt
$ ls docs/personal src/app
docs/personal:
notes.txt
src/app:
main.py
utils
$ cd docs/work/2026
$ pwd
/docs/work/2026
$ ls
q3
report.txt
$ cd ../..
$ pwd
/docs
$ cd /src/app/utils
$ ls -l
- root         28 helpers.py
$ cd
$ tree
.
├── docs
│   ├── index.txt
│   ├── personal
│   │   └── notes.txt
│   └── work
│       ├── 2026
│       │   ├── q3
│       │   │   └── summary.txt
│       │   └── report.txt
│       └── plan.txt
├── root.txt
└── src
    └── app
        ├── main.py
        └── utils
            └── helpers.py

каталогов: 8, файлов: 8
$ tree docs/work
docs/work
├── 2026
│   ├── q3
│   │   └── summary.txt
│   └── report.txt
└── plan.txt

каталогов: 2, файлов: 3
$ tree -a src
src
└── app
    ├── main.py
    └── utils
        └── helpers.py

каталогов: 2, файлов: 2
$ tac root.txt
Корневой файл
$ tac docs/work/plan.txt
Квартал 3
Квартал 2
Квартал 1
План работ на год
$ tac docs/index.txt docs/personal/notes.txt
Документы
Личные заметки
```

Ошибки команд этапа 4 (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage4_error_ls.emu
[заголовок окна] Эмулятор оболочки — deep
$ ls docs
index.txt
personal
work
$ ls -z
ls: неверная опция -- 'z'
[скрипт] остановлен: ошибка в строке 3: ls -z

$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage4_error_cd.emu
[заголовок окна] Эмулятор оболочки — deep
$ cd docs
$ cd /root.txt
cd: /root.txt: Не каталог
[скрипт] остановлен: ошибка в строке 3: cd /root.txt

$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage4_error_tree.emu
[заголовок окна] Эмулятор оболочки — deep
$ tree docs/personal
docs/personal
└── notes.txt

каталогов: 0, файлов: 1
$ tree root.txt
tree: root.txt: Не каталог
[скрипт] остановлен: ошибка в строке 3: tree root.txt

$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage4_error_tac.emu
[заголовок окна] Эмулятор оболочки — deep
$ tac root.txt
Корневой файл
$ tac docs
tac: docs: Это каталог
[скрипт] остановлен: ошибка в строке 3: tac docs
```

chown: все режимы и ошибки (вывод окна):

```
$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage5_all.emu
[заголовок окна] Эмулятор оболочки — deep
$ ls -l
d root          - docs
- root         26 root.txt
d root          - src
$ chown alice root.txt
$ ls -l
d root          - docs
- alice        26 root.txt
d root          - src
$ chown bob docs src
$ ls -l
d bob           - docs
- alice        26 root.txt
d bob           - src
$ chown -R carol docs/work
$ ls -l docs/work
d carol         - 2026
- carol        83 plan.txt
$ tree docs
docs
├── index.txt
├── personal
│   └── notes.txt
└── work
    ├── 2026
    │   ├── q3
    │   │   └── summary.txt
    │   └── report.txt
    └── plan.txt

каталогов: 4, файлов: 5
$ cd docs
$ chown dave index.txt
$ ls -l
- dave         19 index.txt
d root          - personal
d carol         - work
$ cd /
$ vfs-save out/stage5-copy
VFS сохранена в out/stage5-copy

$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage5_error_path.emu
[заголовок окна] Эмулятор оболочки — deep
$ chown alice root.txt
$ chown bob no_such_file
chown: невозможно получить доступ к 'no_such_file': Нет такого файла или каталога
[скрипт] остановлен: ошибка в строке 3: chown bob no_such_file

$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage5_error_args.emu
[заголовок окна] Эмулятор оболочки — deep
$ chown -R alice docs
$ chown alice
chown: пропущен операнд
использование: chown [-R] владелец путь...
[скрипт] остановлен: ошибка в строке 3: chown alice

$ python -m shell_emulator --vfs examples/vfs/deep --script examples/scripts/stage5_error_group.emu
[заголовок окна] Эмулятор оболочки — deep
$ chown alice:staff root.txt
chown: группы не поддерживаются: 'alice:staff'
[скрипт] остановлен: ошибка в строке 2: chown alice:staff root.txt
```
