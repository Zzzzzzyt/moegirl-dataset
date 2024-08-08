import os
from utils.file import load_json

bgm2moegirl = load_json('bgm2moegirl.json')
moegirl2bgm = load_json('moegirl2bgm.json')

use_160k = (
    os.path.exists("bgm_chars_160k.json")
    and os.path.exists("bgm_subjects_160k.json")
    and os.path.exists("bgm_index_160k.json")
)

bgm_index = None
bgm_chars = None
bgm_subjects = None
if use_160k:
    bgm_index = load_json("bgm_index_160k.json")
    bgm_chars = load_json("bgm_chars_160k.json")
    # bgm_subjects = load_json("bgm_subjects_160k.json")
else:
    print("160k not found. falling back to 20k.")
    bgm_index = load_json("bgm_index_20k.json")
    bgm_chars = load_json("bgm_chars_20k.json")
    # bgm_subjects = load_json("bgm_subjects_20k.json")


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


test_moe('碧蓝航线:33')
test_moe('Towa')
test_moe('托娃(Evenicle)')
test_moe('碧蓝航线:飞云')
test_moe('小不点(LoveLive!)')
test_moe('奥兹(原神)')
test_moe('芙蕾雅(上古卷轴)')
