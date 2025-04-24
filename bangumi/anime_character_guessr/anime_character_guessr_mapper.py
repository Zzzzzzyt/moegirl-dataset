from utils.file import load_json, save_json

bgm2moegirl = load_json('../bgm2moegirl.json')
bgm_index = load_json('../bgm_index_full.json')
char2attr = load_json('../../moegirl/preprocess/char2attr.json')
attr2char = load_json('../../moegirl/preprocess/attr2char.json')
fundamental_attr = set(load_json('../../moegirl/preprocess/fundamental_attr.json'))
user_char_tags_raw = load_json('tags.character_tags.json')

conv = {
    '茶色瞳': '棕瞳',
    '中二': '中二病',
    '单马尾': '马尾',
    '渐变发': '渐变色发',
    '白发': '银发',
    'tv': 'TV',
    '偶像': '偶像(萌属性)',
}

bgm_entry = {entry['id']: entry for entry in bgm_index}

user_char_tags = {}
for i in user_char_tags_raw:
    id = str(i['_id'])
    tagCounts = i['tagCounts']
    tags = {}
    for k, v in tagCounts.items():
        if k in conv:
            k = conv[k]
        tags[k] = v
    user_char_tags[id] = tags


hair_attrs = [
    '黑发',
    '银发',
    '金发',
    '棕发',
    '蓝发',
    '长直',
    '短发',
    '呆毛',
    '紫发',
    '粉发',
    '红发',
    '双马尾',
    '长发',
    '绿发',
    '卷发',
    '黑长直',
    '橙发',
    '高马尾',
    '挑染',
    '马尾',
    '麻花辫',
    '长鬓角',
    '齐刘海',
    '遮单眼发',
    'M形刘海',
    '下双马尾',
    '中长发',
    '妹妹头',
    '渐变色发',
    '进气口发型',
    '侧单马尾',
    '披肩双马尾',
    '中分',
    '姬发式',
    '斜刘海',
    '束鬓',
    '半马尾',
    '偏分',
    '双麻花辫',
    '低马尾',
    '不对称鬓发',
    '长卷发',
    '丸子头',
    '乱发',
    '内层挑染',
    '环形辫',
    '双丸子头',
    '长刘海',
    '双色发',
    '遮耳发',
    '盘发',
    '人字刘海',
    '尾扎长发',
    '单麻花辫',
    '另类发型',
    '大背头',
    '刺猬头',
    '双螺旋',
    '鬓角麻花辫',
    '龙须刘海',
    '精灵耳发型',
    '短刘海',
    '死亡发型',
    '翻翘',
    '公主辫',
    '两根呆毛',
    '变发色',
    '交叉刘海',
    '刘海尾',
    '辫子',
]

priority_attrs_raw = [
    "渐变瞳",
    "彩虹瞳",
    "异色瞳",
    "挑染",
    "双色发",
    "彩虹发",
    "多色发",
    "阴阳发",
    "光头",
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
]

priority_attrs = {}

for idx, i in enumerate(priority_attrs_raw):
    priority_attrs[i] = (len(priority_attrs_raw) - idx) * 1000000

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
    # "双色发",
    # "彩虹发",
    # "多色发",
    # "阴阳发",
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
    # "异色瞳",
    # "渐变瞳",
    # "彩虹瞳",
]


def merge_user(bgmid, tags, user_tags):
    # tags.sort(key=value_func, reverse=True)

    multicolor_hair = False

    merged_tags = tags + list(
        map(lambda x: x[0], filter(lambda x: x[1] > 1, user_tags.items()))
    )
    if (
        '双色发' in merged_tags
        or '渐变色发' in merged_tags
        or '彩虹发' in merged_tags
        or '多色发' in merged_tags
        or '阴阳发' in merged_tags
        or '挑染' in merged_tags
        or '内层挑染' in merged_tags
        or '变发色' in merged_tags
    ):
        multicolor_hair = True

    multicolor_eye = False
    if '异色瞳' in merged_tags or '渐变瞳' in merged_tags or '彩虹瞳' in merged_tags:
        multicolor_eye = True

    d = {}
    d_hair = {}
    d_eye = {}
    for tag in tags:
        if tag in hair_color_attr:
            d_hair[tag] = 4
        elif tag in eye_color_attr:
            d_eye[tag] = 4
        else:
            d[tag] = 4

    original_hair = list(d_hair.keys())
    original_eye = list(d_eye.keys())

    for tag, count in user_tags.items():
        if count <= 1:
            continue
        if tag in hair_color_attr:
            # for i in hair_color_attr:
            #     if i != tag:
            #         d_hair[i] = d_hair.get(i, 0) - count
            d_hair[tag] = d_hair.get(tag, 0) + count
        elif tag in eye_color_attr:
            # for i in eye_color_attr:
            #     if i != tag:
            #         d_eye[i] = d_eye.get(i, 0) - count
            d_eye[tag] = d_eye.get(tag, 0) + count
        else:
            d[tag] = d.get(tag, 0) + count

    ret = []
    for tag, count in d.items():
        if count >= 2:
            ret.append(tag)

    d_hair = sorted(
        filter(lambda x: x[1] > 1, list(d_hair.items())),
        key=lambda x: x[1],
        reverse=True,
    )
    d_eye = sorted(
        filter(lambda x: x[1] > 1, list(d_eye.items())),
        key=lambda x: x[1],
        reverse=True,
    )

    ret_hair = original_hair.copy()
    if multicolor_hair:
        if len(d_hair) < 2:
            pass
        elif len(d_hair) == 2:
            ret_hair = [d_hair[0][0], d_hair[1][0]]
        else:
            if d_hair[1][1] >= d_hair[2][1] * 2:
                ret_hair = [d_hair[0][0], d_hair[1][0]]
    else:
        if len(d_hair) < 1:
            pass
        elif len(d_hair) == 1:
            ret_hair = [d_hair[0][0]]
        else:
            if d_hair[0][1] >= d_hair[1][1] * 2:
                ret_hair = [d_hair[0][0]]

    ret_eye = original_eye.copy()
    if multicolor_eye:
        if len(d_eye) < 2:
            pass
        elif len(d_eye) == 2:
            ret_eye = [d_eye[0][0], d_eye[1][0]]
        else:
            if d_eye[1][1] >= d_eye[2][1] * 2:
                ret_eye = [d_eye[0][0], d_eye[1][0]]
    else:
        if len(d_eye) < 1:
            pass
        elif len(d_eye) == 1:
            ret_eye = [d_eye[0][0]]
        else:
            if d_eye[0][1] >= d_eye[1][1] * 2:
                ret_eye = [d_eye[0][0]]

    ret = ret_hair + ret_eye + ret
    # ret.sort(key=value_func, reverse=True)

    if set(ret_eye) != set(original_eye) or set(ret_hair) != set(original_hair):
        print(bgmid, bgm_entry[bgmid]['name'])
        print(bgm2moegirl[bgmid])
        print(tags)
        print(user_tags)
        print(d)
        print(d_hair)
        print(d_eye)
        print(ret)
        print(original_hair, ret_hair)
        print(original_eye, ret_eye)
        print()

    # if set(ret) != set(tags):
    #     print(bgmid, bgm_entry[bgmid]['name'])
    #     print(bgm2moegirl[bgmid])
    #     print(tags)
    #     print(user_tags)
    #     print(ret)
    #     print()

    return ret


bgm2attr = []
for k, v in bgm2moegirl.items():
    if len(v) == 0:
        continue
    if len(v) > 1:
        continue
    moeid = v[0]
    assert moeid in char2attr
    attrs = char2attr[moeid]
    tags = []
    for i in attrs:
        if i in fundamental_attr:
            tags.append(i)

    def value_func(x):
        if x in priority_attrs:
            return priority_attrs[x] * 100000
        if x in attr2char:
            return len(attr2char[x])
        return 0

    for i in range(len(tags)):
        tags[i] = tags[i].replace('(萌属性)', '')
    # print(moeid, tmp)
    if '光头' in tags:
        for i in hair_attrs:
            if i in tags:
                tags.remove(i)

    if k in user_char_tags:
        tags = merge_user(k, tags, user_char_tags[k])

    tags.sort(key=value_func, reverse=True)
    if len(tags) == 0:
        continue
    bgm2attr.append((k, tags))

bgm2attr.sort(key=lambda x: bgm_entry[x[0]]['rank'])
bgm2attr = dict(bgm2attr)
print('mapped:', len(bgm2attr))
save_json(bgm2attr, 'id_tags.json')

with open("id_tags.js", "w", encoding='utf-8') as f:
    f.write('export const idToTags = {\n')
    tags = []
    for k, v in bgm2attr.items():
        tags.append(str(k) + ':[' + ','.join(map(lambda x: f'"{x}"', v)) + ']')
    f.write(',\n'.join(tags))
    f.write('\n};')
