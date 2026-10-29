"""тесты загрузки json"""

import gzip
import json

import pytest

from depviz.errors import HttpStatusError, RepositoryError
from depviz.http import decode_body, fetch_json

PAYLOAD = {"items": [1, 2], "name": "тест"}


def test_plain_json_is_decoded():
    """обычный json разбирается"""
    data = json.dumps(PAYLOAD).encode("utf-8")
    assert decode_body(data) == PAYLOAD


def test_gzip_json_is_decoded():
    """json, сжатый gzip, распаковывается"""
    data = gzip.compress(json.dumps(PAYLOAD).encode("utf-8"))
    assert decode_body(data) == PAYLOAD


def test_broken_json_raises():
    """битый json вызывает ValueError"""
    with pytest.raises(ValueError):
        decode_body(b"{not json")


def test_unreachable_host_gives_repository_error():
    """недоступный адрес превращается в RepositoryError"""
    with pytest.raises(RepositoryError):
        fetch_json("http://127.0.0.1:1/index.json")


def test_http_status_error_keeps_code():
    """ошибка статуса хранит код ответа"""
    err = HttpStatusError(404, "http://x/y")
    assert err.status == 404
    assert "404" in str(err)
