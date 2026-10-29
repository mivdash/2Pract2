"""загрузка и проверка конфига"""

from dataclasses import dataclass, fields
from pathlib import Path
from urllib.parse import urlparse

import yaml

ALLOWED_SCHEMES = ("http", "https")
IMAGE_EXTENSION = ".png"


class ConfigError(Exception):
    """ошибка конфига"""


@dataclass(frozen=True)
class Config:
    """параметры пользователя"""

    package_name: str
    repository: str
    test_mode: bool
    output_image: str
    ascii_tree: bool
    filter_substring: str


def read_yaml(path):
    """чтение yaml в словарь"""
    file = Path(path)
    if not file.exists():
        raise ConfigError(f"Файл конфигурации не найден: {path}")
    if not file.is_file():
        raise ConfigError(f"Это не файл: {path}")
    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        raise ConfigError(f"Некорректный YAML: {err}") from err
    except UnicodeDecodeError as err:
        raise ConfigError("Файл должен быть в кодировке UTF-8") from err
    if not isinstance(data, dict):
        raise ConfigError("Конфигурация должна быть набором ключ: значение")
    return data


def check_keys(data):
    """проверка набора ключей"""
    expected = {field.name for field in fields(Config)}
    missing = sorted(expected - data.keys())
    if missing:
        raise ConfigError(f"Не хватает параметров: {', '.join(missing)}")


def require_str(data, key, allow_empty=False):
    """строковый параметр"""
    value = data[key]
    if not isinstance(value, str):
        raise ConfigError(f"Параметр '{key}' должен быть строкой")
    value = value.strip()
    if not value and not allow_empty:
        raise ConfigError(f"Параметр '{key}' не должен быть пустым")
    return value


def require_bool(data, key):
    """логический параметр"""
    value = data[key]
    if not isinstance(value, bool):
        raise ConfigError(f"Параметр '{key}' должен быть true или false")
    return value


def check_repository(repository, test_mode):
    """проверка url или файла"""
    if test_mode:
        if not Path(repository).is_file():
            raise ConfigError(
                f"Файл тестового репозитория не найден: {repository}"
            )
        return
    url = urlparse(repository)
    if url.scheme not in ALLOWED_SCHEMES or not url.netloc:
        raise ConfigError(
            "Параметр 'repository' должен быть URL вида http(s)://хост/..."
        )


def check_output_image(name):
    """проверка имени картинки"""
    if not name.lower().endswith(IMAGE_EXTENSION):
        raise ConfigError(
            f"Имя файла изображения должно оканчиваться на {IMAGE_EXTENSION}"
        )


def load_config(path):
    """загрузка конфига из файла"""
    data = read_yaml(path)
    check_keys(data)
    config = Config(
        package_name=require_str(data, "package_name"),
        repository=require_str(data, "repository"),
        test_mode=require_bool(data, "test_mode"),
        output_image=require_str(data, "output_image"),
        ascii_tree=require_bool(data, "ascii_tree"),
        filter_substring=require_str(
            data, "filter_substring", allow_empty=True
        ),
    )
    check_repository(config.repository, config.test_mode)
    check_output_image(config.output_image)
    return config
