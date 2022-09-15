# main.py
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEPS_URL, EXPECTED_STATUS
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        section_session = requests_cache.CachedSession()
        section_response = get_response(section_session, version_link)
        if section_response is None:
            continue

        section_soup = BeautifulSoup(section_response.text, features='lxml')
        dl = find_tag(section_soup, 'dl')
        h1 = find_tag(section_soup, 'h1')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status,))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    pattern_file = r'.+pdf-a4\.zip$'
    soup = BeautifulSoup(response.text, features='lxml')
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(pattern_file)}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив {filename} был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    pattern_number = r'^\d+$'
    pattern_status = r'^Status.*'
    results = [('Статус', 'Количество')]
    count_statuses = {}
    soup = BeautifulSoup(response.text, features='lxml')
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    for tr_tag in tqdm(tr_tags):
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
            logging.info(
                f'Несовпадающие статусы: '
                f'{pep_link} '
                f'Статус в карточке: {card_status} '
                f'Ожидаемые статусы: {statuses} ',
            )
        else:
            if card_status not in count_statuses:
                count_statuses[card_status] = 1
            else:
                count_statuses[card_status] += 1
    results.extend([*count_statuses.items()])
    results.append(['Total', len(tr_tags)])
    return results


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
