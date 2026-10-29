"""тесты командной строки"""

from depviz import cli
from depviz.cli import EXIT_ERROR, EXIT_OK, main
from depviz.errors import PackageNotFoundError, RenderError

REPO_TEXT = "A: B C\nB: C\nC:\n"
SAVED_LINES = 2


def make_config(
    tmp_path, write_config, repo_text=REPO_TEXT, extra="", root="A",
    ascii=False,
):
    """конфиг тестового режима с файлом репозитория"""
    repo = tmp_path / "repo.txt"
    repo.write_text(repo_text, encoding="utf-8")
    return write_config(
        f"package_name: {root}\n"
        f"repository: {repo}\n"
        "test_mode: true\n"
        "output_image: graph.png\n"
        f"ascii_tree: {str(ascii).lower()}\n"
        f'filter_substring: "{extra}"\n'
    )


def fake_nuget_source(graph):
    """подмена источника nuget готовым словарём"""

    def make_source(repository):
        """источник по словарю"""

        def source(name):
            """зависимости пакета из словаря"""
            if name not in graph:
                raise PackageNotFoundError(f"Пакет не найден: {name}")
            return graph[name]

        return source

    return make_source


def test_prints_graph_in_test_mode(tmp_path, write_config, capsys):
    """в тестовом режиме печатается граф из файла"""
    path = make_config(tmp_path, write_config)
    code = main([path])
    out = capsys.readouterr().out.splitlines()[:-SAVED_LINES]
    assert code == EXIT_OK
    assert out == [
        "Граф зависимостей пакета A (пакетов: 3)",
        "A -> B, C",
        "B -> C",
        "C -> (нет зависимостей)",
    ]


def test_filter_is_applied(tmp_path, write_config, capsys):
    """подстрока фильтра исключает пакеты"""
    path = make_config(tmp_path, write_config, extra="B")
    main([path])
    out = capsys.readouterr().out.splitlines()[:-SAVED_LINES]
    assert out[1:] == ["A -> C", "C -> (нет зависимостей)"]


def test_real_mode_uses_nuget_source(write_config, capsys, monkeypatch):
    """без тестового режима зависимости берутся из nuget"""
    graph = {"Newtonsoft.Json": ["Dep.One"], "Dep.One": []}
    monkeypatch.setattr(cli.nuget, "make_source", fake_nuget_source(graph))
    code = main([write_config()])
    out = capsys.readouterr().out.splitlines()[:-SAVED_LINES]
    assert code == EXIT_OK
    assert out == ["Newtonsoft.Json", "`-- Dep.One"]


def test_unknown_package_goes_to_stderr(write_config, capsys, monkeypatch):
    """неизвестный пакет выводится в stderr с кодом 1"""
    monkeypatch.setattr(cli.nuget, "make_source", fake_nuget_source({}))
    code = main([write_config()])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert captured.err == "Ошибка: Пакет не найден: Newtonsoft.Json\n"


def test_broken_test_repository(tmp_path, write_config, capsys):
    """ошибка в файле репозитория выводится в stderr"""
    path = make_config(tmp_path, write_config, repo_text="A B\n")
    code = main([path])
    assert code == EXIT_ERROR
    assert "Строка 1" in capsys.readouterr().err


def test_config_error_goes_to_stderr(capsys):
    """ошибка конфига выводится в stderr с кодом 1"""
    code = main(["no_such_file.yaml"])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert captured.out == ""
    assert captured.err.startswith("Ошибка:")


def test_reverse_in_test_mode(tmp_path, write_config, capsys):
    """флаг --reverse печатает, кто зависит от пакета"""
    text = "A: B\nB: C\nC:\n"
    path = make_config(tmp_path, write_config, repo_text=text, root="C")
    code = main(["--reverse", path])
    out = capsys.readouterr().out.splitlines()
    assert code == EXIT_OK
    assert out[0] == "Обратные зависимости пакета C (пакетов: 3)"
    assert out[-1] == "Зависят от C: B, A"


def test_reverse_is_not_supported_for_nuget(write_config, capsys):
    """для настоящего репозитория обратные зависимости дают понятную ошибку"""
    code = main(["--reverse", write_config()])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert "только в тестовом режиме" in captured.err


def test_ascii_tree_is_printed_when_enabled(tmp_path, write_config, capsys):
    """при ascii_tree: true печатается дерево вместо списка"""
    path = make_config(tmp_path, write_config, ascii=True)
    code = main([path])
    out = capsys.readouterr().out.splitlines()[:-SAVED_LINES]
    assert code == EXIT_OK
    assert out == [
        "A",
        "|-- B",
        "|   `-- C",
        "`-- C",
    ]


def test_image_paths_are_reported(
    tmp_path, write_config, capsys, no_image_files
):
    """после построения сообщается, где сохранены dot и png"""
    path = make_config(tmp_path, write_config)
    main([path])
    out = capsys.readouterr().out.splitlines()
    assert out[-2:] == [
        "Описание Graphviz сохранено: graph.dot",
        "Изображение сохранено: graph.png",
    ]
    root, graph, image = no_image_files[0]
    assert (root, image) == ("A", "graph.png")
    assert graph == {"A": ["B", "C"], "B": ["C"], "C": []}


def test_reverse_mode_does_not_save_image(
    tmp_path, write_config, no_image_files
):
    """режим обратных зависимостей изображение не создаёт"""
    path = make_config(tmp_path, write_config)
    main(["--reverse", path])
    assert no_image_files == []


def test_render_error_goes_to_stderr(
    tmp_path, write_config, capsys, monkeypatch
):
    """ошибка рисования выводится в stderr с кодом 1"""

    def failing(root, graph, image):
        """graphviz не установлен"""
        raise RenderError("Не найдена программа dot")

    monkeypatch.setattr(cli, "save_image", failing)
    code = main([make_config(tmp_path, write_config)])
    assert code == EXIT_ERROR
    assert "Не найдена программа dot" in capsys.readouterr().err
