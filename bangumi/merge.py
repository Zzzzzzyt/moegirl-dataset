import json
import os

from utils.file import save_json

ret = {}
ret2 = {}
redirects = {}

for i in range(1, 161):
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
            assert k not in ret
            ret[k] = v
    print(i, len(data))

for i in range(1, 161):
    f = f'160k_subjects/bgm_subjects_160k_{i}.json'
    if not os.path.exists(f):
        continue
    cur = open(f, encoding='utf-8').read()
    data = json.loads(cur)
    cnt = 0
    for k, v in data.items():
        if len(v) != 0:
            ret2[k] = v
            cnt += 1
    # ret2.update(data)
    print(i, cnt)

print(len(ret))
print(len(ret2))
print(len(redirects))

save_json(ret, 'bgm_chars_160k.json')
save_json(ret2, 'bgm_subjects_160k.json')
save_json(redirects, 'bgm_redirects_160k.json')
