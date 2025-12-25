import json
import traceback
from typing import Optional
import warnings
import mwparserfromhell as mwp
from tqdm import tqdm
from bs4 import MarkupResemblesLocatorWarning
import re

from utils.file import save_json, save_json_pretty, chdir_project_root
from moegirl.crawler_extra.mwutils import *

chdir_project_root()

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module="bs4")
# warnings.simplefilter("always", UserWarning)


def parse_tab_image(val, prefix=""):
    ret = []
    bt = "bt"
    tab = "tab"
    if str(val.name).lower() == "tabs/core":
        bt = "label"
        tab = "text"
    for i in range(1, 100):
        tmp = {}
        if val.has(bt + str(i)):
            alt = ''.join(extract_text(val.get(bt + str(i))))
            tmp["alt"] = prefix + alt
            if not val.has(tab + str(i)):
                warnings.warn("missing tab for image alt: " + alt)
                continue
            vals = val.get(tab + str(i)).value
            terminate = False
            for j in vals.filter_templates(recursive=False):
                tname = j.name.strip().lower()
                if tname == "到pixiv" or tname == "lj":
                    continue
                # assert j.name == "图片外链"
                if tname == 'tabs':
                    ret.extend(parse_tab_image(j, prefix=prefix + alt + "/"))
                    terminate = True
                    break
                elif tname == "图片外链" or tname == '阴影' or tname == 'pichover':
                    tmp["url"] = j.params[0].value.strip()
                elif tname == 'image-clip':
                    tmp["url"] = j.get('img').value.strip()
                elif tname == 'image':
                    tmp["url"] = j.get('图片').value.strip()
            if terminate:
                continue
            for j in vals.filter_wikilinks(recursive=True):
                tmp["url"] = j.title.strip()
            if "url" not in tmp:
                t = str(vals).strip()
                if t == '':
                    continue
                warnings.warn("malformed image url: " + t)
                if t.startswith("http"):
                    tmp["url"] = t
        else:
            break
        if "url" in tmp:
            ret.append(tmp)
    return ret


def parse_image(result, pname, pvalue):
    val = mwp.parse(remove_html(str(pvalue)))

    # print(val)
    if isinstance(val, mwp.nodes.wikilink.Wikilink) or pname.lower() == 'image':
        if not isinstance(val, mwp.nodes.wikilink.Wikilink):
            url = str(val).strip()
            if url == '':
                return
        else:
            url = val.title.strip()
        if 'image' not in result:
            result['image'] = [{"alt": "", "url": None}]
        else:
            assert isinstance(result['image'], list)
            if len(result['image']) > 1 or (
                len(result['image']) == 1 and result['image'][0]["url"] is not None
            ):
                warnings.warn('warning: single image while tabs present')
                return
            if len(result['image']) == 0:
                result['image'].append({"alt": "", "url": None})

        if not url.startswith('File:'):
            url = 'File:' + url
        result['image'][0]["url"] = url
        return

    ret = []
    val = val.filter_templates()
    if len(val) == 0:
        return
    val = val[0]
    res = parse_tab_image(val)
    if len(res) > 0:
        result['image'] = res


def parse_image_alt(result, pname, pvalue):
    val = conv(remove_html(str(pvalue))).strip()
    if val == '':
        return
    if 'image' not in result or len(result['image']) == 0:
        # warnings.warn("warning: image not present but alt present")
        return
    if len(result['image']) > 1:
        # warnings.warn("warning: multiple images but single image alt present")
        return
    if result['image'][0]['alt'] != "":
        # warnings.warn("warning: image alt already present")
        return
    result['image'][0]['alt'] = val


def parse_moe(result, pname, pvalue):
    global attrs
    val = conv(remove_html(str(pvalue)))
    # print(val)
    res = extract_text(mwp.parse(val), strict_root=True, aggressive=True, wikilink=True)
    ret = []
    for i in res:
        s = i.strip()
        if len(s) == 0:
            continue
        s = lstrip_cat(s)
        s2 = strip_parenthesis(s)
        if s not in attrs and s2 in attrs:
            ret.append(s2)
        else:
            ret.append(s)
    result['萌点'] = unique(result.get('萌点', []) + ret)


def parse_name(result, pname, pvalue):
    root = mwp.parse(conv(remove_html(str(pvalue))))
    ret = extract_text(root, multiline_mode=True)
    # ret = []
    # cur = ""
    # for i in ret2:
    #     cur += i
    #     if i.endswith("\n"):
    #         cur = cur.rstrip()
    #         ret.extend(multisplit(cur, "/\\"))
    #         cur = ""
    # ret.append(cur)
    ret = map(strip_parenthesis, ret)
    ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、"), ret)
    ret = map(
        lambda x: x.replace('zhhans:', '').replace('zhhk:', '').replace('zhtw:', ''),
        ret,
    )
    ret = filter(
        lambda x: len(x) > 0 and x != '未知' and x != '不明' and '本名不明' not in x,
        ret,
    )
    ret = result.get("本名", []) + list(ret)
    ret = unique(ret)
    result["本名"] = ret


def parse_alt(result, pname, pvalue):
    root = mwp.parse(conv(remove_html(str(pvalue))))
    ret = extract_text(root, multiline_mode=True)
    # ret = []
    # for i in res:
    #     s = i.strip()
    #     if len(s) == 0:
    #         continue
    #     s = strip_parenthesis(s)
    #     ret.extend(multisplit(s, "/\\"))
    ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、"), ret)
    ret = filter(lambda x: len(x) > 0, ret)
    ret = result.get("别名", []) + list(ret)
    ret = unique(ret)
    result["别名"] = ret


height_re1 = re.compile(r"(\d+(\.\d+){0,2})\s?(cm|厘米)", flags=re.IGNORECASE)
height_re2 = re.compile(r"(\d+(\.\d+){0,2})\s?(m|米)", flags=re.IGNORECASE)
height_re3 = re.compile(r"(\d+(\.\d+)?)", flags=re.IGNORECASE)


def parse_height(result, pname, pvalue):
    val = conv(str(pvalue))
    val = val.lower().strip().replace(",", "")
    try:
        s = int(val)
        if s < 10:
            s *= 100
        return [s]
    except Exception as e:
        pass
    try:
        if val.endswith("cm") or val.endswith("厘米"):
            return [int(val[:-2])]
    except Exception as e:
        pass
    try:
        if val.endswith("cm") or val.endswith("厘米"):
            return [float(val[:-2])]
    except Exception as e:
        pass
    try:
        if val.endswith("m") or val.endswith("米"):
            return [float(val[:-1]) * 100]
    except Exception as e:
        pass
    try:
        s = float(val)
        if s < 10:
            s *= 100
        return [s]
    except Exception as e:
        pass
    val = remove_html(val)
    # val = val.replace(' ', '')
    ret = []
    for i in height_re1.finditer(val):
        s = i.groups()[0]
        if "." in s:
            ret.append(float(s))
        else:
            ret.append(int(s))
    if len(ret) == 0:
        for i in height_re2.finditer(val):
            s = i.groups()[0]
            if "." in s:
                ret.append(float(s) * 100)
            else:
                ret.append(int(s) * 100)
    if len(ret) == 0:
        for i in height_re3.finditer(val):
            s = i.groups()[0]
            if "." in s:
                tmp = float(s)
            else:
                tmp = int(s)
            if tmp < 10:
                tmp *= 100
            ret.append(tmp)
    if len(ret) > 0:
        for i in ret:
            if i >= 20 and i <= 300:
                result["身高"] = i


weight_re1 = re.compile(r"(\d+(\.\d+)?)\s?(kg|千克|公斤)", flags=re.IGNORECASE)
weight_re2 = re.compile(r"(\d+(\.\d+)?)\s?斤", flags=re.IGNORECASE)
weight_re3 = re.compile(r"(\d+(\.\d+)?)\s?(t|吨)", flags=re.IGNORECASE)
weight_re4 = re.compile(r"(\d+(\.\d+)?)", flags=re.IGNORECASE)


def safediv(a, b):
    if type(a) == int and type(b) == int and a % b == 0:
        return a // b
    return a / b


def parse_weight(result, pname, pvalue):
    val = conv(str(pvalue))
    val = val.lower().strip().replace(",", "")
    try:
        s = int(val)
        return [s]
    except Exception as e:
        pass
    try:
        s = float(val)
        return [s]
    except Exception as e:
        pass
    try:
        if val.endswith("kg") or val.endswith("千克") or val.endswith("公斤"):
            return [int(val[:-2])]
    except Exception as e:
        pass
    try:
        if val.endswith("kg") or val.endswith("千克") or val.endswith("公斤"):
            return [float(val[:-2])]
    except Exception as e:
        pass
    try:
        if val.endswith("斤"):
            return [safediv(int(val[:-1]), 2)]
    except Exception as e:
        pass
    try:
        if val.endswith("斤"):
            return [float(val[:-1]) / 2]
    except Exception as e:
        pass
    try:
        if val.endswith("t") or val.endswith("吨"):
            return [float(val[:-2]) * 1000]
    except Exception as e:
        pass

    val = remove_html(val).strip()
    ret = []
    for i in weight_re1.finditer(val):
        s = i.groups()[0]
        if "." in s:
            ret.append(float(s))
        else:
            ret.append(int(s))
    if len(ret) == 0:
        for i in weight_re2.finditer(val):
            s = i.groups()[0]
            if "." in s:
                tmp = float(s) / 2
            else:
                tmp = safediv(int(s), 2)
            ret.append(tmp)
    if len(ret) == 0:
        for i in weight_re3.finditer(val):
            s = i.groups()[0]
            if "." in s:
                tmp = float(s)
            else:
                tmp = int(s)
            tmp *= 1000
            ret.append(tmp)
    if len(ret) == 0:
        m = weight_re4.match(val)
        if m:
            s = m.groups()[0]
            if "." in s:
                tmp = float(s)
            else:
                tmp = int(s)
            ret.append(tmp)
    if len(ret) > 0:
        if ret[0] >= 20 and ret[0] <= 300:
            result["体重"] = ret[0]
        else:
            mx = max(ret)
            if mx >= 20 and mx <= 300:
                result["体重"] = mx
            else:
                mi = max(ret)
                if mi >= 20 and mi <= 300:
                    result["体重"] = mi
                else:
                    result["体重"] = ret[0]


age_re1 = re.compile(r"(\d+)岁", flags=re.IGNORECASE)
age_re2 = re.compile(r"(\d+)", flags=re.IGNORECASE)


def parse_age(result, pvalue, raw):
    val = conv(str(pvalue))
    val = val.lower().strip().replace(",", "")
    try:
        s = int(val)
        return [s]
    except Exception as e:
        pass
    try:
        if val.endswith("岁"):
            return [int(val[:-1])]
    except Exception as e:
        pass

    val = remove_html(val)
    ret = []
    for i in age_re1.finditer(val):
        s = i.groups()[0]
        ret.append(int(s))
    if len(ret) == 0:
        for i in weight_re2.finditer(val):
            s = i.groups()[0]
            ret.append(int(s))
    if len(ret) > 0:
        if ret[0] <= 100:
            result["年龄"] = ret[0]
        else:
            mi = min(ret)
            if mi <= 100:
                result["年龄"] = mi
            else:
                mx = max(ret)
                if mx <= 100:
                    result["年龄"] = mx
                else:
                    result["年龄"] = ret[0]


bwh_re1 = re.compile(r"B[:：]?(\d+).*?W[:：]?(\d+).*?H[:：]?(\d+)", flags=re.IGNORECASE)
bwh_re2 = re.compile(r"B[:：]?(\d+)", flags=re.IGNORECASE)
bwh_re3 = re.compile(r"(\d+).*?(\d+).*?(\d+)", flags=re.IGNORECASE)


def parse_bwh(result, pname, pvalue):
    val = conv(str(pvalue))

    ret: list[Optional[int]] = [None, None, None]
    for i in bwh_re1.finditer(val):
        ret[0] = int(i.groups()[0])
        ret[1] = int(i.groups()[1])
        ret[2] = int(i.groups()[2])
    if ret[0] is not None:
        result["三围"] = ret
        return

    for i in bwh_re2.finditer(val):
        ret[0] = int(i.groups()[0])
    if ret[0] is not None:
        result["三围"] = ret
        return
    # print(val)
    val = "".join(extract_text(mwp.parse(val)))
    # print(val)
    for i in bwh_re3.finditer(val):
        ret[0] = int(i.groups()[0])
        ret[1] = int(i.groups()[1])
        ret[2] = int(i.groups()[2])
    # print(ret)
    # print()
    if ret[0] is not None:
        result["三围"] = ret


def chain_replace(s, pattern, sub=""):
    if type(pattern) == str:
        pattern = list(pattern)
    for i in pattern:
        s = s.replace(i, sub)
    return s


def remove_lang(s):
    return chain_replace(s, ["[中]", "[日]", "[英]"])


def parse_seyuu_final(val):
    ret = extract_text(mwp.parse(val))
    ret2 = []
    for idx, i in enumerate(ret):
        if idx != len(ret) - 1 and ret[idx + 1] == '》':
            continue
        if i.endswith(':') or i.endswith('：') or i.endswith('】') or i.endswith(']'):
            continue
        if i == '不明' or i == '无':
            continue
        if i.startswith('{{') and i.endswith('}}'):
            ret2.append(i.split('|')[-1])
        elif '/' in i:
            ret2.extend(i.split('/'))
        elif '&' in i:
            ret2.extend(i.split('&'))
        else:
            ret2.append(i)
    ret = ret2
    ret = map(lambda x: lstrip_cat(x.strip("→").strip("-")), ret)
    ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、&；;"), ret)
    ret = filter(
        lambda x: x not in ['PV', 'CM', 'OVA', 'TV']
        and '电影' not in x
        and '动画' not in x,
        ret,
    )
    ret = filter(lambda x: len(x) > 0, ret)
    ret = list(ret)
    ret = unique(ret)
    return ret


def parse_seyuu(result, pname, pvalue):
    val = conv(remove_html(str(pvalue))).strip()
    if "<" in val or "{" in val or "[" in val or "," in val:
        val = strip_parenthesis(val)
        val = remove_lang(val)
        ret = parse_seyuu_final(val)
        result["声优"] = unique(result.get("声优", []) + ret)
    else:
        result["声优"] = unique(result.get("声优", []) + [strip_parenthesis(val)])


def parse_multiple_seyuu(result, pname, pvalue):
    val = conv(remove_html(str(pvalue))).strip()
    val = strip_parenthesis(val)
    val = remove_lang(val)

    if val.lower().startswith("{{cate") or val.startswith("{{分类"):
        ret = []
        code = mwp.parse(val)
        code = code.filter_templates()
        for i in code:
            if i.name.lower() == "cate" or i.name == "分类":
                for j in i.params[1:]:
                    ret.append(str(j.value))
        result["声优"] = unique(result.get("声优", []) + ret)
        return

    ret = parse_seyuu_final(val)
    result["声优"] = unique(result.get("声优", []) + ret)


hair_color_attr = [
    "黑发",
    "金发",
    "蓝发",
    "棕发",
    "银发",
    "红发",
    "紫发",
    "橙发",
    "绿发",
    "粉发",
    "双色发",
    "彩虹发",
    "多色发",
    "阴阳发",
]
eye_color_attr = [
    "黑瞳",
    "金瞳",
    "蓝瞳",
    "棕瞳",
    "灰瞳",
    "红瞳",
    "紫瞳",
    "橙瞳",
    "绿瞳",
    "粉瞳",
    "白瞳",
    "异色瞳",
    "渐变瞳",
    "彩虹瞳",
]


def parse_color(val):
    val = conv(val)
    val = strip_parenthesis(val)
    val = "".join(extract_text(mwp.parse(val)))
    ret = multisplit(val, "/→+-~左右或,，、 ")
    ret = map(lambda x: x.rstrip("瞳").rstrip("发") if len(x) <= 4 else x, ret)
    ret = map(lambda x: x if '异色' in x else x.rstrip('色'), ret)
    ret = filter(lambda x: len(x) > 0, ret)
    ret = list(ret)
    ret = unique(ret)
    return ret


def parse_eye_color(result, pname, pvalue):
    colors = parse_color(conv(remove_html(str(pvalue))))
    if len(colors) > 0:
        result['瞳色'] = colors


def parse_hair_color(result, pname, pvalue):
    colors = parse_color(conv(remove_html(str(pvalue))))
    if len(colors) > 0:
        result['发色'] = colors


def parse_blood(result, pname, pvalue):
    val = remove_html(str(pvalue))
    val = val.split("\n")[0]
    val = conv(val).strip()
    val = val.upper()
    if "稀有" in val:
        result["血型"] = "稀有"
        return
    if len(val) <= 4:
        val = val.rstrip("血").rstrip("型")
    if (
        val == "未知"
        or val == "?"
        or val == "？"
        or val == "秘密"
        or val == "不明"
        or val == ""
    ):
        return
    result["血型"] = val


birthday_re = re.compile(r'((\d+)年)?((\d+)月)?((\d+)[日号])?')
birthday_re2 = re.compile(r'((\d+)[/.])?(\d+)[/.](\d+)')


def parse_birthday(result, pname, pvalue):
    val = mwp.parse(conv(remove_html(str(pvalue))))

    text = None
    for i in val.filter_templates(recursive=True):
        tname = i.name.strip().lower()
        if tname == '生日' or tname == 'birthday':
            if text is not None:
                warnings.warn('multiple birthday template: ' + str(i))
                break
            tmp = []
            for j in i.params:
                if j.name.strip().lower() == 'ft':
                    continue
                tmp.append(str(j.value))
            if len(tmp) == 1:
                text = tmp[0]
            elif len(tmp) == 2:
                text = tmp[0] + '月' + tmp[1] + '日'
            else:
                warnings.warn('malformed birthday template: ' + str(i))
        elif tname == 'birth date' or tname == 'birth date and age':
            y = i.params[0].value.strip()
            m = i.params[1].value.strip()
            d = i.params[2].value.strip()
            text = f"{y}年{m}月{d}日"
        else:
            pass

    if text is None:
        text = ''.join(extract_text(pvalue)).strip()

    if '不详' in text or '未知' in text:
        return

    for m in birthday_re.finditer(text):
        ret: list[Optional[int]] = [None, None, None]
        g = m.groups()
        if g[1] is None and g[3] is None and g[5] is None:
            continue
        if g[1]:
            ret[0] = int(g[1])
        if g[3]:
            ret[1] = int(g[3])
        if g[5]:
            ret[2] = int(g[5])
        # print(val)
        # print(ret)
        # print()
        # if ret[1] is None or ret[2] is None:
        #     pass
        result['生日'] = ret
    if '生日' not in result:
        ret: list[Optional[int]] = [None, None, None]
        m = birthday_re2.match(text)
        if m:
            g = m.groups()
            if g[1] is None and g[3] is None and g[5] is None:
                return
            if g[1]:
                ret[0] = int(g[1])
            if g[2]:
                ret[1] = int(g[2])
            if g[3]:
                ret[2] = int(g[3])
            # print(val)
            # print(ret)
            # print()
            result['生日'] = ret


zodiacs = set(
    [
        "白羊",
        "金牛",
        "双子",
        "巨蟹",
        "狮子",
        "处女",
        "天秤",
        "天蝎",
        "射手",
        "摩羯",
        "水瓶",
        "双鱼",
    ]
)


def parse_zodiac(result, pname, pvalue):
    val = extract_text(mwp.parse(conv(remove_html(str(pvalue)))))
    ret = []
    for i in val:
        i = i.rstrip("座")
        if i == '室女':
            i = '处女'
        if i == '人马':
            i = '射手'
        if i == '宝瓶':
            i = '水瓶'
        if i in zodiacs:
            ret.append(i)
    if len(ret) > 0:
        result['星座'] = unique(result.get('星座', []) + ret)


# info_key_stats = {}
# info_name_stats = {}


# pyright: reportAttributeAccessIssue=none
def parse(infobox):
    wikicode = mwp.parse(infobox).get(0)
    result = {"本名": [], "别名": [], "声优": []}
    tname = str(wikicode.name).strip()
    # info_name_stats.setdefault(tname, 0)
    # info_name_stats[tname] += 1
    for param in wikicode.params:
        pname = str(param.name).strip()
        pvalue = param.value
        if str(pvalue).strip() == '':
            continue
        try:
            # info_key_stats.setdefault(pname, 0)
            # info_key_stats[pname] += 1
            if (
                pname == '本名'
                or pname == '译名'
                or pname == '中文名'
                or pname == '日文名'
                or pname == '英文名'
                or pname == '韩文名'
                or pname == '罗马字'
            ):
                parse_name(result, pname, pvalue)
            elif (
                pname == '别名' or pname == '别称' or pname == '别号' or pname == '昵称'
            ):
                parse_alt(result, pname, pvalue)
            elif pname == 'image' or pname == 'tabs':
                parse_image(result, pname, pvalue)
            elif pname == '图片说明':
                parse_image_alt(result, pname, pvalue)
            elif pname == '瞳色' or pname == '多种瞳色':
                parse_eye_color(result, pname, pvalue)
            elif pname == '发色' or pname == '多种发色':
                parse_hair_color(result, pname, pvalue)
            elif pname == '身高':
                parse_height(result, pname, pvalue)
            elif pname == '体重':
                parse_weight(result, pname, pvalue)
            elif pname == '三围':
                parse_bwh(result, pname, pvalue)
            elif pname == '血型':
                parse_blood(result, pname, pvalue)
            elif pname == '萌点' or pname == '属性' or pname == '萌属性':
                parse_moe(result, pname, pvalue)
            elif pname == '年龄':
                parse_age(result, pvalue, pvalue)
            elif pname == '生日':
                parse_birthday(result, pname, pvalue)
            elif (
                pname == '声优'
                or pname == '配音'
                or pname == '日语配音'
                or pname == '汉语配音'
                or pname == '韩语配音'
            ):
                parse_seyuu(result, pname, pvalue)
            elif pname == '多位声优':
                parse_multiple_seyuu(result, pname, pvalue)
            elif pname == '星座':
                parse_zodiac(result, pname, pvalue)
        except Exception as e:
            print('Error parsing', pname, 'in', tname)
            traceback.print_exc()
    return result


attrs = json.load(open("moegirl/preprocess/attr_index.json", encoding="utf-8"))
attrs = set(attrs)
extra = json.load(open("moegirl/crawler_extra/extra_info.json", encoding="utf-8"))
out = {}

idx = 0
for k, v in extra.items():
    idx += 1
    # print(f"{idx}/{len(extra)} {k}")
    assert len(v) > 0
    # if len(v) > 1:
    #     print('Multiple infoboxes for', k)
    #     for i in v:
    #         print(repr(i[:10]), end=' ')
    #     print()
    infobox = v[0]
    out[k] = parse(infobox)

# for k, v in sorted(info_key_stats.items(), key=lambda x: x[1], reverse=True)[:100]:
#     print(k, v)
# for k, v in sorted(info_name_stats.items(), key=lambda x: x[1], reverse=True)[:100]:
#     print(k, v)

print(f'Valid size: {len(out)} / {len(extra)}')
save_json(out, "moegirl/crawler_extra/extra_processed.json")
