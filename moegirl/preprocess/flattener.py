import json


def dfs(data: dict, ret: list, depth=0):
    pages = []
    if depth != 0:
        pages.extend(data['pages'])
    for i in data['subcategories']:
        pages2 = dfs(i, ret, depth+1)
        pages.extend(pages2)
    if depth != 0 and len(pages) > 0:
        tmp = {'name': data['name'], 'pages': pages}
        if 'article' in data and not data['article']['url'].startswith('/index.php?title='):
            tmp['article'] = data['article']
        ret.append(tmp)
    return pages


data = json.load(open('../crawler/final.json', encoding='utf-8'))

res = []
dfs(data, res)
res.sort(key=lambda x: len(x['pages']))

# for i in res:
#     print(i['name'], len(i['pages']))

char_index = {}
attr_index = {}
for i in res:
    tmp = i.copy()
    tmp.pop('pages')
    attr_index[i['name']] = tmp
    for j in i['pages']:
        page = j['page']
        url = j['url']
        if page not in char_index:
            char_index[page] = j
        # else:
        #     current = char_index[page]
        #     if json.dumps(current) != json.dumps(j):
        #         print(j)
# print(char_index)
# print(attr_index)
json.dump(char_index, open('char_index.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(attr_index, open('attr_index.json', 'w', encoding='utf-8'), ensure_ascii=False)

print('attribute count: {}'.format(len(attr_index)))
print('character count: {}'.format(len(char_index)))

char2attr = {}
attr2char = {}
for i in res:
    if i['name'] in attr2char:
        continue
    chars = []
    for j in i['pages']:
        chars.append(j['page'])
        page = j['page']
        url = j['url']
        if page not in char2attr:
            char2attr[page] = []
        if i['name'] not in char2attr[page]:
            char2attr[page].append(i['name'])
    attr2char[i['name']] = chars

json.dump(attr2char, open('attr2char.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(char2attr, open('char2attr.json', 'w', encoding='utf-8'), ensure_ascii=False)
