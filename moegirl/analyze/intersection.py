import json
from re import L
import numpy as np
from tqdm import tqdm

from utils.file import chdir_project_root

chdir_project_root()

attr2char = json.load(open('moegirl/preprocess/attr2char.json', encoding='utf-8'))

chars = json.load(open('moegirl/preprocess/char_index.json', encoding='utf-8'))
attrs = json.load(open('moegirl/preprocess/attr_index.json', encoding='utf-8'))

charmap = {}
attrmap = {}
for idx, i in enumerate(chars):
    charmap[i] = idx
for idx, i in enumerate(attrs):
    # if len(attr2char[i]) < 100:
    #     continue
    attrmap[i] = idx

char_count = len(chars)
attr_count = len(attrs)

print('char_count: {}'.format(char_count))
print('attr_count: {}'.format(attr_count))

cross = np.zeros(shape=[attr_count, char_count], dtype=np.bool_)
count = np.zeros((attr_count), dtype=np.int32)
tot = []
for i in range(attr_count):
    attr = attrs[i]
    for j in attr2char[attr]:
        charid = charmap[j]
        cross[i][charid] = True
    count[i] = len(attr2char[attr])

# result = []
intersection = np.zeros(shape=[attr_count, attr_count], dtype=np.int32)
with tqdm(total=attr_count * (attr_count - 1) // 2 + attr_count) as pbar:
    for i in range(attr_count):
        intersection[i][i] = cross[i].sum()
        pbar.update(1)
        for j in range(i + 1, attr_count):
            intersection[i][j] = (cross[i] & cross[j]).sum()
            intersection[j][i] = intersection[i][j]
            # result.append((attrs[i], attrs[j], chi2, table))
            pbar.update(1)

# json.dump(attrs, open('moegirl/analyze/attr_ids.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
np.save(open('moegirl/analyze/intersection.npy', 'wb'), intersection, allow_pickle=False)
np.save(open('moegirl/analyze/cross.npy', 'wb'), cross, allow_pickle=False)
np.save(open('moegirl/analyze/count.npy', 'wb'), count, allow_pickle=False)