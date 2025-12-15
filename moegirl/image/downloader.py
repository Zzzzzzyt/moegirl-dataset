import json
import os
import warnings
import requests
import urllib.parse
import time
import shutil
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from tqdm import tqdm
import PIL.Image as Image

from utils.file import chdir_project_root
from utils.network import safe_download, safe_get, title_to_url

chdir_project_root()

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module="bs4")
warnings.simplefilter("always", UserWarning)

base_url = "https://zh.moegirl.org.cn"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": base_url.replace("https://", "").replace("http://", ""),
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

cooldown = 5

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)
cookies = os.getenv("MOEGIRL_COOKIES")
if cookies:
    print('cookies:', cookies)
    print()
    headers['Cookie'] = cookies


def validate_image(fname, bar):
    try:
        img = Image.open(fname)
    except Exception as ee:
        # print(ee)
        bar.write("invalid image: " + fname)
        os.remove(fname)
        return False
    return True


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


extras = json.load(open("moegirl/crawler_extra/extra_info.json", encoding="utf-8"))

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
    fname2 = "moegirl/image/images/{}".format(fname)
    if os.path.exists(fname2):
        if not validate_image(fname2, bar):
            bar.write("invalid " + fname)
            continue
        # bar.write("skip: " + fname)
        continue
    bar.set_description("{} {}".format(name, fname))
    try:
        if url.startswith("https://"):
            safe_download(
                url,
                fname2,
                bar,
                headers=headers,
                cooldown=cooldown,
            )
        else:
            res = safe_get(
                base_url
                + "/api.php?action=parse&text={}&contentmodel=wikitext&format=json".format(
                    title_to_url("[[{}]]".format(url))
                ),
                bar=bar,
                headers=headers,
                cooldown=cooldown,
            )
            res = res.json()
            soup = BeautifulSoup(res["parse"]["text"]["*"], features="html.parser")
            url2 = soup.find("img")
            assert url2 is not None
            url2 = url2.attrs["src"]
            safe_download(
                url2,
                fname2,
                bar,
                headers=headers,
                cooldown=cooldown,
            )
    except Exception as e:
        # print(e)
        bar.write(str(e))
        # print(res)
    bar.write("\n")
