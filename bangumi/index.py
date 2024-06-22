import json
from functools import cmp_to_key

from utils.file import save_json


bgm_chars = json.load(open('bgm_chars_160k.json', encoding='utf-8'))
ret = []

for k, v in bgm_chars.items():
    if str(v['id']) != k:
        continue
    ret.append({'id': k, 'name': v['name'], 'comments': v['stat']['comments'], 'collects': v['stat']['collects']})


def cmp(a, b):
    if a['collects'] != b['collects']:
        return -a['collects']+b['collects']
    if a['comments'] != b['comments']:
        return -a['comments']+b['comments']
    return int(a['id'])-int(b['id'])


print(len(ret))
ret.sort(key=cmp_to_key(cmp))

for rank, i in enumerate(ret):
    i['rank'] = rank+1

print(ret[0])
print(ret[-1])
save_json(ret, 'bgm_index_160k.json')
