import json
import numpy

attrs = json.load(open('attr_index.json', encoding='utf-8'))
chars = json.load(open('../preprocess/char_index.json', encoding='utf-8'))
P = numpy.load(open('intersection.npy', 'rb'), allow_pickle=True)
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


hair_color_attr = json.load(open('../crawler/hair_color_attr.json', encoding='utf-8'))

tmp = query_attr('傲娇')
for i in tmp:
    # if i[-1] in hair_color_attr:
        if i[3] > 0.01:
            print(i)
