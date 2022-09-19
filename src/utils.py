# utils.py
from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

RESPONSE_ERROR = 'Возникла ошибка при загрузке страницы {url}'
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise RequestException(RESPONSE_ERROR.format(url=url))


def make_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None, string=''):
    attrs_find = {} if attrs is None else attrs
    searched_tag = soup.find(tag, attrs=attrs_find, string=string)
    if searched_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tag
