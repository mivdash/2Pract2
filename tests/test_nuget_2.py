"""тесты получения зависимостей из nuget"""

import pytest

from depviz.nuget_2 import poluchit_paket
from depviz.oshibki_2 import OshibkaRepozitoriya, PaketNeNaiden

REPOZITORIY = "https://repo.test/v3/index.json"
REESTR = "https://repo.test/reg/"
KOREN = {
    "resources": [
        {"@id": "https://repo.test/search", "@type": "SearchQueryService"},
        {"@id": REESTR, "@type": "RegistrationsBaseUrl/3.6.0"},
    ]
}


def zapis(versiya, zavisimosti=(), gruppy=None):
    """описание версии пакета в том виде, как его отдаёт nuget"""
    if gruppy is None:
        gruppy = [{"dependencies": list(zavisimosti)}]
    return {
        "catalogEntry": {
            "id": "Demo.Pkg",
            "version": versiya,
            "dependencyGroups": gruppy,
        }
    }


def zavisimost(imya, diapazon="[1.0.0, )"):
    """зависимость в формате nuget"""
    return {"id": imya, "range": diapazon}


def podstavnoy_internet(zapisi, na_otdelnoy_stranice=False):
    """делает вид, что скачивает документы, на деле берёт их из словаря"""
    stranica_adres = REESTR + "demo.pkg/page0.json"
    dokumenty = {REPOZITORIY: KOREN}
    if na_otdelnoy_stranice:
        dokumenty[stranica_adres] = {"items": zapisi}
        stranica = {"@id": stranica_adres}
    else:
        stranica = {"@id": stranica_adres, "items": zapisi}
    dokumenty[REESTR + "demo.pkg/index.json"] = {"items": [stranica]}

    def skachat(adres):
        """отдаёт документ по адресу"""
        return dokumenty[adres]

    return skachat


def test_berutsya_zavisimosti_poslednei_versii():
    """из нескольких версий выбирается последняя"""
    internet = podstavnoy_internet(
        [zapis("1.0.0"), zapis("2.0.0", [zavisimost("B")])]
    )
    paket = poluchit_paket(REPOZITORIY, "Demo.Pkg", internet)
    assert paket.versiya == "2.0.0"
    assert paket.zavisimosti == [("B", "[1.0.0, )")]


def test_stabilnaya_versiya_vazhnee_predvaritelnoi():
    """версия вроде 3.0.0-beta пропускается, если есть стабильная"""
    internet = podstavnoy_internet([zapis("2.0.0"), zapis("3.0.0-beta")])
    assert poluchit_paket(REPOZITORIY, "Demo.Pkg", internet).versiya == "2.0.0"


def test_zavisimosti_raznykh_platform_obedinyayutsya():
    """зависимости из групп для разных платформ собираются без повторов"""
    gruppy = [
        {"dependencies": [zavisimost("B"), zavisimost("A")]},
        {"dependencies": [zavisimost("B"), zavisimost("C")]},
    ]
    internet = podstavnoy_internet([zapis("1.0.0", gruppy=gruppy)])
    paket = poluchit_paket(REPOZITORIY, "Demo.Pkg", internet)
    assert [imya for imya, _ in paket.zavisimosti] == ["A", "B", "C"]


def test_stranica_s_versiyami_skachivaetsya_otdelno():
    """если версии лежат на отдельной странице, она скачивается"""
    internet = podstavnoy_internet(
        [zapis("1.0.0", [zavisimost("B")])], na_otdelnoy_stranice=True
    )
    paket = poluchit_paket(REPOZITORIY, "Demo.Pkg", internet)
    assert paket.zavisimosti == [("B", "[1.0.0, )")]


def test_paket_bez_versiy():
    """если у пакета нет ни одной версии, выдаётся ошибка Пакет не найден"""
    internet = podstavnoy_internet([])
    with pytest.raises(PaketNeNaiden, match="нет версий"):
        poluchit_paket(REPOZITORIY, "Demo.Pkg", internet)


def test_net_resursa_reestra():
    """если в репозитории нет нужного ресурса, выдаётся ошибка"""
    with pytest.raises(OshibkaRepozitoriya, match="RegistrationsBaseUrl"):
        poluchit_paket(REPOZITORIY, "Demo.Pkg", lambda adres: {"resources": []})
