import json
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup
from urllib3 import Retry
from requests.adapters import HTTPAdapter

from utils.file import load_json, save_json, save_json_pretty
from utils.network import safe_soup


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Host': 'zh.moegirl.org.cn',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
cooldown = 4

# requests.adapters.DEFAULT_RETRIES = 3

page_count = 0
characters = {}


def add_prefix(url):
    if url.startswith('/'):
        url = 'https://zh.moegirl.org.cn' + url
    return url


def unique(l):
    ret = []
    s = set()
    for i in l:
        if i['url'] not in s:
            s.add(i['url'])
            ret.append(i)
    return ret


YELLOW = '\033[93m'
GREEN = '\033[32m'
ERROR = '\033[31m'
CYAN = '\033[36m'
FAIL = '\033[91m'
RESET = '\033[0m'
GREY = '\033[2m'


def parse_index(url, ret, stk=[], filter_function=None):
    global page_count
    if 'finished2' in ret:
        return
    if 'pages' not in ret:
        ret['pages'] = []
    if 'subcategories' not in ret:
        ret['subcategories'] = []
    url_now = url
    url_short = url.split(':')[-1]
    depth = len(stk)

    stk2 = stk.copy()
    stk2.append(url)

    def print_debug(s, color=None):
        if color:
            print(color + '  ' * depth + url_short + ':', s + RESET)
        else:
            print('  ' * depth + url_short + ':', s)

    if filter_function and not filter_function(stk2):
        ret['finish1'] = True
        ret['finish2'] = True
        print_debug('filtered.', color=CYAN)
        return

    try:
        print_debug('', color=YELLOW)
        if 'finish1' in ret:
            print_debug('already finish1. skip', color=GREY)
        else:
            while True:
                print('  ' * depth, end='')
                soup = safe_soup(url_now, headers=headers, cooldown=cooldown)

                article = soup.find(text='这个分类的对应条目是')
                if article != None:
                    a = article.parent.find('a')
                    ret['article'] = {
                        'name': a.string,
                        'url': urllib.parse.unquote(a['href']),
                    }

                subcategories_div = soup.find(id='mw-subcategories')
                if subcategories_div != None:
                    for a in subcategories_div.find(
                        'div', class_='mw-content-ltr'
                    ).find_all('a'):
                        url2 = a['href']
                        url2 = urllib.parse.unquote(url2)
                        tmp = {
                            'name': a.string,
                            'url': url2,
                            'pages': [],
                            'subcategories': [],
                        }
                        ret['subcategories'].append(tmp)

                pages_div = soup.find(id='mw-pages')
                if pages_div != None:
                    for a in pages_div.find('div', class_='mw-content-ltr').find_all(
                        'a'
                    ):
                        url2 = a['href']
                        url2 = urllib.parse.unquote(url2)
                        ret['pages'].append({'name': a.string, 'url': url2})
                        page_count += 1

                next = soup.find_all('a', text='下一页')
                if len(next) != 0:
                    if len(next) != 2:
                        print_debug('WARNING: UNEXPECTED NEXT COUNT', color=ERROR)
                        print_debug(next, color=ERROR)
                    url_now = add_prefix(next[0]['href'])
                else:
                    ret['finish1'] = True
                    print_debug('finish1')
                    break

        # assert 'finish1' in ret
        if 'finish1' not in ret:
            print_debug('what happened? why not finish1? skip', color=ERROR)
            return

        if 'finish2' in ret:
            print_debug('already finish2. return', color=GREY)
        else:
            ret['subcategories'] = unique(ret['subcategories'])
            for i in ret['subcategories']:
                name = i['name']
                url2 = i['url']
                parse_index(
                    add_prefix(url2),
                    i,
                    stk2,
                    filter_function=filter_function,
                )

            flag = True
            for i in ret['subcategories']:
                if 'finish2' not in i:
                    flag = False
            if flag:
                ret['finish2'] = True
                print_debug(
                    'finish2',
                )
            else:
                print_debug('what happened? why not finish2? anyway', color=ERROR)

            print_debug(
                'Found {} subcategories, {} pages'.format(
                    len(ret['subcategories']), len(ret['pages'])
                ),
                color=GREEN,
            )
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print_debug('fine. 404 then. mark as finished', color=ERROR)
            ret['finish1'] = True
            ret['finish2'] = True
    except Exception as e:
        if depth == 0:
            print(e)
        # return ret, e, dedupe
    # return ret, None, dedupe


def merge(s, t, depth=0):
    if 'name' in s:
        assert 'url' in s
    if 'name' in t:
        assert 'url' in t
    if 'name' in t:
        if 'name' in s:
            assert s['name'] == t['name']
            assert s['url'] == t['url']
        else:
            s['name'] = t['name']
            s['url'] = t['url']
            print('  ' * depth + 'merge name: ', s['name'])
            print('  ' * depth + 'merge url: ', s['url'])
    # if 'name' in s:
    #     print('  '*depth+'merging:', s['name'])
    if 'article' in t:
        if 'article' in s:
            assert t['article']['name'] == s['article']['name']
            assert t['article']['url'] == s['article']['url']
        else:
            s['article'] = t['article']
            print('  ' * depth + 'merge article: ', s['article'])
    if 'pages' in t:
        if 'pages' not in s:
            s['pages'] = []
        tmp = []
        for i in t['pages']:
            flag = False
            for j in s['pages']:
                if j['name'] == i['name']:
                    assert j['url'] == i['url']
                    flag = True
                    break
            if not flag:
                tmp.append(i)
        if len(tmp) > 0 and 'name' in s:
            print('  ' * depth + 'extra pages for ' + s['name'], len(tmp))
        s['pages'].extend(tmp)
    if 'subcategories' in t:
        if 'subcategories' not in s:
            s['subcategories'] = []
        tmp = []
        for i in t['subcategories']:
            flag = False
            for jdx, j in enumerate(s['subcategories']):
                if i['name'] == j['name']:
                    assert i['url'] == j['url']
                    s['subcategories'][jdx] = merge(j, i, depth + 1)
                    flag = True
                    break
            if not flag:
                tmp.append(i)
        if len(tmp) > 0 and 'name' in s:
            print('  ' * depth + 'extra subcategories for ' + s['name'], len(tmp))
        s['subcategories'].extend(tmp)
    return s


def merge2(*output):
    ret = {'pages': [], 'subcategories': []}
    for i in output:
        ret['pages'].extend(i['pages'])
        ret['subcategories'].extend(i['subcategories'])
    return ret


def parse_index2(url, **args):
    ret = {}
    parse_index(url, ret, [], **args)
    return ret


# def filter_func(stk):
#     if len(stk) == 0:
#         return True
#     url = stk[-1]
#     if url.endswith('模板'):
#         return False
#     if url.endswith('音乐作品'):
#         return False
#     if url.endswith('音乐'):
#         if len(stk) >= 2 and url.replace('音乐', '') == stk[-2]:
#             return False
#     return True


# ret = load_json('subjects2.json')
# # ret = {}
# try:
#     parse_index(
#         'https://zh.moegirl.org.cn/Category:各地区作品',
#         ret,
#         filter_function=filter_func,
#     )
# except BaseException as e:
#     pass
# save_json(ret, 'subjects2.json')

# save_json(parse_index('https://zh.moegirl.org.cn/Category:按角色特征分类', dedupe=filterset)[0], 'by_attr.json')
# parse_index('https://zh.moegirl.org.cn/Category:按着装特征分类', dedupe=filterset)
# save_json(
#     parse_index('https://zh.moegirl.org.cn/Category:虚拟人物', dedupe=filterset)[0],
#     'temp/full3.json',
# )

# ret = load_json('attrs2.json')
# # ret = {}
# try:
#     parse_index(
#         'https://zh.moegirl.org.cn/Category:虚拟人物',
#         ret,
#         # filter_function=filter_func,
#     )
# except BaseException as e:
#     pass
# save_json(ret, 'attrs2.json')

save_json(
    parse_index2('https://zh.moegirl.org.cn/Category:按歌声合成软件分类'),
    'subset/vocaloid.json',
)
