import json
import os
import traceback
import warnings
import requests
import urllib.parse
import time
from bs4 import BeautifulSoup
import mwparserfromhell as mwp
import opencc
from tqdm import tqdm
from bs4 import MarkupResemblesLocatorWarning
import re

from urllib3 import Retry
from requests.adapters import HTTPAdapter

from utils.network import safe_get, title_to_url
from utils.file import save_json, chdir_project_root

chdir_project_root()

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module="bs4")

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "zh.moegirl.org.cn",
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
cooldown = 12

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(raise_error_if_not_found=True), verbose=True)
cookies = os.getenv("MOEGIRL_COOKIES")
if cookies:
    print('cookies:', cookies)
    print()
    headers['Cookie'] = cookies

converter = opencc.OpenCC("t2s.json")


def conv(t):
    return converter.convert(t)


def unique(l):
    ret = []
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret


def multisplit(str, sp=",，、"):
    ret = []
    cur = ""
    for i in str:
        if i in sp:
            ret.append(cur.strip())
            cur = ""
        else:
            cur += i
    if cur != "":
        ret.append(cur.strip())
    return ret


def remove_style(src, strip_wikilink=False):
    ret = ""
    for i in src.nodes:
        if isinstance(i, mwp.nodes.text.Text):
            ret += str(i.value)
        elif isinstance(i, mwp.nodes.template.Template):
            if len(i.params) > 0:
                ret += remove_style(i.params[0].value, strip_wikilink)
        elif isinstance(i, mwp.nodes.wikilink.Wikilink):
            if strip_wikilink:
                ret += remove_style(i.title, strip_wikilink)
            else:
                ret += str(i)
        else:
            ret += str(i)
    return ret


def remove_html(str):
    soup = BeautifulSoup(str, features="html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    return soup.get_text()


def parse_moe(val):
    # print(val.nodes)
    ret = []
    if isinstance(val.get(0), mwp.nodes.template.Template):
        val = val.get(0)
        # assert conv(str(val.name)) == '萌点'
        for j in val.params:
            attr = multisplit(j.value)[0]
            ret.append(conv(attr))
    else:
        l = multisplit(str(val))
        for i in l:
            code = mwp.parse(i)
            ll = code.filter_wikilinks()
            if len(ll) == 0:
                ret.append(conv(str(i).strip()))
            else:
                ret.append(conv(str(ll[0].title).strip()))
    return unique(ret)


def parse_image_tab(val):
    global bar
    # print(val)
    if isinstance(val, mwp.nodes.wikilink.Wikilink):
        return [{"alt": "", "url": val.title.strip()}]
    ret = []
    val = val.filter_templates()
    if len(val) == 0:
        return []
    val = val[0]
    bt = "bt"
    tab = "tab"
    if str(val.name).lower() == "tabs/core":
        bt = "label"
        tab = "text"
    for i in range(1, 100):
        tmp = {}
        if val.has(bt + str(i)):
            tmp["alt"] = remove_html(remove_style(val.get(bt + str(i)).value)).strip()
            vals = val.get(tab + str(i)).value
            for j in vals.filter_templates(recursive=False):
                if j.name == "到pixiv" or j.name == "lj":
                    continue
                # assert j.name == "图片外链"
                if j.name == "图片外链":
                    tmp["url"] = j.params[0].strip()
            for j in vals.filter_wikilinks(recursive=False):
                tmp["url"] = j.title.strip()
            if "url" not in tmp:
                t = str(vals).strip()
                bar.write("malformed image url: " + t)
                if t.startswith("http"):
                    tmp["url"] = t
        else:
            break
        if "url" in tmp:
            ret.append(tmp)
    # print(ret)
    return ret


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


def parse(name):
    cache_name = gen_cache_name(name)
    cache_name = f'raw/{cache_name}.txt'
    if os.path.exists(cache_name):
        # print('cache hit: '+cache_name)
        wikitext = open(cache_name, encoding="utf-8").read()
    else:
        return None
    wikicode = mwp.parse(wikitext)
    try:
        for i in wikicode.filter_templates(recursive=False):
            if len(i.params) < 3:
                continue
            t = i.name
            params = list(map(lambda x: str(x.name).strip(), i.params))
            if (
                "人物信息" in t
                or '角色信息' in t
                or "替身信息" in t
                or '信息栏' in t
                or '宠物信息' in t
                or '基本信息' in t
                or 'Infobox' in t
                or t == 'FlowerKnightGirl'
                or t == 'PvZ2植物'
                or '姓名' in params
                or '本名' in params
                or '名字' in params
            ):
                # print(i)
                char = {}
                char["title"] = name
                # char["pageid"] = pageid
                char["image"] = []
                # char['萌点'] = []
                tmpimage = {"url": "", "alt": ""}
                for param in i.params:
                    pname = str(param.name).strip()
                    pvalue = param.value
                    match pname:
                        # case '萌点':
                        #     char['萌点'] = parse_moe(pvalue)
                        case "tab":
                            char["image"].extend(parse_image_tab(pvalue))
                        case "image":
                            tmpimage["url"] = str(pvalue).strip()
                        case "图片说明":
                            tmpimage["alt"] = remove_html(str(pvalue)).strip()
                        # case '本名':
                        #     char[pname] = str(pvalue).strip()
                        # case '别号':
                        #     names = multisplit(remove_style(pvalue).strip())
                        #     if len(names) == 0:
                        #         continue
                        #     char['别号'] = names
                        case _:
                            pvalue = str(pvalue).strip()
                            if pvalue != "":
                                char[pname] = pvalue
                if tmpimage["url"] != "":
                    char["image"].insert(0, tmpimage)
                # print(char)
                # print('\n\n\n')
                image2 = []
                for v in char["image"]:
                    url = re.sub(r"^file:", "", v["url"], flags=re.IGNORECASE)
                    url = re.sub(r"<!--.*-->", "", url)
                    url = url.strip()
                    # if url != v["url"]:
                    #     bar.write(v["url"] + "\n" + url + "\n\n")
                    v["url"] = url
                    if url != "":
                        image2.append(v)
                char["image"] = image2
                char["raw"] = str(i)
                return char
    except Exception as e:
        bar.write(name)
        # print(wikicode)
        traceback.print_exc()
        raise e
    return None


def crawl(name, bar):
    cache_name = gen_cache_name(name)
    cache_name = f'raw/{cache_name}.txt'
    if os.path.exists(cache_name):
        # bar.write(name + ' exists.')
        return
    url = "https://zh.moegirl.org.cn/index.php?title={}&action=edit".format(
        title_to_url(name)
    )
    try:
        res = safe_get(url, bar, headers=headers, cooldown=cooldown).text
        # print(res)
        soup = BeautifulSoup(res, features="html.parser")
        # print(soup)
        t = soup.find('textarea').contents[0]  # type: ignore

        open(cache_name, 'w', encoding='utf8').write(t)
    except Exception as e:
        traceback.print_exc()
        # print(soup)
    # print(t)


char_index = json.load(open("../preprocess/char_index.json", encoding="utf-8"))
with tqdm(char_index) as bar:
    for i in bar:
        bar.set_description(i)
        crawl(i, bar)

extra_info = {}
bar = tqdm(char_index)
cnt = 0
for idx, name in enumerate(bar):
    # print(name, idx, '/', len(char_index))
    try:
        p = parse(name)
        if p is not None:
            extra_info[name] = p
            cnt += 1
        else:
            bar.write(f'No output: {name}')
    except KeyboardInterrupt as e:
        break
bar.close()
print('Valid extra:', cnt)
save_json(extra_info, 'extra_info.json')
