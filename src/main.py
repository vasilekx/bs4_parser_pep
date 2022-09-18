# main.py
import logging
import re
from urllib.parse import urljoin
from collections import defaultdict

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, MAIN_DOC_URL, PEPS_URL, EXPECTED_STATUS,
                       WHATS_NEW_URL, DOWNLOADS_URL)
from outputs import control_output
from utils import get_response, find_tag, make_soup


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    soup = make_soup(session, WHATS_NEW_URL)
    sections_by_python = soup.select_one(
        '#what-s-new-in-python div.toctree-wrapper'
    ).select('li.toctree-l1')

    for section in tqdm(sections_by_python):
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
    soup = make_soup(session, MAIN_DOC_URL)
    for ul in soup.select('div.sphinxsidebarwrapper ul'):
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
    soup = make_soup(session, DOWNLOADS_URL)
    archive_url = urljoin(
        DOWNLOADS_URL,
        soup.select_one(f'table.docutils a[href$="{pattern_file}"]')['href']
    )
    filename = archive_url.split('/')[-1]

    # Тесты проходит
    DOWNLOADS_DIR = BASE_DIR / 'downloads'
    # Тесты не проходит
    # from constants import DOWNLOADS_DIR

    downloads_dir = DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив {filename} был загружен и сохранён: {archive_path}')


def pep(session):
    pattern_number = r'^\d+$'
    pattern_status = r'^Status.*'
    count_statuses = defaultdict(int)
    soup = make_soup(session, PEPS_URL)
    logs = []

    # попробовать переделать
    for tr_tag in tqdm(soup.select('#numerical-index tbody tr')):
        statuses = EXPECTED_STATUS[find_tag(tr_tag, 'td').text[1:]]
        card_status = ''
        href = find_tag(
            tr_tag,
            'a',
            attrs={'class': 'pep reference internal'},
            string=re.compile(pattern_number),
        )['href']
        pep_link = urljoin(PEPS_URL, href)
        pep_session = requests_cache.CachedSession()
        pep_response = get_response(pep_session, pep_link)
        if pep_response is None:
            continue
        pep_soup = BeautifulSoup(pep_response.text, features='lxml')
        dl_tag = find_tag(
            pep_soup,
            'dl',
            attrs={'class': 'rfc2822 field-list simple'},
        )
        dt_tags = dl_tag.find_all('dt')
        for dt_tag in dt_tags:
            text_match = re.search(pattern_status, dt_tag.text)
            if text_match:
                card_status = dt_tag.find_next_sibling('dd').text
                break
            else:
                continue
        if card_status not in statuses:
            logs.append(
                f'Несовпадающие статусы: '
                f'{pep_link} '
                f'Статус в карточке: {card_status} '
                f'Ожидаемые статусы: {statuses} ',
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
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
