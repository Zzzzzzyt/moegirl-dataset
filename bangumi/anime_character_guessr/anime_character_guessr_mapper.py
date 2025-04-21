from utils.file import load_json, save_json

bgm2moegirl = load_json('../bgm2moegirl.json')
bgm_index = load_json('../bgm_index_full.json')
char2attr = load_json('../../moegirl/preprocess/char2attr.json')
attr2char = load_json('../../moegirl/preprocess/attr2char.json')
fundamental_attr = set(load_json('../../moegirl/preprocess/fundamental_attr.json'))
bgm_entry = {entry['id']: entry for entry in bgm_index}

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

bgm2attr = []
for k, v in bgm2moegirl.items():
    if len(v) == 0:
        continue
    if len(v) > 1:
        continue
    moeid = v[0]
    assert moeid in char2attr
    attrs = char2attr[moeid]
    tmp = []
    for i in attrs:
        if i in fundamental_attr:
            tmp.append(i)
    tmp.sort(key=lambda x: len(attr2char[x]), reverse=True)
    for i in range(len(tmp)):
        tmp[i] = tmp[i].replace('(萌属性)', '')
    # print(moeid, tmp)
    if len(tmp) == 0:
        continue
    if '光头' in tmp:
        for i in hair_attrs:
            if i in tmp:
                tmp.remove(i)
    bgm2attr.append((k, tmp))

bgm2attr.sort(key=lambda x: bgm_entry[x[0]]['rank'])
bgm2attr = dict(bgm2attr)
print('mapped:', len(bgm2attr))
# save_json(bgm2attr, 'filtered_id_tags_mapping.json')

with open("id_tags.js", "w", encoding='utf-8') as f:
    f.write('export const idToTags = {')
    tmp = []
    for k, v in bgm2attr.items():
        tmp.append(str(k) + ':[' + ','.join(map(lambda x: f'"{x}"', v)) + ']')
    f.write(','.join(tmp))
    f.write('};')
