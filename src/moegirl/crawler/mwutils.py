import re
from typing import Any
import warnings
import traceback
import mwparserfromhell as mwp
from bs4 import BeautifulSoup
import opencc

converter = opencc.OpenCC("t2s.json")


def conv(t: str) -> str:
    return converter.convert(t)


def unique(l: list[Any]) -> list[Any]:
    ret = []
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret


def multisplit(str: str, sp=",，、\n ") -> list[str]:
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


def remove_style(src, strip_wikilink=False) -> str:
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


def remove_html(str: str, remove_ref=True) -> str:
    soup = BeautifulSoup(str, features="html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    if remove_ref:
        for s in soup.select("ref"):
            s.extract()
    return soup.get_text()


def calc_zodiac(month: int, day: int) -> str:
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
    raise ValueError(f"Invalid month/day: {month}/{day}")


# pyright: reportAttributeAccessIssue=none
def extract_text(
    code, strict_root=False, aggressive=False, wikilink=False, multiline_mode=False
) -> list[str]:
    ret = []
    try:
        if isinstance(code, mwp.nodes.template.Template):
            name = code.name.lower().strip()
            if (
                name == "cate"
                or name == "黑幕"
                or name == '黒幕'
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
                or name == "已故标注"
                or name == "已故人物标注"
                or name.startswith("lang-")
                or name == "font"
                or name == "注"
                or name == "ljr"
                or name == "黑雾"
                or name == "block"
                or name == "texthover"
                or name == 'hoverinline'
                or name.startswith("photrans")
                or name == "魔女文字"
                or name.startswith("文字描边")
                or name == "writing-mode"
                or name == "文字模糊"
                or name == "填空幕"
                or name == "toggle 内联按钮"
                or name == "文字外发光"
                or name == "tja"
                or name == '瞳色'
                or name == '发色'
                or name == 'eye color'
                or name == 'hair color'
                or name == 'eye_color'
                or name == 'hair_color'
                or name == 'rainbow text'
                or name == 'background color'
                or name == 'ac'
                or name == '模糊文字'
                or name == '舰c'
                or name == '荧光笔'
                or name == 'plain link'
                or name == '东方名词'
                or name == '碧蓝航线links'
                or name == 'center'
                or name == '星座分类'
            ):
                if len(code.params) >= 1:
                    ret.extend(extract_text(code.params[0].value))
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
                or name == "colorlink"
                or name == "lang"
                or name == "gradient_text"
                or name == "cj"
                or name == '#invoke:战舰少女'
            ):
                ret.extend(extract_text(code.get(2).value))
            elif name == "萌点":
                for i in code.params:
                    ret.append(multisplit(str(i.value))[0])
            elif name == "ruby" or name == "rubyh":
                ret.extend(extract_text(code.get(1).value))
                if aggressive:
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
            elif name == "astrology" or name == '星座':
                month = None
                day = None
                try:
                    if len(code.params) == 2:
                        month = int(str(code.get(1).value))
                        day = int(str(code.get(2).value))
                    elif len(code.params) == 3:
                        if str(code.get(3).value).strip() == '':
                            month = int(str(code.get(1).value))
                            day = int(str(code.get(2).value))
                        else:
                            month = int(str(code.get(2).value))
                            day = int(str(code.get(3).value))
                    else:
                        warnings.warn("Invalid astrology template:\n" + str(code))
                except Exception:
                    warnings.warn("Invalid astrology template:\n" + str(code))
                if month is not None and day is not None:
                    ret.append(calc_zodiac(month, day))
            elif name == '折叠属性':
                ret.extend(extract_text(code.get('div').value))
            elif name == 'moe-hover':
                ret.extend(extract_text(code.get('hover1').value))
            elif (
                '注释' in name
                or name == 'ref'
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
                or name == "space"
                or name == "nbsp"
                or name == 'bilibiliup'
                or name == 'colorbox'
                or name.startswith('#switch:')
            ):
                pass
            # elif name == 'birthday':
            #     for i in code.params:
            #         if i.name.strip() == 'ft':
            #             continue
            #         ret.extend(extract_text(i.value))
            #         break
            elif len(code.params) == 0:
                pass
            else:
                warnings.warn("Unkown template name: " + name + "\n" + str(code))
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
        traceback.print_exc()
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
