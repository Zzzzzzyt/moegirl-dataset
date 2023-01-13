import json


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


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


special_map = {
    '10452': '初音未来',  # 初音未来
    '24094': '加藤惠(路人女主的养成方法)',  # 加藤惠
    '3': 'C.C.(CODE GEASS)',  # C.C.
    '1': '鲁路修·vi·布里塔尼亚',  # 鲁路修·兰佩路基
    '87968': '后藤独',  # 后藤一里
    '16490': '结城明日奈',  # 亚丝娜／结城明日奈
    '46465': '洛琪希·米格路迪亚',  # 洛琪希·米格路迪亚·格雷拉特
    '3218': '伊莉雅丝菲尔·冯·爱因兹贝伦',  # 伊莉雅斯菲尔·冯·爱因兹贝伦
    '12929': None,  # 地球
    '35681': '惠惠(为美好的世界献上祝福)',  # 惠惠
    '10446': '丘比(魔法少女小圆)',  # 丘比
    '35608': '爱蜜莉雅',  # 艾米莉娅
    '12392': '冈部伦太郎',  # 冈部伦太郎
    '35615': '雷姆(Re:从零开始的异世界生活)',  # 蕾姆
    '24093': '泽村·斯宾塞·英梨梨',  # 泽村·史宾瑟·英梨梨
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
    '16684': '龙崎(虚拟UP主)',  # L
    '75': '猫咪老师',  # 喵先生/斑
    '15499': '散华礼弥(角色)',  # 散华礼弥
    '11909': '博士(日常)',  # 博士
}

bgm_index = json.load(open('bgm_index.json', encoding='utf-8'))
bgm_chars = json.load(open('bgm_chars.json', encoding='utf-8'))
moegirl_chars = json.load(open('../moegirl/preprocess/char_index.json', encoding='utf-8'))


def multimatch(bgm_name):
    ret = []
    for i in moegirl_chars:
        idx = i.find(bgm_name)
        if idx == 0:
            if len(bgm_name) == len(i):
                ret.append(i)
            else:
                if i[-1] == ')' and i[len(bgm_name)] == '(':
                    ret.append(i)
        elif idx > 0:
            if i[idx-1] == ':':
                ret.append(i)
    return ret


def is_postfix(a, b):
    if len(a) < len(b):
        offset = len(b)-len(a)
        return b[offset-1] == ':' and a == b[offset:]
    else:
        return a == b


def map_bgm(entry):
    id = str(entry['id'])
    if id in special_map:
        return special_map[id]
    canon_name = []
    names = []
    if id in bgm_chars:
        char = bgm_chars[id]
        names.extend(multisplit(char['name']))
        for i in char['infobox']:
            if i['key'] == '简体中文名':
                canon_name = multisplit(i['value'])
            elif i['key'] == '别名':
                for j in i['value']:
                    split = multisplit(j['v'])
                    names.extend(split)
        names = canon_name+names
    else:
        # fallback
        canon_name.append(entry['name'])

    ret = []
    for i in names:
        ret.extend(multimatch(i))
    if len(ret) == 0:
        print('{}: None, #{}'.format(id, names))
        return None
    elif len(ret) == 1:
        flag = True
        for i in names:
            if is_postfix(i, ret[0]):
                flag = False
                break
        if flag:
            print('{}: {}, #{}'.format(id, ret, names))
    elif ret[0] not in canon_name:
        print('{}: {}, #{}'.format(id, ret, names))
    return ret[0]


bgm_to_moegirl = {}
moegirl_to_bgm = {}
for cnt, i in enumerate(bgm_index):
    moegirl_id = map_bgm(i)
    bgm_id = i['id']
    print(cnt, bgm_id, i['name'], moegirl_id)
    bgm_to_moegirl[bgm_id] = moegirl_id
    if moegirl_id != None:
        moegirl_to_bgm[moegirl_id] = bgm_id

print(f'successful map: {len(moegirl_to_bgm)}')
save_json(bgm_to_moegirl, 'bgm_to_moegirl.json')
save_json(moegirl_to_bgm, 'moegirl_to_bgm.json')
