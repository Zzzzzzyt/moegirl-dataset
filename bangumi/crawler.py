import json
import requests
import urllib.parse
import time
import shutil
from bs4 import BeautifulSoup
from tqdm import tqdm

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'User-Agent': 'Zzzyt/MoeRanker (https://github.com/Zzzzzzyt/MoeRanker)',
}
cooldown = 2

requests.adapters.DEFAULT_RETRIES = 10


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


def safe_get(url, bar=None):
    url = urllib.parse.unquote(url)
    if bar is not None:
        bar.write('GET: {} '.format(url), end='')
    else:
        print('GET: {} '.format(url), end='')
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    elapsed = r.elapsed.total_seconds()
    if bar is not None:
        bar.write('{} in {:.3f}s'.format(r.status_code, elapsed))
    else:
        print('{} in {:.3f}s'.format(r.status_code, elapsed))
    if r.status_code != 200:
        print('ERROR: {}'.format(r.status_code))
        raise RuntimeError('Network error')
    if elapsed < cooldown:
        time.sleep(cooldown-elapsed)
    return r


def safe_download(url, path, bar=None):
    url = urllib.parse.unquote(url)
    r = requests.get(url, stream=True, headers=headers)
    if bar is not None:
        bar.write('Download {} '.format(url))
    else:
        print('Download {} '.format(url), end='')
    if r.status_code != 200:
        print('ERROR: {}'.format(r.status_code))
    else:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    elapsed = r.elapsed.total_seconds()
    if bar is not None:
        bar.write('{:.3f}s'.format(elapsed))
    else:
        print('{:.3f}s'.format(elapsed))
    if elapsed < cooldown:
        time.sleep(cooldown-elapsed)
    return r


def safe_soup(url) -> BeautifulSoup:
    return BeautifulSoup(safe_get(url).text, 'html.parser')


def crawl_index(count):
    ret = []
    for i in range(count):
        soup = safe_soup(f'https://bgm.tv/character?orderby=collects&page={i+1}')
        chars = soup.find(id='columnCrtBrowserB').find_all('div')[1]
        for char in chars.children:
            id = int(char.find('a')['href'].replace('/character/', ''))
            avatar = 'https:'+char.find('img')['src']
            name = char.find('h3').contents[0].text.strip()
            print(id, avatar, name)
            ret.append({
                'id': id,
                'name': name,
                'avatar': avatar,
            })
    return ret


def crawl_characters(index):
    bar = tqdm(index, total=len(index))
    ret = {}
    try:
        for i in bar:
            id = i['id']
            bar.set_description('{} {}'.format(i['name'], id))
            data = json.loads(safe_get(f'https://api.bgm.tv/v0/characters/{id}', bar).text)
            ret[id] = data
    except BaseException as e:
        return ret, e
    return ret, None


def crawl_subjects(index):
    bar = tqdm(index, total=len(index))
    ret = {}
    try:
        for i in bar:
            id = i['id']
            bar.set_description('{} {}'.format(i['name'], id))
            data = json.loads(safe_get(f'https://api.bgm.tv/v0/characters/{id}/subjects', bar).text)
            ret[id] = data
    except BaseException as e:
        return ret, e
    return ret, None


def download_thumnail(index, chars):
    bar = tqdm(enumerate(index), total=len(index))
    for idx, i in bar:
        if idx >= len(chars):
            return
        id = str(i['id'])
        # print(idx, id, i['name'])
        bar.set_description('{} {} {}'.format(idx, id, i['name']))
        if idx < 200:
            continue
        images = chars[str(id)]['images']
        safe_download(i['avatar'], 'images/{}-avatar.jpg'.format(id), bar)
        # safe_download(images['small'], 'images/{}-small.jpg'.format(id),bar)
        # safe_download(images['grid'], 'images/{}-grid.jpg'.format(id),bar)
        # safe_download(images['medium'], 'images/{}-medium.jpg'.format(id),bar)
        safe_download(images['large'], 'images/{}-large.jpg'.format(id), bar)


if __name__ == '__main__':
    # index = crawl_index(1000)
    # save_json(index, 'bgm_index.json')
    index = json.load(open("bgm_index.json", encoding='utf-8'))
    # chars, e = crawl_characters(index)
    # print(chars, e)
    # save_json(chars, 'bgm_chars.json')

    subjects, e = crawl_subjects(index)
    print(subjects, e)
    save_json(subjects, 'bgm_subjects.json')

    # chars = json.load(open('bgm_chars.json', encoding='utf-8'))
    # download_thumnail(index, chars)
