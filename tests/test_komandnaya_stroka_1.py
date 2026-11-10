"""тесты командной строки"""

from depviz.komandnaya_stroka_1 import KOD_OSHIBKA, KOD_USPEH, main


def test_pechataet_vse_nastroyki(zapisat_nastroyki, capsys):
    """с правильным файлом печатает шесть настроек и возвращает 0"""
    kod = main([zapisat_nastroyki()])
    vyvod = capsys.readouterr().out.splitlines()
    assert kod == KOD_USPEH
    assert vyvod == [
        "package_name: Newtonsoft.Json",
        "repository: https://api.nuget.org/v3/index.json",
        "test_mode: False",
        "output_image: graph.png",
        "ascii_tree: True",
        "filter_substring: ",
    ]


def test_oshibka_idet_v_stderr(capsys):
    """без файла настроек пишет ошибку в stderr и возвращает 1"""
    kod = main(["net_takogo_fayla.yaml"])
    perehvacheno = capsys.readouterr()
    assert kod == KOD_OSHIBKA
    assert perehvacheno.out == ""
    assert perehvacheno.err.startswith("Ошибка:")
