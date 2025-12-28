from utils.file import load_json, save_json, chdir_project_root
import matplotlib.pyplot as plt

chdir_project_root()

fundamental_attr = set(load_json('moegirl/fundamental_attr.json'))
chars = load_json('bangumi/subset/bgm20000_subset.json')[5000:10000]
moegirl2bgm = load_json('bangumi/moegirl2bgm.json')
char2attr = load_json('moegirl/char2attr.json')
ignore_attr = set(
    ['学生', '高中生', '优等生', '差生', '妹妹', '实妹', '义妹', '女儿', '妈妈']
)

l = []
for i in chars:
    if ':' in i and '(' not in i:
        continue
    if len(moegirl2bgm[i]) != 1:
        continue
    attrs = char2attr[i]
    cnt1 = 0
    cnt2 = 0
    for j in attrs:
        if j in ignore_attr:
            continue
        if j in fundamental_attr:
            cnt1 += 1
        else:
            cnt2 += 1
    if cnt2 > 3:
        continue
    if cnt1 < 2:
        continue
    l.append((i, cnt1))


l.sort(key=lambda x: x[1], reverse=True)
l = list(map(lambda x: x[0], l))
print(len(l))
save_json(l, 'moegirl/analysis/stereotype_subset.json')
