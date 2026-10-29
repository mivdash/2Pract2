"""ошибки работы с репозиторием"""


class RepositoryError(Exception):
    """репозиторий недоступен или вернул неверный ответ"""


class HttpStatusError(RepositoryError):
    """сервер ответил кодом ошибки"""

    def __init__(self, status, url):
        """запоминает код ответа и адрес"""
        super().__init__(f"HTTP {status}: {url}")
        self.status = status


class PackageNotFoundError(RepositoryError):
    """пакет не найден в репозитории"""
