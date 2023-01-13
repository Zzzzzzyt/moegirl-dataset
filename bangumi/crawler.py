import json
import requests
import urllib.parse
import time
import shutil
from bs4 import BeautifulSoup

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'User-Agent': 'Zzzyt/MoeRanker (https://github.com/Zzzzzzyt/MoeRanker)',
}
cooldown = 3

requests.adapters.DEFAULT_RETRIES = 3


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


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


def safe_download(url, path):
    url = urllib.parse.unquote(url)
    r = requests.get(url, stream=True, headers=headers)
    print("Download {} ".format(url), end='')
    if r.status_code != 200:
        print('ERROR: {}'.format(r.status_code))
    else:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    elapsed = r.elapsed.total_seconds()
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
            name = char.find('h3').contents[0].text
            print(id, avatar, name)
            ret.append({
                'id': id,
                'name': name,
                'avatar': avatar,
            })
    return ret


def crawl_characters(index):
    ret = {}
    try:
        for cnt, i in enumerate(index):
            print(cnt, i['name'], end=' ')
            id = i['id']
            data = json.loads(safe_get(f'https://api.bgm.tv/v0/characters/{id}').text)
            ret[id] = data
    except BaseException as e:
        return ret, e
    return ret, None


def download_thumnail(index, chars):
    for idx, i in enumerate(index):
        if idx >= len(chars):
            return
        id = str(i['id'])
        print(idx, id, i['name'])
        if idx < 200:
            continue
        images = chars[str(id)]['images']
        safe_download(i['avatar'], 'images/{}-avatar.jpg'.format(id))
        # safe_download(images['small'], 'images/{}-small.jpg'.format(id))
        # safe_download(images['grid'], 'images/{}-grid.jpg'.format(id))
        # safe_download(images['medium'], 'images/{}-medium.jpg'.format(id))
        safe_download(images['large'], 'images/{}-large.jpg'.format(id))


if __name__ == '__main__':
    index = crawl_index(1000)
    save_json(index, 'bgm_index.json')
    # index = json.load(open("bgm_index.json", encoding='utf-8'))
    # chars, e = crawl_characters(index)
    # print(chars, e)
    # save_json(chars, 'bgm_chars.json')

    # chars = json.load(open('bgm_chars.json', encoding='utf-8'))
    # download_thumnail(index, chars)
