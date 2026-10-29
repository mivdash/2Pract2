"""тесты тестового репозитория"""

import pytest

from depviz.errors import PackageNotFoundError, RepositoryError
from depviz.testrepo import load_repository, make_source, parse_repository


def test_valid_text():
    """корректный текст разбирается в словарь"""
    packages = parse_repository("A: B C\nB: C\nC:\n")
    assert packages == {"A": ["B", "C"], "B": ["C"], "C": []}


def test_blank_lines_are_skipped():
    """пустые строки пропускаются"""
    assert parse_repository("\nA: B\n\nB:\n\n") == {"A": ["B"], "B": []}


def test_extra_spaces_are_allowed():
    """лишние пробелы не мешают"""
    assert parse_repository("  A :  B   C \n") == {"A": ["B", "C"]}


@pytest.mark.parametrize(
    "text, message",
    [
        ("A B\n", "двоеточия"),
        ("a: B\n", "заглавных"),
        ("A: b\n", "заглавных"),
        ("A1: B\n", "заглавных"),
        (": B\n", "заглавных"),
        ("A: B\nA: C\n", "повторяется"),
    ],
)
def test_invalid_text(text, message):
    """неверные строки дают ошибку с номером строки"""
    with pytest.raises(RepositoryError, match=message):
        parse_repository(text)


def test_error_contains_line_number():
    """в ошибке указан номер строки"""
    with pytest.raises(RepositoryError, match="Строка 2"):
        parse_repository("A: B\nbroken\n")


def test_load_from_file(test_repo_file):
    """файл репозитория читается"""
    assert load_repository(test_repo_file)["A"] == ["B", "C"]


def test_load_missing_file(tmp_path):
    """отсутствующий файл даёт RepositoryError"""
    with pytest.raises(RepositoryError, match="Не удалось"):
        load_repository(str(tmp_path / "nope.txt"))


def test_load_not_utf8(tmp_path):
    """файл не в utf-8 даёт RepositoryError"""
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff\xfe\x00A: B")
    with pytest.raises(RepositoryError):
        load_repository(str(path))


def test_source_returns_dependencies():
    """источник отдаёт зависимости известного пакета"""
    source = make_source({"A": ["B"]})
    assert source("A") == ["B"]


def test_source_unknown_package():
    """источник сообщает о неизвестном пакете"""
    with pytest.raises(PackageNotFoundError, match="Z"):
        make_source({"A": []})("Z")
