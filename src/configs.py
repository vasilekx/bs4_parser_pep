# configs.py
import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (LOG_DIR, LOG_FILE, PRETTY_ARGUMENT_NAME,
                       FILE_ARGUMENT_NAME)

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY_ARGUMENT_NAME, FILE_ARGUMENT_NAME),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(
            RotatingFileHandler(LOG_FILE, maxBytes=10 ** 6, backupCount=5),
            logging.StreamHandler()
        )
    )
