import json
import os
from functools import cmp_to_key
from utils.file import save_json

bgm_chars = {}
bgm_subjects = {}
redirects = {}

for i in range(1, 200):
    f = f'160k_chars/bgm_chars_160k_{i}.json'
    if not os.path.exists(f):
        continue
    cur = open(f, encoding='utf-8').read()
    data = json.loads(cur)
    for k, v in data.items():
        if len(v) == 0:
            continue
        if k != str(v['id']):
            redirects[k] = v['id']
        else:
            assert k not in bgm_chars
            bgm_chars[k] = v
    print(i, len(data))

for i in range(1, 200):
    f = f'160k_subjects/bgm_subjects_160k_{i}.json'
    if not os.path.exists(f):
        continue
    cur = open(f, encoding='utf-8').read()
    data = json.loads(cur)
    cnt = 0
    for k, v in data.items():
        if len(v) != 0:
            bgm_subjects[k] = v
            cnt += 1
    # ret2.update(data)
    print(i, cnt)

bgm_index = []

for k, v in bgm_chars.items():
    if str(v['id']) != k:
        continue
    bgm_index.append(
        {
            'id': k,
            'name': v['name'],
            'comments': v['stat']['comments'],
            'collects': v['stat']['collects'],
        }
    )


def cmp(a, b):
    if a['collects'] != b['collects']:
        return -a['collects'] + b['collects']
    if a['comments'] != b['comments']:
        return -a['comments'] + b['comments']
    return int(a['id']) - int(b['id'])

bgm_index.sort(key=cmp_to_key(cmp))

for rank, i in enumerate(bgm_index):
    i['rank'] = rank + 1

print(bgm_index[0])
print(bgm_index[-1])
print('bgm_index:', len(bgm_index))
print('bgm_chars:', len(bgm_chars))
print('bgm_subjects:', len(bgm_subjects))
print('bgm_redirects:', len(redirects))

save_json(bgm_index, 'bgm_index_160k.json')
save_json(bgm_chars, 'bgm_chars_160k.json')
save_json(bgm_subjects, 'bgm_subjects_160k.json')
save_json(redirects, 'bgm_redirects_160k.json')
