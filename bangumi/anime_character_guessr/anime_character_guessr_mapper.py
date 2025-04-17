from utils.file import load_json, save_json

bgm2moegirl = load_json('../bgm2moegirl.json')
bgm_index = load_json('../bgm_index_full.json')
char2attr = load_json('../../moegirl/preprocess/char2attr.json')
attr2char = load_json('../../moegirl/preprocess/attr2char.json')
fundamental_attr = set(load_json('../../moegirl/preprocess/fundamental_attr.json'))
bgm_entry = {entry['id']: entry for entry in bgm_index}

bgm2attr = []
for k, v in bgm2moegirl.items():
    if len(v) == 0:
        continue
    if len(v) > 1:
        continue
    moeid = v[0]
    assert moeid in char2attr
    attrs = char2attr[moeid]
    tmp = []
    for i in attrs:
        if i in fundamental_attr:
            tmp.append(i)
    tmp.sort(key=lambda x: len(attr2char[x]), reverse=True)
    for i in range(len(tmp)):
        tmp[i] = tmp[i].replace('(萌属性)', '')
    # print(moeid, tmp)
    if len(tmp) == 0:
        continue
    bgm2attr.append((k, tmp))

bgm2attr.sort(key=lambda x: bgm_entry[x[0]]['rank'])
bgm2attr = dict(bgm2attr)
print('mapped:', len(bgm2attr))
# save_json(bgm2attr, 'filtered_id_tags_mapping.json')

with open("id_tags.js", "w", encoding='utf-8') as f:
    f.write('export const idToTags = {')
    tmp = []
    for k, v in bgm2attr.items():
        tmp.append(str(k) + ':[' + ','.join(map(lambda x: f'"{x}"', v)) + ']')
    f.write(','.join(tmp))
    f.write('};')
