import json
import opencc
import os
from tqdm import tqdm


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


special_map = {
    '10452': '初音未来',  # 初音ミク
    '273': '阿尔托莉雅·潘德拉贡',  # アルトリア・ペンドラゴン
    '3': 'C.C.(CODE GEASS)',  # C.C.
    '1': '鲁路修·vi·布里塔尼亚',  # ルルーシュ・ランペルージ
    '46465': '洛琪希·米格路迪亚',  # ロキシー・ミグルディア・グレイラット
    '10609': '立华奏',  # 立華かなで
    '12929': None,  # 地球君
    '1976': '赫萝',  # ホロ
    '64640': '宝多六花',  # 宝多六花
    '35615': '雷姆(Re:从零开始的异世界生活)',  # レム
    '19529': '时崎狂三',  # 時崎狂三
    '24093': '泽村·斯宾塞·英梨梨',  # 澤村・スペンサー・英梨々
    '116353': None,  # Lucy  TODO
    '14468': None,  # 圣光君
    '19546': '利威尔·阿克曼',  # 利威尔
    '72355': '伊蕾娜',  # イレイナ
    '14477': None,  # (bgm38)
    '16369': '主人公(人类衰退之后)',  # 我
    '57751': '02',  # ゼロツー
    '46464': '艾莉丝·伯雷亚斯·格雷拉特',  # 艾莉丝·格雷拉特
    '77': '斯派克·斯皮格尔',  # 史派克·斯皮格尔  TODO
    '336': '中原岬',  # 中原岬  TODO
    '79': '菲·瓦伦丁',  # 菲·瓦伦坦
    '606': '雨宫优子',  # 雨宮 優子
    '293': '奇尔希',  # 銀
    '2355': None,  # ニア・テッペリン 妮亚  TODO
    '11546': None,  # アルパカ 羊驼
    '3216': '英灵卫宫',  # 卫宫
    '75': '猫咪老师',  # 喵先生/斑
    '10639': '一方通行',  # 一方通行
    '88130': '南梦芽',  # 南夢芽
    '16684': 'L·罗莱特',  # L
    '5922': '天海春香',  # 天海春香
    '53208': '绊爱',  # Kizuna AI
    '64641': '新条茜',  # 新条アカネ
    '57715': '芙拉蒂蕾娜·米利杰',  # ヴラディレーナ・ミリーゼ
    '11926': '紫苑寺有子',  # アリス
    '5928': '如月千早',  # 如月千早
    '13375': '奈亚子',  # ニャルラトホテプ
    '2902': '泰蕾莎·泰斯塔罗莎',  # テレサ・テスタロッサ
    '71479': '阿尼亚·福杰',  # アーニャ
    '223': '露易丝(零之使魔)',  # ルイズ・フランソワーズ・ル・ブラン・ド・ラ・ヴァリエール
    '855': '爱尔奎特·布伦史塔德',  # アルクェイド・ブリュンスタッド
    '116359': None,  # Rebecca TODO
    '12423': None  # 杨威利ヤン・ウェンリー
}
# special_map = {}

revserse_special = {}
for k, v in special_map.items():
    if v is not None:
        revserse_special[v] = k


use_120k = os.path.exists('bgm_chars_120k.json') and os.path.exists('bgm_subjects_120k.json') and os.path.exists('bgm_index_120k.json')

bgm_index = None
bgm_chars = None
bgm_subjects = None
if use_120k:
    bgm_index = json.load(open('bgm_index_120k.json', encoding='utf-8'))
    bgm_chars = json.load(open('bgm_chars_120k.json', encoding='utf-8'))
    bgm_subjects = json.load(open('bgm_subjects_120k.json', encoding='utf-8'))
else:
    print('120k not found. falling back to 20k.')
    bgm_index = json.load(open('bgm_index_20k.json', encoding='utf-8'))
    bgm_chars = json.load(open('bgm_chars_20k.json', encoding='utf-8'))
    bgm_subjects = json.load(open('bgm_subjects_20k.json', encoding='utf-8'))

moegirl_chars = json.load(open('../moegirl/preprocess/char_index.json', encoding='utf-8'))
moe_split = {}


def is_postfix(a, b):
    if len(a) < len(b):
        offset = len(b)-len(a)
        return b[offset-1] == ':' and a == b[offset:]
    else:
        return a == b


converter = opencc.OpenCC('jp2t.json')
converter2 = opencc.OpenCC('t2s.json')


def conv(t):
    ret = []
    for i in t:
        s = converter2.convert(converter.convert(i))
        ret.append(s)
    return ret+t


def unique(l):
    ret = []
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret


def multisplit(str, sp=',，/／'):
    ret = []
    cur = ''
    for i in str:
        if i in sp:
            ret.append(cur.strip())
            cur = ''
        else:
            cur += i
    if cur != '':
        ret.append(cur.strip())
    return ret


def moegirl_split(name):
    cur = name
    pre = ''
    prepos = cur.find(':')
    if prepos != -1:
        pre = cur[:prepos]
        cur = cur[prepos+1:]
    post = ''
    postpos = cur.find('(')
    if postpos != -1 and cur[-1] == ')':
        post = cur[postpos+1:-1]
        cur = cur[:postpos]
    return cur, pre, post


def smatch(name, subjects):
    if name == '':
        return False
    for i in subjects:
        if name in i:
            return True
    return False


def map_bgm(entry):
    id = str(entry['id'])
    if id in special_map:
        special = special_map[id]
        if special is None:
            return []
        else:
            return [special]

    subjects = []
    if id in bgm_subjects:
        for i in bgm_subjects[id]:
            if i['staff'] == '客串':
                continue
            subjects.append(i['name_cn'])
            subjects.append(i['name'])
        subjects = unique(subjects)

    canon_name = []
    names = []
    if id in bgm_chars:
        char = bgm_chars[id]
        names.extend(multisplit(char['name']))
        for i in char['infobox']:
            if i['key'] == '简体中文名':
                canon_name.extend(multisplit(i['value']))
            elif i['key'] == '别名':
                if type(i['value']) == str:
                    names.extend(multisplit(i['value']))
                else:
                    for j in i['value']:
                        split = multisplit(j['v'])
                        names.extend(split)
    if 'name' in entry:
        canon_name.extend(multisplit(entry['name']))

    canon_name = unique(conv(canon_name))
    names = unique(conv(names))
    canon_name.sort(key=lambda x: len(x)-x.isascii()*10, reverse=True)
    names.sort(key=lambda x: len(x)-x.isascii()*10, reverse=True)
    names = canon_name+names

    subject_match = []
    none_match = []
    normal_match = []
    for i in names:
        if i in moe_split:
            for j in moe_split[i]:
                if j[0] not in revserse_special:
                    if j[2] == '':
                        none_match.append(j[0])
                    elif smatch(j[1], subjects) or smatch(j[2], subjects):
                        subject_match.append(j[0])
                    else:
                        normal_match.append(j[0])
    subject_match = unique(subject_match)
    none_match = unique(none_match)
    normal_match = unique(normal_match)

    # print(entry, subjects)
    # print(names)
    # print(subject_match)
    # print(none_match)
    # print(normal_match)

    if len(subject_match) > 0:
        return subject_match
    if len(none_match) > 0:
        return none_match

    return normal_match


for i in moegirl_chars:
    name, pre, post = moegirl_split(i)
    if name not in moe_split:
        moe_split[name] = []
    moe_split[name].append((i, pre, post))

bgm2moegirl = {}
moegirl2bgm = {}
# bgm_index = bgm_index[:250]

multicount = 0
nonecount = 0

print(f'subject map len={len(bgm_subjects)}')
print(f'char map len={len(bgm_chars)}')

for cnt, i in enumerate(bgm_index):
    moegirl_ids = map_bgm(i)
    bgm_id = i['id']
    if bgm_id not in special_map:
        if len(moegirl_ids) == 0:
            nonecount += 1
        elif len(moegirl_ids) > 1:
            multicount += 1
    # if len(moegirl_ids) != 1:
        # pass
        # print(cnt, bgm_id, i['name'], moegirl_ids)
    # print('\'{}\':'.format(bgm_id), moegirl_ids, '#', i['name'])
    bgm2moegirl[bgm_id] = moegirl_ids
    for moegirl_id in moegirl_ids:
        if moegirl_id not in moegirl2bgm:
            moegirl2bgm[moegirl_id] = []
        if bgm_id not in moegirl2bgm[moegirl_id]:
            moegirl2bgm[moegirl_id].append(bgm_id)

for k, v in revserse_special.items():
    # print(k, v)
    moegirl2bgm[k] = [v]

print('successful bgm2moegirl: {}/{}'.format(len(bgm_index)-nonecount, len(bgm_index)))
print(f'multi={multicount} none={nonecount}')

multicount2 = 0

for i in moegirl2bgm.values():
    if len(i) > 1:
        multicount2 += 1
print('successful moegirl2bgm: {}/{}'.format(len(moegirl2bgm), len(moegirl_chars)))
print(f'multi={multicount2} none={len(moegirl_chars)-len(moegirl2bgm)}')

save_json(bgm2moegirl, 'bgm2moegirl.json')
save_json(moegirl2bgm, 'moegirl2bgm.json')
