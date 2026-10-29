"""обратные зависимости: какие пакеты зависят от данного"""

from depviz.errors import PackageNotFoundError


def reverse_index(packages):
    """словарь пакет-список пакетов, которые от него зависят"""
    index = {}
    for name, dependencies in packages.items():
        index.setdefault(name, [])
        for dependency in dependencies:
            users = index.setdefault(dependency, [])
            if name not in users:
                users.append(name)
    return index


def make_source(packages):
    """источник для обхода: у пакета берутся пакеты, зависящие от него"""
    index = reverse_index(packages)

    def source(name):
        """пакеты, которые зависят от данного"""
        if name not in index:
            raise PackageNotFoundError(f"Пакет не найден: {name}")
        return index[name]

    return source
