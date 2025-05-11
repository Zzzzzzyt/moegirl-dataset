import json
import matplotlib.pyplot as plt

from mplfonts import use_font

from utils.file import save_json

use_font('Noto Sans CJK SC')

char_index: list = json.load(open('char_index.json', encoding='utf-8'))
attr_index: list = json.load(open('attr_index.json', encoding='utf-8'))
attr2char: dict = json.load(open('attr2char.json', encoding='utf-8'))
char2attr: dict = json.load(open('char2attr.json', encoding='utf-8'))

# l = list(map(lambda vk: (len(vk[1]), vk[0]), char2attr.items()))
# l.sort(reverse=True)
# for idx, i in enumerate(l[:10]):
#     # print(i)
#     # print(char2attr[i[1]])
#     print('#{} {} {}种'.format(idx+1, i[1], i[0]))
#     for i in char2attr[i[1]]:
#         print(i, end=' ')
#     print()

l = list(map(lambda vk: (len(vk[1]), vk[0]), attr2char.items()))
l.sort(reverse=True)
for idx, i in enumerate(l[:50]):
    # print(i)
    # print(char2attr[i[1]])
    print('#{} {} {}人'.format(idx + 1, i[1], i[0]))

# save_json(list(map(lambda x: x[1], l[:1000])), 'male_attrs.json')

# cnt1 = 0
# l1 = []
# for i in char2attr.values():
#     l1.append(len(i))
#     if len(i) <= 1:
#         cnt1 += 1
# print(cnt1, len(char2attr), cnt1/len(char2attr))
# l1.sort(reverse=True)

# plt.plot(range(1, len(l1)+1), l1)
# plt.xlabel('角色排名')
# plt.ylabel('属性数')
# plt.show()

# cnt2 = 0
# l2 = []
# for i in attr2char.values():
#     l2.append(len(i))
#     if len(i) <= 10:
#         cnt2 += 1
# print(cnt2, len(attr2char), cnt2/len(attr2char))
# l2.sort(reverse=True)

# plt.plot(range(1, len(l2)+1), l2)
# plt.xlabel('属性排名')
# plt.ylabel('角色数')
# plt.show()
