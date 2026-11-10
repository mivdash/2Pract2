"""чтение и проверка файла настроек nastroyki.yaml"""

from dataclasses import dataclass, fields
from pathlib import Path
from urllib.parse import urlparse

import yaml

RAZRESHENNYE_SXEMY = ("http", "https")


class ConfigError(Exception):
    """ошибка в настройках, её текст увидит пользователь"""


@dataclass(frozen=True)
class Nastroyki:
    """все настройки программы в одном месте"""

    package_name: str
    repository: str
    test_mode: bool
    output_image: str
    ascii_tree: bool
    filter_substring: str


def prochitat_yaml(put):
    """превращает файл настроек в словарь"""
    fayl = Path(put)
    if not fayl.exists():
        raise ConfigError(f"Файл конфигурации не найден: {put}")
    if not fayl.is_file():
        raise ConfigError(f"Это не файл: {put}")
    try:
        slovar = yaml.safe_load(fayl.read_text(encoding="utf-8"))
    except yaml.YAMLError as oshibka:
        raise ConfigError(f"Некорректный YAML: {oshibka}") from oshibka
    except UnicodeDecodeError as oshibka:
        raise ConfigError("Файл должен быть в кодировке UTF-8") from oshibka
    if not isinstance(slovar, dict):
        raise ConfigError("Конфигурация должна быть набором ключ: значение")
    return slovar


def proverit_nalichie_klyuchey(slovar):
    """убеждается, что пользователь не забыл ни одной настройки"""
    nuzhnye = {pole.name for pole in fields(Nastroyki)}
    nedostayet = sorted(nuzhnye - slovar.keys())
    if nedostayet:
        raise ConfigError(
            f"Не хватает параметров: {', '.join(nedostayet)}"
        )


def vzyat_stroku(slovar, klyuch, mozhno_pustuyu=False):
    """достаёт текстовую настройку и проверяет её"""
    znachenie = slovar[klyuch]
    if not isinstance(znachenie, str):
        raise ConfigError(f"Параметр '{klyuch}' должен быть строкой")
    znachenie = znachenie.strip()
    if not znachenie and not mozhno_pustuyu:
        raise ConfigError(f"Параметр '{klyuch}' не должен быть пустым")
    return znachenie


def vzyat_da_net(slovar, klyuch):
    """достаёт настройку true/false и проверяет её"""
    znachenie = slovar[klyuch]
    if not isinstance(znachenie, bool):
        raise ConfigError(
            f"Параметр '{klyuch}' должен быть true или false"
        )
    return znachenie


def check_repository(repozitoriy, testovyy_rezhim):
    """проверяет, что repository указан правильно"""
    if testovyy_rezhim:
        if not Path(repozitoriy).is_file():
            raise ConfigError(
                f"Файл тестового репозитория не найден: {repozitoriy}"
            )
        return
    adres = urlparse(repozitoriy)
    if adres.scheme not in RAZRESHENNYE_SXEMY or not adres.netloc:
        raise ConfigError(
            "Параметр 'repository' должен быть URL вида http(s)://хост/..."
        )


def zagruzit_nastroyki(put):
    """собирает проверенные настройки из файла"""
    slovar = prochitat_yaml(put)
    proverit_nalichie_klyuchey(slovar)
    nastroyki = Nastroyki(
        package_name=vzyat_stroku(slovar, "package_name"),
        repository=vzyat_stroku(slovar, "repository"),
        test_mode=vzyat_da_net(slovar, "test_mode"),
        output_image=vzyat_stroku(slovar, "output_image"),
        ascii_tree=vzyat_da_net(slovar, "ascii_tree"),
        filter_substring=vzyat_stroku(
            slovar, "filter_substring", mozhno_pustuyu=True
        ),
    )
    check_repository(nastroyki.repository, nastroyki.test_mode)
    return nastroyki
