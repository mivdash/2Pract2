"""командная строка: разбор аргументов, запуск и вывод результата"""

import argparse
import sys

from depviz.nastroyki_1 import ConfigError, zagruzit_nastroyki
from depviz.nuget_2 import poluchit_paket
from depviz.oshibki_2 import OshibkaRepozitoriya

FAYL_NASTROEK_PO_UMOLCHANIYU = "nastroyki.yaml"
KOD_USPEH = 0
KOD_OSHIBKA = 1


def sozdat_razborshchik():
    """учит программу понимать, что пользователь написал в команде"""
    razborshchik = argparse.ArgumentParser(
        prog="depviz",
        description="Визуализация графа зависимостей NuGet-пакетов.",
    )
    razborshchik.add_argument(
        "nastroyki",
        nargs="?",
        default=FAYL_NASTROEK_PO_UMOLCHANIYU,
        help=f"путь к YAML-файлу (по умолчанию {FAYL_NASTROEK_PO_UMOLCHANIYU})",
    )
    return razborshchik


def zagruzit_paket(nastroyki):
    """берёт пакет из настоящего репозитория nuget"""
    if nastroyki.test_mode:
        raise ConfigError("Тестовый режим появится на этапе 3")
    return poluchit_paket(nastroyki.repository, nastroyki.package_name)


def napechatat_zavisimosti(paket):
    """показывает пользователю прямые зависимости пакета"""
    print(f"Пакет: {paket.imya} {paket.versiya}")
    if not paket.zavisimosti:
        print("Прямые зависимости: нет")
        return
    print(f"Прямые зависимости: {len(paket.zavisimosti)}")
    for imya, diapazon in paket.zavisimosti:
        print(f"  {imya} {diapazon}")


def main(argv=None):
    argumenty = sozdat_razborshchik().parse_args(argv)
    try:
        nastroyki = zagruzit_nastroyki(argumenty.nastroyki)
        paket = zagruzit_paket(nastroyki)
    except (ConfigError, OshibkaRepozitoriya) as oshibka:
        print(f"Ошибка: {oshibka}", file=sys.stderr)
        return KOD_OSHIBKA
    napechatat_zavisimosti(paket)
    return KOD_USPEH
