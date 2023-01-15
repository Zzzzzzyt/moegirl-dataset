import json


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)


bgm_index = json.load(open('../bgm_index.json', encoding='utf-8'))
bgm2moegirl = json.load(open('../bgm2moegirl.json', encoding='utf-8'))


def topk(k):
    ret = []
    cnt = 0
    for i in bgm_index:
        if str(i['id']) not in bgm2moegirl:
            continue
        moeid = bgm2moegirl[str(i['id'])]
        print(moeid)
        if len(moeid) == 0:
            continue
        ret.append(moeid[0])
        cnt += 1
        if cnt > k:
            return ret
    return ret


save_json(topk(200), 'bgm200_subset.json')
save_json(topk(2000), 'bgm2000_subset.json')
save_json(topk(20000), 'bgm20000_subset.json')
