"""тесты командной строки"""

from depviz import komandnaya_stroka_1
from depviz.komandnaya_stroka_1 import KOD_OSHIBKA, KOD_USPEH, main
from depviz.nuget_2 import Paket
from depviz.oshibki_2 import OshibkaRepozitoriya


def podstavit_nuget(monkeypatch, otvet):
    """заменяет настоящий запрос в nuget готовым ответом или ошибкой"""

    def poluchit_paket(repozitoriy, imya_paketa):
        """возвращает заготовленный пакет или выдаёт заготовленную ошибку"""
        if isinstance(otvet, Exception):
            raise otvet
        return otvet

    monkeypatch.setattr(
        komandnaya_stroka_1, "poluchit_paket", poluchit_paket
    )


def test_pechataet_pryamye_zavisimosti(zapisat_nastroyki, capsys, monkeypatch):
    """печатает пакет с версией и список его прямых зависимостей"""
    paket = Paket("Demo.Pkg", "2.0.0", [("Dep.One", "[1.0.0, )")])
    podstavit_nuget(monkeypatch, paket)
    kod = main([zapisat_nastroyki()])
    assert kod == KOD_USPEH
    assert capsys.readouterr().out.splitlines() == [
        "Пакет: Demo.Pkg 2.0.0",
        "Прямые зависимости: 1",
        "  Dep.One [1.0.0, )",
    ]


def test_oshibka_repozitoriya_idet_v_stderr(
    zapisat_nastroyki, capsys, monkeypatch
):
    """если репозиторий недоступен, ошибка идёт в stderr, код 1"""
    podstavit_nuget(monkeypatch, OshibkaRepozitoriya("сервер недоступен"))
    kod = main([zapisat_nastroyki()])
    perehvacheno = capsys.readouterr()
    assert kod == KOD_OSHIBKA
    assert perehvacheno.out == ""
    assert perehvacheno.err == "Ошибка: сервер недоступен\n"


def test_oshibka_nastroek_idet_v_stderr(capsys):
    """без файла настроек пишет ошибку в stderr и возвращает 1"""
    kod = main(["net_takogo_fayla.yaml"])
    assert kod == KOD_OSHIBKA
    assert capsys.readouterr().err.startswith("Ошибка:")


def test_testovyy_rezhim_poka_ne_podderzhivaetsya(
    zapisat_nastroyki, fayl_testovogo_repozitoriya, capsys
):
    """тестовый режим появится на этапе 3, пока он даёт ошибку"""
    tekst = (
        "package_name: A\n"
        f"repository: {fayl_testovogo_repozitoriya}\n"
        "test_mode: true\n"
        "output_image: graph.png\n"
        "ascii_tree: true\n"
        'filter_substring: ""\n'
    )
    kod = main([zapisat_nastroyki(tekst)])
    assert kod == KOD_OSHIBKA
    assert "этапе 3" in capsys.readouterr().err
