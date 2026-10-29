"""командная строка"""

import argparse
import sys

from depviz import nuget, testrepo
from depviz.config import ConfigError, load_config
from depviz.errors import GraphError, RepositoryError
from depviz.graph import build_graph

DEFAULT_CONFIG = "config.yaml"
EXIT_OK = 0
EXIT_ERROR = 1
NO_DEPENDENCIES = "(нет зависимостей)"


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


def make_source(config):
    """источник зависимостей: файл в тестовом режиме, иначе nuget"""
    if config.test_mode:
        packages = testrepo.load_repository(config.repository)
        return testrepo.make_source(packages)
    return nuget.make_source(config.repository)


def print_graph(root, graph):
    """вывод графа списком: пакет и его зависимости"""
    print(f"Граф зависимостей пакета {root} (пакетов: {len(graph)})")
    for name, dependencies in graph.items():
        targets = ", ".join(dependencies) or NO_DEPENDENCIES
        print(f"{name} -> {targets}")


def main(argv=None):
    """запуск приложения"""
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        source = make_source(config)
        graph = build_graph(
            config.package_name, source, config.filter_substring
        )
    except (ConfigError, RepositoryError, GraphError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    print_graph(config.package_name, graph)
    return EXIT_OK
