import requests

from bs4 import BeautifulSoup


def parse_url(url):
    parse_dict = {}
    parse = requests.get(url).text
    soup = BeautifulSoup(parse, 'html.parser')
    parse_dict['description'] = find_description(soup)
    if soup.h1:
        parse_dict['h1'] = soup.h1.string
    if soup.title:
        parse_dict['title'] = soup.title.string
    return parse_dict


def find_description(soup):
    tag = soup.find('meta', content=True, attrs={'name': 'description', })
    if tag:
        return tag['content']
    return ''


def get_url_content(url_content):
    h1 = url_content.get('h1', ' ')
    title = url_content.get('title', ' ')
    description = url_content.get('description', ' ')
    return {'h1': h1, 'title': title, 'description': description}
