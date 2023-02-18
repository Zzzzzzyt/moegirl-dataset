import json


def save_json(data, path):
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


bgm_index = json.load(open('../bgm_index_120k.json', encoding='utf-8'))
bgm2moegirl = json.load(open('../bgm2moegirl.json', encoding='utf-8'))
char_index = json.load(open('../../moegirl/preprocess/char_index.json', encoding='utf-8'))


def topk(k):
    st = set()
    ret = []
    cnt = 0
    trueCnt = 0
    for i in bgm_index:
        trueCnt += 1
        if i['id'] not in bgm2moegirl:
            continue
        moeid = bgm2moegirl[i['id']]
        # print(moeid)
        if len(moeid) == 0:
            continue
        mid = moeid[0]
        if mid not in char_index:
            continue
        if mid in st:
            continue
        st.add(mid)
        ret.append(mid)
        cnt += 1
        if cnt >= k:
            break
    print(f'k={k} size={len(ret)} trueCnt={trueCnt}')
    return ret


save_json(topk(200), 'bgm200_subset.json')
save_json(topk(2000), 'bgm2000_subset.json')
save_json(topk(20000), 'bgm20000_subset.json')
