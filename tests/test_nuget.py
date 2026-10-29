"""тесты получения зависимостей nuget"""

import pytest

from depviz.errors import (
    HttpStatusError,
    PackageNotFoundError,
    RepositoryError,
)
from depviz.nuget import (
    Dependency,
    find_registration_base,
    get_package,
    parse_version,
    registration_url,
)

REPO = "https://repo.test/v3/index.json"
BASE = "https://repo.test/reg/"
INDEX = {
    "resources": [
        {"@id": "https://repo.test/search", "@type": "SearchQueryService"},
        {"@id": BASE, "@type": "RegistrationsBaseUrl/3.6.0"},
    ]
}


def make_entry(version, deps=None, listed=True, groups=None):
    """запись версии для подставного ответа"""
    if groups is None:
        groups = [{"targetFramework": "net8.0", "dependencies": deps or []}]
    return {
        "catalogEntry": {
            "id": "Demo.Pkg",
            "version": version,
            "listed": listed,
            "dependencyGroups": groups,
        }
    }


def make_fetch(documents):
    """подставная загрузка из словаря адрес-документ"""

    def fetch(url):
        """отдаёт документ или ошибку 404"""
        if url not in documents:
            raise HttpStatusError(404, url)
        return documents[url]

    return fetch


def make_repo(leaves, paged=False):
    """репозиторий с одним пакетом demo.pkg"""
    documents = {REPO: INDEX}
    page_url = BASE + "demo.pkg/page0.json"
    if paged:
        documents[page_url] = {"items": leaves}
        page = {"@id": page_url}
    else:
        page = {"@id": page_url, "items": leaves}
    documents[BASE + "demo.pkg/index.json"] = {"items": [page]}
    return make_fetch(documents)


def dep(name, version_range="[1.0.0, )"):
    """зависимость в формате nuget"""
    return {"id": name, "range": version_range}


def test_direct_dependencies_are_returned():
    """возвращаются прямые зависимости последней версии"""
    fetch = make_repo([make_entry("1.0.0"), make_entry("2.0.0", [dep("B")])])
    info = get_package("Demo.Pkg", REPO, fetch)
    assert info.version == "2.0.0"
    assert info.dependencies == [Dependency("B", "[1.0.0, )")]


def test_package_without_dependencies():
    """пакет без зависимостей даёт пустой список"""
    info = get_package("Demo.Pkg", REPO, make_repo([make_entry("1.0.0")]))
    assert info.dependencies == []


def test_page_without_inline_items_is_fetched():
    """страница без вложенных версий загружается отдельно"""
    fetch = make_repo([make_entry("1.5.0", [dep("C")])], paged=True)
    info = get_package("Demo.Pkg", REPO, fetch)
    assert [item.name for item in info.dependencies] == ["C"]


def test_latest_is_compared_by_numbers_not_text():
    """версия 1.10.0 новее 1.9.0"""
    leaves = [make_entry("1.9.0", [dep("Old")]), make_entry("1.10.0")]
    info = get_package("Demo.Pkg", REPO, make_repo(leaves))
    assert info.version == "1.10.0"


def test_prerelease_is_skipped_when_stable_exists():
    """предварительная версия не выбирается, если есть стабильная"""
    leaves = [make_entry("1.0.0"), make_entry("2.0.0-beta.1")]
    info = get_package("Demo.Pkg", REPO, make_repo(leaves))
    assert info.version == "1.0.0"


def test_only_prerelease_is_used_as_fallback():
    """если стабильных нет, берётся предварительная"""
    info = get_package(
        "Demo.Pkg", REPO, make_repo([make_entry("1.0.0-rc.1")])
    )
    assert info.version == "1.0.0-rc.1"


def test_unlisted_version_is_skipped():
    """снятая с публикации версия не выбирается"""
    leaves = [make_entry("1.0.0"), make_entry("2.0.0", listed=False)]
    info = get_package("Demo.Pkg", REPO, make_repo(leaves))
    assert info.version == "1.0.0"


def test_dependencies_are_merged_across_frameworks():
    """зависимости разных платформ объединяются без повторов"""
    groups = [
        {"targetFramework": "net6.0", "dependencies": [dep("B"), dep("A")]},
        {"targetFramework": "net8.0", "dependencies": [dep("B")]},
        {"targetFramework": "netstandard2.0"},
    ]
    leaves = [make_entry("1.0.0", groups=groups)]
    info = get_package("Demo.Pkg", REPO, make_repo(leaves))
    assert [item.name for item in info.dependencies] == ["A", "B"]


def test_package_name_is_lowercased_in_url():
    """в адресе имя пакета записывается строчными буквами"""
    assert registration_url(BASE, "Demo.PKG") == BASE + "demo.pkg/index.json"


def test_unknown_package():
    """неизвестный пакет даёт PackageNotFoundError"""
    with pytest.raises(PackageNotFoundError, match="Ghost"):
        get_package("Ghost", REPO, make_repo([make_entry("1.0.0")]))


def test_package_without_versions():
    """пакет без версий считается ненайденным"""
    with pytest.raises(PackageNotFoundError, match="нет версий"):
        get_package("Demo.Pkg", REPO, make_repo([]))


def test_repository_without_registration_resource():
    """в репозитории без registration возникает ошибка"""
    fetch = make_fetch({REPO: {"resources": []}})
    with pytest.raises(RepositoryError, match="RegistrationsBaseUrl"):
        get_package("Demo.Pkg", REPO, fetch)


def test_other_http_error_is_not_hidden():
    """ошибка сервера не превращается в пакет не найден"""

    def fetch(url):
        """сервер возвращает 500 для документа пакета"""
        if url == REPO:
            return INDEX
        raise HttpStatusError(500, url)

    with pytest.raises(HttpStatusError, match="500"):
        get_package("Demo.Pkg", REPO, fetch)


def test_registration_type_priority():
    """выбирается более новый тип ресурса registration"""
    index = {
        "resources": [
            {"@id": "old/", "@type": "RegistrationsBaseUrl"},
            {"@id": "new/", "@type": ["RegistrationsBaseUrl/3.6.0"]},
        ]
    }
    assert find_registration_base(index) == "new/"


@pytest.mark.parametrize(
    "older, newer",
    [("1.9.0", "1.10.0"), ("1.0", "1.0.1"), ("1.2.3.4", "1.2.3.5")],
)
def test_version_order(older, newer):
    """версии сравниваются по числам"""
    assert parse_version(older) < parse_version(newer)


def test_version_suffix_is_ignored():
    """суффикс предварительной версии не мешает разбору"""
    assert parse_version("1.2.3-beta+build") == (1, 2, 3, 0)
