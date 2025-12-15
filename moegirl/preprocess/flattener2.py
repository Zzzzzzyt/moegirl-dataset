from utils.file import load_json, save_json,chdir_project_root
from utils.network import title_to_url

chdir_project_root()

chars: set[str] = set(load_json('moegirl/preprocess/char_index.json'))
subjects: dict = load_json('moegirl/crawler/subjects.json')
attr_index: set[str] = set(load_json('moegirl/preprocess/attr_index.json'))


def dfs(data: dict, ret: dict, stk: list = []):
    if 'name' in data:
        rname = data['name']
        rurl = data['url']
        if '/Category:' + rname.replace(' ', '_') != rurl:
            print(data)
        assert '/Category:' + rname.replace(' ', '_') == rurl
        if rname in ['白眼', '轮回眼', '写轮眼', 'MS少女']:
            return
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


char2subject: dict[str, list[str]] = {}
dfs(subjects, char2subject, [])
# for k, v in ret.items():
# print(k, v)
print('all:', len(chars))
print('found:', len(char2subject))
save_json(char2subject, 'moegirl/preprocess/char2subject.json')

subject_index: list[str] = []
for i in subjects['subcategories'][3:]:
    for j in i['subcategories']:
        name, url = j['name'], j['url']
        assert '/Category:' + name.replace(' ', '_') == url
        subject_index.append(name)

save_json(subject_index, 'moegirl/preprocess/subject_index.json')
