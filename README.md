# depviz

Программа показывает, от каких пакетов зависит NuGet-пакет (.NET).
Зависимости берутся напрямую из репозитория, без `dotnet` и `nuget`.
Практическая работа №2, вариант 7.

**Этап 1:** программа читает файл настроек, проверяет его и печатает
настройки. При ошибке пишет `Ошибка: ...` и завершается с кодом 1.
Ловит: нет файла, вместо файла папка, сломанный YAML, нет настройки,
неверный тип значения, пустое значение, адрес не похож на URL,
нет файла тестового репозитория.

## Настройки

Файл `nastroyki.yaml`, нужны все шесть настроек:

```yaml
package_name: Newtonsoft.Json                    # какой пакет смотрим
repository: https://api.nuget.org/v3/index.json  # адрес репозитория или файл
test_mode: false                                 # true: данные из файла
output_image: graph.png                          # имя картинки с графом
ascii_tree: true                                 # true: вывод деревом из символов
filter_substring: ""                             # пакеты с этим словом пропускаем
```

## Функции

- `prochitat_yaml`: превращает файл настроек в словарь
- `proverit_nalichie_klyuchey`: проверяет, что не забыта ни одна настройка
- `vzyat_stroku`: достаёт текстовую настройку и проверяет её
- `vzyat_da_net`: достаёт настройку true/false и проверяет её
- `check_repository`: проверяет, что `repository` указан правильно
- `zagruzit_nastroyki`: собирает проверенные настройки из файла
- `sozdat_razborshchik`: учит программу понимать команду пользователя
- `napechatat_nastroyki`: показывает, какие настройки прочитаны
- `main`: запускает программу и сообщает, чем всё закончилось

## Запуск и тесты

```
py -m pip install -r requirements.txt
run.bat
run.bat moi_nastroyki.yaml
py -m pytest -v
```

## Примеры

```
> run.bat
package_name: Newtonsoft.Json
repository: https://api.nuget.org/v3/index.json
test_mode: False
output_image: graph.png
ascii_tree: True
filter_substring:

> run.bat net_takogo_fayla.yaml
Ошибка: Файл конфигурации не найден: net_takogo_fayla.yaml
```
