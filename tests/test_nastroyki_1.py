"""тесты чтения и проверки настроек"""

import pytest

from conftest import PRAVILNYE_NASTROYKI
from depviz.nastroyki_1 import Nastroyki, ConfigError, zagruzit_nastroyki


def test_pravilnye_nastroyki_zagruzhayutsya(zapisat_nastroyki):
    """правильный файл превращается в объект с шестью настройками"""
    nastroyki = zagruzit_nastroyki(zapisat_nastroyki())
    assert nastroyki == Nastroyki(
        package_name="Newtonsoft.Json",
        repository="https://api.nuget.org/v3/index.json",
        test_mode=False,
        output_image="graph.png",
        ascii_tree=True,
        filter_substring="",
    )


def test_testovyy_rezhim_prinimaet_fayl(
    zapisat_nastroyki, fayl_testovogo_repozitoriya
):
    """в тестовом режиме вместо адреса принимается существующий файл"""
    tekst = PRAVILNYE_NASTROYKI.replace(
        "https://api.nuget.org/v3/index.json", fayl_testovogo_repozitoriya
    ).replace("test_mode: false", "test_mode: true")
    nastroyki = zagruzit_nastroyki(zapisat_nastroyki(tekst))
    assert nastroyki.test_mode is True
    assert nastroyki.repository == fayl_testovogo_repozitoriya


def test_net_fayla_nastroek():
    """если файла нет, выдаётся ошибка со словом не найден"""
    with pytest.raises(ConfigError, match="не найден"):
        zagruzit_nastroyki("net_takogo_fayla.yaml")


def test_slomannyy_yaml(zapisat_nastroyki):
    """если yaml написан с ошибкой, выдаётся ошибка Некорректный YAML"""
    with pytest.raises(ConfigError, match="Некорректный YAML"):
        zagruzit_nastroyki(zapisat_nastroyki("package_name: [unclosed"))


def test_ne_xvataet_parametra(zapisat_nastroyki):
    """если нет одной настройки, ошибка называет её по имени"""
    tekst = PRAVILNYE_NASTROYKI.replace("package_name: Newtonsoft.Json\n", "")
    with pytest.raises(ConfigError, match="package_name"):
        zagruzit_nastroyki(zapisat_nastroyki(tekst))


def test_nepravilnyy_tip_znacheniya(zapisat_nastroyki):
    """число вместо true или false даёт ошибку про true или false"""
    tekst = PRAVILNYE_NASTROYKI.replace("test_mode: false", "test_mode: 1")
    with pytest.raises(ConfigError, match="true или false"):
        zagruzit_nastroyki(zapisat_nastroyki(tekst))


def test_adres_ne_pokhozh_na_url(zapisat_nastroyki):
    """адрес без http или https даёт ошибку про URL"""
    tekst = PRAVILNYE_NASTROYKI.replace(
        "https://api.nuget.org/v3/index.json", "not-a-url"
    )
    with pytest.raises(ConfigError, match="URL"):
        zagruzit_nastroyki(zapisat_nastroyki(tekst))


def test_testovyy_rezhim_bez_fayla(zapisat_nastroyki):
    """в тестовом режиме несуществующий файл даёт ошибку про репозиторий"""
    tekst = PRAVILNYE_NASTROYKI.replace("test_mode: false", "test_mode: true")
    with pytest.raises(ConfigError, match="тестового репозитория"):
        zagruzit_nastroyki(zapisat_nastroyki(tekst))
