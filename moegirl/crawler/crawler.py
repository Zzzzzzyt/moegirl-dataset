import json
import traceback
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup
from urllib3 import Retry
from requests.adapters import HTTPAdapter

from utils.file import *
from utils.network import safe_soup, quote_all

chdir_project_root()

# base_url = 'https://zh.moegirl.org.cn'

# base_url = 'https://moegirl.uk'
# base_url = 'https://moegirl.icu'
# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
#     'Connection': 'keep-alive',
#     'Host': base_url.replace("https://", "").replace("http://", ""),
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'none',
#     'Sec-Fetch-User': '?1',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
#     'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
# }

base_url = "https://mobile.moegirl.org.cn"
headers = {
    "upgrade-insecure-requests": "1",
    "user-agent": "Moegirl-Mobile os=android&version=4280&layout=sliver&theme=dark",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "x-requested-with": "org.moegirl.moegirlview",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://mobile.moegirl.org.cn/mobile",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}
cooldown = 1.2

page_count = 0
characters = {}


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
PURPLE = '\033[95m'
FAIL = '\033[91m'
RESET = '\033[0m'
GREY = '\033[2m'


def uncensor(result):
    name = result['name']
    url = result['url']
    if '♯' not in name:
        return
    url2 = name.replace(' ', '_')
    if url.startswith('/Category:'):
        if '/Category:' + url2 != url:
            ret = url[10:].replace('_', ' ')
            print(PURPLE + "uncensored:", url, name, '->', ret, RESET)
            result['name_censored'] = name
            result['name'] = ret
    else:
        if '/' + url2 != url:
            ret = url[1:].replace('_', ' ')
            print(PURPLE + "uncensored:", url, name, '->', ret, RESET)
            result['name_censored'] = name
            result['name'] = ret


def parse_index(url, ret, stk=[], filter_function=None):
    global page_count

    # if len(stk) <= 1:
    #     del ret['finish1']
    #     del ret['finish2']

    if 'pages' not in ret:
        ret['pages'] = []
    if 'subcategories' not in ret:
        ret['subcategories'] = []

    pages_set = set(map(lambda x: x['url'], ret['pages']))
    pages_cur = list(map(lambda x: {'name': x['name'], 'url': x['url']}, ret['pages']))
    subcategories_set = set(map(lambda x: x['url'], ret['subcategories']))
    subcategories_cur = list(
        map(lambda x: {'name': x['name'], 'url': x['url']}, ret['subcategories'])
    )

    url_now = base_url + '/' + quote_all(url)
    category_name = url.replace('/Category:', '')
    depth = len(stk)

    stk2 = stk.copy()
    stk2.append(url)

    def print_debug(s, color=None):
        if color:
            print(color + '  ' * depth + category_name + ':', s + RESET)
        else:
            print('  ' * depth + category_name + ':', s)

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
            retry_cnt = None
            while True:
                prev_pages_count = len(ret['pages'])
                prev_subcategories_count = len(ret['subcategories'])

                print('  ' * depth, end='')

                soup = safe_soup(
                    url_now,
                    headers=headers,
                    cooldown=cooldown,
                )
                soup = soup.find('div', id='mw-content-text')
                assert soup is not None

                if 'article' not in ret:
                    article = soup.find(string='这个分类的对应条目是')
                    if article != None:
                        a = article.parent.find('a')
                        url2 = urllib.parse.unquote(a['href'])
                        if "action=edit" not in url2 and not url2.startswith(
                            '/Category:'
                        ):
                            ret['article'] = {
                                'name': a.string,
                                'url': url2,
                            }
                            uncensor(ret['article'])

                subcategories_div = soup.find(id='mw-subcategories')
                subcategories_cnt = 0
                if subcategories_div != None:
                    subcategories_text = subcategories_div.find('p').string
                    assert subcategories_text is not None
                    if '只有' in subcategories_text:
                        subcategories_cnt = 1
                    else:
                        assert '共有' in subcategories_text
                        subcategories_cnt = int(
                            subcategories_text.split('共有')[-1]
                            .split('个子分类')[0]
                            .strip()
                            .replace(',', '')
                        )

                    for a in subcategories_div.find(
                        'div', class_='mw-content-ltr'
                    ).find_all('a'):
                        name = a.string
                        if name is None or name.strip() == '':
                            continue
                        url2 = a['href']
                        if "action=edit" in url2:
                            continue
                        url_unquote = urllib.parse.unquote(url2)
                        tmp = {
                            'name': name,
                            'url': url_unquote,
                            'pages': [],
                            'subcategories': [],
                        }
                        uncensor(tmp)
                        subcategories_cur.append(tmp)
                        if tmp['url'] in subcategories_set:
                            continue
                        subcategories_set.add(tmp['url'])
                        ret['subcategories'].append(tmp)
                    if retry_cnt is not None:
                        diff = len(ret['subcategories']) - prev_subcategories_count
                        if diff > 100:
                            print_debug(
                                f'found {diff} new subcategories. reset retry_cnt',
                                color=YELLOW,
                            )
                            retry_cnt = None

                pages_div = soup.find(id='mw-pages')
                pages_cnt = 0
                if pages_div != None:
                    pages_cnt_text = pages_div.find('p').string
                    assert pages_cnt_text is not None
                    if '只含有' in pages_cnt_text:
                        pages_cnt = 1
                    else:
                        assert '属于本分类' in pages_cnt_text
                        pages_cnt = int(
                            pages_cnt_text.split('共')[-1]
                            .split('个页面')[0]
                            .strip()
                            .replace(',', '')
                        )

                    for a in pages_div.find('div', class_='mw-content-ltr').find_all(
                        'a'
                    ):
                        name = a.string
                        if name is None or name.strip() == '':
                            continue
                        url2 = a['href']
                        if "action=edit" in url2:
                            continue
                        url_unquote = urllib.parse.unquote(url2)
                        tmp = {'name': name, 'url': url_unquote}
                        uncensor(tmp)
                        pages_cur.append(tmp)
                        if tmp['url'] in pages_set:
                            continue
                        pages_set.add(tmp['url'])
                        ret['pages'].append(tmp)
                        page_count += 1

                    if retry_cnt is not None:
                        diff = len(ret['pages']) - prev_pages_count
                        if diff > 100:
                            print_debug(
                                f'found {diff} new pages. reset retry_cnt',
                                color=YELLOW,
                            )
                            retry_cnt = None

                next = soup.find_all('a', string='下一页')
                if len(next) != 0 and retry_cnt is None:
                    if len(next) != 2:
                        print_debug('UNEXPECTED NEXT COUNT!!!', color=ERROR)
                        print_debug(next, color=ERROR)
                        raise RuntimeError('Unexpected next count')
                    next_url = next[0]['href']

                    if 'pagefrom=' in next_url:
                        next_index = len(pages_cur) - 3
                        while next_index >= 0 and ':' in pages_cur[next_index]['name']:
                            next_index -= 1
                        if next_index < len(pages_cur) - 180:
                            next_index = len(pages_cur) - 3
                        url_now = (
                            base_url
                            + '/'
                            + quote_all(url)
                            + '?pagefrom='
                            + quote_all(pages_cur[next_index]['name'])
                        )
                    elif 'subcatfrom=' in next_url:
                        next_index = len(subcategories_cur) - 3
                        while (
                            next_index >= 0
                            and ':' in subcategories_cur[next_index]['name']
                        ):
                            next_index -= 1
                        if next_index < len(subcategories_cur) - 180:
                            next_index = len(subcategories_cur) - 3
                        url_now = (
                            base_url
                            + '/'
                            + quote_all(url)
                            + '?subcatfrom='
                            + quote_all(subcategories_cur[next_index]['name'])
                        )
                    # url_now = base_url + next_url.replace(
                    #     'index.php?title=', ''
                    # ).replace('&', '?')
                else:
                    if len(ret['subcategories']) > 0 and subcategories_cnt == 0:
                        print_debug(
                            'has subcategories before but now none?!!!', color=ERROR
                        )
                        ret['subcategories'] = []
                        raise RuntimeError('subcategories count decreased')
                    if len(ret['pages']) > 0 and pages_cnt == 0:
                        print_debug('has pages before but now none?!!!', color=ERROR)
                        ret['pages'] = []
                        raise RuntimeError('pages count decreased')

                    subcategories_cnt_error = False
                    pages_cnt_error = False
                    if len(ret['subcategories']) < subcategories_cnt:
                        print_debug(
                            'subcategories_cnt too small!!!',
                            color=ERROR,
                        )
                        print_debug(
                            'expected: {}, got: {}'.format(
                                subcategories_cnt, len(ret['subcategories'])
                            ),
                            color=ERROR,
                        )
                        subcategories_cnt_error = True
                        if retry_cnt is None:
                            retry_cnt = len(ret['subcategories']) - 2
                    elif len(ret['subcategories']) > subcategories_cnt:
                        print_debug(
                            'subcategories_cnt too large??!',
                            color=YELLOW,
                        )
                        print_debug(
                            'expected: {}, got: {}'.format(
                                subcategories_cnt, len(ret['subcategories'])
                            ),
                            color=YELLOW,
                        )
                    if len(ret['pages']) < pages_cnt:
                        print_debug(
                            'pages_cnt too small!!!',
                            color=ERROR,
                        )
                        print_debug(
                            'expected: {}, got: {}'.format(
                                pages_cnt, len(ret['pages'])
                            ),
                            color=ERROR,
                        )
                        pages_cnt_error = True
                        if retry_cnt is None:
                            retry_cnt = len(ret['pages']) - 2
                    elif len(ret['pages']) > pages_cnt:
                        print_debug('pages_cnt too large??!', color=YELLOW)
                        print_debug(
                            'expected: {}, got: {}'.format(
                                pages_cnt, len(ret['pages'])
                            ),
                            color=YELLOW,
                        )

                    assert not (pages_cnt_error and subcategories_cnt_error)
                    if pages_cnt_error or subcategories_cnt_error:
                        assert retry_cnt is not None
                        print_debug(f"retry_cnt: {retry_cnt}", color=ERROR)
                        if retry_cnt < 0:
                            print_debug(
                                'reached max retry for next page. give up',
                                color=ERROR,
                            )
                            break
                        if pages_cnt_error:
                            url_now = (
                                base_url
                                + '/'
                                + quote_all(url)
                                + '?pagefrom='
                                + quote_all(ret['pages'][retry_cnt]['name'])
                            )
                            retry_cnt -= 42
                            continue
                        if subcategories_cnt_error:
                            url_now = (
                                base_url
                                + '/'
                                + quote_all(url)
                                + '?subcatfrom='
                                + quote_all(ret['subcategories'][retry_cnt]['name'])
                            )
                            retry_cnt -= 42
                            continue
                    ret['finish1'] = True
                    # print_debug('finish1', color=GREY)
                    break

        # assert 'finish1' in ret
        if 'finish1' not in ret:
            print_debug('what happened? why not finish1? skip', color=ERROR)
            return

        print_debug(
            'Found {} subcategories, {} pages'.format(
                len(ret['subcategories']), len(ret['pages'])
            ),
            color=GREEN,
        )

        if 'finish2' in ret:
            print_debug('already finish2. return', color=GREY)
        else:
            ret['subcategories'] = unique(ret['subcategories'])
            for i in ret['subcategories']:
                name = i['name']
                parse_index(
                    i['url'],
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
                # print_debug('finish2', color=GREY)
            else:
                print_debug('what happened? why not finish2? anyway', color=ERROR)

    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print_debug('fine. 404 then.', color=ERROR)
            # ret['finish1'] = True
            # ret['finish2'] = True
        else:
            print_debug(RESET)
            print_debug(traceback.format_exc(), color=ERROR)
    # except requests.ConnectionError as e:
    #     print_debug(RESET)
    #     print_debug(traceback.format_exc(), color=ERROR)


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


def crawl(root: str, path: str, filter_function=None):
    ret = load_json_or_none(path) or {}
    try:
        parse_index(
            root,
            ret,
            filter_function=filter_function,
        )
    except KeyboardInterrupt as e:
        pass
    except requests.RequestException as e:
        traceback.print_exc()
        pass
    except RuntimeError as e:
        if (
            str(e) == 'subcategories count decreased'
            or str(e) == 'pages count decreased'
        ):
            print('skip and save partial result')
        else:
            raise e
    save_json(ret, path)


def filter_func_subjects(stk):
    if len(stk) == 0:
        return True
    url = stk[-1]
    if url == '/Category:游戏王:游戏王卡片':
        return False
    if url == '/Category:各地区游戏作品':
        return False
    if url == '/Category:各地区音乐作品':
        return False
    if url.endswith('模板'):
        return False
    if url.endswith('音乐'):
        if len(stk) >= 2 and url == stk[-2] + '音乐':
            return False
    return True


def filter_func_attrs(stk):
    if len(stk) == 0:
        return True
    url = stk[-1]
    if '虚拟UP主组合' in url:
        return False
    return True


crawl(
    '/Category:虚拟人物',
    'moegirl/crawler/attrs.json',
    filter_function=filter_func_attrs,
)
crawl(
    '/Category:各地区作品',
    'moegirl/crawler/subjects.json',
    filter_function=filter_func_subjects,
)
