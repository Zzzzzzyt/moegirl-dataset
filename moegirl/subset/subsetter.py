import json


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


char_index = json.load(open('../preprocess/char_index.json', encoding='utf-8'))
moegirl_to_bgm = json.load(open('../../bangumi/moegirl_to_bgm.json', encoding='utf-8'))

def subset(out):
    ret = []
    for i in out['pages']:
        if i['page'] in char_index and i['page'] in moegirl_to_bgm:
            ret.append(i)
    for i in out['subcategories']:
        ret.extend(subset(i))
    return ret

touhou_subset = subset(json.load(open('../crawler/touhou_out.json', encoding='utf-8')))
save_json(touhou_subset, 'touhou_subset.json')

toaru_subset = subset(json.load(open('../crawler/toaru_out.json', encoding='utf-8')))
save_json(toaru_subset, 'toaru_subset.json')

kyoani_subset = subset(json.load(open('../crawler/kyoani_out.json', encoding='utf-8')))
save_json(kyoani_subset, 'kyoani_subset.json')