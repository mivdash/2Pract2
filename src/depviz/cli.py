"""командная строка"""

import argparse
import sys

from depviz import nuget, reverse, testrepo
from depviz.asciitree import format_tree
from depviz.config import ConfigError, load_config
from depviz.dot import save_image
from depviz.errors import GraphError, RenderError, RepositoryError
from depviz.graph import build_graph

DEFAULT_CONFIG = "config.yaml"
EXIT_OK = 0
EXIT_ERROR = 1
NO_DEPENDENCIES = "(нет зависимостей)"
NO_DEPENDENTS = "(никто не зависит)"


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
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="показать обратные зависимости: кто зависит от пакета",
    )
    return parser


def make_source(config):
    """источник зависимостей: файл в тестовом режиме, иначе nuget"""
    if config.test_mode:
        packages = testrepo.load_repository(config.repository)
        return testrepo.make_source(packages)
    return nuget.make_source(config.repository)


def make_reverse_source(config):
    """источник обратных зависимостей, только для тестового репозитория"""
    if not config.test_mode:
        raise ConfigError(
            "Обратные зависимости доступны только в тестовом режиме: "
            "у NuGet нет способа узнать всех, кто зависит от пакета"
        )
    packages = testrepo.load_repository(config.repository)
    return reverse.make_source(packages)


def print_graph(root, graph):
    """вывод графа списком: пакет и его зависимости"""
    print(f"Граф зависимостей пакета {root} (пакетов: {len(graph)})")
    for name, dependencies in graph.items():
        targets = ", ".join(dependencies) or NO_DEPENDENCIES
        print(f"{name} -> {targets}")


def print_reverse(root, graph):
    """вывод обратных зависимостей: кто зависит от пакета"""
    print(f"Обратные зависимости пакета {root} (пакетов: {len(graph)})")
    for name, users in graph.items():
        print(f"{name} <- {', '.join(users) or NO_DEPENDENTS}")
    dependents = [name for name in graph if name != root]
    print(f"Зависят от {root}: {', '.join(dependents) or 'никто'}")


def show_graph(config, graph):
    """дерево из ascii при включённом параметре, иначе список"""
    if config.ascii_tree:
        print("\n".join(format_tree(config.package_name, graph)))
    else:
        print_graph(config.package_name, graph)


def run_forward(config):
    """строит граф зависимостей, показывает и сохраняет изображение"""
    graph = build_graph(
        config.package_name, make_source(config), config.filter_substring
    )
    show_graph(config, graph)
    dot_file = save_image(config.package_name, graph, config.output_image)
    print(f"Описание Graphviz сохранено: {dot_file}")
    print(f"Изображение сохранено: {config.output_image}")


def run_reverse(config):
    """строит и печатает обратные зависимости"""
    graph = build_graph(
        config.package_name,
        make_reverse_source(config),
        config.filter_substring,
    )
    print_reverse(config.package_name, graph)


def run(args, config):
    """выбирает режим работы"""
    if args.reverse:
        run_reverse(config)
    else:
        run_forward(config)


def main(argv=None):
    """запуск приложения"""
    args = build_parser().parse_args(argv)
    try:
        run(args, load_config(args.config))
    except (ConfigError, RepositoryError, GraphError, RenderError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK
