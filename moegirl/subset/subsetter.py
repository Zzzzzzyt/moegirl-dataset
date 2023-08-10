import json
import os


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


char_index = json.load(open('../preprocess/char_index.json', encoding='utf-8'))
# moegirl2bgm = json.load(open('../../bangumi/moegirl2bgm.json', encoding='utf-8'))
moegirl2bgm = None


def unique(a):
    s = set(a)
    ret = []
    for i in a:
        if i in s:
            s.remove(i)
            ret.append(i)
    return ret


def subset(out):
    ret = []
    for i in out['pages']:
        name = i['name']
        if name in char_index and (moegirl2bgm == None or name in moegirl2bgm):
            ret.append(name)
    for i in out['subcategories']:
        ret.extend(subset(i))
    return unique(ret)


def subset2(name):
    sub = subset(json.load(open(f'../crawler/subset_uncensored/{name}_out.json', encoding='utf-8')))
    out = f'subset/{name}_subset.json'
    if os.path.exists(out):
        oldsub = json.load(open(out, encoding='utf-8'))
        if set(oldsub) == set(sub):
            print(f'subset {name} size={len(oldsub)} same:skipped')
            return
    print(f'subset {name} size={len(sub)}')
    save_json(sub, out)


l = os.listdir('../crawler/subset_uncensored/')
for i in l:
    if i.endswith('_out.json'):
        subset2(i.replace('_out.json', ''))
