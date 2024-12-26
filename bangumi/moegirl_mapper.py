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
    '35614': '拉姆(Re:从零开始的异世界生活)',
    '15420': None,
    '108666': '胡桃(莉可丽丝)',
    '70504': '鹭宫诗织',
    '91297': '雨(主播女孩重度依赖)',
    '22783': None,  # 春日步(阿滋漫画大王)
}
# special_map = {}

reverse_special = {
    '胡桃(莉可丽丝)': '108666',
    '碧蓝航线:22': '10849',
    '碧蓝航线:33': '10850',
    'Towa': '87184',
    'トワ': '87184',
    '小不点(LoveLive!)': '110647',
    '芙蕾雅(上古卷轴)': None,
    '菲兹·艾贝琳': None,
    '小小兔': '6684',
    '梦王国与沉睡的100王子:阿尔弗雷德': '157300',
    '文豪与炼金术师:太宰治': '76133',
    '米勒(虚拟UP主)': None,
    '茶茶丸': None,
    '秋田小町': None,
    '苏苏(个人势)': None,
    '里克(王国之心)': '15850',
    '刑天(京剧猫)': None,
    '我的魔塔:刷子': None,
    '我(光与夜之恋)': '97750',
    '修女(星之梦)': None,
    '阿杰(快乐星猫)': None,
    '克劳德(侠盗猎车)': '72922',
    '幻书启世录:桃乐丝': None,
    '小月(巴啦啦小魔仙)': None,
    'Abigail(Rainimator)': None,
    '拉娜(坎公骑冠剑)': None,
    '天国(少女兵器)': None,
    '塞巴斯蒂安(COCOTAMA)': None,
    '格林笔记:白雪姬': '67888',
    '女儿(中国式家长)': None,
    '优子(老爹餐厅系列)': None,
    '小吉(快乐星猫)': None,
    '夏洛克·福尔摩斯(歌舞伎町夏洛克)': '67109',
    '木叶(女忍者椿的心事)': '107238',
    'Ruby(VOCALOID)': None,
    '八戒(唐山葬)': None,
    '月光(海底囚人)': None,
    '丹尼(JOJO的奇妙冒险)': None,
    '春日野丽': '7859',
    '妈妈(hap系列)': None,
    'Isla(海底囚人)': None,
    '机动战队:优子': '2354',
    '汤姆(万圣街)': None,
    '爱丽丝(东方Project旧作)': '10796',
    '博丽灵梦(东方Project旧作)': '485',
    '雾雨魔理沙(东方Project旧作)': '486',
    '野兽(约会大作战)': None,
    '雪儿(洛克人系列)': '1087',
    '洞爷湖仙人': None,
    '帕克(成龙历险记)': None,
    '小白(猪猪侠)': None,
    '贝塔(摩尔庄园)': None,
    '皮诺(Fate)': None,
    '托尔(魔法禁书目录)': None,
    '主人公(火焰之纹章_风花雪月)': '69218',
    '莲华(美少女万华镜)': '16164',
    '莲华(歌姬)': None,
    '猫猫(七色战记)': None,
    '猫猫(药师少女的独语)': '61330',
    '碧翠丝(Re:从零开始的异世界生活)': '35616',
    '电次(电锯人)': '71335',
    '凛(Muse Dash)': None,
    '山田凉': '87974',
    '阿库娅(为美好的世界献上祝福)': '35678',
    '神乐(银魂)': '229',
    '高木同学': '41849',
    '托尔(小林家的龙女仆)': '47659',
    '小林(小林家的龙女仆)': '47658',
    '乔瑟夫·乔斯达': '879',
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
    (
        [
            "东方灵异传 ～ Highly Responsive to Prayers.",
            "东方封魔录 ～ the Story of Eastern Wonderland.",
            "东方梦时空 ～ Phantasmagoria of Dim. Dream.",
            "东方幻想乡 ～ Lotus Land Story.",
            "东方怪绮谈 ～ Mystic Square.",
            "东方红魔乡 ～ the Embodiment of Scarlet Devil.",
            "东方妖妖梦 ～ Perfect Cherry Blossom.",
            "东方永夜抄 ～ Imperishable Night.",
            "东方花映塚 ～ Phantasmagoria of Flower View.",
            "东方文花帖 ～ Shoot the Bullet.",
            "东方风神录 ～ Mountain of Faith.",
            "东方地灵殿 ～ Subterranean Animism.",
            "东方星莲船 ～ Undefined Fantastic Object.",
            "Double Spoiler ～ 东方文花帖",
            "妖精大战争 ~ 东方三月精",
            "东方神灵庙 ～ Ten Desires.",
            "东方辉针城 ～ Double Dealing Character.",
            "东方绀珠传 ～ Legacy of Lunatic Kingdom.",
            "东方天空璋 ～ Hidden Star in Four Seasons.",
            "东方鬼形兽 ～ Wily Beast and Weakest Creature.",
            "东方虹龙洞 ～ Unconnected Marketeers.",
            "弹幕狂们的黑市 ～ 100th Black Market.",
            "东方兽王园 ～ Unfinished Dream of All Living Ghost.",
            "东方凭依华 ～ Antinomy of Common Flowers.",
            "东方萃梦想 ～ Immaterial and Missing Power.",
            "东方绯想天 ～ Scarlet Weather Rhapsody.",
            "东方非想天则 ～ 追寻特大型人偶之谜",
            "东方深秘录 ～ Urban Legend in Limbo.",
            "弹幕天邪鬼 ～ Impossible Spell Card.",
            "东方心绮楼 ～ Hopeless Masquerade.",
            "秘封噩梦日记 ～ Violet Detector.",
            "东方刚欲异闻 ～ 被水淹没的沉愁地狱",
        ],
        ['东方Project'],
    ),
    (['梦王国与沉睡的100名王子'], ['梦王国与沉睡的100王子']),
    (['美少女花骑士'], ['美少女花骑士']),
    (['东京放学后召唤师'], ['东京放课后召唤师']),
    (
        ['坎特伯雷公主与骑士唤醒冠军之剑的奇幻冒险'],
        ['坎特伯雷公主与骑士唤醒冠军之剑的奇幻冒险'],
    ),
    (['公主连结 Re:Dive'], ['公主连结Re:Dive']),
]

subject_special = {}

subject_reverse_special = {}

for k, v in subject_map:
    for i in k:
        subject_special[i] = set(v)
    for i in v:
        subject_reverse_special[i] = set(k)

for k, v in special_map.items():
    if v is not None and v not in reverse_special:
        reverse_special[v] = k


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
    for name, w in subjects:
        if name == moename:
            cnt += w
    return cnt


def map_bgm(entry, verbose=False):
    id = str(entry["id"])
    if id in special_map:
        special = special_map[id]
        if special is None:
            return []
        else:
            return [(special, 19260817)]

    subjects = bgm_subjects2[id]

    moe_subjects_special = set()
    for i, w in subjects:
        if w < 0.5:
            continue
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
                if moeid in reverse_special:
                    continue
                moesub = moe_subjects[moeid]
                # print(moeid, moesub)
                if len(moesub) > 0 and len(subjects) > 0:
                    subscore = 0
                    for k in moesub:
                        subscore += smatch(k, subjects)
                    # if subscore == 0:
                    #     continue
                    score += subscore * 2
                match.append((moeid, score, moesub))

                if len(moe_subjects_special) > 0:
                    flag = False
                    for k in moesub:
                        if k in moe_subjects_special:
                            flag = True
                    if flag:
                        match.append((moeid, score + 1000, moesub))
    match.sort(reverse=True, key=lambda x: x[1])

    dedupe = {}
    match2 = []
    for i in match:
        if i[0] in dedupe:
            dedupe[i[0]] = (i[0], max(i[1], dedupe[i[0]][1]), i[2])
        else:
            dedupe[i[0]] = i

    for k, v in dedupe.items():
        match2.append(v)

    if verbose:
        print('first stage:', match2)

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
        match2[idx] = (mid, score, i[2])
    match2.sort(reverse=True, key=lambda x: x[1])

    if verbose:
        print('second stage:', match2)

    if len(match2) > 1:
        mains = {}
        for i in range(len(match2)):
            name, pre, post = moegirl_split(match2[i][0])
            if pre == "" and post == "" and match2[i][1] >= 3:
                mains[name] = i
        for main, idx in mains.items():
            cnt = 0
            wsum = 0
            for i in match2:
                name, pre, post = moegirl_split(i[0])
                if name == main:
                    cnt += 1
                    wsum += i[1]
            if cnt >= 2:
                if verbose:
                    print('possinle main:', main)
                match2[idx] = (match2[idx][0], wsum, match2[idx][2])
            match2.sort(reverse=True, key=lambda x: x[1])
            if verbose:
                print('third stage:', match2)

    return match2


bgm_subjects2 = {}

for entry in bgm_index:
    id = str(entry["id"])
    subjects = []
    if id in bgm_subjects:
        for i in bgm_subjects[id]:
            score = 1
            if i["staff"] == "客串":
                score = 0.3
            subjects.append((i["name_cn"], score))
            subjects.append((i["name"], score * 0.5))

    subjects = list(filter(lambda x: len(x[0]) > 0, subjects))
    subjects.sort(key=lambda x: x[1], reverse=True)
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

if __name__ == "__main__":
    bgm2moegirl = {}
    moegirl2bgm = {}
    # bgm_index = bgm_index[:20000]

    multicount = 0
    nonecount = 0

    print(f"subject map len={len(bgm_subjects)}")
    print(f"char map len={len(bgm_chars)}")

    for cnt, i in enumerate(tqdm(bgm_index)):
        moegirl_ids = map_bgm(i, verbose=False)
        bgm_id = i["id"]
        if bgm_id not in special_map:
            if len(moegirl_ids) == 0:
                nonecount += 1
            elif len(moegirl_ids) > 1:
                multicount += 1
        # print(cnt, bgm_id, i['name'], moegirl_ids)
        # print('\'{}\':'.format(bgm_id), moegirl_ids, '#', i['name'])
        tmp = []
        for res in moegirl_ids:
            moegirl_id, score = res[0], res[1]
            tmp.append(moegirl_id)
            if moegirl_id not in moegirl2bgm:
                moegirl2bgm[moegirl_id] = []
            moegirl2bgm[moegirl_id].append((bgm_id, score, cnt))
        bgm2moegirl[bgm_id] = tmp

    for k, v in moegirl2bgm.items():
        if k not in moe_subjects:
            continue
        moesub = moe_subjects[k]
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
                for j, w in bgm_subjects2[i[0]]:
                    if j in bgmsub:
                        flag = True
                        break
                if flag:
                    v2.append(i)
            moegirl2bgm[k] = v2
            # print(list(map(lambda x: [bgm_chars[x[0]]["name"]] + list(x), v2)))
            # print()

    for k, v in reverse_special.items():
        if v is None:
            moegirl2bgm[k] = []
        else:
            moegirl2bgm[k] = [(v, 998244353, -1)]

    print(
        "successful bgm2moegirl: {}/{}".format(
            len(bgm_index) - nonecount, len(bgm_index)
        )
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
