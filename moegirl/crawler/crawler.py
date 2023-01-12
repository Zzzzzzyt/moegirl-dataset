import json
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup

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
cooldown = 2

requests.adapters.DEFAULT_RETRIES = 3

page_count = 0
characters = {}


def safe_get(url):
    url = urllib.parse.unquote(url)
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    elapsed = r.elapsed.total_seconds()
    print('GET: {} {} in {:.3f}s'.format(url, r.status_code, elapsed))
    if r.status_code != 200:
        print('ERROR: {}'.format(r.status_code))
        raise RuntimeError('Network error')
    if elapsed < cooldown:
        time.sleep(cooldown-elapsed)
    return r


def safe_soup(url):
    return BeautifulSoup(safe_get(url).text, 'html.parser')


def add_prefix(url):
    if url.startswith('/'):
        url = 'https://zh.moegirl.org.cn'+url
    return url


def parse_index(url, depth=0, first_page=True):
    global page_count

    ret = {'pages': [], 'subcategories': []}
    try:
        print('  '*depth, end='')
        soup = safe_soup(url)
        if first_page or depth == 0:
            subcategories_div = soup.find(id='mw-subcategories')
            if subcategories_div != None:
                for a in subcategories_div.find('div', class_='mw-content-ltr').find_all('a'):
                    url = a['href']
                    url = urllib.parse.unquote(url)
                    ret2, err = parse_index(add_prefix(url), depth+1)
                    tmp = {'name': a.string, 'url': url}
                    tmp.update(ret2)
                    ret['subcategories'].append(tmp)

                    if depth == 0 and len(ret['subcategories']) % 10 == 0:
                        # checkpoint
                        print(' CHECKPOINT '.center(40, '='))
                        print('Root subcategory count: {}'.format(len(ret['subcategories'])))
                        print('Page count: {}'.format(page_count))
                        print('Character count: {}'.format(len(characters)))
                        print(' CHECKPOINT END '.center(40, '='))

                    if err:
                        raise err

        pages_div = soup.find(id='mw-pages')
        if pages_div != None:
            for a in pages_div.find('div', class_='mw-content-ltr').find_all('a'):
                url = a['href']
                url = urllib.parse.unquote(url)
                ret['pages'].append({'page': a.string, 'url': url})
                page_count += 1
                characters[url] = 0

        print('  '*depth, end='')
        print('Found {} subcategories, {} pages'.format(len(ret['subcategories']), len(ret['pages'])))

        article = soup.find(text='这个分类的对应条目是')
        if article != None:
            a = article.parent.find('a')
            ret['article'] = {'page': a.string, 'url': urllib.parse.unquote(a['href'])}

        next = soup.find_all('a', text='下一页')
        if len(next) != 0:
            if len(next) != 2:
                print('WARNING: UNEXPECTED NEXT COUNT')
                print(next)
            ret2, err = parse_index(add_prefix(next[0]['href']), depth, first_page=False)
            ret['pages'].extend(ret2['pages'])
            ret['subcategories'].extend(ret2['subcategories'])
            if err:
                raise err
    except BaseException as e:
        return ret, e
    return ret, None


# safe_soup('https://zh.moegirl.org.cn/index.php?title=asdfasdfsa')
# parse_index('https://zh.moegirl.org.cn/Category:%E9%95%BF%E7%9B%B4')
res, err = parse_index('https://zh.moegirl.org.cn/index.php?title=Category:按角色特征分类')
# res, err = parse_index('https://zh.moegirl.org.cn/index.php?title=Category:按角色特征分类&subcatfrom=大小眼#mw-subcategories', first_page=False)
# res, err = parse_index('https://zh.moegirl.org.cn/index.php?title=Category:按角色特征分类&pagefrom=A&filefrom=A&subcatfrom=异性恐惧症#mw-subcategories', first_page=False)
# res, err = parse_index('https://zh.moegirl.org.cn/index.php?title=Category:按角色特征分类&pagefrom=A&filefrom=A&subcatfrom=紫瞳%E2%80%8E%E2%80%8E#mw-subcategories', first_page=False)
print(err)
json.dump(res, open('out.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('json saved.')
