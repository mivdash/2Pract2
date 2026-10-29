"""получение прямых зависимостей пакета из nuget v3"""

from typing import NamedTuple

from depviz.errors import (
    HttpStatusError,
    PackageNotFoundError,
    RepositoryError,
)
from depviz.http import fetch_json

NOT_FOUND = 404
VERSION_PARTS = 4
REGISTRATION_TYPES = (
    "RegistrationsBaseUrl/3.6.0",
    "RegistrationsBaseUrl/3.4.0",
    "RegistrationsBaseUrl/3.0.0-rc",
    "RegistrationsBaseUrl/3.0.0-beta",
    "RegistrationsBaseUrl",
)


class Dependency(NamedTuple):
    """зависимость: имя и диапазон версий"""

    name: str
    version_range: str


class PackageInfo(NamedTuple):
    """пакет с версией и прямыми зависимостями"""

    name: str
    version: str
    dependencies: list


def resource_types(resource):
    """типы ресурса списком"""
    kind = resource.get("@type", [])
    return [kind] if isinstance(kind, str) else list(kind)


def find_registration_base(index):
    """ищет адрес registration в корневом документе репозитория"""
    resources = index.get("resources", [])
    for wanted in REGISTRATION_TYPES:
        for resource in resources:
            if wanted in resource_types(resource):
                return resource["@id"]
    raise RepositoryError("В репозитории нет ресурса RegistrationsBaseUrl")


def registration_url(base, name):
    """адрес документа registration для пакета"""
    return f"{base.rstrip('/')}/{name.lower()}/index.json"


def load_leaves(registration, fetch):
    """собирает записи версий со всех страниц registration"""
    leaves = []
    for page in registration.get("items", []):
        items = page.get("items")
        if items is None:
            items = fetch(page["@id"]).get("items", [])
        leaves.extend(items)
    return leaves


def parse_version(text):
    """версия в виде кортежа чисел для сравнения"""
    core = text.replace("+", "-").split("-", 1)[0]
    parts = [int(part) for part in core.split(".") if part.isdigit()]
    parts += [0] * (VERSION_PARTS - len(parts))
    return tuple(parts[:VERSION_PARTS])


def pick_latest(leaves, name):
    """выбирает последнюю стабильную опубликованную версию"""
    entries = [
        leaf["catalogEntry"] for leaf in leaves if leaf.get("catalogEntry")
    ]
    listed = [entry for entry in entries if entry.get("listed", True)]
    listed = listed or entries
    stable = [entry for entry in listed if "-" not in entry["version"]]
    candidates = stable or listed
    if not candidates:
        raise PackageNotFoundError(f"У пакета {name} нет версий")
    return max(candidates, key=lambda entry: parse_version(entry["version"]))


def direct_dependencies(entry):
    """прямые зависимости версии, объединённые по всем платформам"""
    found = {}
    for group in entry.get("dependencyGroups", []):
        for item in group.get("dependencies", []):
            found.setdefault(item["id"], item.get("range", ""))
    pairs = sorted(found.items(), key=lambda pair: pair[0].lower())
    return [Dependency(name, version_range) for name, version_range in pairs]


def fetch_registration(base, name, fetch):
    """скачивает документ registration, пакет не найден при 404"""
    try:
        return fetch(registration_url(base, name))
    except HttpStatusError as err:
        if err.status == NOT_FOUND:
            raise PackageNotFoundError(f"Пакет не найден: {name}") from err
        raise


def cache_index(fetch, repository):
    """запоминает корневой документ репозитория, остальное не хранит"""
    memo = {}

    def cached(url):
        """корневой документ загружается один раз"""
        if url != repository:
            return fetch(url)
        if url not in memo:
            memo[url] = fetch(url)
        return memo[url]

    return cached


def make_source(repository, fetch=fetch_json):
    """источник зависимостей из nuget для построения графа"""
    cached = cache_index(fetch, repository)

    def source(name):
        """имена прямых зависимостей пакета"""
        package = get_package(name, repository, cached)
        return [item.name for item in package.dependencies]

    return source


def get_package(name, repository, fetch=fetch_json):
    """возвращает последнюю версию пакета и его прямые зависимости"""
    index = fetch(repository)
    base = find_registration_base(index)
    registration = fetch_registration(base, name, fetch)
    leaves = load_leaves(registration, fetch)
    entry = pick_latest(leaves, name)
    return PackageInfo(
        entry.get("id", name), entry["version"], direct_dependencies(entry)
    )
