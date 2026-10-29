"""тесты примеров из папки examples"""

from pathlib import Path

import pytest

from depviz.cli import EXIT_ERROR, EXIT_OK, main

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


def run_example(name, monkeypatch, capsys, reverse=False):
    """запускает пример из корня проекта и возвращает код и вывод"""
    monkeypatch.chdir(ROOT)
    args = [str(EXAMPLES / f"{name}.yaml")]
    code = main(["--reverse", *args] if reverse else args)
    return code, capsys.readouterr()


@pytest.mark.parametrize(
    "name, expected",
    [
        ("chain", ["A -> B", "B -> C", "C -> (нет зависимостей)"]),
        (
            "diamond",
            ["A -> B, C", "B -> D", "C -> D", "D -> (нет зависимостей)"],
        ),
        ("cycle", ["A -> B", "B -> C", "C -> A"]),
        (
            "filter",
            ["A -> B, C", "B -> (нет зависимостей)", "C -> (нет зависимостей)"],
        ),
    ],
)
def test_example_output(name, expected, monkeypatch, capsys):
    """пример печатает ожидаемый граф"""
    code, captured = run_example(name, monkeypatch, capsys)
    assert code == EXIT_OK
    assert captured.out.splitlines()[1:] == expected


@pytest.mark.parametrize(
    "name, message",
    [
        ("unknown", "Пакет не найден: Z"),
    ],
)
def test_example_errors(name, message, monkeypatch, capsys):
    """примеры с ошибками завершаются с кодом 1"""
    code, captured = run_example(name, monkeypatch, capsys)
    assert code == EXIT_ERROR
    assert message in captured.err


@pytest.mark.parametrize(
    "name, expected",
    [
        (
            "rev_diamond",
            [
                "D <- B, C",
                "B <- A",
                "C <- A",
                "A <- (никто не зависит)",
                "Зависят от D: B, C, A",
            ],
        ),
        (
            "rev_top",
            ["A <- (никто не зависит)", "Зависят от A: никто"],
        ),
        (
            "rev_cycle",
            ["A <- C", "C <- B", "B <- A", "Зависят от A: C, B"],
        ),
        (
            "rev_filter",
            [
                "D <- C",
                "C <- A",
                "A <- (никто не зависит)",
                "Зависят от D: C, A",
            ],
        ),
        (
            "rev_chain",
            [
                "C <- B",
                "B <- A",
                "A <- (никто не зависит)",
                "Зависят от C: B, A",
            ],
        ),
    ],
)
def test_reverse_example_output(name, expected, monkeypatch, capsys):
    """пример печатает ожидаемые обратные зависимости"""
    code, captured = run_example(name, monkeypatch, capsys, reverse=True)
    assert code == EXIT_OK
    assert captured.out.splitlines()[1:] == expected


def test_reverse_example_error(monkeypatch, capsys):
    """неизвестный пакет в режиме обратных зависимостей даёт ошибку"""
    code, captured = run_example("rev_unknown", monkeypatch, capsys, True)
    assert code == EXIT_ERROR
    assert "Пакет не найден: Z" in captured.err
