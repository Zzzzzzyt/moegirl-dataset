import json
import os
import traceback
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import PIL.Image as Image
from utils.file import load_json, chdir_project_root

from mplfonts import use_font

chdir_project_root()

use_font('Noto Sans CJK SC')

attrs = load_json('moegirl/preprocess/attr_index.json')
chars = load_json('moegirl/preprocess/char_index.json')
P = np.load(open('moegirl/analyze/intersection.npy', 'rb'))
gain = np.load(open('moegirl/analyze/gain.npy', 'rb'))
chi2 = np.load(open('moegirl/analyze/chi2.npy', 'rb'))
attr_count = len(attrs)
char_count = len(chars)
attrmap = {}
for i in range(len(attrs)):
    attrmap[attrs[i]] = i

hair_color_attr = load_json('moegirl/preprocess/hair_color_attr.json')
# hair_color_attr.sort(key=lambda x: P[attrmap[x]][attrmap[x]], reverse=True)
eye_color_attr = load_json('moegirl/preprocess/eye_color_attr.json')
# eye_color_attr.sort(key=lambda x: P[attrmap[x]][attrmap[x]], reverse=True)

bgm2moegirl = load_json('bangumi/bgm2moegirl.json')
bgm_index = load_json('bangumi/bgm_index_full.json')
l = []
for i in bgm_index:
    mapped = bgm2moegirl[i['id']]
    if len(mapped) > 0:
        l.append((mapped[0], i['id']))

char2attr = load_json('moegirl/preprocess/char2attr.json')
subset = list(char2attr.keys())
# subset = load_json('moegirl/subset/subset/blue_archive_subset.json')
# subset = json.load(open('../subset/subset/jojo_subset.json', encoding='utf-8'))
# touhou_set += json.load(open('../subset/subset/touhou_old_subset.json', encoding='utf-8'))

# attrid = attrmap['傲娇']
# res = []
# for i in range(attr_count):
#     # if i[-1] in hair_color_attr:
#     # print(i, attrs[i], chi2[attrid][i])
#     if P[i][attrid]>=20:
#         res.append((gain[i][attrid], attrs[i], P[i][attrid]))
# res.sort()
# for i in res:
#     print(i)

hair_eye = np.zeros((len(hair_color_attr), len(eye_color_attr)), np.int32)
char = np.zeros_like(hair_eye).tolist()
for i in range(len(hair_color_attr)):
    for j in range(len(eye_color_attr)):
        hair = hair_color_attr[i]
        eye = eye_color_attr[j]
        p = 0
        for k in subset:
            if hair in char2attr[k] and eye in char2attr[k]:
                p += 1
        # p = P[attrmap[hair]][attrmap[eye]]
        hair_eye[i][j] = p
        char[i][j] = []
        cnt = 0
        for k in l:
            if k[0] in subset and hair in char2attr[k[0]] and eye in char2attr[k[0]]:
                if hair != '多色发' and '多色发' in char2attr[k[0]]:
                    continue
                if hair != '彩虹发' and '彩虹发' in char2attr[k[0]]:
                    continue
                if hair != '双色发' and '双色发' in char2attr[k[0]]:
                    continue
                if eye != '异色瞳' and '异色瞳' in char2attr[k[0]]:
                    continue
                if eye != '彩虹瞳' and '彩虹瞳' in char2attr[k[0]]:
                    continue
                if eye != '渐变瞳' and '渐变瞳' in char2attr[k[0]]:
                    continue
                char[i][j].append(k)
                print(k)
                cnt += 1
                if cnt >= 4:
                    break
        print(hair, eye, p)

plt.subplot(1, 2, 1)
mx = hair_eye.max()
plt.imshow(hair_eye, origin='lower')
plt.yticks(np.arange(len(hair_color_attr)), labels=hair_color_attr)
plt.xticks(np.arange(len(eye_color_attr)), labels=eye_color_attr)
for i in range(len(hair_color_attr)):
    for j in range(len(eye_color_attr)):
        plt.text(
            j,
            i,
            hair_eye[i, j],
            ha='center',
            va='center',
            color='black' if hair_eye[i][j] > mx * 0.8 else 'white',
        )


plt.subplot(1, 2, 2)
plt.yticks(
    (np.arange(0, len(hair_color_attr) * 75, 75) + 75 / 2)[::-1] * 2,
    labels=hair_color_attr,
)
plt.xticks(
    (np.arange(0, len(eye_color_attr) * 75, 75) + 75 / 2) * 2, labels=eye_color_attr
)

img = Image.new(
    'RGB',
    (len(eye_color_attr) * 75 * 2, len(hair_color_attr) * 75 * 2),
    (255, 255, 255),  # type: ignore
)

offsetx = [0, 75, 0, 75]
offsety = [0, 0, 75, 75]

for i in range(len(hair_color_attr)):
    for j in range(len(eye_color_attr)):
        cnt = 0
        for k in char[i][j]:
            fname = 'bangumi/images/{}-avatar.jpg'.format(k[1])

            if os.path.exists(fname):
                try:
                    img2 = Image.open(fname)
                    img.paste(
                        img2,
                        (
                            j * 75 * 2 + offsetx[cnt],
                            (len(hair_color_attr) - 1 - i) * 75 * 2 + offsety[cnt],
                        ),
                    )
                    cnt += 1
                except Exception as e:
                    traceback.print_exc()
        # # plt.text(j, i, char[i][j][0], fontsize=10, wrap=True, ha='center', va='center', color='black' if hair_eye[i][j] > 1500 else 'white')

imgarray = np.array(img)
for i in range(len(eye_color_attr) - 1):
    imgarray[(i + 1) * 75 * 2 - 1 : (i + 1) * 75 * 2 + 1, :] = 0
for i in range(len(hair_color_attr) - 1):
    imgarray[:, (i + 1) * 75 * 2 - 1 : (i + 1) * 75 * 2 + 1] = 0
plt.imshow(imgarray)

# # img.show()
plt.show()
