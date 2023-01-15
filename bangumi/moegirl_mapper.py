import json
import opencc
from tqdm import tqdm


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


special_map = {
    '12393': '牧濑红莉栖',  # 牧瀬紅莉栖
    '10452': '初音未来',  # 初音未来
    '24094': '加藤惠(路人女主的养成方法)',  # 加藤惠
    '3': 'C.C.(CODE GEASS)',  # C.C.
    '1': '鲁路修·vi·布里塔尼亚',  # 鲁路修·兰佩路基
    '87968': '后藤独',  # 后藤一里
    '16490': '结城明日奈',  # 亚丝娜／结城明日奈
    '46465': '洛琪希·米格路迪亚',  # 洛琪希·米格路迪亚·格雷拉特
    '10609': '立华奏',  # 立華かなで
    '3218': '伊莉雅丝菲尔·冯·爱因兹贝伦',  # 伊莉雅斯菲尔·冯·爱因兹贝伦
    '12929': None,  # 地球
    '35681': '惠惠(为美好的世界献上祝福)',  # 惠惠
    '1976': '赫萝',  # 赫萝
    '10446': '丘比(魔法少女小圆)',  # 丘比
    '35608': '爱蜜莉雅',  # 艾米莉娅
    '12392': '冈部伦太郎',  # 冈部伦太郎
    '35615': '雷姆(Re:从零开始的异世界生活)',  # 蕾姆
    '3215': '间桐樱',  # 間桐桜
    '19529': '时崎狂三',  # 時崎狂三
    '24093': '泽村·斯宾塞·英梨梨',  # 泽村·史宾瑟·英梨梨
    '12381': '椎名真由理',  # 椎名まゆり
    '116353': '露西(赛博朋克边缘行者)',  # 露西                            # TODO
    '14468': None,  # 圣光君
    '19546': '利威尔·阿克曼',  # 利威尔
    '26090': '一色伊吕波',  # 一色彩羽
    '14477': None,  # 班固米三八
    '16369': '主人公(人类衰退之后)',  # 我
    '46464': '艾莉丝·伯雷亚斯·格雷拉特',  # 艾莉丝·格雷拉特
    '77': '斯派克·斯皮格尔',  # 史派克·斯皮格尔                                        # TODO
    '336': '中原岬',  # 中原岬                                            # TODO
    '79': '菲·瓦伦丁',  # 菲·瓦伦坦
    '2765': '木之本樱',  # 木之本桜
    '606': '雨宫优子',  # 雨宮 優子
    '1227': '吉尔伽美什(Fate)',  # 吉尔伽美什
    '293': '奇尔希',  # 银
    '229': '神乐(银魂)',  # 神乐
    '50578': '东海帝王',  # 东海帝皇
    '2355': None,  # 妮亚                                                 # TODO
    '35678': '阿库娅(为美好的世界献上祝福)',  # 阿克娅
    '19915': '明石(四叠半神话大系)',  # 明石
    '469': '琴吹䌷',  # 琴吹紬
    '266': '金色暗影',  # 金色暗影/DARKNESS
    '292': '黑(DARKER THAN BLACK)',  # 黑
    '11546': None,  # 羊驼
    '16817': '梦梦·贝莉雅·戴比路克',  # 茉茉·贝莉雅·戴比路克
    '3216': '英灵卫宫',  # 卫宫
    '16684': 'L·罗莱特',  # L
    '75': '猫咪老师',  # 喵先生/斑
    '15499': '散华礼弥(角色)',  # 散华礼弥
    '11909': '博士(日常)',  # 博士
    # '485': '博丽灵梦',  # 博麗霊夢
    '10639': '一方通行',  # 一方通行
    '53208': '绊爱'  # Kizuna AI
}

revserse_special = set(special_map.values())

bgm_index = json.load(open('bgm_index.json', encoding='utf-8'))
bgm_chars = json.load(open('bgm_chars.json', encoding='utf-8'))
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
    return ret


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


# def multimatch(bgm_name):
#     ret = []
#     for i in moegirl_chars:
#         idx = i.find(bgm_name)
#         if idx == 0:
#             if len(bgm_name) == len(i):
#                 ret.append(i)
#             else:
#                 if i[-1] == ')' and i[len(bgm_name)] == '(':
#                     ret.append(i)
#         elif idx > 0:
#             if i[idx-1] == ':' and is_postfix(bgm_name, i):
#                 ret.append(i)
#     return ret


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


def map_bgm(entry):
    id = str(entry['id'])
    if id in special_map:
        special = special_map[id]
        if special is None:
            return []
        else:
            return [special]

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
    canon_name.extend(multisplit(entry['name']))

    canon_name = unique(conv(canon_name))
    names = unique(conv(names))
    canon_name.sort(key=lambda x: len(x)-x.isascii()*10, reverse=True)
    names.sort(key=lambda x: len(x)-x.isascii()*10, reverse=True)
    names = canon_name+names

    ret = []
    exact = []
    for i in names:
        if i in moe_split:
            for j in moe_split[i]:
                if j[0] not in revserse_special:
                    if j[0] == i:
                        exact.append(j[0])
                    ret.append(j[0])
    ret = unique(ret)
    exact = unique(exact)
    if len(exact) > 0:
        return exact
    return ret


for i in moegirl_chars:
    name, pre, post = moegirl_split(i)
    if name not in moe_split:
        moe_split[name] = []
    moe_split[name].append((i, pre, post))

bgm2moegirl = {}
moegirl2bgm = {}
bgm_index = bgm_index

multicount = 0
nonecount = 0

for cnt, i in enumerate(bgm_index):
    moegirl_ids = map_bgm(i)
    if len(moegirl_ids) == 0:
        nonecount += 1
    elif len(moegirl_ids) > 1:
        multicount += 1
    bgm_id = i['id']
    print(cnt, bgm_id, i['name'], moegirl_ids)
    # print('\'{}\':'.format(bgm_id), moegirl_ids, '#', i['name'])
    bgm2moegirl[bgm_id] = moegirl_ids
    for moegirl_id in moegirl_ids:
        if moegirl_id not in moegirl2bgm:
            moegirl2bgm[moegirl_id] = []
        moegirl2bgm[moegirl_id].append(bgm_id)

print('successful map: {}/{}'.format(len(bgm_index)-nonecount, len(bgm_index)))
print(f'multi={multicount} none={nonecount}')

save_json(bgm2moegirl, 'bgm2moegirl.json')
save_json(moegirl2bgm, 'moegirl2bgm.json')
