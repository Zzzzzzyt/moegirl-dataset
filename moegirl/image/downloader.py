import json
import os
import requests
import urllib.parse
import time
import shutil
from bs4 import BeautifulSoup
from tqdm import tqdm
import PIL.Image as Image

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "User-Agent": "Zzzyt/MoeRanker (https://github.com/Zzzzzzyt/MoeRanker)",
}
cooldown = 5

requests.adapters.DEFAULT_RETRIES = 10


def save_json(data, path):
    print("saving to {}".format(path))
    json.dump(
        data,
        open(path, "w", encoding="utf-8"),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def safe_get(url, bar: tqdm = None, verbose=True):
    url = urllib.parse.unquote(url)
    if verbose:
        if bar is not None:
            bar.write("GET: {} ".format(url))
        else:
            print("GET: {} ".format(url), end="")
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    elapsed = r.elapsed.total_seconds()
    if verbose:
        if bar is not None:
            bar.write("{} in {:.3f}s".format(r.status_code, elapsed))
        else:
            print("{} in {:.3f}s".format(r.status_code, elapsed))
    if r.status_code != 200:
        # if verbose:
        #     if bar is not None:
        #         bar.write('ERROR: {}'.format(r.status_code))
        #     else:
        #         print('ERROR: {}'.format(r.status_code))
        if elapsed < cooldown:
            time.sleep(cooldown - elapsed)
        raise RuntimeError(r.status_code)
    if elapsed < cooldown:
        time.sleep(cooldown - elapsed)
    return r


def validate_image(fname, bar):
    try:
        img = Image.open(fname)
    except Exception as ee:
        # print(ee)
        bar.write("invalid image: " + fname)
        os.remove(fname)
        return False
    return True


def safe_download(url, path, bar=None, verbose=True):
    url = urllib.parse.unquote(url)
    r = requests.get(url, stream=True, headers=headers)
    if verbose:
        if bar is not None:
            bar.write("Download {} ".format(url))
        else:
            print("Download {} ".format(url), end="")
    if r.status_code != 200:
        if verbose:
            print("ERROR: {}".format(r.status_code))
    else:
        with open(path, "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            validate_image(path)
    elapsed = r.elapsed.total_seconds()
    if verbose:
        if bar is not None:
            bar.write("{:.3f}s".format(elapsed))
        else:
            print("{:.3f}s".format(elapsed))
    if elapsed < cooldown:
        time.sleep(cooldown - elapsed)
    return r


def gen_cache_name(name):
    name = name.replace("/", "")
    name = name.replace("\\", "")
    name = name.replace("?", "")
    name = name.replace(":", "")
    name = name.replace("*", "")
    name = name.replace('"', "")
    name = name.replace("|", "")
    name = name.replace("<", "")
    name = name.replace(">", "")
    return name
    # return 'raw/{}.json'.format(name)


extras = json.load(open("../crawler2/extra_info.json", encoding="utf-8"))

l = []
for k, v in extras.items():
    for i in v["image"]:
        if "url" in i:
            l.append((i["url"], k))
# print(l)
print(len(l))

bar = tqdm(l)
for idx, i in enumerate(bar):
    url = i[0]
    name = i[1]
    fname = gen_cache_name(url)
    fname2 = "images/{}".format(fname)
    if os.path.exists(fname2):
        if not validate_image(fname2, bar):
            bar.write("invalid " + fname)
            continue
        # bar.write("skip: " + fname)
        continue
    bar.set_description("{} {}".format(name, fname))
    try:
        if url.startswith("https://"):
            safe_download(url, fname2, bar)
        else:
            res = safe_get(
                "https://zh.moegirl.org.cn/api.php?action=parse&text={}&contentmodel=wikitext&format=json".format(
                    urllib.parse.quote("[[{}]]".format(url))
                ),
                bar=bar,
            )
            res = res.json()
            soup = BeautifulSoup(res["parse"]["text"]["*"], features="html.parser")
            url2 = soup.find("img").attrs["src"]
            safe_download(url2, fname2, bar)
    except Exception as e:
        # print(e)
        bar.write(str(e))
        # print(res)
    bar.write("\n")
