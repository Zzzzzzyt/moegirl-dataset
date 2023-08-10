import json
import warnings
from bs4 import BeautifulSoup
import mwparserfromhell as mwp
import opencc
from tqdm import tqdm
from bs4 import MarkupResemblesLocatorWarning
import re

warnings.filterwarnings(
    "ignore", category=MarkupResemblesLocatorWarning, module="bs4")
warnings.simplefilter("always", UserWarning)


def save_json(data, path):
    json.dump(
        data,
        open(path, "w", encoding="utf-8"),
        ensure_ascii=False,
        separators=(",", ":"),
    )


converter = opencc.OpenCC("t2s.json")


def conv(t):
    return converter.convert(t)


def unique(l):
    ret = []
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret


def multisplit(str, sp=",，、\n "):
    ret = []
    cur = ""
    for i in str:
        if i in sp:
            ret.append(cur.strip())
            cur = ""
        else:
            cur += i
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


def remove_html(str, remove_ref=True):
    soup = BeautifulSoup(str, features="html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    if remove_ref:
        for s in soup.select("ref"):
            s.extract()
    return soup.get_text()


def calc_zodiac(month, day):
    # who tf made this template?????
    match (month):
        case 1:
            if day > 19:
                return "水瓶座"
            else:
                return "摩羯座"
        case 2:
            if day > 18:
                return "双鱼座"
            else:
                return "水瓶座"
        case 3:
            if day > 20:
                return "白羊座"
            else:
                return "双鱼座"
        case 4:
            if day > 19:
                return "金牛座"
            else:
                return "白羊座"
        case 5:
            if day > 20:
                return "双子座"
            else:
                return "金牛座"
        case 6:
            if day > 21:
                return "巨蟹座"
            else:
                return "双子座"
        case 7:
            if day > 22:
                return "狮子座"
            else:
                return "巨蟹座"
        case 8:
            if day > 22:
                return "处女座"
            else:
                return "狮子座"
        case 9:
            if day > 22:
                return "天秤座"
            else:
                return "处女座"
        case 10:
            if day > 23:
                return "天蝎座"
            else:
                return "天秤座"
        case 11:
            if day > 20:
                return "射手座"
            else:
                return "天蝎座"
        case 12:
            if day > 21:
                return "摩羯座"
            else:
                return "射手座"


def extract_text(
    code, strict_root=False, agressive=False, wikilink=False, multiline_mode=False
):
    ret = []
    try:
        if isinstance(code, mwp.nodes.template.Template):
            name = code.name.lower().strip()
            if name == "萌点":
                for i in code.params:
                    ret.append(multisplit(i.value)[0])
            elif (
                name == "cate"
                or name == "黑幕"
                or name == "heimu"
                or name == "假黑幕"
                or name == "jk"
                or name == "胡话"
                or name == "注解"
                or name == "lj"
                or name == "彩幕"
                or name == "彩色幕"
                or name == "模糊"
                or name == "文字模糊"
                or name == "dead"
                or name == "small"
                or name == "citation needed"
                or name == "示亡"
                or name.startswith("lang-")
                or name == "font"
                or name == "注"
                or name == "ref"
                or name == "ljr"
                or name == ""
                or name == "黑雾"
                or name == "block"
                or name == "texthover"
                or name == ""
                or name.startswith("photrans")
                or name == "魔女文字"
                or name.startswith("文字描边")
                or name == "writing-mode"
            ):
                if len(code.params) > 0:
                    ret.extend(extract_text(code.get(1).value))
                else:
                    warnings.warn(
                        "template "
                        + name
                        + " has fewer params than expected:\n"
                        + str(code)
                    )
            elif (
                name == "切换显示"
                or name == "color"
                or name == "coloredlink"
                or name == "lang"
                or name == "gradient_text"
            ):
                ret.extend(extract_text(code.get(2).value))
            elif name == "ruby" or name == "rubyh":
                ret.extend(extract_text(code.get(1).value))
                if agressive:
                    ret.extend(extract_text(code.get(2).value))
            elif name == "username" or name == "0" or name == "fact":
                if code.has(1):
                    ret.extend(extract_text(code.get(1).value))
            elif name == "rubya":
                for i in code.params:
                    if i.name == "lang":
                        continue
                    ret.append(multisplit(str(i.value))[0])
            elif name == "hide":
                if code.has(1) and code.get(1) == "show":
                    if code.has(2):
                        ret.extend(extract_text(code.get(2).value))
                    else:
                        ret.extend(extract_text(code.get("内容").value))
                else:
                    if code.has(1):
                        ret.extend(extract_text(code.get(1).value))
                    else:
                        ret.extend(extract_text(code.get("内容").value))
            elif name == "日本人名" or name == "jpn":
                tmp = ""
                if code.has(1):
                    tmp += "".join(extract_text(code.get(1).value))
                if code.has(3):
                    tmp += "".join(extract_text(code.get(3).value))
                ret.append(tmp)
            elif name == "gup" or name == "少战":
                if code.has(2):
                    ret.extend(extract_text(code.get(2).value))
                else:
                    ret.extend(extract_text(code.get(1).value))
            elif name == "link":
                for i in code.params:
                    if i.name == "char":
                        continue
                    ret.extend(extract_text(i.value))
            elif name == "toggle" or name == "toggle2":
                ret.extend(extract_text(code.get("content").value))
            elif name == "hideinline":
                if code.has_param("内容"):
                    ret.extend(extract_text(code.get("内容").value))
                else:
                    if code.get(1).value == "show":
                        ret.extend(extract_text(code.get(3).value))
                    else:
                        ret.extend(extract_text(code.get(2).value))
            elif name == "文字模糊":
                ret.extend(extract_text(code.get(1).value))
            elif name == "astrology":
                ret.append(
                    calc_zodiac(
                        int(str(code.get(1).value)), int(
                            str(code.get(2).value))
                    )
                )
            elif (
                name == "注释"
                or name == "refn"
                or name == "#invoke:housamo"
                or name == "ps"
                or name == "note"
                or name == "来源请求"
                or name == "w"
                or name == "·"
                or name == "bilibililink"
                or name == "pg"
                or name == "zh-hant"
                or name == "regionicon"
                or name == "图片外链"
                or name == "color_block/wl"
            ):
                pass
            elif len(code.params) == 0:
                pass
            else:
                warnings.warn("Unkown template name: " +
                              name + "\n" + str(code))
        elif isinstance(code, mwp.nodes.wikilink.Wikilink):
            if wikilink or code.text is None:
                ret.append(str(code.title).strip())
            else:
                ret.append(str(code.text).strip())
        elif isinstance(code, mwp.wikicode.Wikicode):
            for idx, i in enumerate(code.nodes):
                if isinstance(i, mwp.nodes.text.Text):
                    l = multisplit(i.value, ",，、\n")
                    if strict_root:
                        if idx != 0:
                            if len(l) > 1:
                                l = l[1:]
                            else:
                                continue
                        if idx != len(code.nodes) - 1:
                            if len(l) > 1:
                                l = l[:-1]
                            else:
                                continue
                    for j in l:
                        ret.append(j.strip())
                elif isinstance(i, mwp.nodes.tag.Tag):
                    if i.tag != "ref" and i.tag != "br":
                        ret.extend(extract_text(i.contents))
                    if i.tag == "br" and multiline_mode:
                        ret.append("\n")
                else:
                    ret.extend(extract_text(i))
        elif isinstance(code, mwp.nodes.text.Text):
            l = multisplit(code.value, ",，、\n")
            for i in l:
                ret.append(i.strip())
        elif isinstance(code, mwp.nodes.tag.Tag):
            if code.tag != "ref" and code.tag != "br":
                ret.extend(extract_text(code.contents))
            if code.tag == "br" and multiline_mode:
                ret.append("\n")
    except Exception as e:
        print(code)
        raise e
    ret = list(filter(lambda x: len(x) > 0, ret))
    return ret


strip_parenthesis_re = re.compile(r"[\(（][^()（）]*?[\)）]")


def strip_parenthesis(s: str):
    nb_rep = 1
    while nb_rep:
        s, nb_rep = strip_parenthesis_re.subn("", s)
    return s


def lstrip_cat(str):
    return re.sub("^(Category:|分类:)", "", str, flags=re.IGNORECASE)


def parse_moe(val, raw):
    global attrs
    val = conv(remove_html(val))
    # print(val)
    res = extract_text(mwp.parse(val), strict_root=True,
                       agressive=True, wikilink=True)
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
    ret = unique(ret)
    return ret


def parse_name(val, raw):
    root = mwp.parse(val)
    ret2 = extract_text(root, multiline_mode=True)
    ret = []
    cur = ""
    for i in ret2:
        cur += i
        if i.endswith("\n"):
            cur = cur.rstrip()
            ret.extend(multisplit(cur, "/\\"))
            cur = ""
    ret.append(cur)
    ret = map(strip_parenthesis, ret)
    ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、"), ret)
    ret = filter(lambda x: len(x) > 0, ret)
    ret = list(ret)
    ret = unique(ret)
    # print(val)
    # print(ret2)
    # print(ret)
    # print()
    return ret


def parse_alt(val, raw):
    val = conv(remove_html(val))
    res = extract_text(mwp.parse(val))
    ret = []
    for i in res:
        s = i.strip()
        if len(s) == 0:
            continue
        s = strip_parenthesis(s)
        ret.extend(multisplit(s, "/\\"))
    ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、"), ret)
    ret = filter(lambda x: len(x) > 0, ret)
    ret = list(ret)
    ret = unique(ret)
    return ret


height_re1 = re.compile(r"(\d+(\.\d+){0,2})\s?(cm|厘米)", flags=re.IGNORECASE)
height_re2 = re.compile(r"(\d+(\.\d+){0,2})\s?(m|米)", flags=re.IGNORECASE)
height_re3 = re.compile(r"(\d+(\.\d+)?)", flags=re.IGNORECASE)


def parse_height(val, raw):
    val = conv(val)
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
    return ret


weight_re1 = re.compile(r"(\d+(\.\d+)?)\s?(kg|千克|公斤)", flags=re.IGNORECASE)
weight_re2 = re.compile(r"(\d+(\.\d+)?)\s?斤", flags=re.IGNORECASE)
weight_re3 = re.compile(r"(\d+(\.\d+)?)\s?(t|吨)", flags=re.IGNORECASE)
weight_re4 = re.compile(r"(\d+(\.\d+)?)", flags=re.IGNORECASE)


def safediv(a, b):
    if type(a) == int and type(b) == int and a % b == 0:
        return a // b
    return a / b


def parse_weight(val, raw):
    val = conv(val)
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

    val = remove_html(val)
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
        for i in weight_re4.finditer(val):
            s = i.groups()[0]
            if "." in s:
                tmp = float(s)
            else:
                tmp = int(s)
            ret.append(tmp)
    return ret


age_re1 = re.compile(r"(\d+)岁", flags=re.IGNORECASE)
age_re2 = re.compile(r"(\d+)", flags=re.IGNORECASE)


def parse_age(val, raw):
    val = conv(val)
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
    return ret


bwh_re1 = re.compile(
    r"B[:：]?(\d+).*?W[:：]?(\d+).*?H[:：]?(\d+)", flags=re.IGNORECASE)
bwh_re2 = re.compile(r"B[:：]?(\d+)", flags=re.IGNORECASE)
bwh_re3 = re.compile(r"(\d+).*?(\d+).*?(\d+)", flags=re.IGNORECASE)


def parse_bwh(val, raw):
    ret = [None, None, None]
    for i in bwh_re1.finditer(val):
        ret[0] = int(i.groups()[0])
        ret[1] = int(i.groups()[1])
        ret[2] = int(i.groups()[2])
    if ret[0] is not None:
        return ret
    for i in bwh_re2.finditer(val):
        ret[0] = int(i.groups()[0])
    if ret[0] is not None:
        return ret
    # print(val)
    val = "".join(extract_text(mwp.parse(val)))
    # print(val)
    for i in bwh_re3.finditer(val):
        ret[0] = int(i.groups()[0])
        ret[1] = int(i.groups()[1])
        ret[2] = int(i.groups()[2])
    # print(ret)
    # print()
    return ret


def chain_replace(s, pattern, sub=""):
    if type(pattern) == str:
        pattern = list(pattern)
    for i in pattern:
        s = s.replace(i, sub)
    return s


def remove_lang(s):
    return chain_replace(s, ["[中]", "[日]", "[英]"])


def parse_seyuu(val, raw):
    val = val.strip()
    val = conv(val)
    if "<" in val or "{" in val or "[" in val or "," in val:
        val = strip_parenthesis(val)
        val = remove_lang(val)
        ret = extract_text(mwp.parse(val))
        ret = map(
            lambda x: lstrip_cat(x.strip("→").strip("-")), ret
        )
        ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、"), ret)
        ret = filter(lambda x: len(x) > 0, ret)
        ret = list(ret)
        ret = unique(ret)
        return ret
    else:
        return [strip_parenthesis(val)]


def parse_multiple_seyuu(val, raw):
    val = val.strip()
    val = conv(val)
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
        return ret

    ret = extract_text(mwp.parse(val))
    ret = map(lambda x: lstrip_cat(x.strip("→").strip("-")), ret)
    ret = map(lambda x: chain_replace(x, "《》/\\-()（）【】⌈⌋⌊⌉[]{},，、"), ret)
    ret = filter(lambda x: len(x) > 0, ret)
    ret = list(ret)
    ret = unique(ret)
    return ret


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


def parse_color(val, raw):
    val = conv(val)
    val = strip_parenthesis(val)
    val = "".join(extract_text(mwp.parse(val)))
    ret = multisplit(val, "/→+-~左右或,，、 ")
    ret = map(
        lambda x: x.rstrip("瞳").rstrip("发").rstrip(
            "色") if len(x) <= 4 else x, ret
    )
    ret = filter(lambda x: len(x) > 0, ret)
    ret = list(ret)
    ret = unique(ret)
    return ret


def parse_blood(val, raw):
    val = remove_html(val)
    val = val.split("\n")[0]
    val = conv(val)
    val = val.upper()
    if "稀有" in val:
        return "稀有"
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
        val = None
    return val


birthday_re = re.compile(r'((\d*)年)?((\d*)月)?((\d*)日)?')


def parse_birthday(val, raw):
    m = birthday_re.search(val)
    ret = [None, None, None]
    if m:
        g = m.groups()
        if g[1]:
            ret[0] = int(g[1])
        if g[3]:
            ret[1] = int(g[3])
        if g[5]:
            ret[2] = int(g[5])
        # print(val)
        # print(ret)
        # print()
        return ret
    return None


d = dict()
attrs = json.load(open("../preprocess/attr_index.json", encoding="utf-8"))
extra = json.load(open("extra_info.json", encoding="utf-8"))
out = {}

s = set()
cnt = 0
cntt = 0
for k, v in extra.items():
    # print(k)
    tmp = {"萌点": [], "声优": []}
    for pname, pvalue in v.items():
        match pname:
            case "萌点":
                res = parse_moe(pvalue, v["raw"])
                tmp["萌点"] = res
            case "别号":
                res = parse_alt(pvalue, v["raw"])
                tmp["别号"] = res
            case "本名":
                res = parse_name(pvalue, v["raw"])
                tmp["本名"] = res
            case "身高":
                res = parse_height(pvalue, v["raw"])
                if len(res) > 0:
                    for i in res:
                        if i >= 20 and i <= 300:
                            tmp["身高"] = i
            case "体重":
                res = parse_weight(pvalue, v["raw"])
                if len(res) > 0:
                    if res[0] >= 20 and res[0] <= 300:
                        tmp["体重"] = res[0]
                    else:
                        mx = max(res)
                        if mx >= 20 and mx <= 300:
                            tmp["体重"] = mx
                        else:
                            mi = max(res)
                            if mi >= 20 and mi <= 300:
                                tmp["体重"] = mi
                            else:
                                tmp["体重"] = res[0]
            case "声优":
                res = parse_seyuu(pvalue, v["raw"])
                tmp["声优"].extend(res)
            case "多位声优":
                res = parse_multiple_seyuu(pvalue, v["raw"])
                tmp["声优"].extend(res)
            case "三围":
                res = parse_bwh(pvalue, v["raw"])
                tmp["三围"] = res
            case "发色":
                res = parse_color(pvalue, v["raw"])
                if len(res) > 0:
                    tmp["发色"] = res
            case "瞳色":
                res = parse_color(pvalue, v["raw"])
                if len(res) > 0:
                    tmp["瞳色"] = res
            case "血型":
                # print(pvalue)
                res = parse_blood(pvalue, v["raw"])
                # print(res)
                # s.add(res)
                tmp["血型"] = res
            case "年龄":
                res = parse_age(pvalue, v["raw"])
                if len(res) > 0:
                    if res[0] <= 100:
                        tmp["年龄"] = res[0]
                    else:
                        mi = min(res)
                        if mi <= 100:
                            tmp["年龄"] = mi
                        else:
                            mx = max(res)
                            if mx <= 100:
                                tmp["年龄"] = mx
                            else:
                                tmp["年龄"] = res[0]
            case "生日":
                res = parse_birthday(pvalue, v["raw"])
                if res:
                    tmp['生日'] = res
    tmp["声优"] = unique(tmp["声优"])
    out[k] = tmp
    # print('\n\n\n')
# print(cnt, cntt)

print(s)
save_json(out, "extra_processed.json")

"""
('讨厌', 371)
('学校', 388)
('爱好', 398)
('能力', 419)
('喜欢', 453)
('服役', 456)
('代号', 463)
('动工', 465)
('印象色', 489)
('下水', 525)
('结局', 560)
('演员', 575)
('初登场作品', 578)
('译名', 579)
('属性', 591)
('画师', 681)
('别名', 731)
('粉丝勋章', 750)
('职业', 926)
('特殊生日', 1053)
('性别', 1055)
('种族', 1743)
('tabs', 1922)
('多种瞳色', 2010)
('多种发色', 2250)
('三围', 3065)
('血型', 5046)
('体重', 6351)
('多位声优', 6444)
('星座', 8647)
('生日', 11449)
('年龄', 11532)
('身高', 13028)
('个人状态', 13066)
('声优', 14639)
('出身地区', 15788)
('活动范围', 16512)
('所属团体', 19994)
('别号', 22836)
('发色', 25829)
('瞳色', 26127)
('相关人士', 28132)
('本名', 32805)
('title', 33969)
('pageid', 33969)
('image', 33969)
('萌点', 33969)
"""
