"""тесты ascii-дерева"""

from depviz.asciitree import format_tree
from depviz.graph import build_graph
from depviz.testrepo import make_source, parse_repository


def tree_of(text, root="A", substring=""):
    """строки дерева по тексту тестового репозитория"""
    source = make_source(parse_repository(text))
    return format_tree(root, build_graph(root, source, substring))


def test_single_package():
    """пакет без зависимостей это одна строка"""
    assert tree_of("A:\n") == ["A"]


def test_chain():
    """цепочка рисуется уступами"""
    assert tree_of("A: B\nB: C\nC:\n") == ["A", "`-- B", "    `-- C"]


def test_siblings_use_branch_and_last_branch():
    """несколько зависимостей: ветки и последняя ветка"""
    assert tree_of("A: B C\nB:\nC:\n") == ["A", "|-- B", "`-- C"]


def test_pipe_continues_under_non_last_branch():
    """вертикальная черта идёт под не последней веткой"""
    lines = tree_of("A: B C\nB: D\nC:\nD:\n")
    assert lines == ["A", "|-- B", "|   `-- D", "`-- C"]


def test_repeated_package_is_not_expanded_again():
    """повторный пакет помечается и не раскрывается второй раз"""
    lines = tree_of("A: B C\nB: D\nC: D\nD: E\nE:\n")
    assert lines == [
        "A",
        "|-- B",
        "|   `-- D",
        "|       `-- E",
        "`-- C",
        "    `-- D (см. выше)",
    ]


def test_repeated_leaf_has_no_mark():
    """повторный пакет без зависимостей не помечается"""
    lines = tree_of("A: B C\nB: D\nC: D\nD:\n")
    assert lines[-1] == "    `-- D"


def test_cycle_is_marked():
    """цикл помечается и обход на нём останавливается"""
    lines = tree_of("A: B\nB: C\nC: A\n")
    assert lines == ["A", "`-- B", "    `-- C", "        `-- A (цикл)"]


def test_self_dependency_is_marked_as_cycle():
    """зависимость от самого себя помечается как цикл"""
    assert tree_of("A: A\n") == ["A", "`-- A (цикл)"]


def test_filtered_package_is_absent():
    """отфильтрованный пакет в дереве отсутствует"""
    assert tree_of("A: B C\nB:\nC:\n", substring="B") == ["A", "`-- C"]
