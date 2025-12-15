from pypinyin import Style, lazy_pinyin
from utils.file import save_json, load_json, chdir_project_root

chdir_project_root()

char2subject: dict[str, str] = load_json('moegirl/preprocess/char2subject.json')
chars: set[str] = set(load_json('moegirl/preprocess/char_index.json'))


def sort_chn(a):
    return sorted(a, key=lambda x: lazy_pinyin(x))


def gen(tags):
    if type(tags) == str:
        tags = [tags]
    ret: list[str] = []
    for k, v in char2subject.items():
        for i in tags:
            if i in v:
                ret.append(k)
                assert k in chars
                break
    print(tags, len(ret))
    return ret


def dfs(d):
    ret: set[str] = set()
    if 'pages' in d:
        for i in d['pages']:
            v = i['name']
            if v in chars:
                ret.add(v)
    if 'subcategories' in d:
        for i in d['subcategories']:
            ret |= dfs(i)
    return ret


# d={}
# for k,v in subjects.items():
#     for i in v:
#         if i not in d:
#             d[i]=0
#         d[i]+=1
# dd=[]
# for k,v in d.items():
#     dd.append((v,k))
# dd.sort()
# for i in dd:
#     print(i)

attrs = load_json('moegirl/crawler/attrs.json')
vocaloid_root = None
for i in attrs['subcategories']:
    if i['name'] == '按歌声合成软件分类':
        vocaloid_root = i
        break
assert vocaloid_root is not None

save_json(
    list(dfs(vocaloid_root)),
    'moegirl/subset/vocaloid_subset.json',
)

save_json(
    sort_chn(
        list(
            set(gen('AIR'))
            | set(gen('古典部系列'))
            | set(gen('吹响！上低音号'))
            | set(gen('CLANNAD'))
            | set(gen('二十世纪电气目录'))
            | set(gen('Free!'))
            | set(gen('甘城光辉游乐园'))
            | set(gen('境界的彼方'))
            | set(gen('紫罗兰永恒花园'))
            | set(gen('Kanon'))
            | set(gen('凉宫春日系列'))
            | set(gen('轻音少女'))
            | set(gen('全金属狂潮'))
            | set(gen('日常'))
            | set(gen('声之形'))
            | set(gen('弦音 -风舞高中弓道部-'))
            | set(gen('小林家的龙女仆'))
            | set(gen('幸运星'))
            | set(gen('玉子市场'))
            | set(gen('中二病也要谈恋爱！'))
            | set(gen('无彩限的怪灵世界'))
            | set(gen('仰望天空的少女瞳孔中所映照的世界'))
        )
    ),
    'moegirl/subset/kyoani_subset.json',
)

save_json(sort_chn(gen('东方正作人物')), 'moegirl/subset/touhou_new_subset.json')
save_json(sort_chn(gen('东方旧作人物')), 'moegirl/subset/touhou_old_subset.json')

save_json(sort_chn(gen('魔法禁书目录')), 'moegirl/subset/toaru_subset.json')
save_json(sort_chn(gen('某科学的超电磁炮')), 'moegirl/subset/railgun_subset.json')

save_json(sort_chn(gen('明日方舟角色')), 'moegirl/subset/arknights_subset.json')
save_json(sort_chn(gen('原神')), 'moegirl/subset/genshin_subset.json')
save_json(sort_chn(gen('崩坏3')), 'moegirl/subset/honkai3_subset.json')
save_json(sort_chn(gen('崩坏：星穹铁道')), 'moegirl/subset/honkai_starrail_subset.json')
save_json(sort_chn(gen('绝区零')), 'moegirl/subset/zzz_subset.json')
save_json(sort_chn(gen('鸣潮')), 'moegirl/subset/wuthering_waves_subset.json')
save_json(sort_chn(gen('尘白禁区')), 'moegirl/subset/snowbreak_subset.json')
save_json(sort_chn(gen('阴阳师(手游)')), 'moegirl/subset/onmyoji_subset.json')
save_json(sort_chn(gen('Fate系列角色')), 'moegirl/subset/fate_subset.json')
save_json(sort_chn(gen('JOJO的奇妙冒险')), 'moegirl/subset/jojo_subset.json')
save_json(sort_chn(gen('机动战士高达系列')), 'moegirl/subset/gundam_subset.json')
save_json(sort_chn(gen('火影忍者')), 'moegirl/subset/naruto_subset.json')
save_json(sort_chn(gen('BLEACH')), 'moegirl/subset/bleach_subset.json')
save_json(sort_chn(gen('魔法少女小圆')), 'moegirl/subset/madoka_subset.json')
save_json(sort_chn(gen('进击的巨人')), 'moegirl/subset/AOT_subset.json')
save_json(sort_chn(gen('咒术回战')), 'moegirl/subset/jujutsu_subset.json')
save_json(sort_chn(gen('英雄联盟')), 'moegirl/subset/lol_subset.json')
save_json(sort_chn(gen('名侦探柯南')), 'moegirl/subset/conan_subset.json')
save_json(sort_chn(gen('LoveLive!系列')), 'moegirl/subset/lovelive_subset.json')
save_json(sort_chn(gen('BanG Dream!')), 'moegirl/subset/bangdream_subset.json')
save_json(sort_chn(gen('少女歌剧 Revue Starlight')), 'moegirl/subset/revue_subset.json')
save_json(sort_chn(gen('赛马娘 Pretty Derby角色')), 'moegirl/subset/derby_subset.json')
save_json(sort_chn(gen('舰队Collection舰娘')), 'moegirl/subset/kancolle_subset.json')
save_json(sort_chn(gen('战舰少女')), 'moegirl/subset/kanR_subset.json')
save_json(sort_chn(gen('碧蓝航线舰船')), 'moegirl/subset/azur_lane_subset.json')
save_json(sort_chn(gen('蔚蓝档案')), 'moegirl/subset/blue_archive_subset.json')
save_json(sort_chn(gen('少女前线')), 'moegirl/subset/girls_frontline_subset.json')
save_json(sort_chn(gen('少女与战车')), 'moegirl/subset/GUP_subset.json')
save_json(
    sort_chn(list(set(gen('AIR')) | set(gen('Kanon')) | set(gen('CLANNAD')))),
    'moegirl/subset/key3_subset.json',
)
save_json(sort_chn(gen('宝可梦系列角色')), 'moegirl/subset/pokemon_char_subset.json')
save_json(sort_chn(gen('宝可梦')), 'moegirl/subset/pokemon_subset.json')
save_json(sort_chn(gen('彩虹小马')), 'moegirl/subset/pony_subset.json')
save_json(sort_chn(gen('偶像大师系列')), 'moegirl/subset/idolmaster_subset.json')
save_json(sort_chn(gen('偶像梦幻祭')), 'moegirl/subset/ES_subset.json')
save_json(sort_chn(gen('公主连结Re:Dive')), 'moegirl/subset/PCR_subset.json')
save_json(sort_chn(gen('炼金工房系列')), 'moegirl/subset/housamo_subset.json')
save_json(sort_chn(gen('东京放课后召唤师')), 'moegirl/subset/atelier_subset.json')
save_json(sort_chn(gen('假面骑士系列')), 'moegirl/subset/kamen_rider_subset.json')
save_json(sort_chn(gen('弹丸论破')), 'moegirl/subset/danganronpa_subset.json')
save_json(sort_chn(gen('女神异闻录系列')), 'moegirl/subset/persona_subset.json')
save_json(sort_chn(gen('RWBY')), 'moegirl/subset/rwby_subset.json')
