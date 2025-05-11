import json
import numpy as np
from tqdm import tqdm

attrs = json.load(open("../preprocess/attr_index.json", encoding="utf-8"))
chars = json.load(open("../preprocess/char_index.json", encoding="utf-8"))
P = np.load(open("intersection.npy", "rb"))
attr_count = len(attrs)
char_count = len(chars)
attrmap = {}
for i in range(len(attrs)):
    attrmap[attrs[i]] = i


def query_attr(x, limit=None):
    tmp = []
    attrid = attrmap[x]
    paa = P[attrid][attrid]
    for i in range(len(attrs)):
        if i == attrid:
            continue
        pai = P[attrid][i]
        pii = P[i][i]
        tmp.append(((pai / paa) / (pii / char_count), pai, pii, pai / paa, attrs[i]))
    tmp.sort()
    if limit:
        tmp = tmp[-limit:]
    return tmp


def calc(x, y):
    pxy = P[x][y]
    pxx = P[x][x]
    pyy = P[y][y]
    # if (pxy / pxx) / (pyy / char_count) == 0:
    #     print(attrs[i], attrs[j])
    if pxx == 0:
        return (1, pxy, pxx, pxy / pxx)
    return ((pxy / pxx) / (pyy / char_count), pxy, pxx, pxy / pxx)


def calc_chi2(x, y):
    pxx = float(P[x][x])
    pyy = float(P[y][y])
    p11 = float(P[x][y])
    p10 = pxx - p11
    p01 = pyy - p11
    p00 = char_count - p11 - p10 - p01
    chi2 = (p11 * p00 - p10 * p01) / (pxx * pyy * (char_count - pxx) * (char_count - pyy)) ** 0.5
    return chi2


def calc_name(x, y):
    xx = attrmap[x]
    yy = attrmap[y]
    res = calc(x, y)
    return tuple(list(res) + [xx, yy])


# hair_color_attr = json.load(open('../preprocess/hair_color_attr.json', encoding='utf-8'))

# tmp = query_attr("辫子")
# for i in tmp:
#     # if i[-1] in hair_color_attr:
#     if i[2] > 30 and i[3] > 0.01:
#         print(i)


gain = np.zeros(shape=[attr_count, attr_count], dtype=np.float32)
chi2 = np.zeros(shape=[attr_count, attr_count], dtype=np.float32)
contain = np.zeros(shape=[attr_count, attr_count], dtype=np.bool8)
with tqdm(total=attr_count * (attr_count - 1) // 2 + attr_count) as pbar:
    for i in range(attr_count):
        for j in range(i, attr_count):
            gain[i][j] = calc(i, j)[0]
            gain[j][i] = gain[i][j]
            chi2[i][j] = calc_chi2(i, j)
            chi2[j][i] = chi2[i][j]
            # result.append((attrs[i], attrs[j], chi2, table))
            if i == j:
                contain[i][j] = True
            else:
                if P[i][j] > 10:
                    if P[i][j] / P[j][j] > 0.99:
                        contain[i][j] = True
                        pbar.write(attrs[i] + " " + attrs[j])
                    if P[i][j] / P[i][i] > 0.99:
                        contain[j][i] = True
                        pbar.write(attrs[j] + " " + attrs[i])
            pbar.update(1)

np.save(open("contain.npy", "wb"), contain)
np.save(open("gain.npy", "wb"), gain)
np.save(open("chi2.npy", "wb"), chi2)
