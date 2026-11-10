"""ошибки при работе с репозиторием пакетов"""


class OshibkaRepozitoriya(Exception):
    """репозиторий недоступен или ответил не так, как ждали"""


class PaketNeNaiden(OshibkaRepozitoriya):
    """такого пакета нет в репозитории"""
