import json
import random
import urllib.parse

from utils.file import save_json


def char_filter(char_name):
    # if random.random() > 0.01:
    #     return True
    return char_name.startswith("Template:")


def attr_filter(attr_name):
    if attr_name.startswith("按") and attr_name.endswith("分类"):
        return True


dededupe = {}


def dfs(data: dict, ret: dict, stk: list, no_further: bool = False):
    global dededupe
    if (
        len(data["subcategories"]) == 0
        and len(data["pages"]) == 0
        and data["url"] in dededupe
    ):
        # print(stk)
        # print("dededupe:", data["url"], stk)
        dfs(dededupe[data["url"]], ret, stk, no_further)
    if "url" in data and data["url"] not in dededupe:
        # print("set", data["url"])
        dededupe[data["url"]] = data
    global attr_index, attr_index_set
    global cv_index, cv_index_set
    global char_index, char_index_set
    global attr2article
    if "name" in data and not no_further:
        attr_name = data["name"]
        if (
            len(stk) == 0
            and attr_name != "按角色特征分类"
            and attr_name != '按声优分类'
        ):
            no_further = True
        if attr_name not in attr_index_set and attr_name not in cv_index:
            # attr_index[attr_name] = {"name": attr_name, "url": data["url"]}
            assert '/Category:' + attr_name.replace(" ", "_") == data['url']
            if attr_name.endswith('配音角色'):
                cv_index_set.add(attr_name[:-4])
                cv_index.append(attr_name[:-4])
            else:
                attr_index_set.add(attr_name)
                attr_index.append(attr_name)
                if 'article' in data:
                    url = data['article']['url']
                    if 'redlink' not in url:
                        attr2article[attr_name] = url
                    # print(data['article'])
                else:
                    for i in range(len(stk) - 1, -1, -1):
                        if stk[i] in attr2article:
                            attr2article[attr_name] = attr2article[stk[i]]
                            break
            stk.append(attr_name)
        # if attr_name not in ['按角色特征分类', '按声优分类']:
    # print(stk)
    for i in data["pages"]:
        char_name = i["name"]
        if char_filter(char_name):
            continue
        char_url = i['url']
        assert '/' + char_name.replace(" ", "_") == char_url
        if char_name not in char_index_set:
            char_index_set.add(char_name)
            char_index.append(char_name)
            # char_index[char_name] = i
        if char_name not in ret:
            ret[char_name] = []
        ret[char_name].extend(stk)
    for i in data["subcategories"]:
        dfs(i, ret, stk.copy(), no_further)


attr2article = {}
attr_index = []
attr_index_set = set()
char_index = []
char_index_set = set()
cv_index = []
cv_index_set = set()

data = json.load(open("../crawler/attrs.json", encoding="utf-8"))
char2attr = {}
char2cv = {}
dfs(data, char2attr, [])
attr_index.sort()
char_index.sort()
cv_index.sort()

for k, v in char2attr.items():
    tmp = []
    tmp2 = []
    for i in v:
        if attr_filter(i):
            continue
        if i.endswith('配音角色'):
            tmp2.append(i[:-4])
            continue
        if i not in tmp:
            tmp.append(i)
    char2attr[k] = tmp
    char2cv[k] = tmp2

# char_index.sort()
# print("raw character count:", len(raw_chars))
# save_json(raw_chars, "../crawler2/raw_chars.json")

char2attr = dict(filter(lambda x: len(x[1]) > 0, char2attr.items()))
char2cv = dict(filter(lambda x: len(x[1]) > 0 and x[0] in char2attr, char2cv.items()))

attr2char = {}
for k, v in char2attr.items():
    for i in v:
        if i not in attr2char:
            attr2char[i] = []
        attr2char[i].append(k)
for k, v in attr2char.items():
    v = list(set(v))
    if len(v) == 0:
        print("wtf???", k)

cv2char = {}
for k, v in char2cv.items():
    for i in v:
        if i not in cv2char:
            cv2char[i] = []
        cv2char[i].append(k)
for k, v in cv2char.items():
    v = list(set(v))
    if len(v) == 0:
        print("wtf???", k)

attr_index2 = []
attr2article2 = {}
for name in attr_index:
    if name not in attr2char:
        continue
    if len(attr2char[name]) == 0:
        continue
    attr_index2.append(name)
    if name in attr2article:
        attr2article2[name] = attr2article[name]
    else:
        if name.startswith('第一人称'):
            attr2article2[name] = '/特殊第一人称'
        elif name.startswith('第二人称'):
            attr2article2[name] = '/特殊第二人称'
        elif name in ['AB型', 'A型', 'B型', 'O型']:
            attr2article2[name] = '/ABO血型'
        elif name in ['RH-O型', 'RH型']:
            attr2article2[name] = '/稀有血型'
        else:
            print('no article:', name)
# attr_index2.sort()
# attr_index2 = dict(sorted(attr_index2, key=lambda x: len(attr2char[x])))

char_index2 = []
for name in char_index:
    if name not in char2attr:
        continue
    if len(char2attr[name]) == 0:
        continue
    char_index2.append(name)
# char_index2.sort()
# char_index2 = dict(sorted(char_index2, key=lambda x: len(char2attr[x])))

cv_index2 = []
for name in cv_index:
    if name not in cv2char:
        continue
    if len(cv2char[name]) == 0:
        continue
    cv_index2.append(name)
# cv_index2.sort()
# cv_index2 = dict(sorted(char_index2, key=lambda x: len(cv2char[x])))


attr2char = dict(sorted(attr2char.items(), key=lambda x: len(x[1])))
char2attr = dict(sorted(char2attr.items(), key=lambda x: len(x[1])))
save_json(attr2char, "attr2char.json")
save_json(char2attr, "char2attr.json")
save_json(char2cv, "char2cv.json")
save_json(cv2char, "cv2char.json")

print("attribute count: {}".format(len(attr_index2)))
print("article count: {}".format(len(attr2article2)))
print("cv count: {}".format(len(cv_index2)))
print("character count: {}".format(len(char_index2)))

save_json(char_index2, "char_index.json")
save_json(attr_index2, "attr_index.json")
save_json(cv_index2, "cv_index.json")
save_json(attr2article2, "attr2article.json")
