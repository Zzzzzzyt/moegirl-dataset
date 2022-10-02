import json

char_index = json.load(open('char_index.json', encoding='utf-8'))
attr_index = json.load(open('attr_index.json', encoding='utf-8'))
attr2char = json.load(open('attr2char.json', encoding='utf-8'))
char2attr = json.load(open('char2attr.json', encoding='utf-8'))


def subset(fp, topk=len(attr_index)):
    ret_char_index = []
    ret_attr_index = []
    ret_char2attr = []

    subattr = list(attr_index.keys())
    subattr.sort(key=lambda x: len(attr2char[x]))
    subattr = subattr[-topk:]
    subattr_map = {}
    for i, attr in enumerate(subattr):
        subattr_map[attr] = i
        ret_attr_index.append(attr_index[attr])

    subchar = []
    for i in char_index:
        for j in char2attr[i]:
            if j in subattr:
                subchar.append(i)
                ret_char_index.append(char_index[i])
                break

    for i in subchar:
        tmp = []
        for j in char2attr[i]:
            if j in subattr_map:
                tmp.append(subattr_map[j])
        ret_char2attr.append(tmp)

    print(subattr)
    print(subchar)
    print('char_index: {}'.format(len(ret_char_index)))
    print('attr_index: {}'.format(len(ret_attr_index)))
    print(len(json.dumps(ret_char_index, ensure_ascii=False)))
    print(len(json.dumps(ret_attr_index, ensure_ascii=False)))
    print(len(json.dumps(ret_char2attr, ensure_ascii=False)))
    ret = {
        'char_index': ret_char_index,
        'attr_index': ret_attr_index,
        'char2attr': ret_char2attr
    }
    json.dump(ret, fp, ensure_ascii=False, separators=(',', ':'))


# subset(open('subset_100.json', 'w', encoding='utf-8'), 100)
# subset(open('subset_500.json', 'w', encoding='utf-8'), 500)
subset(open('data_min.json', 'w', encoding='utf-8'))
