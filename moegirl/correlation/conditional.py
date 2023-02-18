import json
import numpy as np
from tqdm import tqdm

attrs = json.load(open('attr_ids.json', encoding='utf-8'))
chars = json.load(open('../preprocess/char_index.json', encoding='utf-8'))
P = np.load(open('intersection.npy', 'rb'))
attr_count = len(attrs)
char_count = len(chars)
attrmap = {}
for i in range(len(attrs)):
    attrmap[attrs[i]] = i


def query_attr(x, limit=None):
    tmp = []
    attrid = attrmap[x]
    paa = P[attrid][attrid]
    for i in range(len(attrs)):
        if i == attrid:
            continue
        pai = P[attrid][i]
        pii = P[i][i]
        tmp.append(((pai / paa) / (pii/char_count), pai, pii, pai/paa, attrs[i]))
    tmp.sort()
    if limit:
        tmp = tmp[-limit:]
    return tmp


def calc(x, y):
    pxy = P[x][y]
    pxx = P[x][x]
    pyy = P[y][y]
    return ((pxy/pxx)/(pyy/char_count), pxy, pxx, pxy/pxx)


def calc_name(x, y):
    xx = attrmap[x]
    yy = attrmap[y]
    res = calc(x, y)
    return tuple(list(res)+[xx, yy])

# hair_color_attr = json.load(open('../crawler/hair_color_attr.json', encoding='utf-8'))

# tmp = query_attr('傲娇')
# for i in tmp:
#     # if i[-1] in hair_color_attr:
#     if i[2] > 30 and i[3] > 0.01:
#         print(i)


res = np.zeros(shape=[attr_count, attr_count], dtype=np.int32)
with tqdm(total=attr_count*(attr_count-1)//2+attr_count) as pbar:
    for i in range(attr_count):
        for j in range(i, attr_count):
            res[i][j] = calc(i, j)[0]
            res[j][i] = res[i][j]
            # result.append((attrs[i], attrs[j], chi2, table))
            pbar.update(1)

np.save(open('gain.npy', 'wb'), res)
