"""тесты описания graphviz и сохранения png"""

import shutil
import subprocess

import pytest

from depviz.dot import (
    dot_path,
    quote,
    render_png,
    save_image,
    to_dot,
    write_dot,
)
from depviz.errors import RenderError

GRAPH = {"A": ["B", "C"], "B": ["C"], "C": []}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
needs_dot = pytest.mark.skipif(
    shutil.which("dot") is None, reason="Graphviz не установлен"
)


def test_to_dot_has_all_edges():
    """в описании есть все связи графа"""
    text = to_dot("A", GRAPH)
    assert text.startswith("digraph dependencies {")
    assert text.endswith("}\n")
    for edge in ('"A" -> "B";', '"A" -> "C";', '"B" -> "C";'):
        assert edge in text


def test_to_dot_marks_root():
    """корневой пакет выделен цветом"""
    assert '"A" [style=filled' in to_dot("A", GRAPH)


def test_to_dot_single_package():
    """граф из одного пакета содержит только корень"""
    text = to_dot("A", {"A": []})
    assert "->" not in text
    assert '"A"' in text


def test_to_dot_keeps_cycle_edges():
    """связи цикла попадают в описание"""
    text = to_dot("A", {"A": ["B"], "B": ["A"]})
    assert '"A" -> "B";' in text and '"B" -> "A";' in text


def test_quote_escapes_special_characters():
    """кавычки и обратная косая черта в имени экранируются"""
    assert quote('a"b\\c') == '"a\\"b\\\\c"'


def test_dot_path_replaces_extension():
    """dot-файл лежит рядом с png"""
    assert dot_path("graph.png") == "graph.dot"


def test_write_dot_error(tmp_path):
    """ошибка записи превращается в RenderError"""
    with pytest.raises(RenderError, match="Не удалось сохранить"):
        write_dot("x", str(tmp_path / "no_dir" / "g.dot"))


def test_render_png_calls_dot_with_text():
    """dot запускается с нужными аргументами и получает текст"""
    calls = []

    def runner(command, input, capture_output):
        """запоминает вызов и сообщает об успехе"""
        calls.append((command, input))
        return subprocess.CompletedProcess(command, 0, b"", b"")

    render_png("digraph {}", "out.png", runner)
    assert calls == [(["dot", "-Tpng", "-o", "out.png"], b"digraph {}")]


def test_render_png_without_graphviz():
    """если dot не установлен, ошибка подсказывает, что делать"""

    def runner(command, input, capture_output):
        """программа не найдена"""
        raise FileNotFoundError(command[0])

    with pytest.raises(RenderError, match="Graphviz"):
        render_png("x", "out.png", runner)


def test_render_png_reports_dot_failure():
    """ошибка dot показывается пользователю"""

    def runner(command, input, capture_output):
        """dot завершился с ошибкой"""
        return subprocess.CompletedProcess(command, 1, b"", b"syntax error")

    with pytest.raises(RenderError, match="syntax error"):
        render_png("x", "out.png", runner)


@needs_dot
def test_real_png_is_created(tmp_path):
    """настоящий dot создаёт файл png и dot-файл"""
    image = str(tmp_path / "graph.png")
    path = save_image("A", GRAPH, image)
    assert path == str(tmp_path / "graph.dot")
    with open(image, "rb") as file:
        assert file.read(len(PNG_SIGNATURE)) == PNG_SIGNATURE
    with open(path, encoding="utf-8") as file:
        assert file.read() == to_dot("A", GRAPH)


@needs_dot
def test_real_png_with_cyrillic_and_quotes(tmp_path):
    """имена с кириллицей и кавычками не ломают dot"""
    graph = {'Пакет "1"': ["Библиотека"], "Библиотека": []}
    image = str(tmp_path / "ru.png")
    save_image('Пакет "1"', graph, image)
    with open(image, "rb") as file:
        assert file.read(len(PNG_SIGNATURE)) == PNG_SIGNATURE
