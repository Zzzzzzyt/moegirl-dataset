import json
import numpy as np
from tqdm import tqdm

from utils.file import save_json

attrs = json.load(open("../preprocess/attr_index.json", encoding="utf-8"))
chars = json.load(open("../preprocess/char_index.json", encoding="utf-8"))
gain = np.load(open("gain.npy", "rb"))
count = np.load(open("count.npy", "rb"))
contain = np.load(open("contain.npy", "rb"))
contain = 1 - contain
intersection = np.load(open("intersection.npy", "rb"))
attr_count = len(attrs)
char_count = len(chars)
attrmap = {}
for i in range(len(attrs)):
    attrmap[attrs[i]] = i

weight = np.minimum(count, 500)
weight = np.power(weight, 0.3)

importance = np.zeros((attr_count))
for i in range(attr_count):
    # a goddess gave me this formula
    s = (np.maximum(np.log2(gain[i]), 0) * weight * contain[i]).sum()
    # nerf rare attributes
    s *= min(np.log2(count[i] / 3 + 500) - 8.5, 1)
    importance[i] = s

importance /= importance[attrmap["黑发"]]

hair_color_attr = json.load(open("../crawler/hair_color_attr.json", encoding="utf-8"))
eye_color_attr = json.load(open("../crawler/eye_color_attr.json", encoding="utf-8"))

res = []
for i in range(attr_count):
    res.append((importance[i], i, attrs[i]))

res.sort()
out = {}
for i in res:
    if i[2] in hair_color_attr:
        print(i[0], i[2], count[i[1]])
    out[i[2]] = round(importance[i[1]], 5)
print(out["蝴蝶结"], count[attrmap["蝴蝶结"]])
save_json(out, 'importance.json')
np.save(open("importance.npy", "wb"), importance, allow_pickle=False)
