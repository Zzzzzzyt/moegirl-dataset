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


def calc_chi2(arr, x, y):
    #   F T x
    # F a b
    # T c d
    # y
    d = int((arr[x] & arr[y]).sum())
    totx = tot[x]
    toty = tot[y]
    c = toty-d
    b = totx-d
    a = char_count-b-c-d
    chi2 = (char_count)*(a*d-b*c)**2/(char_count-totx)/totx/(char_count-toty)/toty
    return chi2, [[a, b], [c, d]]


result = []
P = np.zeros(shape=[attr_count, attr_count], dtype=np.float32)
Chi2 = np.zeros(shape=[attr_count, attr_count], dtype=np.float32)
with tqdm(total=attr_count*(attr_count-1)//2) as pbar:
    for i in range(attr_count):
        for j in range(i+1, attr_count):
            chi2, table = calc_chi2(data, i, j)
            # if table[0][1] == 0 or table[1][0] == 0:
            #     continue
            result.append((attrs[i], attrs[j], chi2, table))
            Chi2[i][j] = chi2
            Chi2[j][i] = chi2
            P[i][j] = table[1][1]/(table[1][1]+table[0][1])
            P[j][i] = table[1][1]/(table[1][1]+table[1][0])
            pbar.update(1)

json.dump(attrs, open('attr_index.json', 'w', encoding='utf-8'), ensure_ascii=False)
P.dump(open('conditional.npy', 'wb'))
Chi2.dump(open('chi2.npy', 'wb'))
