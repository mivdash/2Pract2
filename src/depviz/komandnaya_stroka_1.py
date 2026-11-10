"""командная строка: разбор аргументов, запуск и вывод результата"""

import argparse
import sys
from dataclasses import asdict

from depviz.nastroyki_1 import ConfigError, zagruzit_nastroyki

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


def napechatat_nastroyki(nastroyki):
    """показывает пользователю, какие настройки прочитаны"""
    for imya, znachenie in asdict(nastroyki).items():
        print(f"{imya}: {znachenie}")


def main(argv=None):
    argumenty = sozdat_razborshchik().parse_args(argv)
    try:
        nastroyki = zagruzit_nastroyki(argumenty.nastroyki)
    except ConfigError as oshibka:
        print(f"Ошибка: {oshibka}", file=sys.stderr)
        return KOD_OSHIBKA
    napechatat_nastroyki(nastroyki)
    return KOD_USPEH
