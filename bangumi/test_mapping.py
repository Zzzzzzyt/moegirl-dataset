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
for entry in bgm_index:
    bgm_entry[entry['id']] = entry

# test_moe('碧蓝航线:33')
# test_moe('Towa')
# test_moe('托娃(Evenicle)')
# test_moe('碧蓝航线:飞云')
# test_moe('小不点(LoveLive!)')
# test_moe('奥兹(原神)')
# test_moe('芙蕾雅(上古卷轴)')
# test_moe('胡桃(东方Project)')
# print(map_bgm(bgm_entry['55053'], verbose=True))
# test_moe('小小兔')
# test_moe('梦王国与沉睡的100王子:阿尔弗雷德')
# test_moe('文豪与炼金术师:太宰治')
# test_moe('茶茶丸')
# test_moe('里克(王国之心)')
# test_moe('我(光与夜之恋)')
# test_moe('修女(星之梦)')
# test_moe('阿杰(快乐星猫)')
# test_moe('克劳德(侠盗猎车)')
# test_moe('梦王国与沉睡的100王子:阿波罗')
# test_moe('小月(巴啦啦小魔仙)')
# test_moe('美少女花骑士:胡桃')
# print(map_bgm(bgm_entry['79480'], verbose=True))
# print(moegirl_extra['美少女花骑士:胡桃'])
# test_moe('胡桃(莉可丽丝)')
# test_moe('Abigail(Rainimator)')
# test_moe('拉娜(坎公骑冠剑)')
# test_moe('天国(少女兵器)')
# test_moe('塞巴斯蒂安(COCOTAMA)')
# test_moe('格林笔记:白雪姬')
# test_moe('女儿(中国式家长)')
# test_moe('优子(老爹餐厅系列)')
# test_moe('咩咩(光之美少女系列)')
# test_moe('小吉(快乐星猫)')
# test_moe('夏洛克·福尔摩斯(歌舞伎町夏洛克)')
# test_moe('Ruby(VOCALOID)')
# test_moe('战舰少女:Musashi')
# test_moe('八戒(唐山葬)')
# test_moe('月光(海底囚人)')
# test_moe('丹尼(JOJO的奇妙冒险)')
# test_moe('春日野丽')
# print(map_bgm(bgm_entry['7859'], verbose=True))
# test_moe('妈妈(hap系列)')
# test_moe('Isla(海底囚人)')
# test_moe('机动战队:优子')
# test_moe('汤姆(万圣街)')
# test_moe('萨拉(东方Project)')
# test_moe('爱丽丝(东方Project旧作)')
# print(map_bgm(bgm_entry['10796'], verbose=True))
# test_moe('博丽灵梦(东方Project旧作)')
# test_moe('雾雨魔理沙(东方Project旧作)')
# test_moe('野兽(约会大作战)')
# test_moe('雪儿(洛克人系列)')
# test_moe('东京放课后召唤师:爱丽丝')
# test_moe('洞爷湖仙人')
# test_moe('小白(猪猪侠)')
# test_moe('美少女花骑士:百合')
# test_moe('贝塔(摩尔庄园)')
# test_moe('久远(传颂之物)')
# test_moe('皮诺(Fate)')
# test_moe('莫妮卡(坎公骑冠剑)')
# test_moe('凯伊(坎公骑冠剑)')
# test_moe('托尔(魔法禁书目录)')
# test_moe('主人公(火焰之纹章 风花雪月)')
# print(map_bgm(bgm_entry['35614'], verbose=True))
# print(map_bgm(bgm_entry['108666'], verbose=True))
# print(map_bgm(bgm_entry['91909'], verbose=True))

# test_moe('小莫(喜羊羊与灰太狼)')
# test_moe('红(凹凸世界)')
# test_moe('阿布(熊出没)')
# test_moe('鲨鱼(虚拟UP主)')
# test_moe('椿(废墟图书馆)')
# test_moe('猎鹰(漫威)')

# print(map_bgm(bgm_entry['87974'], verbose=True))
# test_moe('山田凉')

# test_moe('阿洛娜')
# print(map_bgm(bgm_entry['104651'], verbose=True))

# print(map_bgm(bgm_entry['104093'], verbose=True))
# test_moe('翠(异世界舅舅)')

# print(map_bgm(bgm_entry['8937'], verbose=True))

# print(map_bgm(bgm_entry['35609'], verbose=True))
# test_moe('帕克(Re:从零开始的异世界生活)')

# test_moe('谛听(星穹铁道)')
# test_moe('庞培')
# test_moe('佩佩')
# test_moe('萨姆')

# test_moe('消灭都市:夏树')

# test_moe('慢羊羊')
# print(map_bgm(bgm_entry['68639'], verbose=True))

# test_moe('灰烬战线:百夫长')
# test_moe('格雷伊')
# print(map_bgm(bgm_entry['70840'], verbose=True))

# test_moe('雪莉(荒野乱斗)')

# test_moe('幽灵(全金属狂潮)')

# st = set()
# for i in bgm_subjects2.values():
#     for j in i:
#         if '假面骑士' in j[0]:
#             print(j)
#             st.add(j[0])
# for i in st:
#     print(repr(i) + ',')

# test_moe('月读(假面骑士Zi-O)')
# test_moe('空(假面骑士电王)')
# test_moe('赤羽(假面骑士Build)')
# test_moe('Vice(假面骑士Revice)')

# test_moe('金色暗影darkness')
# test_moe('雫(妃十三学园)')
# test_moe('妖怪屋:薰')
# test_moe('苍蓝钢铁的琶音:吸血鬼')
# test_moe('莉莉安(虚拟UP主)')
# test_moe('Queen(TYPE-0)')
# test_moe('小萤(守护甜心)')
# test_moe('拉娜(我的世界)')

test_moe('芙蕾雅(圣斗士星矢)')
test_moe('世界(飙马野郎)')