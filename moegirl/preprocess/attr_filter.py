from utils.file import load_json, save_json

attr_index = load_json('attr_index.json')
attr_index = set(attr_index)
data = load_json('../crawler/attrs.json')


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
    if i['name'] in ['按外貌特征分类', '按体型特征分类', '按年龄性征分类']:
        dfs(i, ret)
ret = list(ret)
print(ret)

save_json(ret, 'external_attr.json')
