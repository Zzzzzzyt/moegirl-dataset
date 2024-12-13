import os
from utils.file import load_json
from moegirl_mapper import *

bgm2moegirl = load_json('bgm2moegirl.json')
moegirl2bgm = load_json('moegirl2bgm.json')


def test_moe(k):
    if k in moegirl2bgm:
        bgms = moegirl2bgm[k]
        print(
            k,
            '->',
            list(map(lambda x: (bgm_chars[x]["name"], x), bgms)),
        )
    else:
        print(k, '->', 'None')


def test_bgm(k):
    if k in bgm2moegirl:
        moes = bgm2moegirl[k]
        print(k, bgm_chars[k]["name"], '->', moes)
    else:
        print(k, bgm_chars[k]["name"], '->', 'None')


bgm_entry = {}
for i in bgm_index:
    bgm_entry[i['id']] = i

# test_moe('碧蓝航线:33')
# test_moe('Towa')
# test_moe('托娃(Evenicle)')
# test_moe('碧蓝航线:飞云')
# test_moe('小不点(LoveLive!)')
# test_moe('奥兹(原神)')
# test_moe('芙蕾雅(上古卷轴)')
# test_moe('胡桃(东方Project)')
# print(map_bgm(bgm_entry['55053'], verbose=True))
