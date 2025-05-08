from pypinyin import Style, lazy_pinyin
from utils.file import save_json, load_json

char2subject = load_json('../preprocess/char2subject.json')
chars = set(load_json('../preprocess/char_index.json'))


def sort_chn(a):
    return sorted(a, key=lambda x: lazy_pinyin(x))


def gen(tags):
    if type(tags) == str:
        tags = [tags]
    ret = []
    for k, v in char2subject.items():
        for i in tags:
            if i in v:
                ret.append(k)
                assert k in chars
                break
    print(tags, len(ret))
    return ret


def dfs(d):
    ret = set()
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

save_json(
    list(dfs(load_json('../crawler/subset/vocaloid.json'))),
    'subset/vocaloid_subset.json',
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
    'subset/kyoani_subset.json',
)

save_json(sort_chn(gen('东方正作人物')), 'subset/touhou_new_subset.json')
save_json(sort_chn(gen('东方旧作人物')), 'subset/touhou_old_subset.json')

save_json(sort_chn(gen('魔法禁书目录')), 'subset/toaru_subset.json')
save_json(sort_chn(gen('某科学的超电磁炮')), 'subset/railgun_subset.json')

save_json(sort_chn(gen('明日方舟角色')), 'subset/arknights_subset.json')
save_json(sort_chn(gen('原神')), 'subset/genshin_subset.json')
save_json(sort_chn(gen('崩坏3')), 'subset/honkai3_subset.json')
save_json(sort_chn(gen('崩坏：星穹铁道')), 'subset/honkai_starrail_subset.json')
save_json(sort_chn(gen('绝区零')), 'subset/zzz_subset.json')
save_json(sort_chn(gen('鸣潮')), 'subset/wuthering_waves_subset.json')
save_json(sort_chn(gen('尘白禁区')), 'subset/snowbreak_subset.json')
save_json(sort_chn(gen('阴阳师(手游)')), 'subset/onmyoji_subset.json')
save_json(sort_chn(gen('Fate系列角色')), 'subset/fate_subset.json')
save_json(sort_chn(gen('JOJO的奇妙冒险')), 'subset/jojo_subset.json')
save_json(sort_chn(gen('机动战士高达系列')), 'subset/gundam_subset.json')
save_json(sort_chn(gen('火影忍者')), 'subset/naruto_subset.json')
save_json(sort_chn(gen('BLEACH')), 'subset/bleach_subset.json')
save_json(sort_chn(gen('魔法少女小圆')), 'subset/madoka_subset.json')
save_json(sort_chn(gen('进击的巨人')), 'subset/AOT_subset.json')
save_json(sort_chn(gen('咒术回战')), 'subset/jujutsu_subset.json')
save_json(sort_chn(gen('英雄联盟')), 'subset/lol_subset.json')
save_json(sort_chn(gen('名侦探柯南')), 'subset/conan_subset.json')
save_json(sort_chn(gen('LoveLive!系列')), 'subset/lovelive_subset.json')
save_json(sort_chn(gen('BanG Dream!')), 'subset/bangdream_subset.json')
save_json(sort_chn(gen('少女歌剧 Revue Starlight')), 'subset/revue_subset.json')
save_json(sort_chn(gen('赛马娘 Pretty Derby角色')), 'subset/derby_subset.json')
save_json(sort_chn(gen('舰队Collection舰娘')), 'subset/kancolle_subset.json')
save_json(sort_chn(gen('战舰少女')), 'subset/kanR_subset.json')
save_json(sort_chn(gen('碧蓝航线舰船')), 'subset/azur_lane_subset.json')
save_json(sort_chn(gen('蔚蓝档案')), 'subset/blue_archive_subset.json')
save_json(sort_chn(gen('少女前线')), 'subset/girls_frontline_subset.json')
save_json(sort_chn(gen('少女与战车')), 'subset/GUP_subset.json')
save_json(
    sort_chn(list(set(gen('AIR')) | set(gen('Kanon')) | set(gen('CLANNAD')))),
    'subset/key3_subset.json',
)
save_json(sort_chn(gen('宝可梦系列角色')), 'subset/pokemon_char_subset.json')
save_json(sort_chn(gen('宝可梦')), 'subset/pokemon_subset.json')
save_json(sort_chn(gen('彩虹小马')), 'subset/pony_subset.json')
save_json(sort_chn(gen('偶像大师系列')), 'subset/idolmaster_subset.json')
save_json(sort_chn(gen('偶像梦幻祭')), 'subset/ES_subset.json')
save_json(sort_chn(gen('公主连结Re:Dive')), 'subset/PCR_subset.json')
save_json(sort_chn(gen('炼金工房系列')), 'subset/housamo_subset.json')
save_json(sort_chn(gen('东京放课后召唤师')), 'subset/atelier_subset.json')
save_json(sort_chn(gen('假面骑士系列')), 'subset/kamen_rider_subset.json')
save_json(sort_chn(gen('弹丸论破')), 'subset/danganronpa_subset.json')
save_json(sort_chn(gen('女神异闻录系列')), 'subset/persona_subset.json')
save_json(sort_chn(gen('RWBY')), 'subset/rwby_subset.json')
