from utils.file import load_json, save_json
from utils.network import title_to_url


chars = set(load_json('char_index.json'))
data = load_json('../crawler/subjects.json')


def dfs(data, ret, stk: list = []):
    if 'name' in data:
        rname = data['name']
        rurl = data['url']
        if '/Category:' + rname.replace(' ', '_') != rurl:
            print(data)
        assert '/Category:' + rname.replace(' ', '_') == rurl
        stk.append(rname)
    if 'pages' in data:
        for i in data['pages']:
            name = i['name']
            url = i['url']
            if '/' + name.replace(' ', '_') != url:
                print(i)
            assert '/' + name.replace(' ', '_') == url
            if name in chars:
                # print(name, stk)
                if name in ret:
                    stk2 = ret[name]
                    for j in stk:
                        if j not in stk2:
                            stk2.append(j)
                else:
                    ret[name] = stk.copy()
    if 'subcategories' in data:
        for i in data['subcategories']:
            dfs(i, ret, stk)
    if 'name' in data:
        stk.pop()


ret = {}
dfs(data, ret, [])
# for k, v in ret.items():
# print(k, v)
print('all:', len(chars))
print('found:', len(ret))
save_json(ret, 'char2subject.json')
