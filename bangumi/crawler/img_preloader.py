import json
import os
import requests
import urllib.parse
import time

from utils.file import save_json

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "User-Agent": "Zzzyt/MoeRanker (https://github.com/Zzzzzzyt/MoeRanker)",
}
cooldown = 2

requests.adapters.DEFAULT_RETRIES = 10


def safe_get302(url, bar=None, verbose=True):
    url = urllib.parse.unquote(url)
    if verbose:
        if bar is not None:
            bar.write("GET: {} ".format(url), end="")
        else:
            print("GET: {} ".format(url), end="")
    r = requests.get(url, headers=headers, allow_redirects=False)
    elapsed = r.elapsed.total_seconds()
    if verbose:
        if bar is not None:
            bar.write("{} in {:.3f}s".format(r.status_code, elapsed))
        else:
            print("{} in {:.3f}s".format(r.status_code, elapsed))
    if r.status_code != 302:
        if verbose:
            print("ERROR: {}".format(r.status_code))
        raise RuntimeError(r.status_code)
    if elapsed < cooldown:
        time.sleep(cooldown - elapsed)
    return r.headers["Location"]


subset = []
for i in os.listdir("../../moegirl/subset/subset/"):
    subset += json.load(open("../../moegirl/subset/subset/" + i, encoding="utf-8"))
subset += json.load(open("../subset/bgm200_subset.json", encoding="utf-8"))
subset += json.load(open("../subset/bgm2000_subset.json", encoding="utf-8"))
subset = set(subset)
print("subset len={}".format(len(subset)))

mapping = json.load(open("../moegirl2bgm.json", encoding="utf-8"))
print("mapping len={}".format(len(mapping)))

chars = json.load(open("../bgm_chars_full.json", encoding="utf-8"))
res = {}
for i in subset:
    if i in mapping:
        for j in mapping[i]:
            if j in res:
                continue
            if chars[j]['images'] is None:
                print("no images:", chars[j]['name'])
                continue
            if chars[j]["images"]["medium"] == "":
                print("no image:", chars[j]["name"])
                continue
            # small = char['images']['small'].replace('https://lain.bgm.tv/r/100/pic/crt/l/', '')
            # grid = char['images']['grid'].replace('https://lain.bgm.tv/r/200/pic/crt/l/', '')
            # large = char['images']['large'].replace('https://lain.bgm.tv/pic/crt/l/', '')
            medium = chars[j]["images"]["medium"].replace(
                "https://lain.bgm.tv/r/400/pic/crt/l/", ""
            )
            # res[i] = [small, grid, large, medium]
            res[j] = medium

print("res len={}".format(len(res)))
save_json(res, "../bgm_images_medium_mapped.json")
