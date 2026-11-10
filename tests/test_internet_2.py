"""тесты скачивания json"""

import gzip
import json

import pytest

from depviz.internet_2 import razobrat_otvet, skachat_json
from depviz.oshibki_2 import OshibkaRepozitoriya


def test_obychnyy_json_razbiraetsya():
    """несжатый ответ превращается в словарь"""
    assert razobrat_otvet(b'{"a": 1}') == {"a": 1}


def test_szhatyy_json_razbiraetsya():
    """ответ, сжатый gzip, распаковывается и разбирается"""
    dannye = gzip.compress(json.dumps({"a": 2}).encode("utf-8"))
    assert razobrat_otvet(dannye) == {"a": 2}


def test_nedostupnyy_adres_daet_oshibku_repozitoriya():
    """если адрес не открывается, выдаётся понятная ошибка"""
    with pytest.raises(OshibkaRepozitoriya, match="Не удалось получить"):
        skachat_json("http://127.0.0.1:1/index.json")
