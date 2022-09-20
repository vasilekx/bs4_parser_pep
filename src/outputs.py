# outputs.py
import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, PRETTY_ARGUMENT_NAME,
                       RESULTS_DIR_NAME, FILE_ARGUMENT_NAME)


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """
    Проблема с тестами:

    Проходит тесты:

    results_dir = BASE_DIR / 'results'
    results_dir = BASE_DIR / RESULTS_DIR_NAME


    а это:

    from constants import RESULTS_DIR
    results_dir = RESULTS_DIR

    почему-то не проходит тесты,
    хотя на практике все работает...
    """
    results_dir = BASE_DIR / RESULTS_DIR_NAME
    results_dir.mkdir(exist_ok=True)
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_name = f'{cli_args.mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(f'Файл {file_name} с результатами был сохранён: {file_path}')


CASES_OUTPUT = {
    PRETTY_ARGUMENT_NAME: pretty_output,
    FILE_ARGUMENT_NAME: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    CASES_OUTPUT.get(cli_args.output)(results, cli_args)
