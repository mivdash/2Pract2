"""построение графа зависимостей обходом в ширину без рекурсии"""

from collections import deque

from depviz.errors import GraphError, PackageNotFoundError


def is_filtered(name, substring):
    """имя содержит подстроку фильтра, регистр не важен"""
    return bool(substring) and substring.lower() in name.lower()


def read_dependencies(name, source, is_root):
    """зависимости пакета, неизвестный не корневой пакет считается листом"""
    try:
        return source(name)
    except PackageNotFoundError:
        if is_root:
            raise
        return []


def clean_dependencies(names, substring, canonical):
    """убирает повторы и отфильтрованные пакеты"""
    result = []
    for name in names:
        name = canonical(name)
        if name not in result and not is_filtered(name, substring):
            result.append(name)
    return result


def build_graph(root, source, substring=""):
    """строит граф от корня, возвращает словарь пакет-список зависимостей"""
    if is_filtered(root, substring):
        raise GraphError(f"Пакет {root} содержит подстроку фильтра")
    names = {}

    def canonical(name):
        """одно написание для имён, отличающихся регистром"""
        return names.setdefault(name.lower(), name)

    root = canonical(root)
    graph = {}
    queue = deque([root])
    seen = {root}
    while queue:
        name = queue.popleft()
        found = read_dependencies(name, source, name == root)
        graph[name] = clean_dependencies(found, substring, canonical)
        for dependency in graph[name]:
            if dependency not in seen:
                seen.add(dependency)
                queue.append(dependency)
    return graph
