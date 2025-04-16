import json
import os
import requests
import urllib.parse
import time
import shutil
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib3 import Retry
from requests.adapters import HTTPAdapter

from utils.network import safe_get, safe_soup, safe_download
from utils.file import save_json

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Zzzyt/MoeRanker (https://github.com/Zzzzzzyt/MoeRanker)',
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}
cooldown = 2
TIMEOUT = 10

# requests.adapters.DEFAULT_RETRIES = 10

ses = requests.Session()
retry = Retry(total=10, backoff_factor=cooldown, backoff_max=10)
ses.mount('https', HTTPAdapter(max_retries=retry))


def crawl_index(count):
    ret = []
    bar = tqdm(range(count))
    try:
        for i in bar:
            soup = safe_soup(
                f'https://bgm.tv/character?orderby=collects&page={i+1}',
                bar,
                cooldown=cooldown,
                headers=headers,
            )
            chars = soup.find(id='columnCrtBrowserB').find_all('div')[1]
            for char in chars.children:
                id = int(char.find('a')['href'].replace('/character/', ''))
                avatar = 'https:' + char.find('img')['src']
                name = char.find('h3').find('a').text.strip()
                # print(id, avatar, name)
                bar.write(f'{id} {avatar} {name}')
                ret.append(
                    {
                        'id': str(id),
                        'name': name,
                        'avatar': avatar,
                    }
                )
    except Exception as e:
        print(e)
    return ret


def crawl_characters(index):
    bar = tqdm(index, total=len(index))
    ret = {}
    try:
        for i in bar:
            id = i['id']
            bar.set_description('{} {}'.format(i['name'], id))
            data = json.loads(
                safe_get(
                    f'https://api.bgm.tv/v0/characters/{id}',
                    bar,
                    headers=headers,
                    cooldown=cooldown,
                ).text,
            )
            ret[id] = data
    except BaseException as e:
        print(e)
        return ret, e
    return ret, None


def crawl_bangumi_id(index, url, ret: dict = {}):
    bar = tqdm(index, total=len(index))
    try:
        for idx, i in enumerate(bar):
            bar.set_description('{} {}'.format(i, idx))
            if str(i) in ret:
                continue
            try:
                res = safe_get(
                    url.format(i),
                    bar,
                    headers=headers,
                    verbose=True,
                    cooldown=cooldown,
                )
                ret[i] = res.json()
            except KeyboardInterrupt as e:
                raise e
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    # continue
                    ret[i] = {}
                    # return {}, None
                else:
                    raise e
    except BaseException as e:
        bar.write(str(e))
        return ret, e
    return ret, None


def download_thumnail(index, chars):
    bar = tqdm(enumerate(index), total=len(index))
    for idx, i in bar:
        if idx >= len(chars):
            return
        id = i['id']
        if os.path.exists('images/{}-avatar.jpg'.format(id)) and os.path.exists(
            'images/{}-large.jpg'.format(id)
        ):
            bar.write('skip: ' + i['name'])
            continue
        # print(idx, id, i['name'])
        bar.set_description('{} {} {}'.format(idx, id, i['name']))
        try:
            images = chars[str(id)]['images']
            if images['large'] == '':
                continue
            avatar = images['large'].replace(
                'https://lain.bgm.tv/pic/crt/l/', 'https://lain.bgm.tv/pic/crt/g/'
            )
            safe_download(avatar, 'images/{}-avatar.jpg'.format(id), bar)
            # safe_download(images['small'], 'images/{}-small.jpg'.format(id),bar)
            # safe_download(images['grid'], 'images/{}-grid.jpg'.format(id),bar)
            # safe_download(images['medium'], 'images/{}-medium.jpg'.format(id),bar)
            safe_download(images['large'], 'images/{}-large.jpg'.format(id), bar)
        except Exception as e:
            print(e)


# index = crawl_index(9999)
# save_json(index, 'bgm_index_20k.json')
# index = json.load(open("bgm_index_20k.json", encoding='utf-8'))
# # print(index)
# chars, e = crawl_characters(index)
# # print(chars, e)
# save_json(chars, 'bgm_chars_20k.json')

# subjects, e = crawl_subjects(index)
# print(subjects, e)
# save_json(subjects, 'bgm_subjects.json')

# chars = json.load(open('bgm_chars_160k.json', encoding='utf-8'))
# download_thumnail(index[:10000], chars)

# set20k = set()
# for i in index:
#     id = i['id']
#     set20k.add(id)

for i in list(range(1, 175)):
    print(f'crawl: {(i-1)*1000+1} - {i*1000}')
    fname = f'160k_chars/bgm_chars_160k_{i}.json'
    if os.path.exists(fname):
        crawled = json.load(open(fname, encoding='utf-8'))
    else:
        crawled = {}
    subjects, e = crawl_bangumi_id(
        range((i - 1) * 1000 + 1, i * 1000 + 1),
        'https://api.bgm.tv/v0/characters/{}',
        crawled,
    )
    save_json(subjects, fname)
    if type(e) == KeyboardInterrupt:
        break

# for i in range(1,169):
#     fname = f'160k_subjects/bgm_subjects_160k_{i}.json'
#     if os.path.exists(fname):
#         crawled = json.load(open(fname, encoding='utf-8'))
#         for id in set20k:
#             if id in crawled:
#                 del crawled[id]
#         save_json(crawled, fname)


for i in list(range(1, 175)):
    print(f'crawl: {(i-1)*1000+1} - {i*1000}')
    fname = f'160k_subjects/bgm_subjects_160k_{i}.json'
    if os.path.exists(fname):
        crawled = json.load(open(fname, encoding='utf-8'))
    else:
        crawled = {}
    subjects, e = crawl_bangumi_id(
        range((i - 1) * 1000 + 1, i * 1000 + 1),
        'https://api.bgm.tv/v0/characters/{}/subjects',
        crawled,
    )
    save_json(subjects, fname)
    if type(e) == KeyboardInterrupt:
        break
