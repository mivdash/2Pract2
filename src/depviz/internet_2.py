"""скачивание json из интернета"""

import gzip
import json
from urllib.request import Request, urlopen

from depviz.oshibki_2 import OshibkaRepozitoriya

TAYMAUT_SEKUND = 20
GZIP_NACHALO = b"\x1f\x8b"
ZAGOLOVKI = {"Accept-Encoding": "gzip", "User-Agent": "depviz/0.2"}


def razobrat_otvet(dannye):
    """превращает ответ сервера в json, nuget может прислать его сжатым"""
    if dannye.startswith(GZIP_NACHALO):
        dannye = gzip.decompress(dannye)
    return json.loads(dannye.decode("utf-8"))


def skachat_json(adres):
    """скачивает json по адресу, сбои сети превращает в понятные ошибки"""
    zapros = Request(adres, headers=ZAGOLOVKI)
    try:
        with urlopen(zapros, timeout=TAYMAUT_SEKUND) as otvet:
            return razobrat_otvet(otvet.read())
    except (OSError, ValueError) as oshibka:
        raise OshibkaRepozitoriya(
            f"Не удалось получить {adres}: {oshibka}"
        ) from oshibka
