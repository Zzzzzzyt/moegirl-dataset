import json
import os
import time
from utils.file import load_json, save_json,chdir_project_root

chdir_project_root()

char_index = load_json('moegirl/char_index.json')
attr_index = load_json('moegirl/attr_index.json')
attr2char = load_json('moegirl/attr2char.json')
char2attr = load_json('moegirl/char2attr.json')
attr2article = load_json('moegirl/attr2article.json')
gender = load_json('moegirl/char2gender.json')


def subset(fp, topk=len(attr_index)):
    ret_char_index = []
    ret_attr_index = []
    ret_char2attr = []
    ret_attr2article = []
    gender_info = []

    # subattr = list(attr_index.keys())
    subattr = attr_index.copy()
    subattr.sort(key=lambda x: len(attr2char[x]))
    subattr = subattr[-topk:]
    subattr_map = {}
    for i, attr in enumerate(subattr):
        subattr_map[attr] = i
        ret_attr_index.append(attr)
        if attr in attr2article:
            url = attr2article[attr]
            if url == '/' + attr:
                ret_attr2article.append('')
            else:
                ret_attr2article.append(url[1:])
        else:
            ret_attr2article.append(None)

    subchar = []
    for i in char_index:
        for j in char2attr[i]:
            if j in subattr:
                subchar.append(i)
                ret_char_index.append(i)
                break

    for i in subchar:
        tmp = []
        for j in char2attr[i]:
            if j in subattr_map:
                tmp.append(subattr_map[j])
        ret_char2attr.append(tmp)

    for i in ret_char_index:
        if i in gender:
            if gender[i] == 'male':
                gender_info.append(0)
            elif gender[i] == 'female':
                gender_info.append(1)
            else:
                gender_info.append(2)
        else:
            gender_info.append(2)

    # print(subattr)
    # print(subchar)
    print('char_index: {}'.format(len(ret_char_index)))
    print('attr_index: {}'.format(len(ret_attr_index)))
    print('article count: {}'.format(len(ret_attr2article)))
    print(
        'char_index encoded:',
        len(json.dumps(ret_char_index, ensure_ascii=False, separators=(',', ':'))),
    )
    print(
        'attr_index encoded:',
        len(json.dumps(ret_attr_index, ensure_ascii=False, separators=(',', ':'))),
    )
    print(
        'char2attr encoded:',
        len(json.dumps(ret_char2attr, ensure_ascii=False, separators=(',', ':'))),
    )
    print(
        'attr2article encoded:',
        len(json.dumps(ret_attr2article, ensure_ascii=False, separators=(',', ':'))),
    )
    print(
        'gender_info encoded:',
        len(json.dumps(gender_info, ensure_ascii=False, separators=(',', ':'))),
    )
    date = time.asctime()
    ret = {
        'pack_date': date,
        'pack_timestamp': time.time(),
        'char_index': ret_char_index,
        'attr_index': ret_attr_index,
        'attr2article': ret_attr2article,
        'char2attr': ret_char2attr,
        'gender_info': gender_info,
    }
    s = json.dumps(ret, ensure_ascii=False, separators=(',', ':'))
    s = s.encode('utf8')
    print('total file size:', len(s))
    with open(fp, 'wb') as f:
        f.write(s)


os.makedirs("moeranker", exist_ok=True)
# subset(open('moeranker/subset_100.json', 'w', encoding='utf-8'), 100)
# subset(open('moeranker/subset_500.json', 'w', encoding='utf-8'), 500)
subset('moeranker/data_min.json')
