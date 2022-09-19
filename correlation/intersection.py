import json
from re import L
import numpy as np
import scipy.stats
from tqdm import tqdm

attr2char = json.load(open('../preprocess/attr2char.json', encoding='utf-8'))

char_index = json.load(open('../preprocess/char_index.json', encoding='utf-8'))
attr_index = json.load(open('../preprocess/attr_index.json', encoding='utf-8'))

chars = []
charmap = {}
attrs = []
attrmap = {}
for i in char_index:
    charmap[i] = len(chars)
    chars.append(i)
for i in attr_index:
    # if len(attr2char[i]) < 100:
    #     continue
    attrmap[i] = len(attrs)
    attrs.append(i)

char_count = len(chars)
attr_count = len(attrs)

print('char_count: {}'.format(char_count))
print('attr_count: {}'.format(attr_count))

data = np.zeros(shape=[attr_count, char_count], dtype=np.bool8)
tot = []
for i in range(attr_count):
    attr = attrs[i]
    for j in attr2char[attr]:
        charid = charmap[j]
        data[i][charid] = True
    tot.append(len(attr2char[attr]))


# result = []
intersection = np.zeros(shape=[attr_count, attr_count], dtype=np.int32)
with tqdm(total=attr_count*(attr_count-1)//2+attr_count) as pbar:
    for i in range(attr_count):
        intersection[i][i] = data[i].sum()
        for j in range(i+1, attr_count):
            intersection[i][j] = (data[i] & data[j]).sum()
            intersection[j][i] = intersection[i][j]
            # result.append((attrs[i], attrs[j], chi2, table))
            pbar.update(1)

json.dump(attrs, open('attr_index.json', 'w', encoding='utf-8'), ensure_ascii=False)
intersection.dump(open('intersection.npy', 'wb'))
