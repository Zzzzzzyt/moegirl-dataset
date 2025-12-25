import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.file import chdir_project_root

chdir_project_root()

attrs = json.load(open('moegirl/preprocess/attr_index.json', encoding='utf-8'))
attrs = set(attrs)
extra = json.load(open('moegirl/crawler_extra/extra_processed.json', encoding='utf-8'))

# d = dict()
# for k, v in extra.items():
#     for i in v['声优']:
#         if i not in attrs:
#             if i not in d:
#                 d[i] = 0
#             d[i] += 1

# l = list(d.items())
# l.sort(key=lambda x: x[1])
# for i in l:
#     print(i)


d = dict()
for k, v in extra.items():
    if '血型' in v:
        x = v['血型']
        if x not in d:
            d[x] = 0
        d[x] += 1

l = list(d.items())
l.sort(key=lambda x: x[1])
for i in l:
    print(i)

tot = d['O'] + d['A'] + d['B'] + d['AB']
for i in ['O', 'A', 'B', 'AB']:
    print(i, d[i], f"{d[i]/tot:.2%}")

# d = dict()
# for k, v in extra.items():
#     if '星座' in v:
#         if len(v['星座']) != 1:
#             print(k, v['星座'])
#         x = v['星座'][0]
#         if x not in d:
#             d[x] = 0
#         d[x] += 1

# l = list(d.items())
# l.sort(key=lambda x: x[1])
# for i in l:
#     print(i)


# l = []
# for i in extra.values():
#     if '三围' in i:
#         l.append(i['三围'])
# # print(l)
# s = pd.DataFrame(l)
# # s = s.loc[lambda x: (x >= 0) & (x <= 300)]
# print(s.describe())
# s.plot.hist(bins=list(range(0, 301)), alpha=0.5)
# plt.show()
