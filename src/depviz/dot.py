"""текст на языке graphviz и сохранение png"""

import subprocess
from pathlib import Path

from depviz.errors import RenderError

ROOT_STYLE = "style=filled, fillcolor=lightblue"


def quote(name):
    """имя узла в кавычках с экранированием"""
    escaped = name.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def to_dot(root, graph):
    """описание графа на языке dot"""
    lines = [
        "digraph dependencies {",
        "    rankdir=LR;",
        f"    {quote(root)} [{ROOT_STYLE}];",
    ]
    for name, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"    {quote(name)} -> {quote(dependency)};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def dot_path(image):
    """путь к dot-файлу рядом с изображением"""
    return str(Path(image).with_suffix(".dot"))


def write_dot(text, path):
    """сохраняет описание графа в файл"""
    try:
        Path(path).write_text(text, encoding="utf-8")
    except OSError as err:
        raise RenderError(f"Не удалось сохранить {path}: {err}") from err


def render_png(text, image, runner=subprocess.run):
    """рисует png программой dot из graphviz"""
    try:
        result = runner(
            ["dot", "-Tpng", "-o", image],
            input=text.encode("utf-8"),
            capture_output=True,
        )
    except FileNotFoundError as err:
        raise RenderError(
            "Не найдена программа dot из Graphviz: установите Graphviz "
            "и добавьте её в PATH"
        ) from err
    except OSError as err:
        raise RenderError(f"Не удалось запустить dot: {err}") from err
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise RenderError(f"dot завершился с ошибкой: {message}")


def save_image(root, graph, image):
    """сохраняет dot-файл и png, возвращает путь к dot-файлу"""
    text = to_dot(root, graph)
    path = dot_path(image)
    write_dot(text, path)
    render_png(text, image)
    return path
