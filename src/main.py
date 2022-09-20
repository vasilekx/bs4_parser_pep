# main.py
import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, MAIN_DOC_URL, PEPS_URL, EXPECTED_STATUS,
                       WHATS_NEW_URL, DOWNLOADS_URL)
from outputs import control_output
from utils import find_tag, make_soup

STATUS_PEP_NOT_FOUND = (
    'Несовпадающие статусы: '
    '{pep_link} '
    'Статус в карточке: {card_status} '
    'Ожидаемые статусы: {statuses} '
)
PROGRAM_MALFUNCTION = (
    'Сбой в работе программы: {error}'
)


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(
        make_soup(session, WHATS_NEW_URL).select_one(
            '#what-s-new-in-python div.toctree-wrapper'
        ).select('li.toctree-l1')
    ):
        version_link = urljoin(WHATS_NEW_URL, find_tag(section, 'a')['href'])
        section_soup = make_soup(session, version_link)
        results.append(
            (version_link,
             find_tag(section_soup, 'h1').text,
             find_tag(section_soup, 'dl').text.replace('\n', ' '))
        )
    return results


def latest_versions(session):
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for ul in make_soup(session, MAIN_DOC_URL).select(
        'div.sphinxsidebarwrapper ul'
    ):
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise KeyError('Ничего не нашлось')

    for a_tag in tqdm(a_tags):
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status,))
    return results


def download(session):
    pattern_file = '-docs-pdf-a4.zip'
    archive_url = urljoin(
        DOWNLOADS_URL,
        make_soup(session, DOWNLOADS_URL).select_one(
            f'table.docutils a[href$="{pattern_file}"]'
        )['href']
    )
    filename = archive_url.split('/')[-1]

    # Тесты проходит
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    # Тесты не проходит
    # from constants import DOWNLOADS_DIR

    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив {filename} был загружен и сохранён: {archive_path}')


def pep(session):
    pattern_status = r'^Status.*'
    count_statuses = defaultdict(int)
    logs = []
    for tr_tag in tqdm(
        make_soup(session, PEPS_URL).select('#numerical-index tbody tr')
    ):
        statuses = EXPECTED_STATUS[find_tag(tr_tag, 'td').text[1:]]
        card_status = ''
        pep_link = urljoin(
            PEPS_URL,
            tr_tag.select_one('td a.pep.reference.internal')['href']
        )
        try:
            pep_soup = make_soup(session, pep_link)
        except ConnectionError as error:
            logs.append(error)
            continue
        dt_tags = pep_soup.select_one('dl.rfc2822.field-list.simple').select(
            'dt'
        )
        for dt_tag in dt_tags:
            text_match = re.search(pattern_status, dt_tag.text)
            if text_match:
                card_status = dt_tag.find_next_sibling('dd').text
                break
            else:
                continue
        if card_status not in statuses:
            logs.append(
                STATUS_PEP_NOT_FOUND.format(
                    pep_link=pep_link,
                    card_status=card_status,
                    statuses=statuses
                )
            )
        else:
            count_statuses[card_status] += 1
    for log in logs:
        logging.info(log)
    return [
        ('Статус', 'Количество'),
        *count_statuses.items(),
        ('Total', sum(count_statuses.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info('Парсер запущен!')
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as error:
        logging.exception(
            PROGRAM_MALFUNCTION.format(error=error),
            stack_info=True
        )
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
