"""общие фикстуры"""

import pytest

from depviz import cli

VALID_YAML = """\
package_name: Newtonsoft.Json
repository: https://api.nuget.org/v3/index.json
test_mode: false
output_image: graph.png
ascii_tree: true
filter_substring: ""
"""


@pytest.fixture
def write_config(tmp_path):
    """запись временного конфига"""
    def _write(text=VALID_YAML):
        """пишет конфиг и отдаёт путь"""
        path = tmp_path / "config.yaml"
        path.write_text(text, encoding="utf-8")
        return str(path)

    return _write


@pytest.fixture
def test_repo_file(tmp_path):
    """файл тестового репозитория"""
    path = tmp_path / "repo.txt"
    path.write_text("A: B C\nB: C\nC:\n", encoding="utf-8")
    return str(path)


@pytest.fixture(autouse=True)
def no_image_files(monkeypatch):
    """тесты cli не создают файлы и не запускают dot"""
    saved = []

    def fake_save(root, graph, image):
        """запоминает вызов вместо сохранения"""
        saved.append((root, graph, image))
        return image.replace(".png", ".dot")

    monkeypatch.setattr(cli, "save_image", fake_save)
    return saved
