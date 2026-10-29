"""тесты конфига"""

import pytest

from conftest import VALID_YAML
from depviz.config import Config, ConfigError, load_config


def test_valid_config_is_loaded(write_config):
    """корректный конфиг"""
    config = load_config(write_config())
    assert config == Config(
        package_name="Newtonsoft.Json",
        repository="https://api.nuget.org/v3/index.json",
        test_mode=False,
        output_image="graph.png",
        ascii_tree=True,
        filter_substring="",
    )


def test_test_mode_accepts_existing_file(write_config, test_repo_file):
    """тестовый режим с файлом"""
    text = VALID_YAML.replace(
        "https://api.nuget.org/v3/index.json", test_repo_file
    ).replace("test_mode: false", "test_mode: true")
    config = load_config(write_config(text))
    assert config.test_mode is True
    assert config.repository == test_repo_file


def test_filter_substring_can_be_filled(write_config):
    """непустой фильтр"""
    text = VALID_YAML.replace('filter_substring: ""', "filter_substring: Test")
    assert load_config(write_config(text)).filter_substring == "Test"


def test_missing_file():
    """нет файла"""
    with pytest.raises(ConfigError, match="не найден"):
        load_config("no_such_file.yaml")


def test_path_is_directory(tmp_path):
    """вместо файла папка"""
    with pytest.raises(ConfigError, match="не файл"):
        load_config(str(tmp_path))


def test_broken_yaml(write_config):
    """битый yaml"""
    with pytest.raises(ConfigError, match="Некорректный YAML"):
        load_config(write_config("package_name: [unclosed"))


def test_empty_file(write_config):
    """пустой файл"""
    with pytest.raises(ConfigError, match="ключ: значение"):
        load_config(write_config(""))


def test_not_a_mapping(write_config):
    """не словарь"""
    with pytest.raises(ConfigError, match="ключ: значение"):
        load_config(write_config("- a\n- b\n"))


@pytest.mark.parametrize(
    "key",
    [
        "package_name",
        "repository",
        "test_mode",
        "output_image",
        "ascii_tree",
        "filter_substring",
    ],
)
def test_missing_key(write_config, key):
    """пропущен параметр"""
    lines = [
        line for line in VALID_YAML.splitlines()
        if not line.startswith(key + ":")
    ]
    with pytest.raises(ConfigError, match=key):
        load_config(write_config("\n".join(lines)))


@pytest.mark.parametrize(
    "old, new, message",
    [
        ("package_name: Newtonsoft.Json", "package_name: 42", "строкой"),
        ("package_name: Newtonsoft.Json", 'package_name: ""', "пустым"),
        ("repository: https://api.nuget.org/v3/index.json",
         "repository: not-a-url", "URL"),
        ("repository: https://api.nuget.org/v3/index.json",
         "repository: ftp://host/x", "URL"),
        ("repository: https://api.nuget.org/v3/index.json",
         'repository: ""', "пустым"),
        ("test_mode: false", "test_mode: yes please", "true или false"),
        ("test_mode: false", "test_mode: 1", "true или false"),
        ("output_image: graph.png", "output_image: graph.jpg", ".png"),
        ("ascii_tree: true", "ascii_tree: maybe", "true или false"),
        ('filter_substring: ""', "filter_substring: 5", "строкой"),
    ],
)
def test_invalid_values(write_config, old, new, message):
    """неверные значения"""
    with pytest.raises(ConfigError, match=message):
        load_config(write_config(VALID_YAML.replace(old, new)))


def test_test_mode_with_missing_file(write_config):
    """тестовый режим без файла"""
    text = VALID_YAML.replace("test_mode: false", "test_mode: true")
    with pytest.raises(ConfigError, match="тестового репозитория"):
        load_config(write_config(text))
