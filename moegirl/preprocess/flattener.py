import json
import random


def save_json(data, path):
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


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
    if len(data["subcategories"]) == 0 and len(data["pages"]) == 0 and data["url"] in dededupe:
        # print(stk)
        print("dededupe:", data["url"], stk)
        dfs(dededupe[data["url"]], ret, stk, no_further)
    if "url" in data and data["url"] not in dededupe:
        # print("set", data["url"])
        dededupe[data["url"]] = data
    global attr_index
    global char_index
    if "name" in data and not no_further:
        attr_name = data["name"]
        if len(stk) == 0 and attr_name != "按角色特征分类":
            no_further = True
        if attr_name not in attr_index:
            attr_index[attr_name] = {"name": attr_name, "url": data["url"]}
            stk.append(attr_name)
        # if attr_name not in ['按角色特征分类', '按声优分类']:
    # print(stk)
    for i in data["pages"]:
        char_name = i["name"]
        if char_filter(char_name):
            continue
        if char_name not in char_index:
            char_index[char_name] = i
        if char_name not in ret:
            ret[char_name] = []
        ret[char_name].extend(stk)
    for i in data["subcategories"]:
        dfs(i, ret, stk.copy(), no_further)


attr_index = {}
char_index = {}

data = json.load(open("../crawler/uncensored.json", encoding="utf-8"))
char2attr = {}
dfs(data, char2attr, [])

for k, v in char2attr.items():
    tmp = []
    for i in v:
        if attr_filter(i):
            continue
        if i not in tmp:
            tmp.append(i)
    char2attr[k] = tmp

raw_chars = list(char_index.values())
raw_chars.sort(key=lambda x: x["name"])
print("raw character count:", len(raw_chars))
save_json(raw_chars, "../crawler2/raw_chars.json")

char2attr = dict(filter(lambda x: len(x[1]) > 0, char2attr.items()))

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

attr_index2 = {}
for k, v in attr_index.items():
    assert k == v["name"]
    if k not in attr2char:
        continue
    if len(attr2char[k]) == 0:
        continue
    attr_index2[k] = v
attr_index2 = dict(sorted(attr_index2.items(), key=lambda x: len(attr2char[x[1]["name"]])))

char_index2 = {}
for k, v in char_index.items():
    assert k == v["name"]
    if k not in char2attr:
        continue
    if len(char2attr[k]) == 0:
        continue
    char_index2[k] = v
char_index2 = dict(sorted(char_index2.items(), key=lambda x: len(char2attr[x[1]["name"]])))

attr2char = dict(sorted(attr2char.items(), key=lambda x: len(x[1])))
char2attr = dict(sorted(char2attr.items(), key=lambda x: len(x[1])))
save_json(attr2char, "attr2char.json")
save_json(char2attr, "char2attr.json")

print("attribute count: {}".format(len(attr_index2)))
print("character count: {}".format(len(char_index2)))
save_json(char_index2, "char_index.json")
save_json(attr_index2, "attr_index.json")
