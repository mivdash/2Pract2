"""загрузка json по http"""

import gzip
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from depviz.errors import HttpStatusError, RepositoryError

TIMEOUT_SECONDS = 20
GZIP_MAGIC = b"\x1f\x8b"
HEADERS = {"Accept-Encoding": "gzip", "User-Agent": "depviz/0.2"}


def decode_body(data):
    """распаковывает gzip при необходимости и разбирает json"""
    if data[:2] == GZIP_MAGIC:
        data = gzip.decompress(data)
    return json.loads(data.decode("utf-8"))


def fetch_json(url):
    """скачивает адрес и возвращает json"""
    request = Request(url, headers=HEADERS)
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return decode_body(response.read())
    except HTTPError as err:
        raise HttpStatusError(err.code, url) from err
    except (OSError, ValueError) as err:
        raise RepositoryError(f"Не удалось получить {url}: {err}") from err
