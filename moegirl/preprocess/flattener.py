import json


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


def dfs(data: dict, ret: list, depth=0):
    pages = []
    if depth != 0:
        pages.extend(data['pages'])
    for i in data['subcategories']:
        pages2 = dfs(i, ret, depth+1)
        pages.extend(pages2)
    if depth != 0 and len(pages) > 0:
        tmp = {'name': data['name'], 'pages': pages}
        if 'article' in data and 'action=edit' not in data['article']['url']:
            tmp['article'] = data['article']
        ret.append(tmp)
    return pages


data = json.load(open('../crawler/final.json', encoding='utf-8'))

res = []
dfs(data, res)
res.sort(key=lambda x: len(x['pages']))

# for i in res:
# print(i['name'], len(i['pages']))

# char_filter = json.load(open('../../bangumi/moegirl_to_bgm.json', encoding='utf-8'))


def char_filter(page: str):
    return page.startswith('Template:')


char_index = {}
attr_index = {}
for i in res:
    cnt = 0
    for j in i['pages']:
        page = j['page']
        url = j['url']
        pg2 = '/'+page.replace(' ', '_')
        assert pg2 == url
        if char_filter(page):
            continue
        cnt += 1
        if page not in char_index:
            char_index[page] = {'name': page}
        # else:
        #     current = char_index[page]
        #     if json.dumps(current) != json.dumps(j):
        #         print(j)
    if cnt > 0:
        tmp = {'name': i['name']}
        if 'article' in i:
            tmp['article'] = i['article']['page']
        attr_index[i['name']] = tmp

save_json(char_index, 'char_index.json')
save_json(attr_index, 'attr_index.json')

print('attribute count: {}'.format(len(attr_index)))
print('character count: {}'.format(len(char_index)))

char2attr = {}
attr2char = {}
for i in res:
    if i['name'] not in attr_index:
        continue
    if i['name'] in attr2char:
        continue
    chars = []
    for j in i['pages']:
        page = j['page']
        if char_filter(page):
            continue
        chars.append(page)
        url = j['url']
        if page not in char2attr:
            char2attr[page] = []
        if i['name'] not in char2attr[page]:
            char2attr[page].append(i['name'])
    if len(chars) > 0:
        attr2char[i['name']] = chars

save_json(attr2char, 'attr2char.json')
save_json(char2attr, 'char2attr.json')
