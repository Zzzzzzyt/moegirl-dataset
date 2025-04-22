from utils.file import load_json, save_json

attr_index = load_json('attr_index.json')
attr_index = set(attr_index)
data = load_json('../crawler/attrs.json')
attr2char = load_json('attr2char.json')
hair_color_attr = load_json('../crawler/hair_color_attr.json')
eye_color_attr = load_json('../crawler/eye_color_attr.json')


def dfs(data, ret):
    if 'name' in data:
        name = data['name']
        if name in attr_index:
            ret.add(name)
    for i in data['subcategories']:
        dfs(i, ret)


for i in data['subcategories']:
    if i['name'] == '按角色特征分类':
        data = i
        break

ret = set()
for i in data['subcategories']:
    tmp = set()
    if i['name'] in [
        '按外貌特征分类',
        '按体型特征分类',
        '按体质特征分类',
        '按年龄性征分类',
        '按种族分类',
        '按综合特征分类',
        '按特殊能力分类',
        '按嗜好习惯分类',
        '按人际关系分类',
        '按非职业身份分类',
        '按性格心理分类',
    ]:
        dfs(i, tmp)
        tmp2 = list(filter(lambda x: len(attr2char[x]) >= 100, tmp))
        tmp2.sort(key=lambda x: len(attr2char[x]), reverse=True)
        print(i['name'], tmp2)
        ret |= tmp

ret |= set(
    [
        '面具',
        '眼罩',
        '眼镜',
        '耳环',
        '耳钉',
    ]
)
ret = list(ret)
ret = list(filter(lambda x: len(attr2char[x]) >= 100, ret))
for i in hair_color_attr:
    if i not in ret:
        ret.append(i)
for i in eye_color_attr:
    if i not in ret:
        ret.append(i)
ret.sort(key=lambda x: len(attr2char[x]), reverse=True)
print()
print(ret)

save_json(ret, 'fundamental_attr.json')
