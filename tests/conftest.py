"""общие заготовки для тестов"""

import pytest

PRAVILNYE_NASTROYKI = """\
package_name: Newtonsoft.Json
repository: https://api.nuget.org/v3/index.json
test_mode: false
output_image: graph.png
ascii_tree: true
filter_substring: ""
"""


@pytest.fixture
def zapisat_nastroyki(tmp_path):
    """готовит временный файл настроек для теста"""

    def zapisat(tekst=PRAVILNYE_NASTROYKI):
        """создаёт файл с нужным текстом настроек"""
        put = tmp_path / "nastroyki.yaml"
        put.write_text(tekst, encoding="utf-8")
        return str(put)

    return zapisat


@pytest.fixture
def fayl_testovogo_repozitoriya(tmp_path):
    """готовит временный файл тестового репозитория"""
    put = tmp_path / "repo.txt"
    put.write_text("A: B C\nB: C\nC:\n", encoding="utf-8")
    return str(put)
