"""тесты построения графа"""

import pytest

from depviz.errors import GraphError, PackageNotFoundError, RepositoryError
from depviz.graph import build_graph, is_filtered
from depviz.testrepo import make_source, parse_repository


def graph_of(text, root="A", substring=""):
    """граф по тексту тестового репозитория"""
    source = make_source(parse_repository(text))
    return build_graph(root, source, substring)


def test_chain():
    """цепочка зависимостей"""
    graph = graph_of("A: B\nB: C\nC:\n")
    assert graph == {"A": ["B"], "B": ["C"], "C": []}


def test_diamond_visits_shared_package_once():
    """общий пакет в ромбе попадает в граф один раз"""
    graph = graph_of("A: B C\nB: D\nC: D\nD:\n")
    assert list(graph) == ["A", "B", "C", "D"]
    assert graph["B"] == ["D"] and graph["C"] == ["D"]


def test_bfs_visits_level_by_level():
    """пакеты обходятся по уровням, а не вглубь"""
    graph = graph_of("A: B C\nB: D\nC: E\nD:\nE:\n")
    assert list(graph) == ["A", "B", "C", "D", "E"]


def test_cycle_terminates():
    """цикл не приводит к бесконечному обходу"""
    graph = graph_of("A: B\nB: C\nC: A\n")
    assert graph == {"A": ["B"], "B": ["C"], "C": ["A"]}


def test_self_dependency_terminates():
    """зависимость пакета от самого себя не зацикливает обход"""
    graph = graph_of("A: A B\nB:\n")
    assert graph == {"A": ["A", "B"], "B": []}


def test_isolated_root():
    """пакет без зависимостей даёт граф из одного узла"""
    assert graph_of("A:\n") == {"A": []}


def test_unreachable_packages_are_not_included():
    """пакеты, недостижимые из корня, в граф не попадают"""
    graph = graph_of("A: B\nB:\nX: Y\nY:\n")
    assert list(graph) == ["A", "B"]


def test_duplicate_dependencies_are_merged():
    """повтор зависимости в списке убирается"""
    assert graph_of("A: B B\nB:\n")["A"] == ["B"]


def test_filter_removes_package_and_its_subtree():
    """отфильтрованный пакет и всё за ним не учитываются"""
    graph = graph_of("A: B C\nB: D\nC:\nD:\n", substring="B")
    assert graph == {"A": ["C"], "C": []}


def test_filter_keeps_package_reachable_by_other_path():
    """пакет за фильтром остаётся, если до него есть другой путь"""
    graph = graph_of("A: B C\nB: D\nC: D\nD:\n", substring="B")
    assert graph == {"A": ["C"], "C": ["D"], "D": []}


def test_filter_ignores_case():
    """регистр в подстроке фильтра не важен"""
    graph = graph_of("A: B C\nB:\nC:\n", substring="b")
    assert "B" not in graph


def test_filtered_root_is_an_error():
    """корневой пакет с подстрокой фильтра нельзя обработать"""
    with pytest.raises(GraphError, match="подстроку"):
        graph_of("A: B\nB:\n", substring="A")


def test_unknown_root():
    """неизвестный корневой пакет даёт ошибку"""
    with pytest.raises(PackageNotFoundError, match="Z"):
        graph_of("A:\n", root="Z")


def test_unknown_dependency_is_a_leaf():
    """неизвестная зависимость считается пакетом без зависимостей"""
    assert graph_of("A: B\n") == {"A": ["B"], "B": []}


def test_names_differing_in_case_are_one_package():
    """имена, отличающиеся регистром, считаются одним пакетом"""
    deps = {"Root": ["Lib.One", "lib.one"], "Lib.One": []}

    def source(name):
        """словарь без учёта регистра"""
        key = name if name in deps else "Lib.One"
        return deps[key]

    assert build_graph("Root", source) == {"Root": ["Lib.One"], "Lib.One": []}


def test_other_repository_errors_are_not_hidden():
    """сетевая ошибка при обходе не скрывается"""

    def source(name):
        """второй пакет недоступен"""
        if name == "A":
            return ["B"]
        raise RepositoryError("сеть недоступна")

    with pytest.raises(RepositoryError, match="сеть"):
        build_graph("A", source)


def test_very_deep_chain_has_no_recursion_limit():
    """цепочка из 5000 пакетов проходит без рекурсии"""
    size = 5000

    def source(name):
        """пакет n зависит от n+1"""
        number = int(name)
        return [str(number + 1)] if number < size else []

    graph = build_graph("1", source)
    assert len(graph) == size


@pytest.mark.parametrize(
    "name, substring, expected",
    [("Newtonsoft.Json", "json", True), ("A", "", False), ("A", "B", False)],
)
def test_is_filtered(name, substring, expected):
    """проверка совпадения имени с подстрокой"""
    assert is_filtered(name, substring) is expected
