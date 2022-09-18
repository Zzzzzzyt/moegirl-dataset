import json
import numpy

attrs = json.load(open('attr_index.json', encoding='utf-8'))
P = numpy.load(open('conditional.npy', 'rb'), allow_pickle=True)
attrmap = {}
for i in range(len(attrs)):
    attrmap[attrs[i]] = i


def query_attr(x, limit=None):
    tmp = []
    attrid = attrmap[x]
    for i in range(len(attrs)):
        if i == attrid:
            continue
        tmp.append((P[attrid][i], attrs[i]))
    tmp.sort()
    if limit:
        tmp = tmp[-limit:]
    return tmp


hair_color_attr = json.load(open('../crawler/hair_color_attr.json', encoding='utf-8'))

tmp = query_attr('傲娇')
for i in tmp:
    if i[1] in hair_color_attr:
        print(i)
