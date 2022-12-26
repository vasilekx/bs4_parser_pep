# Проект парсинга pep

## Описание
Парсер собирает данные обо всех PEP-документах,сравниваетихстатуси записываетв файл,собираетинформациюо статусеверсии,скачиваетархивысдокументацией,атакжесобираетссылкинановостив Python.

### Функции парсера:

* Сброр ссылок на статьи о нововведениях в Python;
* Сброр информации о версиях Python;
* Скачивание архива с актуальной документацией;
* Сброр статусов документов PEP и подсчёт статусов документов;
* Вывод информации в терминал (в обычном и табличном виде) и сохранение результатов работы парсинга в формате csv;
* Логирование работы парсинга;
* Обработка ошибок в работе парсинга.

## Применяемые технологии

[![Python](https://img.shields.io/badge/Python-3.7-blue?style=flat-square&logo=Python&logoColor=3776AB&labelColor=d0d0d0)](https://www.python.org/)
[![Beautiful Soup 4](https://img.shields.io/badge/BeautifulSoup-4.9.3-blue?style=flat-square&labelColor=d0d0d0)](https://beautiful-soup-4.readthedocs.io)

### Порядок действия для запуска парсера

Клонировать репозиторий и перейти в папку в проектом:

```bash
git clone git@github.com:vasilekx/bs4_parser_pep.git
```

```bash
cd bs4_parser_pep
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

* Если у вас Linux/MacOS

    ```bash
    source venv/bin/activate
    ```

* Если у вас windows

    ```bash
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

## Работа с парсером

### Режимы работы
Сброр ссылок на статьи о нововведениях в Python:
```bash
python main.py whats-new
```
Сброр информации о версиях Python:
```bash
python main.py latest-versions
```
Скачивание архива с актуальной документацией:
```bash
python main.py download
```
Сброр статусов документов PEP и подсчёт статусов:
```bash
python main.py pep
```

### Аргументы командной строки
Полный список аргументов:
```bash
python main.py -h
```
```bash
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```

## Директории для файлов с результатами парсинга
* _downloads_ - для архива с документацией Python;
* _results_ - для результатов парсинга;
* _logs_ - для логов.

## Примеры работы парсинга:
Сброр информации о версиях Python с опцией вывода результата в табличном виде:
```bash
python main.py latest-versions -o pretty
```
```bash
"15.09.2022 21:35:50 - [INFO] - Парсер запущен!"
"15.09.2022 21:35:50 - [INFO] - Аргументы командной строки: Namespace(clear_cache=False, mode='latest-versions', output='pretty')"
+--------------------------------------+--------------+----------------+
| Ссылка на документацию               | Версия       | Статус         |
+--------------------------------------+--------------+----------------+
| https://docs.python.org/3.12/        | 3.12         | in development |
| https://docs.python.org/3.11/        | 3.11         | pre-release    |
| https://docs.python.org/3.10/        | 3.10         | stable         |
| https://docs.python.org/3.9/         | 3.9          | security-fixes |
| https://docs.python.org/3.8/         | 3.8          | security-fixes |
| https://docs.python.org/3.7/         | 3.7          | security-fixes |
| https://docs.python.org/3.6/         | 3.6          | EOL            |
| https://docs.python.org/3.5/         | 3.5          | EOL            |
| https://docs.python.org/2.7/         | 2.7          | EOL            |
| https://www.python.org/doc/versions/ | All versions |                |
+--------------------------------------+--------------+----------------+
"15.09.2022 21:35:50 - [INFO] - Парсер завершил работу."
```

Скачивание архива с актуальной документацией:
```bash
python main.py download
```
```bash
"15.09.2022 21:38:48 - [INFO] - Парсер запущен!"
"15.09.2022 21:38:48 - [INFO] - Аргументы командной строки: Namespace(clear_cache=False, mode='download', output=None)"
"15.09.2022 21:38:48 - [INFO] - Архив python-3.10.7-docs-pdf-a4.zip был загружен и сохранён: /Users/your_user/Documents/bs4_parser_pep/src/downloads/python-3.10.7-docs-pdf-a4.zip"
"15.09.2022 21:38:48 - [INFO] - Парсер завершил работу."
```

Сброр статусов документов PEP и подсчёт статусов документов с опцией вывода результата в csv-файл:
```bash
python main.py pep -o file
```
```bash
"15.09.2022 21:44:11 - [INFO] - Парсер запущен!"
"15.09.2022 21:44:11 - [INFO] - Аргументы командной строки: Namespace(clear_cache=False, mode='pep', output='file')"
"15.09.2022 21:44:14 - [INFO] - Несовпадающие статусы: https://peps.python.org/pep-0401 Статус в карточке: April Fool! Ожидаемые статусы: ['Rejected'] "
"15.09.2022 21:44:20 - [INFO] - Файл pep_2022-09-15_21-44-20.csv с результатами был сохранён: /Users/your_user/Documents/bs4_parser_pep/src/results/pep_2022-09-15_21-44-20.csv"
"15.09.2022 21:44:20 - [INFO] - Парсер завершил работу."
```
Содержимое файла **pep_2022-09-15_21-44-20.csv**:

|Статус    | Количество |
|----------|------------|
|Active    | 36         |
|Superseded| 16         |
|Withdrawn | 54         |
|Final     | 263        |
|Rejected  | 118        |
|Deferred  | 37         |
|Accepted  | 40         |
|Draft     | 30         |
|Total     | 594        |


## Автор
Владислав Василенко
