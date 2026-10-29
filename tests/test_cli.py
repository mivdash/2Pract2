"""тесты командной строки"""

from depviz import cli
from depviz.cli import EXIT_ERROR, EXIT_OK, main
from depviz.errors import PackageNotFoundError
from depviz.nuget import Dependency, PackageInfo


def fake_package(dependencies):
    """подмена получения пакета"""

    def get_package(name, repository):
        """возвращает готовый пакет"""
        return PackageInfo(name, "2.0.0", dependencies)

    return get_package


def test_prints_direct_dependencies(write_config, capsys, monkeypatch):
    """печатаются версия пакета и его прямые зависимости"""
    deps = [Dependency("A", "[1.0.0, )"), Dependency("B", "[2.1.0, 3.0.0)")]
    monkeypatch.setattr(cli, "get_package", fake_package(deps))
    code = main([write_config()])
    out = capsys.readouterr().out.splitlines()
    assert code == EXIT_OK
    assert out == [
        "Пакет: Newtonsoft.Json 2.0.0",
        "Прямые зависимости: 2",
        "  A [1.0.0, )",
        "  B [2.1.0, 3.0.0)",
    ]


def test_prints_message_without_dependencies(
    write_config, capsys, monkeypatch
):
    """у пакета без зависимостей выводится слово нет"""
    monkeypatch.setattr(cli, "get_package", fake_package([]))
    code = main([write_config()])
    out = capsys.readouterr().out.splitlines()
    assert code == EXIT_OK
    assert out[-1] == "Прямые зависимости: нет"


def test_repository_error_goes_to_stderr(write_config, capsys, monkeypatch):
    """ошибка репозитория выводится в stderr с кодом 1"""

    def failing(name, repository):
        """всегда сообщает, что пакет не найден"""
        raise PackageNotFoundError(f"Пакет не найден: {name}")

    monkeypatch.setattr(cli, "get_package", failing)
    code = main([write_config()])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert captured.err == "Ошибка: Пакет не найден: Newtonsoft.Json\n"


def test_config_error_goes_to_stderr(capsys):
    """ошибка конфига выводится в stderr с кодом 1"""
    code = main(["no_such_file.yaml"])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert captured.err.startswith("Ошибка:")


def test_test_mode_is_not_supported_yet(write_config, test_repo_file, capsys):
    """тестовый режим пока даёт понятную ошибку"""
    text = (
        "package_name: A\n"
        f"repository: {test_repo_file}\n"
        "test_mode: true\n"
        "output_image: graph.png\n"
        "ascii_tree: false\n"
        'filter_substring: ""\n'
    )
    code = main([write_config(text)])
    assert code == EXIT_ERROR
    assert "Тестовый режим" in capsys.readouterr().err
