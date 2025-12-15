import json

from utils.file import save_json, chdir_project_root

chdir_project_root()

bgm_index = json.load(open('bangumi/bgm_index_full.json', encoding='utf-8'))
bgm2moegirl = json.load(open('bangumi/bgm2moegirl.json', encoding='utf-8'))
moegirl2bgm = json.load(open('bangumi/moegirl2bgm.json', encoding='utf-8'))
char_index = json.load(open('moegirl/preprocess/char_index.json', encoding='utf-8'))
char_index = set(char_index)


def topk(k):
    st = set()
    ret = []
    trueCnt = 0
    for i in bgm_index:
        trueCnt += 1
        id = str(i['id'])
        if id not in bgm2moegirl:
            continue
        moeids = bgm2moegirl[id]
        # print(moeid)
        if len(moeids) == 0:
            continue
        for mid in moeids:
            if mid in st:
                continue
            if mid not in moegirl2bgm:
                continue
            if mid not in char_index:
                continue
            bids = moegirl2bgm[mid]
            if len(bids) == 0:
                continue
            if bids[0] != id:
                continue
            st.add(mid)
            ret.append(mid)
            break
        if len(ret) >= k:
            break
    print(f'k={k} size={len(ret)} trueCnt={trueCnt}')
    return ret


save_json(topk(200), 'bangumi/subset/bgm200_subset.json')
save_json(topk(2000), 'bangumi/subset/bgm2000_subset.json')
save_json(topk(20000), 'bangumi/subset/bgm20000_subset.json')
