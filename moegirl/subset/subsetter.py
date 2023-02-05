import json


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


char_index = json.load(open('../preprocess/char_index.json', encoding='utf-8'))
# moegirl2bgm = json.load(open('../../bangumi/moegirl2bgm.json', encoding='utf-8'))
moegirl2bgm = None


def subset(out):
    ret = set()
    for i in out['pages']:
        name = i['page']
        if name in char_index and (moegirl2bgm == None or name in moegirl2bgm):
            ret.add(name)
    for i in out['subcategories']:
        ret.update(subset(i))
    return list(ret)


def subset2(name):
    sub = subset(json.load(open(f'../crawler/subset/{name}_out.json', encoding='utf-8')))
    print(f'subset {name} size={len(sub)}')
    save_json(sub, f'{name}_subset.json')


# subset2('touhou_new')
# subset2('touhou_old')
# subset2('toaru')
# subset2('kyoani')
# subset2('arknights')
# subset2('genshin')
# subset2('fate')
# subset2('jojo')
# subset2('gundam')
# subset2('naruto')
# subset2('zzzyt')
# subset2('furry')
# subset2('lovelive')