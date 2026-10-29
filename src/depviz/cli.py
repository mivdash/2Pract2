"""командная строка"""

import argparse
import sys

from depviz.config import ConfigError, load_config
from depviz.errors import RepositoryError
from depviz.nuget import get_package

DEFAULT_CONFIG = "config.yaml"
EXIT_OK = 0
EXIT_ERROR = 1


def build_parser():
    """разбор аргументов"""
    parser = argparse.ArgumentParser(
        prog="depviz",
        description="Визуализация графа зависимостей NuGet-пакетов.",
    )
    parser.add_argument(
        "config",
        nargs="?",
        default=DEFAULT_CONFIG,
        help=f"путь к YAML-конфигу (по умолчанию {DEFAULT_CONFIG})",
    )
    return parser


def check_supported(config):
    """тестовый режим появится на следующем этапе"""
    if config.test_mode:
        raise ConfigError("Тестовый режим пока не поддерживается")


def print_package(info):
    """вывод пакета и его прямых зависимостей"""
    print(f"Пакет: {info.name} {info.version}")
    if not info.dependencies:
        print("Прямые зависимости: нет")
        return
    print(f"Прямые зависимости: {len(info.dependencies)}")
    for dependency in info.dependencies:
        print(f"  {dependency.name} {dependency.version_range}".rstrip())


def main(argv=None):
    """запуск приложения"""
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        check_supported(config)
        info = get_package(config.package_name, config.repository)
    except (ConfigError, RepositoryError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    print_package(info)
    return EXIT_OK
