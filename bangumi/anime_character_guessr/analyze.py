from utils.file import load_json

attr_index = load_json('../../moegirl/preprocess/attr_index.json')
bgm2moegirl = load_json('../../bangumi/bgm2moegirl.json')
bgm_index = load_json('../../bangumi/bgm_index_full.json')
new_tags = load_json('tags.new_tags.json')
char_tags = load_json('tags.character_tags.json')
char2attr = load_json('../../moegirl/preprocess/char2attr.json')

bgm_entry = {i['id']: i for i in bgm_index}

conv = {
    '茶色瞳': '棕瞳',
    '中二': '中二病',
    '单马尾': '马尾',
    '渐变发': '渐变色发',
    '白发': '银发',
    'tv': 'TV',
    '偶像': '偶像(萌属性)',
}

d = {}

for i in char_tags:
    bgmid = str(i['_id'])
    if bgmid not in bgm_entry:
        print('wtf?????????', bgmid)
        continue
    if bgmid not in bgm2moegirl:
        print('no mapping: ', bgmid, bgm_entry[bgmid])
    moeids = bgm2moegirl[bgmid]
    if len(moeids) != 1:
        continue
    print(bgmid, bgm_entry[bgmid]['name'], moeids)
    moeid = moeids[0]
    tags = []
    for tag in i['tagCounts']:
        tag = tag.replace(' ', '')
        if tag in conv:
            tag = conv[tag]
        if tag not in char2attr[moeid]:
            tags.append(tag)
    print(tags)


d = sorted(d.items(), key=lambda x: x[1], reverse=True)
for i in d[:100]:
    print(i[0], i[1])
