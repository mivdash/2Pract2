"""получение прямых зависимостей пакета из репозитория nuget"""

from typing import NamedTuple

from depviz.internet_2 import skachat_json
from depviz.oshibki_2 import OshibkaRepozitoriya, PaketNeNaiden

TIP_REESTRA = "RegistrationsBaseUrl/3.6.0"


class Paket(NamedTuple):
    """пакет: имя, версия и список прямых зависимостей"""

    imya: str
    versiya: str
    zavisimosti: list


def nayti_adres_reestra(korenvoy_dokument):
    """ищет в корневом документе адрес, где лежат данные о версиях пакетов"""
    for resurs in korenvoy_dokument.get("resources", []):
        if resurs.get("@type") == TIP_REESTRA:
            return resurs["@id"]
    raise OshibkaRepozitoriya("В репозитории нет ресурса RegistrationsBaseUrl")


def adres_paketa(adres_reestra, imya_paketa):
    """собирает адрес документа пакета, в nuget имя пишется строчными"""
    return f"{adres_reestra.rstrip('/')}/{imya_paketa.lower()}/index.json"


def sobrat_versii(dokument_paketa, skachat):
    """собирает описания версий, у больших пакетов они на отдельных страницах"""
    versii = []
    for stranica in dokument_paketa.get("items", []):
        zapisi = stranica.get("items")
        if zapisi is None:
            zapisi = skachat(stranica["@id"]).get("items", [])
        versii.extend(zapis["catalogEntry"] for zapis in zapisi)
    return versii


def vybrat_poslednyuyu(versii, imya_paketa):
    """берёт последнюю стабильную версию, если таких нет, то последнюю любую"""
    if not versii:
        raise PaketNeNaiden(f"У пакета {imya_paketa} нет версий")
    stabilnye = [versiya for versiya in versii if "-" not in versiya["version"]]
    return (stabilnye or versii)[-1]


def pryamye_zavisimosti(versiya):
    """собирает зависимости версии, группы для разных платформ объединяет"""
    naydeno = {}
    for gruppa in versiya.get("dependencyGroups", []):
        for zavisimost in gruppa.get("dependencies", []):
            naydeno.setdefault(zavisimost["id"], zavisimost.get("range", ""))
    return sorted(naydeno.items(), key=lambda para: para[0].lower())


def poluchit_paket(repozitoriy, imya_paketa, skachat=skachat_json):
    """находит пакет в репозитории и возвращает его версию и зависимости"""
    adres_reestra = nayti_adres_reestra(skachat(repozitoriy))
    dokument = skachat(adres_paketa(adres_reestra, imya_paketa))
    versiya = vybrat_poslednyuyu(sobrat_versii(dokument, skachat), imya_paketa)
    return Paket(
        versiya.get("id", imya_paketa),
        versiya["version"],
        pryamye_zavisimosti(versiya),
    )
