import json
import re
import opencc
import os
from tqdm import tqdm

from utils.file import load_json, save_json


special_map = {
    "10452": "初音未来",  # 初音ミク
    "273": "阿尔托莉雅·潘德拉贡",  # アルトリア・ペンドラゴン
    "3": "C.C.(CODE GEASS)",  # C.C.
    "1": "鲁路修·vi·布里塔尼亚",  # ルルーシュ・ランペルージ
    "46465": "洛琪希·米格路迪亚",  # ロキシー・ミグルディア・グレイラット
    "10609": "立华奏",  # 立華かなで
    "12929": None,  # 地球君
    "1976": "赫萝",  # ホロ
    "64640": "宝多六花",  # 宝多六花
    "35615": "雷姆(Re:从零开始的异世界生活)",  # レム
    "19529": "时崎狂三",  # 時崎狂三
    "24093": "泽村·斯宾塞·英梨梨",  # 澤村・スペンサー・英梨々
    "116353": "露西(赛博朋克边缘行者)",  # Lucy  TODO
    "14468": None,  # 圣光君
    "19546": "利威尔·阿克曼",  # 利威尔
    "72355": "伊蕾娜",  # イレイナ
    "14477": None,  # (bgm38)
    "16369": "主人公(人类衰退之后)",  # 我
    "57751": "02",  # ゼロツー
    "46464": "艾莉丝·伯雷亚斯·格雷拉特",  # 艾莉丝·格雷拉特
    "77": "斯派克·斯皮格尔",  # 史派克·斯皮格尔  TODO
    "336": "中原岬",  # 中原岬  TODO
    "79": "菲·瓦伦丁",  # 菲·瓦伦坦
    "606": "雨宫优子",  # 雨宮 優子
    "293": "奇尔希",  # 銀
    "2355": "机动战队:尼娅",  # ニア・テッペリン 妮亚  TODO
    "11546": None,  # アルパカ 羊驼
    "3216": "英灵卫宫",  # 卫宫
    "75": "猫咪老师",  # 喵先生/斑
    "10639": "一方通行",  # 一方通行
    "88130": "南梦芽",  # 南夢芽
    "16684": "L·罗莱特",  # L
    "5922": "天海春香",  # 天海春香
    "53208": "绊爱",  # Kizuna AI
    "64641": "新条茜",  # 新条アカネ
    "57715": "芙拉蒂蕾娜·米利杰",  # ヴラディレーナ・ミリーゼ
    "11926": "紫苑寺有子",  # アリス
    "5928": "如月千早",  # 如月千早
    "13375": "奈亚子",  # ニャルラトホテプ
    "2902": "泰蕾莎·泰斯塔罗莎",  # テレサ・テスタロッサ
    "71479": "阿尼亚·福杰",  # アーニャ
    "223": "露易丝(零之使魔)",  # ルイズ・フランソワーズ・ル・ブラン・ド・ラ・ヴァリエール
    "855": "爱尔奎特·布伦史塔德",  # アルクェイド・ブリュンスタッド
    "12423": None,  # 杨威利ヤン・ウェンリー
    '87184': '托娃(Evenicle)',
    '35614': '拉姆(Re:从零开始的异世界生活)',
    '15420': None,
    '108666': '胡桃(莉可丽丝)',
    '70504': '鹭宫诗织',
    '91297': '雨(主播女孩重度依赖)',
    '22783': None,  # 春日步(阿滋漫画大王)
    '104095': '艾丽西亚·伊德露西亚',
    '266': '金色暗影',
    '1227': '吉尔伽美什(Fate)',
    '63762': '忍野忍',
    '35608': '爱蜜莉雅',
    '108660': '木更',
    '10446': '丘比',
    '23425': '白(游戏人生)',
    '86247': '菲伦',
    '156': '银古',
    '11909': '博士(日常)',
    '29362': '艾拉(可塑性记忆)',
    '39362': '丛雨',
    '116359': '丽贝卡',
    '292': '黑(DARKER THAN BLACK)',
    '37455': '无名(甲铁城的卡巴内瑞)',
    '13245': '卡斯瓦尔·雷姆·戴肯',
    '61546': None,
    '15139': None,
    '170520': 'Vice(假面骑士Revice)',
}
# special_map = {}

reverse_special = {
    '胡桃(莉可丽丝)': '108666',
    '碧蓝航线:22': '10849',
    '碧蓝航线:33': '10850',
    'Towa': '87184',
    'トワ': '87184',
    '小不点(LoveLive!)': '110647',
    '芙蕾雅(上古卷轴)': None,
    '菲兹·艾贝琳': None,
    '小小兔': '6684',
    '梦王国与沉睡的100王子:阿尔弗雷德': '157300',
    '文豪与炼金术师:太宰治': '76133',
    '米勒(虚拟UP主)': None,
    '茶茶丸': None,
    '秋田小町': None,
    '苏苏(个人势)': None,
    '里克(王国之心)': '15850',
    '刑天(京剧猫)': None,
    '我的魔塔:刷子': None,
    '我(光与夜之恋)': '97750',
    '修女(星之梦)': None,
    '阿杰(快乐星猫)': None,
    '克劳德(侠盗猎车)': '72922',
    '幻书启世录:桃乐丝': None,
    '小月(巴啦啦小魔仙)': None,
    'Abigail(Rainimator)': None,
    '拉娜(坎公骑冠剑)': None,
    '天国(少女兵器)': None,
    '塞巴斯蒂安(COCOTAMA)': None,
    '格林笔记:白雪姬': '67888',
    '女儿(中国式家长)': None,
    '优子(老爹餐厅系列)': None,
    '小吉(快乐星猫)': None,
    '夏洛克·福尔摩斯(歌舞伎町夏洛克)': '67109',
    '木叶(女忍者椿的心事)': '107238',
    'Ruby(VOCALOID)': None,
    '八戒(唐山葬)': None,
    '月光(海底囚人)': None,
    '丹尼(JOJO的奇妙冒险)': None,
    '春日野丽': '7859',
    '妈妈(hap系列)': None,
    'Isla(海底囚人)': None,
    '机动战队:优子': '2354',
    '汤姆(万圣街)': None,
    '爱丽丝·玛格特罗依德': '10796',
    '爱丽丝(东方Project旧作)': '10796',
    '博丽灵梦': '485',
    '博丽灵梦(东方Project旧作)': '485',
    '雾雨魔理沙': '486',
    '雾雨魔理沙(东方Project旧作)': '486',
    '野兽(约会大作战)': None,
    '雪儿(洛克人系列)': '1087',
    '洞爷湖仙人': None,
    '帕克(成龙历险记)': None,
    '小白(猪猪侠)': None,
    '贝塔(摩尔庄园)': None,
    '皮诺(Fate)': None,
    '托尔(魔法禁书目录)': None,
    '主人公(火焰之纹章 风花雪月)': '69218',
    '莲华(美少女万华镜)': '16164',
    '莲华(歌姬)': None,
    '猫猫(七色战记)': None,
    '猫猫(药师少女的独语)': '61330',
    '碧翠丝(Re:从零开始的异世界生活)': '35616',
    '电次(电锯人)': '71335',
    '凛(Muse Dash)': None,
    '山田凉': '87974',
    '阿库娅(为美好的世界献上祝福)': '35678',
    '神乐(银魂)': '229',
    '高木同学': '41849',
    '托尔(小林家的龙女仆)': '47659',
    '小林(小林家的龙女仆)': '47658',
    '乔瑟夫·乔斯达': '879',
    '小莫(喜羊羊与灰太狼)': None,
    '红(凹凸世界)': None,
    '阿布(熊出没)': None,
    '鲨鱼(虚拟UP主)': None,
    '椿(废墟图书馆)': None,
    '猎鹰(漫威)': None,
    '消灭都市:夏树': None,
    '米内特': None,
    '灰烬战线:百夫长': '132339',
    '百闻牌:樱花妖': None,
    '幽灵(全金属狂潮)': None,
    '金色暗影darkness': None,
    '雫(妃十三学园)': None,
    '妖怪屋:薰': None,
    '苍蓝钢铁的琶音:吸血鬼': None,
    '莉莉安(虚拟UP主)': None,
    '小萤(守护甜心)': None,
    '拉娜(我的世界)': None,
}

# bgm <-> moegirl
subject_map = [
    (['原神'], ['原神']),
    (['崩坏3'], ['崩坏3']),
    (['崩坏:星穹铁道'], ['崩坏:星穹铁道']),
    (['绝区零'], ['绝区零']),
    (['阴阳师'], ['阴阳师(手游)']),
    (['舰队Collection'], ['舰队Collection舰娘']),
    (['战舰少女R'], ['战舰少女']),
    (['明日方舟'], ['明日方舟角色']),
    (['碧蓝航线'], ['碧蓝航线']),
    (['蔚蓝档案'], ['蔚蓝档案']),
    (['ONE PIECE'], ['海贼王']),
    (
        [
            "东方灵异传 ~ Highly Responsive to Prayers.",
            "东方封魔录 ~ the Story of Eastern Wonderland.",
            "东方梦时空 ~ Phantasmagoria of Dim. Dream.",
            "东方幻想乡 ~ Lotus Land Story.",
            "东方怪绮谈 ~ Mystic Square.",
            "东方红魔乡 ~ the Embodiment of Scarlet Devil.",
            "东方妖妖梦 ~ Perfect Cherry Blossom.",
            "东方永夜抄 ~ Imperishable Night.",
            "东方花映塚 ~ Phantasmagoria of Flower View.",
            "东方文花帖 ~ Shoot the Bullet.",
            "东方风神录 ~ Mountain of Faith.",
            "东方地灵殿 ~ Subterranean Animism.",
            "东方星莲船 ~ Undefined Fantastic Object.",
            "Double Spoiler ~ 东方文花帖",
            "妖精大战争 ~ 东方三月精",
            "东方神灵庙 ~ Ten Desires.",
            "东方辉针城 ~ Double Dealing Character.",
            "东方绀珠传 ~ Legacy of Lunatic Kingdom.",
            "东方天空璋 ~ Hidden Star in Four Seasons.",
            "东方鬼形兽 ~ Wily Beast and Weakest Creature.",
            "东方虹龙洞 ~ Unconnected Marketeers.",
            "弹幕狂们的黑市 ~ 100th Black Market.",
            "东方兽王园 ~ Unfinished Dream of All Living Ghost.",
            "东方凭依华 ~ Antinomy of Common Flowers.",
            "东方萃梦想 ~ Immaterial and Missing Power.",
            "东方绯想天 ~ Scarlet Weather Rhapsody.",
            "东方非想天则 ~ 追寻特大型人偶之谜",
            "东方深秘录 ~ Urban Legend in Limbo.",
            "弹幕天邪鬼 ~ Impossible Spell Card.",
            "东方心绮楼 ~ Hopeless Masquerade.",
            "秘封噩梦日记 ~ Violet Detector.",
            "东方刚欲异闻 ~ 被水淹没的沉愁地狱",
        ],
        ['东方Project'],
    ),
    (['梦王国与沉睡的100名王子'], ['梦王国与沉睡的100王子']),
    (['美少女花骑士'], ['美少女花骑士']),
    (['东京放学后召唤师'], ['东京放课后召唤师']),
    (
        ['坎特伯雷公主与骑士唤醒冠军之剑的奇幻冒险'],
        ['坎特伯雷公主与骑士唤醒冠军之剑的奇幻冒险'],
    ),
    (['公主连结 Re:Dive'], ['公主连结Re:Dive']),
    (['灰烬战线'], ['灰烬战线']),
    (['荒野乱斗'], ['荒野乱斗']),
    (
        [
            '假面骑士平成世代 Dr.吃豆人对Ex-Aid&Ghost with传说骑士',
            '假面骑士 巅峰英雄',
            '假面骑士DECADE',
            '假面骑士V3',
            '假面骑士Decade 超冒险DVD 守护!<电视君的世界>',
            '假面骑士Drive 秘密·任务 type LUPIN ~鲁邦,最后的挑战书~',
            '剧场版 假面骑士电王 老子,诞生!',
            '假面骑士玛洁德 with Girls Remix',
            '假面骑士外界者',
            '网络版 假面骑士W FOREVER AtoZ爆笑26连发',
            '假面骑士W Returns:假面骑士Accel',
            '假面骑士黑日',
            '假面骑士零一 最终舞台＆演员脱口秀',
            '假面骑士电王 超战斗DVD ~唱吧,跳吧,大特训!!~',
            '完全假面骑士:骑士世纪',
            '假面骑士歌查德 毕业篇',
            '剧场版 假面骑士响鬼与7人之战鬼',
            '假面骑士极狐 外传 假面骑士谛睨',
            '假面骑士利维斯 The Mystery',
            '假面骑士(天空骑士)',
            '剧场版 假面骑士555 消失的天堂',
            '假面骑士时王 NEXT TIME Geiz,Majesty',
            '假面骑士W FOREVER A 至 Z 命运的Gaia Memory',
            '假面骑士stronger',
            '假面骑士×假面骑士 W&DECADE MOVIE大战2010',
            '骑士时刻 假面骑士时王 VS Decade 7个时王!',
            '完全假面骑士 骑士世纪2',
            '剧场版 假面骑士X',
            '剧场版 假面骑士V3',
            '假面骑士W RETURNS 假面骑士Eternal',
            '完全假面骑士:骑士革命',
            '假面骑士Fourze 超战斗DVD 友情之Rocket Drill States',
            '奥特曼VS假面骑士',
            '假面骑士Build 超战斗DVD 假面骑士PRIME ROGUE',
            '假面骑士AGITO 三大骑士超战斗影像',
            '舞台(假面骑士斩月)‐铠武外传‐',
            '假面骑士极狐',
            '假面骑士V3对迪斯特龙怪人',
            '假面骑士空我 特别篇',
            '网络版 假面骑士Wizard 在真的吗?!大陆',
            'TV君超战斗DVD 假面骑士Zero-One 袋鼠的袋袋里跳出了什么?那种事自己带带脑子想想吧!好,一定得是我或人!!',
            '极狐Extra 假面骑士太狸meets假面骑士Shinobi',
            '假面骑士Genms SMART BRAIN 和1000%的危机',
            '剧场版 假面骑士KIVA 魔界城之王',
            '铠武外传:假面骑士杜古 / 假面骑士纳高尔',
            '假面骑士对修卡',
            '01 Others 假面骑士Vulcan ＆ Valkyrie',
            '假面骑士W',
            '假面骑士EX-AID',
            '假面骑士555 超战斗影像 新武器FaizSound完成!!',
            '假面骑士 英雄寻忆',
            '假面骑士W DVD 盖亚记忆体大图鉴',
            '假面骑士响鬼',
            '剧场版 假面骑士DECADE ALL RIDER对大修卡',
            '剧场版 假面骑士Wizard in Magic Land',
            '假面骑士Amazons',
            '假面骑士超一号',
            '假面骑士ZO',
            '假面骑士×超级战队×宇宙刑事 超级英雄大战Z',
            '剧场版 假面骑士EX-AID True・Ending',
            '假面骑士剑 20th Anniversary STAGE&TALK',
            '假面骑士J',
            '假面骑士Amazons THE MOVIE 最后的审判',
            '假面骑士歌查德',
            '假面骑士Drive',
            'DRIVE SAGA 假面骑士Brain',
            '假面骑士Build 超战斗DVD 诞生!熊电视!! VS假面骑士Grease',
            '假面骑士Wizard',
            '假面骑士圣刃',
            '假面骑士AGITO',
            '假面骑士×假面骑士 Drive & 铠武 Movie大战Full Throttle',
            '假面骑士 THE FIRST',
            '假面骑士铠武',
            '真·假面骑士 序章',
            '极狐Extra 假面骑士朋克杰克',
            '假面骑士 THE NEXT',
            '假面骑士利维斯:奇美拉的诞生',
            '假面骑士加布',
            '假面骑士空我',
            '假面骑士BLACK 紧急前往鬼之岛',
            '假面骑士 巅峰乱斗',
            '假面骑士:超越世代',
            '假面骑士贞德 & 假面骑士阿基蕾拉 with Girls Remix',
            '假面骑士电王',
            '剧场版 假面骑士剑 MISSING ACE',
            '剧场版 假面骑士利维斯 BATTEL FAMILIA',
            '假面骑士SD',
            '假面骑士KABUTO 超战斗DVD 诞生!Gatack Hyper Form!!',
            '假面骑士SPECTER x BLADES',
            '假面骑士极狐:4位王者与黑狐',
            '剧场版 假面骑士AGITO PROJECT G4',
            '假面骑士剑 超战斗影像 假面骑士剑VS剑',
            '假面骑士 平成世代FINAL Build＆Ex-Aid with 传说骑士',
            '10号诞生!假面骑士全员集合!!',
            '假面骑士:超巅峰英雄',
            '假面骑士Drive 秘密任务 type TV-KUN Hunter & Monster!追缉超怪盗之谜!',
            '假面骑士甲斗',
            '假面骑士圣刃衍生 剑士列传',
            '剧场版 假面骑士BUILD Be The One',
            '假面骑士Juuga VS 假面骑士Orteca',
            '剧场版 假面骑士铠武 足球决战!黄金果实争夺杯!',
            '假面骑士555 杀人事件',
            '剧场版 假面骑士Ghost 100眼魂和Ghost命运的瞬间',
            '假面骑士×假面骑士 Wizard&Fourze Movie大战Ultimatum',
            '假面骑士KIVA',
            '假面骑士铠武 Fresh Orange Arms诞生! ~你也抓住!新鲜之力~',
            '新·假面骑士',
            '假面骑士Ghost 传说! 骑士之魂!',
            '假面骑士Ex-Aid [秘技]虚拟运行',
            '假面骑士555 20周年 天堂·重获',
            '假面骑士(天空骑士) 8大骑士VS银河王',
            '假面骑士Ex-Aid 秘技 假面骑士Para-Dx',
            'TV君超战斗DVD 假面骑士极狐 怎么着!?全是男人的DGP 王蛇是我啊!!',
            '剧场版 假面骑士电王&KIVA 高潮刑事',
            '假面骑士×假面骑士 Ghost & Drive 超MOVIE大战 Genesis',
            '假面骑士空我 新春特别篇',
            '假面骑士Fourze THE MOVIE 大家一起宇宙来了!',
            '东岛丹三郎想成为假面骑士',
            '假面骑士:巅峰英雄Fourze',
            '假面骑士Saber x Ghost',
            'd Video特别篇 假面骑士4号',
            '假面骑士Ghost 超战斗DVD 真相!英雄眼魂的秘密!',
            '假面骑士龙骑 特别篇 13骑士',
            '铠武外传:假面骑士GRIDON VS 假面骑士BRAVO',
            '假面骑士Wizard 舞蹈戒指的Show Time',
            '假面骑士时王',
            '假面骑士Fourze',
            '暴太郎战队咚兄弟遇见假面骑士电王:以咚之王为目标!',
            '假面骑士AGITO 特别篇 新的变身',
            '假面骑士歌查德剧场版:THE·未来·破晓',
            '剧场版 假面骑士OOO WONDERFUL 将军与21核心硬币',
            '假面骑士:巅峰战士',
            '假面骑士Ghost 一休眼魂争夺!机智的胜负!!',
            '假面骑士Drive SURPRISE FUTURE',
            '超战斗DVD 假面骑士利维斯 2号骑士开选了~♪',
            '假面骑士×假面骑士 OOO&W feat.SKULL MOVIE大战CORE',
            '假面骑士龙骑',
            '假面骑士对地狱大使',
            '假面骑士 正义的系谱',
            '剧场版 假面骑士超一号',
            '假面骑士OOO 10th 复活的核心硬币',
            '假面骑士空我 VS 刚力怪人Go·Jiino·Da',
            "网络版 OOO·电王·全体骑士 Let's Go 假面骑士 ~寻找!属于你的骑士48~",
            '假面骑士×超级战队 超级英雄大战',
            '假面骑士亚马逊',
            '剧场版 风都侦探 假面骑士Skull的肖像',
            '剧场版 假面骑士stronger',
            '假面骑士KIVA 超战斗DVD 你也成为KIVA吧',
            '假面骑士 令和的豪华运动会',
            '假面骑士 歌查德 VS 假面骑士 雷杰多',
            '假面骑士EX-AID 电玩救世篇',
            'VCINEXT 利维斯Forward:假面骑士莱伊布＆艾比尔＆戴蒙斯',
            '剧场版 假面骑士利维斯',
            '假面骑士BLACK',
            '假面骑士555',
            '假面骑士Build',
            '假面骑士Ex-Aid [秘技]假面骑士Genm',
            '假面骑士:巅峰英雄OOO',
            "OOO·电王·全体骑士 Let's Go 假面骑士",
            '假面骑士×假面骑士 铠武&Wizard 天下决胜之战国MOVIE大合战',
            '铠武外传:假面骑士斩月 / 假面骑士巴隆',
            '假面骑士EX-AID [秘技]假面骑士Lazer',
            '假面骑士剑',
            '假面骑士Ex-Aid [秘技]假面骑士Snipe EPISODE ZERO',
            '电视君超战斗DVD 假面骑士加布:点心般的美食 Woo!我的海带面!',
            '假面骑士 THE WINTER MOVIE 歌查德&极狐 最强凯米★拿下大作战',
            '假面骑士',
            '小说 假面骑士W',
            '电视君 超战斗DVD 假面骑士歌查德 怎么办!?宝太郎和凛音互换身体了!!',
            '假面骑士Black',
            'RIDER TIME 假面骑士龙骑',
            '平成假面骑士20作纪念 假面骑士 平成Generation FOREVER',
            '假面骑士世界',
            'RIDER TIME 假面骑士Shinobi',
            '假面骑士:斗骑大战 创生',
            '假面骑士极狐 邪魔徒·觉醒',
            '假面骑士×超级战队 超超级英雄大战',
            '假面骑士×假面骑士×假面骑士 THE MOVIE 超・电王三部曲',
            '假面骑士X',
            '假面骑士Ghost 一休入魂!觉醒吧,我的机智力量!!',
            '假面骑士电王 漂亮电王登场',
            'Revie Legacy 假面骑士贝尔',
            '假面骑士BLACK RX',
            '假面骑士01',
            '剧场短篇 假面骑士圣刃 不死鸟的剑士与破坏的书',
            '假面骑士W 超战斗DVD 盖浇饭的α/再会爱的食谱',
            '假面骑士:天唤骑兵',
            'Go!Go!假面骑士',
            '平成骑士VS昭和骑士 假面骑士feat.超级战队',
            '剧场版 假面骑士KABUTO 神·速·爱',
            '假面骑士OOO 超战斗DVD 测验,舞蹈与Takagarooba',
            '假面骑士 巅峰英雄 W',
            '假面骑士Ghost 亚兰英雄传',
            '别册 假面骑士圣刃 万画 假面骑士大剑',
            '假面骑士圣刃衍生 假面骑士佩剑&假面骑士恒剑',
            '假面骑士极狐×利维斯 电影大逃杀',
            '骑士时刻 假面骑士Decade VS 时王 Decade馆的死亡游戏',
            '假面骑士Ex-Aid[秘技] 假面骑士Brave ~生存吧!复活的野兽骑士·小队~',
            '迎向假面骑士的世界',
            '假面骑士Amazons 第二季',
            '初代假面骑士',
            '假面骑士EX-AID 三部曲 Another Ending',
            '假面骑士Drive 秘密任务 type TOKUJO',
            '网络版 假面骑士FOURZE 大家一起上课来啦!',
            '假面骑士1号',
            '假面骑士SPIRITS',
            '剧场版 假面骑士龙骑 EPISODE FINAL',
            '剧场版 假面骑士01 REAL×TIME',
            '假面骑士BATTLE GANBARIDE 卡片大战',
            '超级英雄大战GP 假面骑士3号',
            'DRIVE SAGA 假面骑士Mach / 假面骑士Heart',
            '假面骑士利维斯',
            '假面骑士 令和 The First Generation',
            '假面骑士龙骑 超战斗影像 龙骑VS假面骑士AGITO',
            '假面骑士 斗骑大战',
            '超战斗DVD 假面骑士利维斯 考拉VS袋鼠!!在婚礼上呼唤爱!?',
            '假面骑士Drive 秘密任务 type ZERO 第0话 倒计时to Global Freeze',
            'Build NEW WORLD 假面骑士Grease',
            '假面骑士Build 提高Hazard Level~7个Best Match~',
            '美版 假面骑士龙骑',
            '假面骑士×假面骑士 Fourze & OOO MOVIE大战 MEGA MAX',
            'Build NEW WORLD 假面骑士CROSS-Z',
            '假面骑士Ghost',
            '假面骑士龙骑(美版) 游戏版',
            'DRIVE SAGA 假面骑士Chaser',
            '假面骑士响鬼 超战斗DVD 明日梦变身!你也可以成为鬼!!',
            '剧场版 假面骑士亚马逊',
            '假面骑士圣刃 深罪的三重奏',
            '假面骑士Ghost RE:BIRTH 假面骑士Specter',
            '剧场版 假面骑士时王 Over Quartzer',
            '假面骑士Drive 超战斗DVD 秘密任务type HIGH SPEED! 真正的力量!type HIGH SPEED诞生!',
            '假面骑士Fourze 天文开关秘密报告',
            '假面骑士OOO',
            '假面骑士KABUTO',
            '假面骑士Genms ―The Presidents―',
            '假面骑士时王 最终舞台&番组演员脱口秀',
            '全员集合!7位假面骑士!!',
            '01 Others 假面骑士灭亡迅雷',
        ],
        ['假面骑士'],
    ),
    (['最终幻想 零式'], ['TYPE-0']),
]

subject_special = {}

subject_reverse_special = {}

bgm_index = load_json("bgm_index_full.json")
bgm_chars = load_json("bgm_chars_full.json")
bgm_subjects = load_json("bgm_subjects_full.json")

print("loaded: bgm_index:", len(bgm_index))
print("loaded: bgm_chars:", len(bgm_chars))
print("loaded: bgm_subjects:", len(bgm_subjects))

moegirl_chars = load_json("../moegirl/preprocess/char_index.json")
print("loaded: moegirl_chars:", len(moegirl_chars))
moegirl_extra = load_json("../moegirl/crawler2/extra_processed.json")
print("loaded: moegirl_extra:", len(moegirl_extra))
char2subject = load_json("../moegirl/preprocess/char2subject.json")
print("loaded: char2subject:", len(char2subject))


for k, v in subject_map:
    for entry in k:
        subject_special[entry] = set(v)
    for entry in v:
        subject_reverse_special[entry] = set(k)

for k, v in special_map.items():
    if v is not None and v not in reverse_special:
        reverse_special[v] = k

for k, v in reverse_special.items():
    if v is not None and v not in special_map:
        special_map[v] = k


def is_postfix(a, b):
    if len(a) < len(b):
        offset = len(b) - len(a)
        return b[offset - 1] == ":" and a == b[offset:]
    else:
        return a == b


converter = opencc.OpenCC("jp2t.json")
converter2 = opencc.OpenCC("t2s.json")


def conv(t):
    ret = []
    for i in t:
        s = converter2.convert(converter.convert(i))
        ret.append(s)
    return ret + t


def unique(l):
    ret = []
    for i in l:
        if i not in ret:
            ret.append(i)
    return ret


def conv_subject(t):
    replacements = {
        '：': ':',
        '，': ',',
        '；': ';',
        '！': '!',
        '？': '?',
        '。': '.',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '、': ',',
        '～': '~',
        '〜': '~',
        '（': '(',
        '）': ')',
        '⌈': '(',
        '⌋': ')',
        '⌊': '(',
        '⌉': ')',
        '「': '(',
        '」': ')',
        '《': '(',
        '》': ')',
        '／': '/',
        '〈': '<',
        '〉': '>',
        '【': '[',
        '】': ']',
    }
    for old, new in replacements.items():
        t = t.replace(old, new)
    return t


def multisplit(str, sp=",，/／"):
    ret = []
    cur = ""
    for i in str:
        if i in sp:
            cur = cur.strip()
            if cur != "":
                ret.append(cur)
            cur = ""
        else:
            cur += i
    cur = cur.strip()
    if cur != "":
        ret.append(cur)
    return ret


def moegirl_split(name):
    cur = name
    post = ""
    postpos = cur.find("(")
    if postpos != -1 and cur[-1] == ")":
        post = cur[postpos + 1 : -1]
        cur = cur[:postpos]

    pre = ""
    prepos = cur.find(":")
    if prepos != -1:
        pre = cur[:prepos]
        cur = cur[prepos + 1 :]

    return cur, pre, post


def smatch(moename, subjects):
    if moename == "":
        return 0
    cnt = 0
    for name, w in subjects:
        if name == moename:
            cnt += w
    return cnt


def map_bgm(entry, verbose=False):
    id = entry["id"]
    if id in special_map:
        special = special_map[id]
        if special is None:
            return []
        else:
            return [(special, 19260817)]

    subjects = bgm_subjects2[id]

    moe_subjects_special = set()
    for i, w in subjects:
        if w < 0.5:
            continue
        if i in subject_special:
            moe_subjects_special.update(subject_special[i])

    canon_name = []
    names = []
    char = bgm_chars[id]

    names.extend(multisplit(char["name"]))
    for i in char["infobox"]:
        if i["key"] == "简体中文名":
            if type(i["value"]) == str:
                names.extend(multisplit(i["value"]))
            else:
                for split in i["value"]:
                    split = multisplit(split["v"])
                    names.extend(split)
        elif i["key"] == "别名":
            if type(i["value"]) == str:
                names.extend(multisplit(i["value"]))
            else:
                for split in i["value"]:
                    if split["k"] == "罗马字":
                        continue
                    split = multisplit(split["v"])
                    names.extend(split)
    if "name" in entry:
        canon_name.extend(multisplit(entry["name"]))

    canon_name = unique(conv(canon_name))
    names = unique(conv(names))
    canon_name.sort(key=lambda x: len(x) - x.isascii() * 10, reverse=True)
    names.sort(key=lambda x: len(x) - x.isascii() * 10, reverse=True)
    names = canon_name + names
    names = unique(names)

    if verbose:
        print('subjects:', subjects)
        print("names:", names)

    match = []
    for i in names:
        if i in moe_lookup:
            for j in moe_lookup[i]:
                moeid = j[0]
                score = j[1]
                if moeid in reverse_special:
                    continue
                moesub = moe_subjects[moeid]
                # print(moeid, moesub)
                if len(moesub) > 0 and len(subjects) > 0:
                    subscore = 0
                    for k in moesub:
                        subscore += smatch(k, subjects)
                    # if subscore == 0:
                    #     continue
                    score += subscore * 5
                match.append((moeid, score, moesub))

                if len(moe_subjects_special) > 0:
                    flag = False
                    for k in moesub:
                        if k in moe_subjects_special:
                            flag = True
                    if flag:
                        match.append((moeid, score + 1000, moesub))
    match.sort(reverse=True, key=lambda x: x[1])

    if verbose:
        print('zeroth stage:', match)

    dedupe = {}
    match2 = []
    for i in match:
        if i[0] in dedupe:
            dedupe[i[0]] = (i[0], max(i[1], dedupe[i[0]][1]), i[2])
        else:
            dedupe[i[0]] = i

    for k, v in dedupe.items():
        match2.append(v)

    if verbose:
        print('first stage:', match2)

    birthday = None
    bloodtype = None
    height = None
    if char["blood_type"]:
        bloodtype = ["A", "B", "AB", "O"][char["blood_type"] - 1]
    if char["birth_mon"] and char["birth_day"]:
        birthday = [char["birth_year"], char["birth_mon"], char["birth_day"]]
    for i in char["infobox"]:
        match i["key"]:
            case "生日":
                if birthday is None:
                    tmp = [None, None, None]
                    if type(i["value"]) != str:
                        continue
                    m = re.search(r"((\d*)年)?((\d*)月)?((\d*)日)?", i["value"])
                    if m:
                        g = m.groups()
                        if g[1]:
                            tmp[0] = int(g[1])
                        if g[3]:
                            tmp[1] = int(g[3])
                        if g[5]:
                            tmp[2] = int(g[5])
                    if tmp[0] is None and tmp[1] is None and tmp[2] is None:
                        continue
                    birthday = tmp
            case "血型":
                if bloodtype is None:
                    tmp = i["value"].replace("型", "")
                    if tmp in ["A", "B", "AB", "O"]:
                        bloodtype = tmp
            case "身高":
                if height is None:
                    try:
                        tmp = int(i["value"].replace("cm", ""))
                        if 100 <= tmp <= 200:
                            height = tmp
                    except Exception as e:
                        pass

    if verbose:
        print('birthday:', birthday)
        print('bloodtype:', bloodtype)
        print('height:', height)

    for idx in range(len(match2)):
        mid = match2[idx][0]
        score = match2[idx][1]
        if mid not in moegirl_extra:
            continue
        char2 = moegirl_extra[mid]
        if "生日" in char2 and birthday:
            flag = True
            for j in range(3):
                if char2["生日"][j] and birthday[j] and char2["生日"][j] != birthday[j]:
                    flag = False
                    break
            if flag:
                score += 3
        if "身高" in char2 and height:
            if abs(char2["身高"] - height) <= 1:
                score += 3
        if "血型" in char2 and bloodtype:
            if char2["血型"] == bloodtype:
                score += 1
        match2[idx] = (mid, score, match2[idx][2])
    match2.sort(reverse=True, key=lambda x: x[1])

    if verbose:
        print('second stage:', match2)

    if len(match2) > 1:
        mains = {}
        for i in range(len(match2)):
            name, pre, post = moegirl_split(match2[i][0])
            if pre == "" and post == "" and match2[i][1] >= 3:
                mains[name] = i
        for main, idx in mains.items():
            cnt = 0
            wsum = 0
            for i in match2:
                name, pre, post = moegirl_split(i[0])
                if name == main:
                    cnt += 1
                    wsum += i[1]
            if cnt >= 2:
                if verbose:
                    print('possinle main:', main)
                match2[idx] = (match2[idx][0], wsum, match2[idx][2])
            match2.sort(reverse=True, key=lambda x: x[1])
            if verbose:
                print('third stage:', match2)

    return match2


bgm_subjects2 = {}

for entry in bgm_index:
    id = entry["id"]
    subjects = []
    if id in bgm_subjects:
        for entry in bgm_subjects[id]:
            score = 1
            if entry["staff"] == "客串":
                score = 0.3
            subjects.append((conv_subject(entry["name_cn"]), score))
            subjects.append((conv_subject(entry["name"]), score * 0.5))

    subjects = list(filter(lambda x: len(x[0]) > 0, subjects))
    subjects.sort(key=lambda x: x[1], reverse=True)
    subjects = unique(subjects)
    bgm_subjects2[id] = subjects


for k, v in char2subject.items():
    tmp = []
    for entry in v[1:]:
        if entry.endswith('的页面'):
            continue
        if entry.endswith('系列角色'):
            tmp.append(entry[:-4])
        elif entry.endswith('系列'):
            tmp.append(entry[:-2])
        if entry not in tmp:
            tmp.append(entry)
    char2subject[k] = tmp


moe_lookup = {}
moe_subjects = {}
for moeid in moegirl_chars:
    name, pre, post = moegirl_split(moeid)
    subjects = []
    if pre != "":
        subjects.append(pre)
    if moeid in char2subject:
        subjects.extend(char2subject[moeid])
    if post != "":
        subjects.append(post)
    subjects = unique(subjects)
    subjects = list(map(conv_subject, subjects))
    moe_subjects[moeid] = subjects

    if name not in moe_lookup:
        moe_lookup[name] = []
    moe_lookup[name].append((moeid, 1))
    if moeid in moegirl_extra:
        char = moegirl_extra[moeid]
        if "本名" in char:
            for idx, j in enumerate(char["本名"]):
                j = j.replace(" ", "").lower().strip('"\'')
                j = converter2.convert(converter.convert(j))
                if "不明" in j or "未知" in j or "不详" in j:
                    continue
                if j not in moe_lookup:
                    moe_lookup[j] = []
                moe_lookup[j].append((moeid, 1 / (idx + 2)))

    if '假面骑士' in subjects:
        name2 = '假面骑士' + name
        if name2 not in moe_lookup:
            moe_lookup[name2] = []
        moe_lookup[name2].append((moeid, 1))

if __name__ == "__main__":
    bgm2moegirl = {}
    moegirl2bgm = {}
    # bgm_index = bgm_index[:20000]

    multicount = 0
    nonecount = 0

    print(f"subject map len={len(bgm_subjects)}")
    print(f"char map len={len(bgm_chars)}")

    for cnt, entry in enumerate(tqdm(bgm_index)):
        moegirl_ids = map_bgm(entry, verbose=False)
        if len(moegirl_ids) > 0 and moegirl_ids[0][1] >= 2:
            score_limit = moegirl_ids[0][1] * 0.5
            moegirl_ids = list(filter(lambda x: x[1] >= score_limit, moegirl_ids))

        bgm_id = entry["id"]
        if bgm_id not in special_map:
            if len(moegirl_ids) == 0:
                nonecount += 1
            elif len(moegirl_ids) > 1:
                multicount += 1
                # print(cnt, bgm_id, entry['name'], moegirl_ids)

        tmp = []
        for res in moegirl_ids:
            moegirl_id, score = res[0], res[1]
            if moegirl_id not in moegirl_chars:
                print("not in moegirl_chars:", moegirl_id)
                continue
            tmp.append(moegirl_id)
            if moegirl_id not in moegirl2bgm:
                moegirl2bgm[moegirl_id] = []
            moegirl2bgm[moegirl_id].append((bgm_id, score, cnt))
        bgm2moegirl[bgm_id] = tmp

    for k, v in list(moegirl2bgm.items()):
        if k not in moe_subjects:
            continue
        moesub = moe_subjects[k]
        bgmsub = set()
        for sub in moesub:
            if sub in subject_reverse_special:
                bgmsub.update(subject_reverse_special[sub])
        if len(bgmsub) > 0:
            # print(moesub)
            # print(bgmsub)
            # print(k, list(map(lambda x: [bgm_chars[x[0]]["name"]] + list(x), v)))
            v2 = []
            for entry in v:
                # print(v, bgm_subjects2[i[0]])
                flag = False
                for j, w in bgm_subjects2[entry[0]]:
                    if j in bgmsub:
                        flag = True
                        break
                if flag:
                    v2.append(entry)
            moegirl2bgm[k] = v2
            # print(list(map(lambda x: [bgm_chars[x[0]]["name"]] + list(x), v2)))
            # print()

    for k, v in reverse_special.items():
        if v is None:
            moegirl2bgm[k] = []
        else:
            moegirl2bgm[k] = [(v, 998244353, -1)]

    print(
        "successful bgm2moegirl: {}/{}".format(
            len(bgm_index) - nonecount, len(bgm_index)
        )
    )
    print(f"multi={multicount} none={nonecount}")

    multicount2 = 0

    moegirl2bgm2 = {}
    for k, v in moegirl2bgm.items():
        v = v.copy()
        v.sort(key=lambda x: x[2])
        v.sort(reverse=True, key=lambda x: x[1])
        if len(v) > 0 and v[0][1] >= 2:
            score_limit = v[0][1] * 0.5
            v = list(filter(lambda x: x[1] >= score_limit, v))
        # if len(v) > 1:
        #     v = list(filter(lambda x: x[1] > 1, v))
        if len(v) == 0:
            continue
        if len(v) > 1:
            # print(k, list(map(lambda x: str([bgm_chars[x[0]]["name"]] + list(x)), v)))
            multicount2 += 1
        moegirl2bgm2[k] = list(map(lambda x: x[0], v))

    print("successful moegirl2bgm: {}/{}".format(len(moegirl2bgm2), len(moegirl_chars)))
    print(f"multi={multicount2} none={len(moegirl_chars)-len(moegirl2bgm2)}")

    save_json(bgm2moegirl, "bgm2moegirl.json")
    save_json(moegirl2bgm2, "moegirl2bgm.json")

    bgm_info = {}
    for k, v in moegirl2bgm2.items():
        if len(v) > 1:
            continue
        bgmid = v[0]
        collects = bgm_chars[bgmid]['stat']['collects']
        if collects >= 1:
            bgm_info[bgmid] = collects
    save_json(bgm_info, "bgm_info.json")

    # os.system('python -u img_preloader.py')
