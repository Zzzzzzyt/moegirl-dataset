import json
import re
import opencc
import os
from tqdm import tqdm

from utils.file import load_json, save_json


special_map = {
    "10452": "初音未来",  # 初音ミク
    "273": "阿尔托莉雅·潘德拉贡",  # アルトリア・ペンドラゴン
    "3": "C.C.(CODE GEASS)",  # C.C.
    "1": "鲁路修·vi·布里塔尼亚",  # ルルーシュ・ランペルージ
    "46465": "洛琪希·米格路迪亚",  # ロキシー・ミグルディア・グレイラット
    "10609": "立华奏",  # 立華かなで
    "12929": None,  # 地球君
    "1976": "赫萝",  # ホロ
    "64640": "宝多六花",  # 宝多六花
    "35615": "雷姆(Re:从零开始的异世界生活)",  # レム
    "19529": "时崎狂三",  # 時崎狂三
    "24093": "泽村·斯宾塞·英梨梨",  # 澤村・スペンサー・英梨々
    "116353": "露西(赛博朋克边缘行者)",  # Lucy  TODO
    "14468": None,  # 圣光君
    "19546": "利威尔·阿克曼",  # 利威尔
    "72355": "伊蕾娜",  # イレイナ
    "14477": None,  # (bgm38)
    "16369": "主人公(人类衰退之后)",  # 我
    "57751": "02",  # ゼロツー
    "46464": "艾莉丝·伯雷亚斯·格雷拉特",  # 艾莉丝·格雷拉特
    "77": "斯派克·斯皮格尔",  # 史派克·斯皮格尔  TODO
    "336": "中原岬",  # 中原岬  TODO
    "79": "菲·瓦伦丁",  # 菲·瓦伦坦
    "606": "雨宫优子",  # 雨宮 優子
    "293": "奇尔希",  # 銀
    "2355": "机动战队:尼娅",  # ニア・テッペリン 妮亚  TODO
    "11546": None,  # アルパカ 羊驼
    "3216": "英灵卫宫",  # 卫宫
    "75": "猫咪老师",  # 喵先生/斑
    "10639": "一方通行",  # 一方通行
    "88130": "南梦芽",  # 南夢芽
    "16684": "L·罗莱特",  # L
    "5922": "天海春香",  # 天海春香
    "53208": "绊爱",  # Kizuna AI
    "64641": "新条茜",  # 新条アカネ
    "57715": "芙拉蒂蕾娜·米利杰",  # ヴラディレーナ・ミリーゼ
    "11926": "紫苑寺有子",  # アリス
    "5928": "如月千早",  # 如月千早
    "13375": "奈亚子",  # ニャルラトホテプ
    "2902": "泰蕾莎·泰斯塔罗莎",  # テレサ・テスタロッサ
    "71479": "阿尼亚·福杰",  # アーニャ
    "223": "露易丝(零之使魔)",  # ルイズ・フランソワーズ・ル・ブラン・ド・ラ・ヴァリエール
    "855": "爱尔奎特·布伦史塔德",  # アルクェイド・ブリュンスタッド
    "12423": None,  # 杨威利ヤン・ウェンリー
    '87184': 'トワ',
}
# special_map = {}

revserse_special = {
    # "温妮莎": None,
    # "拉娜(原神)": None,
    # "阿佩普": None,
    # "太郎丸(原神)": None,
    # "查尔斯·狄更斯": None,
    # "亚丝拉琪(崩坏系列)": None,
    # "琥珀(崩坏系列)": None,
    # "德尔塔(崩坏3)": None,
    # "史丹": None,
    # "空(崩坏系列)": None,
    # "薇塔": None,
    # "岚(星穹铁道)": None,
    # "明日方舟:九": None,
    # "明日方舟:博士": "71016",
    # "明日方舟:福尔图娜": None,
    # "明日方舟:ACE": None,
    # "明日方舟:可萝尔": None,
    # "明日方舟:Scout": None,
    # "明日方舟:“剧作家”": None,
    # "明日方舟:米莎": 117894,
    # "明日方舟:皇帝": 70847,
    # "明日方舟:罗伊": None,
    # "明日方舟:郁金香": None,
    # "明日方舟:达莉娅": None,
    # # "明日方舟:科西切":89236,
    # # "明日方舟:文月":70846,
    # "明日方舟:火龙": None,
    # "明日方舟:杜玛": None,
    '碧蓝航线:22': '10849',
    '碧蓝航线:33': '10850',
    'Towa': '87184',
    'トワ': '87184',
    '小不点(LoveLive!)': '110647',
    '芙蕾雅(上古卷轴)': None,
    '菲兹·艾贝琳': None,
}

# bgm <-> moegirl
subject_map = [
    (['原神'], ['原神']),
    (['崩坏3'], ['崩坏3']),
    (['崩坏：星穹铁道'], ['崩坏：星穹铁道']),
    (['阴阳师'], ['阴阳师(手游)']),
    (['舰队Collection'], ['舰队Collection舰娘']),
    (['战舰少女R'], ['战舰少女']),
    (['明日方舟'], ['明日方舟角色']),
    (['碧蓝航线'], ['碧蓝航线']),
    (['Blue Archive'], ['蔚蓝档案']),
    (['ONE PIECE'], ['海贼王']),
]

subject_special = {}

subject_reverse_special = {}

for k, v in subject_map:
    for i in k:
        subject_special[i] = set(v)
    for i in v:
        subject_reverse_special[i] = set(k)

for k, v in special_map.items():
    if v is not None:
        revserse_special[v] = k


use_160k = (
    os.path.exists("bgm_chars_160k.json")
    and os.path.exists("bgm_subjects_160k.json")
    and os.path.exists("bgm_index_160k.json")
)

bgm_index = None
bgm_chars = None
bgm_subjects = None
if use_160k:
    bgm_index = load_json("bgm_index_160k.json")
    bgm_chars = load_json("bgm_chars_160k.json")
    bgm_subjects = load_json("bgm_subjects_160k.json")
else:
    print("160k not found. falling back to 20k.")
    bgm_index = load_json("bgm_index_20k.json")
    bgm_chars = load_json("bgm_chars_20k.json")
    bgm_subjects = load_json("bgm_subjects_20k.json")

print("loaded: bgm_index:", len(bgm_index))
print("loaded: bgm_chars:", len(bgm_chars))
print("loaded: bgm_subjects:", len(bgm_subjects))

moegirl_chars = load_json("../moegirl/preprocess/char_index.json")
print("loaded: moegirl_chars:", len(moegirl_chars))
moegirl_extra = load_json("../moegirl/crawler2/extra_processed.json")
print("loaded: moegirl_extra:", len(moegirl_extra))
char2subject = load_json("../moegirl/preprocess/char2subject.json")
print("loaded: char2subject:", len(char2subject))


def is_postfix(a, b):
    if len(a) < len(b):
        offset = len(b) - len(a)
        return b[offset - 1] == ":" and a == b[offset:]
    else:
        return a == b


converter = opencc.OpenCC("jp2t.json")
converter2 = opencc.OpenCC("t2s.json")


def conv(t):
    ret = []
    for i in t:
        s = converter2.convert(converter.convert(i))
        ret.append(s)
    return ret + t


def unique(l):
    ret = []
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret


def multisplit(str, sp=",，/／"):
    ret = []
    cur = ""
    for i in str:
        if i in sp:
            cur = cur.strip()
            if cur != "":
                ret.append(cur)
            cur = ""
        else:
            cur += i
    cur = cur.strip()
    if cur != "":
        ret.append(cur)
    return ret


def moegirl_split(name):
    cur = name
    pre = ""
    prepos = cur.find(":")
    if prepos != -1:
        pre = cur[:prepos]
        cur = cur[prepos + 1 :]
    post = ""
    postpos = cur.find("(")
    if postpos != -1 and cur[-1] == ")":
        post = cur[postpos + 1 : -1]
        cur = cur[:postpos]
    return cur, pre, post


def smatch(moename, subjects):
    if moename == "":
        return 0
    cnt = 0
    for i in subjects:
        if i.startswith(moename):
            cnt += 1
    return cnt


def map_bgm(entry):
    id = str(entry["id"])
    if id in special_map:
        special = special_map[id]
        if special is None:
            return []
        else:
            return [(special, 19260817)]

    subjects = bgm_subjects2[id]

    moe_subjects_special = set()
    for i in subjects:
        if i in subject_special:
            moe_subjects_special.update(subject_special[i])

    canon_name = []
    names = []
    if id in bgm_chars:
        char = bgm_chars[id]
        names.extend(multisplit(char["name"]))
        for i in char["infobox"]:
            if i["key"] == "简体中文名":
                if type(i["value"]) == str:
                    names.extend(multisplit(i["value"]))
                else:
                    for split in i["value"]:
                        split = multisplit(split["v"])
                        names.extend(split)
            elif i["key"] == "别名":
                if type(i["value"]) == str:
                    names.extend(multisplit(i["value"]))
                else:
                    for split in i["value"]:
                        split = multisplit(split["v"])
                        names.extend(split)
    if "name" in entry:
        canon_name.extend(multisplit(entry["name"]))

    canon_name = unique(conv(canon_name))
    names = unique(conv(names))
    canon_name.sort(key=lambda x: len(x) - x.isascii() * 10, reverse=True)
    names.sort(key=lambda x: len(x) - x.isascii() * 10, reverse=True)
    names = canon_name + names
    names = unique(names)

    match = []
    for i in names:
        if i in moe_lookup:
            for j in moe_lookup[i]:
                moeid = j[0]
                score = j[1]
                if moeid in revserse_special:
                    continue
                moesub = moe_subjects[moeid]
                # print(moeid, moesub)
                if len(moe_subjects_special) == 0:
                    if len(moesub) > 0 and len(subjects) > 0:
                        subscore = 0
                        for k in moesub:
                            subscore += smatch(k, subjects)
                        # if subscore == 0:
                        #     continue
                        score += subscore * 2
                    match.append((moeid, score, moesub))
                else:
                    flag = False
                    for k in moesub:
                        if k in moe_subjects_special:
                            flag = True
                    if flag:
                        match.append((moeid, score + 100, moesub))
    match.sort(reverse=True, key=lambda x: x[1])

    # if len(moe_subjects_special):
    # if '莫里' in names:
    # if 'bilibili-33' in names:
    #     print()
    #     print('names', names)
    #     print('subjects', subjects)
    #     for i in match:
    #         print(i)
    #     input()

    dedupe = set()
    match2 = []
    for i in match:
        if i[0] in dedupe:
            continue
        dedupe.add(i[0])
        match2.append(i)
    # print(match2)
    birthday = None
    bloodtype = None
    height = None
    if char["blood_type"]:
        bloodtype = ["A", "B", "AB", "O"][char["blood_type"] - 1]
    if char["birth_mon"] and char["birth_day"]:
        birthday = [char["birth_year"], char["birth_mon"], char["birth_day"]]
    for i in char["infobox"]:
        match i["key"]:
            case "生日":
                if birthday is None:
                    birthday = [None, None, None]
                    if type(i["value"]) != str:
                        continue
                    m = re.search(r"((\d*)年)?((\d*)月)?((\d*)日)?", i["value"])
                    if m:
                        g = m.groups()
                        if g[1]:
                            birthday[0] = int(g[1])
                        if g[3]:
                            birthday[1] = int(g[3])
                        if g[5]:
                            birthday[2] = int(g[5])
            case "血型":
                if bloodtype is None:
                    bloodtype = i["value"].replace("型", "")
            case "身高":
                if height is None:
                    try:
                        height = int(i["value"].replace("cm", ""))
                    except Exception as e:
                        pass
    for idx, i in enumerate(match2):
        mid = i[0]
        score = i[1]
        if mid not in moegirl_extra:
            continue
        char = moegirl_extra[mid]
        if "生日" in char and birthday:
            flag = True
            for j in range(3):
                if char["生日"][j] and birthday[j] and char["生日"][j] != birthday[j]:
                    flag = False
                    break
            if flag:
                score += 3
        if "身高" in char and height:
            if abs(char["身高"] - height) <= 1:
                score += 3
        if "血型" in char and bloodtype:
            if char["血型"] == bloodtype:
                score += 1
        match2[idx] = (mid, score)
    match2.sort(reverse=True, key=lambda x: x[1])
    # print(match2)
    # ret = list(map(lambda x: x[0], match2))
    # ret = unique(ret)
    return match2


bgm_subjects2 = {}

for entry in bgm_index:
    id = str(entry["id"])
    subjects = []
    if id in bgm_subjects:
        for i in bgm_subjects[id]:
            # if i["staff"] == "客串":
            #     continue
            subjects.append(i["name_cn"])
            subjects.append(i["name"])
        subjects = filter(lambda x: len(x) > 0, subjects)
        subjects = unique(subjects)
    bgm_subjects2[entry["id"]] = subjects


for k, v in char2subject.items():
    tmp = []
    for i in v[1:]:
        if i.endswith('的页面'):
            continue
        if i.endswith('系列角色'):
            tmp.append(i[:-4])
        elif i.endswith('系列'):
            tmp.append(i[:-2])
        if i not in tmp:
            tmp.append(i)
    char2subject[k] = tmp


moe_lookup = {}
moe_subjects = {}
for i in moegirl_chars:
    name, pre, post = moegirl_split(i)

    subjects = []
    if pre != "":
        subjects.append(pre)
    if i in char2subject:
        subjects.extend(char2subject[i])
    if post != "":
        subjects.append(post)
    subjects = unique(subjects)
    moe_subjects[i] = subjects

    if name not in moe_lookup:
        moe_lookup[name] = []
    moe_lookup[name].append((i, 1))
    if i in moegirl_extra:
        char = moegirl_extra[i]
        if "本名" in char:
            for idx, j in enumerate(char["本名"]):
                j = j.replace(" ", "").lower().strip('"\'')
                j = converter2.convert(converter.convert(j))
                if "不明" in j or "未知" in j or "不详" in j:
                    continue
                if j not in moe_lookup:
                    moe_lookup[j] = []
                moe_lookup[j].append((i, 1 / (idx + 2)))

bgm2moegirl = {}
moegirl2bgm = {}
# bgm_index = bgm_index[:250]

multicount = 0
nonecount = 0

print(f"subject map len={len(bgm_subjects)}")
print(f"char map len={len(bgm_chars)}")

for cnt, i in enumerate(tqdm(bgm_index)):
    moegirl_ids = map_bgm(i)
    bgm_id = i["id"]
    if bgm_id not in special_map:
        if len(moegirl_ids) == 0:
            nonecount += 1
        elif len(moegirl_ids) > 1:
            multicount += 1
    # if len(moegirl_ids) != 1:
    # pass
    # print(cnt, bgm_id, i['name'], moegirl_ids)
    # print('\'{}\':'.format(bgm_id), moegirl_ids, '#', i['name'])
    tmp = []
    # print(moegirl_ids)
    for res in moegirl_ids:
        moegirl_id, score = res[0], res[1]
        tmp.append(moegirl_id)
        if moegirl_id not in moegirl2bgm:
            moegirl2bgm[moegirl_id] = []
        if bgm_id not in moegirl2bgm[moegirl_id]:
            moegirl2bgm[moegirl_id].append((bgm_id, score, cnt))
    bgm2moegirl[bgm_id] = tmp

for k, v in moegirl2bgm.items():
    if k not in char2subject:
        continue
    moesub = char2subject[k]
    bgmsub = set()
    for sub in moesub:
        if sub in subject_reverse_special:
            bgmsub.update(subject_reverse_special[sub])
    if len(bgmsub) > 0:
        # print(moesub)
        # print(bgmsub)
        # print(k, list(map(lambda x: [bgm_chars[x[0]]["name"]] + list(x), v)))
        v2 = []
        for i in v:
            # print(v, bgm_subjects2[i[0]])
            flag = False
            for j in bgm_subjects2[i[0]]:
                if j in bgmsub:
                    flag = True
                    break
            if flag:
                v2.append(i)
        moegirl2bgm[k] = v2
        # print(list(map(lambda x: [bgm_chars[x[0]]["name"]] + list(x), v2)))
        # print()


for k, v in revserse_special.items():
    # print(k, v)
    if v is None:
        moegirl2bgm[k] = []
    else:
        moegirl2bgm[k] = [(v, 19260817, -1)]

print(
    "successful bgm2moegirl: {}/{}".format(len(bgm_index) - nonecount, len(bgm_index))
)
print(f"multi={multicount} none={nonecount}")

multicount2 = 0

moegirl2bgm2 = {}
for k, v in moegirl2bgm.items():
    v = v.copy()
    v.sort(key=lambda x: x[2])
    v.sort(reverse=True, key=lambda x: x[1])
    # if len(v) > 1:
    #     v = list(filter(lambda x: x[1] > 1, v))
    if len(v) == 0:
        continue
    if len(v) > 1:
        # print(k, list(map(lambda x: str([bgm_chars[x[0]]["name"]] + list(x)), v)))
        multicount2 += 1
    moegirl2bgm2[k] = list(map(lambda x: x[0], v))

print("successful moegirl2bgm: {}/{}".format(len(moegirl2bgm2), len(moegirl_chars)))
print(f"multi={multicount2} none={len(moegirl_chars)-len(moegirl2bgm2)}")

save_json(bgm2moegirl, "bgm2moegirl.json")
save_json(moegirl2bgm2, "moegirl2bgm.json")

os.system('python -u img_preloader.py')
