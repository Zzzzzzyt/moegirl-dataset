import json
import os
import re
import traceback
import warnings
from bs4 import BeautifulSoup
import mwparserfromhell as mwp
from tqdm import tqdm
from bs4 import MarkupResemblesLocatorWarning

from utils.network import safe_get, title_to_url
from utils.file import load_json_or_none, save_json, chdir_project_root
from src.moegirl.crawler.mwutils import remove_style

chdir_project_root()

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module="bs4")

# base_url = "https://mobile.moegirl.org.cn"
# headers = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
#     "Connection": "keep-alive",
# "Host": base_url.replace("https://", "").replace("http://", ""),
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "none",
#     "Sec-Fetch-User": "?1",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
#     "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Windows"',
# }
# cooldown = 12

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
cooldown = 3

from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path, verbose=True)
    cookies = os.getenv("MOEGIRL_COOKIES")
    if cookies:
        print('cookies:', cookies)
        print()
        headers['Cookie'] = cookies


def extract_infobox(wikitext):
    wikicode = mwp.parse(wikitext)
    ret = []
    for i in wikicode.filter_templates(recursive=False):
        if len(i.params) < 3:
            continue
        tname = str(i.name).strip()
        params = list(map(lambda x: str(x.name).strip(), i.params))
        if (
            "人物信息" in tname
            or '角色信息' in tname
            or "替身信息" in tname
            or '信息栏' in tname
            or '宠物信息' in tname
            or '基本信息' in tname
            or 'Infobox' in tname
            or tname == 'FlowerKnightGirl'
            or tname == 'PvZ2植物'
            or '萌点' in params
            or '姓名' in params
            or '本名' in params
            or '名字' in params
            or '别名' in params
            or '声优' in params
            or '萌属性' in params
        ):
            # print(i)
            ret.append(str(i))
    return ret


def parse(raw):
    p = extract_infobox(raw)
    if len(p) > 0:
        return p
    limit = 10
    for pos in re.finditer(r'\{\{', raw):
        p = extract_infobox(raw[pos.start() :])
        if len(p) > 0:
            return p
        limit -= 1
        if limit <= 0:
            break
    root_templates = []
    cur = 0
    start = None
    for i in range(len(raw) - 1):
        if raw[i : i + 2] == '{{':
            if cur == 0:
                start = i
            cur += 1
        elif raw[i : i + 2] == '}}':
            cur -= 1
            if cur == 0:
                root_templates.append(raw[start : i + 2])
    ret = []
    for i in root_templates:
        l = i.split('\n')
        for j in range(len(l)):
            if l[j].strip().startswith('|') and '=' in l[j]:
                tmp = l[j].split('=')
                pname = tmp[0].strip()
                pvalue = '='.join(tmp[1:])
                if '{' in pname:
                    # print(pname, pvalue)
                    pname = remove_style(mwp.parse(pname))
                    # print(pname)
                l[j] = f'{pname}={pvalue}'
        t = '\n'.join(l)
        ret.extend(extract_infobox(t))
    return ret


def crawl(name, bar):
    try:
        url = base_url + "/index.php?title={}&action=edit".format(title_to_url(name))
        res = safe_get(url, bar, headers=headers, cooldown=cooldown).text
        soup = BeautifulSoup(res, features="html.parser")
        t = soup.find('textarea')
        if t is None:
            bar.write(f'No textarea found: {name}')
            if '权限错误' in res:
                bar.write(f'No permission to edit page: {name}')
                return ''
            return None
        t = t.contents[0]  # type: ignore
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        return None
    return t


char_index = json.load(open("moegirl/char_index.json", encoding="utf-8"))

extra_info = load_json_or_none('moegirl/extra_info.partial.json') or {}
bar = tqdm(char_index)
cnt = 0
cnt_valid = 0
try:
    for idx, name in enumerate(bar):
        if name in extra_info:
            cnt += 1
            if len(extra_info[name]) > 0:
                cnt_valid += 1
            continue
        bar.set_description(name)
        raw = crawl(name, bar)
        if raw is None:
            continue
        p = parse(raw)
        extra_info[name] = p
        if len(p) == 0:
            bar.write(f'No output: {name}')
        else:
            cnt_valid += 1
        cnt += 1
except KeyboardInterrupt as e:
    print('KeyboardInterrupt, saving partial results...')
finally:
    bar.close()
    save_json(extra_info, 'moegirl/extra_info.partial.json')
    if cnt == len(char_index):
        print(f'Crawl complete, valid: {cnt_valid} / {len(char_index)}')
        save_json(extra_info, 'moegirl/extra_info.json')
