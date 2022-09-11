# main.py
import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    # session = requests_cache.CachedSession()
    # response = session.get(whats_new_url)
    # response.encoding = 'utf-8'
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return

    soup = BeautifulSoup(response.text, features='lxml')
    # main_div = soup.find('section', attrs={'id': 'what-s-new-in-python'})
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    # print(sections_by_python[0].prettify())

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for section in tqdm(sections_by_python):
        # version_a_tag = section.find('a')
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        section_session = requests_cache.CachedSession()
        # section_response = section_session.get(version_link)
        # section_response.encoding = 'utf-8'
        section_response = get_response(section_session, version_link)
        if section_response is None:
            # Если страница не загрузится, программа перейдёт к следующей
            # ссылке.
            continue

        section_soup = BeautifulSoup(section_response.text, features='lxml')
        # dl = section_soup.find('dl')
        # h1 = section_soup.find('h1')
        dl = find_tag(section_soup, 'dl')
        h1 = find_tag(section_soup, 'h1')
        dl_text = dl.text.replace('\n', ' ')
        # print(version_link, h1.text, dl_text)
        results.append((version_link, h1.text, dl_text))
    return results
    # for item in results:
    #    print(*item)


def latest_versions(session):
    # session = requests_cache.CachedSession()
    # response = session.get(MAIN_DOC_URL)
    # response.encoding = 'utf-8'
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    soup = BeautifulSoup(response.text, features='lxml')
    # sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
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
    # for row in results:
    #     print(*row)


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # session = requests_cache.CachedSession()
    # response = session.get(downloads_url)
    # response.encoding = 'utf-8'
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    # table_tag = soup.find('table', attrs={'class': 'docutils'})
    # pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
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


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
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
