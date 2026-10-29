"""тесты обратных зависимостей"""

import pytest

from depviz.errors import PackageNotFoundError
from depviz.graph import build_graph
from depviz.reverse import make_source, reverse_index
from depviz.testrepo import parse_repository


def reverse_of(text, root, substring=""):
    """граф обратных зависимостей по тексту тестового репозитория"""
    source = make_source(parse_repository(text))
    return build_graph(root, source, substring)


def test_reverse_index():
    """индекс показывает, кто использует каждый пакет"""
    index = reverse_index({"A": ["B", "C"], "B": ["C"], "C": []})
    assert index == {"A": [], "B": ["A"], "C": ["A", "B"]}


def test_reverse_index_includes_undefined_packages():
    """пакет, упомянутый только как зависимость, тоже есть в индексе"""
    assert reverse_index({"A": ["B"]}) == {"A": [], "B": ["A"]}


def test_chain():
    """по цепочке обратные зависимости идут вверх"""
    graph = reverse_of("A: B\nB: C\nC:\n", "C")
    assert graph == {"C": ["B"], "B": ["A"], "A": []}


def test_diamond_has_each_user_once():
    """в ромбе верхний пакет встречается один раз"""
    graph = reverse_of("A: B C\nB: D\nC: D\nD:\n", "D")
    assert graph == {"D": ["B", "C"], "B": ["A"], "C": ["A"], "A": []}


def test_top_package_has_no_users():
    """от верхнего пакета никто не зависит"""
    assert reverse_of("A: B\nB:\n", "A") == {"A": []}


def test_cycle_terminates():
    """цикл не зацикливает обход"""
    graph = reverse_of("A: B\nB: C\nC: A\n", "A")
    assert graph == {"A": ["C"], "C": ["B"], "B": ["A"]}


def test_filter_cuts_users():
    """отфильтрованный пакет и всё за ним не учитываются"""
    graph = reverse_of("A: B C\nB: D\nC: D\nD:\n", "D", "B")
    assert graph == {"D": ["C"], "C": ["A"], "A": []}


def test_unknown_package():
    """неизвестный пакет даёт ошибку"""
    with pytest.raises(PackageNotFoundError, match="Z"):
        reverse_of("A:\n", "Z")


def test_dependency_only_package_can_be_root():
    """пакет, упомянутый только как зависимость, можно взять корнем"""
    assert reverse_of("A: B\n", "B") == {"B": ["A"], "A": []}
