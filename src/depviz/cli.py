"""командная строка"""

import argparse
import sys
from dataclasses import asdict

from depviz.config import ConfigError, load_config

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


def print_config(config):
    """вывод параметров"""
    for key, value in asdict(config).items():
        print(f"{key}: {value}")


def main(argv=None):
    """запуск приложения"""
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    print_config(config)
    return EXIT_OK
