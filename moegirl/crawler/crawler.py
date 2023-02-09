import json
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


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
    print('GET: {} '.format(url), end='')
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    elapsed = r.elapsed.total_seconds()
    print('{} in {:.3f}s'.format(r.status_code, elapsed))
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


def parse_index(url, depth=0, first_page=True, dedupe=set()):
    global page_count

    ret = {'pages': [], 'subcategories': []}
    try:
        print('  '*depth, end='')
        if url in dedupe:
            print('duplicate: {}'.format(url))
            return ret, None, dedupe
        dedupe.add(url)
        soup = safe_soup(url)
        if first_page or depth == 0:
            subcategories_div = soup.find(id='mw-subcategories')
            if subcategories_div != None:
                for a in subcategories_div.find('div', class_='mw-content-ltr').find_all('a'):
                    url = a['href']
                    url = urllib.parse.unquote(url)
                    ret2, err, dedupe2 = parse_index(add_prefix(url), depth+1, dedupe=dedupe)
                    dedupe.update(dedupe2)
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
            ret2, err, dedupe2 = parse_index(add_prefix(next[0]['href']), depth, first_page=False, dedupe=dedupe)
            dedupe.update(dedupe2)
            ret['pages'].extend(ret2['pages'])
            ret['subcategories'].extend(ret2['subcategories'])
            if err:
                raise err
    except BaseException as e:
        if depth == 0:
            print(e)
        return ret, e, dedupe
    return ret, None, dedupe


def merge(*output):
    ret = {'pages': [], 'subcategories': []}
    for i in output:
        ret['pages'].extend(i['pages'])
        ret['subcategories'].extend(i['subcategories'])
    return ret


# save_json(parse_index('https://zh.moegirl.org.cn/Category:按角色特征分类')[0],'out.json')

# save_json(parse_index('https://zh.moegirl.org.cn/Category:东方正作人物')[0], 'subset/touhou_new_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:东方旧作人物')[0], 'subset/touhou_old_out.json')

# save_json(parse_index('https://zh.moegirl.org.cn/Category:魔法禁书目录')[0],'subset/toaru_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:某科学的超电磁炮')[0], 'subset/railgun_out.json')

# save_json(merge(
#     parse_index('https://zh.moegirl.org.cn/Category:AIR')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:古典部系列')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:CLANNAD')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:Free!')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:甘城光辉游乐园')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:境界的彼方')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:紫罗兰永恒花园')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:Kanon')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:吹响！上低音号')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:凉宫春日系列')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:轻音少女')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:全金属狂潮')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:日常')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:声之形')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:弦音_-风舞高中弓道部-')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:小林家的龙女仆')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:幸运星')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:玉子市场')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:中二病也要谈恋爱！')[0]
# ), 'subset/kyoani_out.json')

# save_json(parse_index('https://zh.moegirl.org.cn/Category:明日方舟')[0], 'subset/arknights_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:原神')[0], 'subset/genshin_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:Fate系列')[0], 'subset/fate_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:JOJO的奇妙冒险')[0], 'subset/jojo_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:机动战士高达系列')[0], 'subset/gundam_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:火影忍者')[0], 'subset/naruto_out.json')

# save_json(merge(
#     parse_index('https://zh.moegirl.org.cn/Category:某科学的超电磁炮')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:孤独摇滚！')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:新世纪福音战士')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:少女终末旅行')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:凉宫春日系列')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:轻音少女')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:幸运星')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:中二病也要谈恋爱！')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:东方正作人物')[0],
# ), 'subset/zzzyt_out.json')

# save_json(parse_index('https://zh.moegirl.org.cn/Category:兽娘')[0], 'subset/furry_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:LoveLive!系列')[0], 'subset/lovelive_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:英雄联盟')[0], 'subset/lol_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:按歌声合成软件分类')[0], 'subset/vocaloid_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:名侦探柯南中角色')[0], 'subset/conan_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:赛马娘_Pretty_Derby中角色')[0], 'subset/derby_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:舰队Collection')[0], 'subset/kanC_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:战舰少女')[0], 'subset/kanR_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:碧蓝航线')[0], 'subset/kanB_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:蔚蓝档案')[0], 'subset/blue_archive_out.json')
# save_json(merge(
#     parse_index('https://zh.moegirl.org.cn/Category:Kanon')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:AIR')[0],
#     parse_index('https://zh.moegirl.org.cn/Category:CLANNAD')[0]), 'subset/key3_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:宝可梦系列角色')[0], 'subset/pokemon_char_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:宝可梦')[0], 'subset/pokemon_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:彩虹小马')[0], 'subset/pony_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:偶像大师系列')[0], 'subset/idolmaster_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:偶像梦幻祭')[0], 'subset/ES_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:公主连结Re:Dive')[0], 'subset/PCR_out.json')
# save_json(parse_index('https://zh.moegirl.org.cn/Category:RWBY')[0], 'subset/RWBY_out.json')
