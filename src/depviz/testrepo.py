"""тестовый репозиторий из файла: пакеты названы заглавными буквами"""

import re
from pathlib import Path

from depviz.errors import PackageNotFoundError, RepositoryError

NAME_PATTERN = re.compile(r"[A-Z]+")


def check_name(name, number):
    """имя пакета только из заглавных латинских букв"""
    if not NAME_PATTERN.fullmatch(name):
        raise RepositoryError(
            f"Строка {number}: имя '{name}' должно быть из заглавных "
            "латинских букв"
        )


def parse_line(line, number):
    """разбирает строку вида 'A: B C'"""
    name, separator, rest = line.partition(":")
    if not separator:
        raise RepositoryError(f"Строка {number}: нет двоеточия")
    name = name.strip()
    dependencies = rest.split()
    for item in [name, *dependencies]:
        check_name(item, number)
    return name, dependencies


def parse_repository(text):
    """разбирает текст файла в словарь пакет-зависимости"""
    packages = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        name, dependencies = parse_line(line, number)
        if name in packages:
            raise RepositoryError(f"Строка {number}: пакет {name} повторяется")
        packages[name] = dependencies
    return packages


def load_repository(path):
    """читает файл тестового репозитория"""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        raise RepositoryError(f"Не удалось прочитать {path}: {err}") from err
    return parse_repository(text)


def make_source(packages):
    """источник зависимостей по словарю тестового репозитория"""

    def source(name):
        """зависимости пакета или ошибка, если пакета нет"""
        if name not in packages:
            raise PackageNotFoundError(f"Пакет не найден: {name}")
        return packages[name]

    return source
