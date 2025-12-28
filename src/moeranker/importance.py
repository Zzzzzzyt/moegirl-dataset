import json
import os
import numpy as np
from tqdm import tqdm

from utils.file import save_json, chdir_project_root

chdir_project_root()

attrs: list[str] = json.load(open("moegirl/attr_index.json", encoding="utf-8"))
chars: list[str] = json.load(open("moegirl/char_index.json", encoding="utf-8"))
gain = np.load(open("moegirl/analysis/gain.npy", "rb"))
count = np.load(open("moegirl/analysis/count.npy", "rb"))
contain = np.load(open("moegirl/analysis/contain.npy", "rb"))
contain = 1 - contain
intersection = np.load(open("moegirl/analysis/intersection.npy", "rb"))
attr_count = len(attrs)
char_count = len(chars)
attrmap: dict[str, int] = {}
for i in range(len(attrs)):
    attrmap[attrs[i]] = i

weight = np.minimum(count, 500)
weight = np.power(weight, 0.3)

importance = np.zeros((attr_count), dtype=np.float64)
for i in range(attr_count):
    # a goddess gave me this formula
    s = (np.maximum(np.log2(gain[i]), 0) * weight * contain[i]).sum()
    # nerf rare attributes
    s *= min(np.log2(count[i] / 3 + 500) - 8.5, 1)
    importance[i] = s

importance /= importance[attrmap["黑发"]]

hair_color_attr: list[str] = json.load(
    open("moegirl/hair_color_attr.json", encoding="utf-8")
)
eye_color_attr: list[str] = json.load(
    open("moegirl/eye_color_attr.json", encoding="utf-8")
)

res = []
for i in range(attr_count):
    res.append((importance[i], i, attrs[i]))

res.sort()
out = {}
for i in res:
    if i[2] in hair_color_attr:
        print(i[0], i[2], count[i[1]])
    out[i[2]] = round(float(importance[i[1]]), 5)
print(out["蝴蝶结"], count[attrmap["蝴蝶结"]])

os.makedirs("moeranker", exist_ok=True)
save_json(out, 'moeranker/importance.json')
# np.save(open("moeranker/importance.npy", "wb"), importance, allow_pickle=False)
