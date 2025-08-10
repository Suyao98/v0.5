# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import streamlit as st
import math

# ========== 全国市级经纬度（KEY 为常用城市名，不带“市/区”后缀；如需可扩展） ==========
# 说明：数百条数据，覆盖全国地级市常用名称（含直辖市、自治州、盟等）
CITY_COORDS = {
    # 直辖市 / 省会
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "天津": (39.3434, 117.3616),
    "重庆": (29.4316, 106.9123),
    
    # 河北
    "石家庄": (38.0428, 114.5149),
    "唐山": (39.6309, 118.1802),
    "秦皇岛": (39.9354, 119.5996),
    "邯郸": (36.6256, 114.5389),
    "邢台": (37.0706, 114.5044),
    "保定": (38.8730, 115.4646),
    "张家口": (40.8244, 114.8875),
    "承德": (40.9515, 117.9624),
    "沧州": (38.3044, 116.8388),
    "廊坊": (39.5378, 116.6838),
    "衡水": (37.7389, 115.6702),

    # 山西
    "太原": (37.8706, 112.5489),
    "大同": (40.0768, 113.3001),
    "阳泉": (37.8612, 113.5690),
    "长治": (36.1954, 113.1163),
    "晋城": (35.4907, 112.8513),
    "朔州": (39.3316, 112.4230),
    "晋中": (37.6870, 112.7528),
    "运城": (35.0264, 111.0075),
    "忻州": (38.4167, 112.7342),
    "临汾": (36.0882, 111.5189),
    "吕梁": (37.5193, 111.1443),

    # 内蒙古
    "呼和浩特": (40.8419, 111.7492),
    "包头": (40.6571, 109.8404),
    "乌海": (39.6737, 106.8260),
    "赤峰": (42.2869, 118.9308),
    "通辽": (43.6529, 122.2434),
    "鄂尔多斯": (39.6081, 109.7813),
    "呼伦贝尔": (49.2116, 119.7658),
    "巴彦淖尔": (40.7430, 107.3877),
    "乌兰察布": (40.9938, 113.1214),
    "兴安盟": (46.0837, 122.0446),
    "锡林郭勒": (43.9334, 116.0482),
    "阿拉善": (38.8497, 105.7359),

    # 辽宁
    "沈阳": (41.8057, 123.4315),
    "大连": (38.9140, 121.6147),
    "鞍山": (41.1106, 122.9946),
    "抚顺": (41.8750, 123.9572),
    "本溪": (41.2943, 123.7669),
    "丹东": (40.1246, 124.3383),
    "锦州": (41.1192, 121.1477),
    "营口": (40.6676, 122.2349),
    "阜新": (42.0113, 121.6480),
    "辽阳": (41.2697, 123.1724),
    "盘锦": (41.1193, 122.0708),
    "铁岭": (42.2996, 123.8440),
    "朝阳": (41.5730, 120.4518),
    "葫芦岛": (40.7556, 120.8564),

    # 吉林
    "长春": (43.8160, 125.3235),
    "吉林": (43.8378, 126.5490),
    "四平": (43.1700, 124.3490),
    "辽源": (42.9026, 125.1365),
    "通化": (41.7250, 125.9580),
    "白山": (41.9420, 126.4246),
    "松原": (45.1360, 124.8250),
    "白城": (45.6191, 122.8367),
    "延边": (42.9048, 129.5150),

    # 黑龙江
    "哈尔滨": (45.8038, 126.5349),
    "齐齐哈尔": (47.3543, 123.9170),
    "牡丹江": (44.5886, 129.6080),
    "佳木斯": (46.8096, 130.3616),
    "大庆": (46.5907, 125.1127),
    "伊春": (47.7333, 128.8409),
    "鸡西": (45.2951, 130.9759),
    "鹤岗": (47.3387, 130.2925),
    "双鸭山": (46.6465, 131.1574),
    "七台河": (45.7722, 130.8936),
    "绥化": (46.6461, 126.9891),
    "黑河": (50.2457, 127.5286),
    "大兴安岭": (51.8083, 124.1006),

    # 上海 / 江苏 / 浙江 / 安徽 / 福建 / 江西 等东部
    "南京": (32.0603, 118.7969),
    "无锡": (31.5744, 120.2886),
    "徐州": (34.2044, 117.2840),
    "苏州": (31.2989, 120.5853),
    "南通": (32.0160, 121.6156),
    "连云港": (34.6016, 119.1738),
    "淮安": (33.5023, 119.0210),
    "盐城": (33.3558, 120.1635),
    "扬州": (32.3932, 119.4129),
    "镇江": (32.1896, 119.4255),
    "泰州": (32.4760, 119.9159),
    "宿迁": (33.9630, 118.2752),

    "杭州": (30.2741, 120.1551),
    "宁波": (29.8683, 121.5440),
    "温州": (27.9949, 120.6994),
    "嘉兴": (30.7461, 120.7550),
    "湖州": (30.8944, 120.1024),
    "绍兴": (30.0024, 120.5925),
    "金华": (29.0791, 119.6474),
    "衢州": (28.9744, 118.8758),
    "舟山": (30.0151, 122.1828),
    "台州": (28.6574, 121.4208),
    "丽水": (28.4675, 119.9226),

    "合肥": (31.8206, 117.2272),
    "芜湖": (31.3529, 118.4335),
    "蚌埠": (32.9396, 117.3570),
    "淮南": (32.6428, 117.0240),
    "马鞍山": (31.6700, 118.5079),
    "安庆": (30.5431, 117.0636),
    "宿州": (33.6454, 116.9849),
    "阜阳": (32.9012, 115.8197),
    "亳州": (33.8790, 115.7829),
    "黄山": (29.7149, 118.3377),
    "滁州": (32.3035, 118.3160),
    "淮北": (33.9600, 116.7918),
    "铜陵": (30.9401, 117.8126),
    "宣城": (30.9401, 118.7528),
    "六安": (31.7410, 116.5053),

    "福州": (26.0745, 119.2965),
    "厦门": (24.4798, 118.0895),
    "莆田": (25.4292, 119.0102),
    "三明": (26.2634, 117.6350),
    "泉州": (24.8739, 118.6758),
    "漳州": (24.5180, 117.6474),
    "南平": (26.6418, 118.1777),
    "龙岩": (25.0780, 117.0175),
    "宁德": (26.6659, 119.0000),

    "南昌": (28.6820, 115.8579),
    "景德镇": (29.2926, 117.2049),
    "萍乡": (27.6229, 113.8531),
    "九江": (29.7058, 115.9998),
    "新余": (27.8100, 114.9300),
    "鹰潭": (28.2386, 117.0336),
    "赣州": (25.8453, 114.9359),
    "吉安": (27.1134, 114.9936),
    "宜春": (27.8119, 114.4236),
    "抚州": (27.9839, 116.3609),
    "上饶": (28.4576, 117.9558),

    # 山东
    "济南": (36.6828, 117.0249),
    "青岛": (36.0671, 120.3826),
    "淄博": (36.8131, 118.0558),
    "枣庄": (34.7878, 117.3230),
    "东营": (37.4346, 118.6750),
    "烟台": (37.4638, 121.4479),
    "潍坊": (36.7127, 119.1618),
    "济宁": (35.4153, 116.5871),
    "泰安": (36.2001, 117.0899),
    "威海": (37.5162, 122.1216),
    "日照": (35.4164, 119.5072),
    "莱芜": (36.2132, 117.6671),
    "临沂": (35.1040, 118.3564),
    "德州": (37.4530, 116.3074),
    "聊城": (36.4560, 115.9804),
    "滨州": (37.3833, 117.9689),
    "菏泽": (35.2475, 115.4800),

    # 河南
    "郑州": (34.7466, 113.6254),
    "开封": (34.7970, 114.3075),
    "洛阳": (34.6574, 112.4355),
    "平顶山": (33.7665, 113.3000),
    "安阳": (36.0964, 114.3525),
    "鹤壁": (35.7526, 114.2978),
    "新乡": (35.3030, 113.9268),
    "焦作": (35.2100, 113.2118),
    "濮阳": (35.7686, 115.0419),
    "许昌": (34.0264, 113.8253),
    "漯河": (33.5758, 114.0264),
    "三门峡": (34.7725, 111.2001),
    "商丘": (34.4155, 115.6564),
    "周口": (33.6374, 114.6966),
    "驻马店": (33.0114, 114.0241),
    "南阳": (33.0090, 112.5285),

    # 湖北
    "武汉": (30.5928, 114.3055),
    "黄石": (30.1999, 115.0385),
    "十堰": (32.6290, 110.7879),
    "宜昌": (30.6910, 111.2867),
    "襄阳": (32.0084, 112.1224),
    "鄂州": (30.3913, 114.8946),
    "荆门": (31.0354, 112.2059),
    "孝感": (30.9247, 113.9166),
    "荆州": (30.3400, 112.2410),
    "黄冈": (30.4477, 114.8720),
    "咸宁": (29.8416, 114.3225),
    "随州": (31.6900, 113.3796),
    "恩施": (30.2832, 109.4869),

    # 湖南
    "长沙": (28.2282, 112.9388),
    "株洲": (27.8270, 113.1410),
    "湘潭": (27.8297, 112.9441),
    "衡阳": (26.9006, 112.6077),
    "邵阳": (27.2389, 111.4680),
    "岳阳": (29.3703, 113.1335),
    "常德": (29.0149, 111.6537),
    "张家界": (29.1171, 110.4792),
    "益阳": (28.5553, 112.3554),
    "郴州": (25.7823, 113.0320),
    "永州": (26.4206, 111.6141),
    "怀化": (27.5501, 109.9869),
    "娄底": (27.7380, 112.0085),
    "湘西": (28.3170, 109.7397),

    # 广东
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "珠海": (22.2707, 113.5767),
    "汕头": (23.3535, 116.6819),
    "佛山": (23.0215, 113.1214),
    "韶关": (24.8106, 113.5945),
    "湛江": (21.1967, 110.3655),
    "肇庆": (23.0515, 112.4792),
    "江门": (22.5780, 113.0815),
    "茂名": (21.6598, 110.9255),
    "惠州": (23.1115, 114.4169),
    "梅州": (24.2796, 116.1275),
    "汕尾": (22.7862, 115.3750),
    "河源": (23.7460, 114.6978),
    "阳江": (21.8592, 111.9759),
    "清远": (23.6850, 113.0579),
    "东莞": (23.0207, 113.7518),
    "中山": (22.5151, 113.3926),
    "潮州": (23.6618, 116.6323),
    "揭阳": (23.5477, 116.3795),
    "云浮": (22.9150, 112.0443),

    # 广西
    "南宁": (22.8170, 108.3669),
    "柳州": (24.3144, 109.4222),
    "桂林": (25.2736, 110.2901),
    "梧州": (23.4745, 111.2975),
    "北海": (21.4811, 109.1200),
    "防城港": (21.6141, 108.3500),
    "钦州": (21.9671, 108.6244),
    "贵港": (23.1115, 109.6115),
    "玉林": (22.6544, 110.1517),
    "百色": (23.9072, 106.6318),
    "贺州": (24.4036, 111.5526),
    "河池": (24.6926, 108.0650),
    "来宾": (23.7338, 109.2276),
    "崇左": (22.3754, 107.3539),

    # 海南
    "海口": (20.0440, 110.1999),
    "三亚": (18.2528, 109.5119),
    "三沙": (16.8341, 112.3517),
    "儋州": (19.5170, 109.5766),

    # 四川
    "成都": (30.5728, 104.0668),
    "自贡": (29.3592, 104.7784),
    "攀枝花": (26.5875, 101.7186),
    "泸州": (28.8956, 105.44397),
    "德阳": (31.1311, 104.4028),
    "绵阳": (31.4675, 104.6796),
    "广元": (32.4355, 105.8298),
    "遂宁": (30.5396, 105.5731),
    "内江": (29.6000, 105.0731),
    "乐山": (29.6000, 103.7614),
    "南充": (30.8378, 106.1170),
    "眉山": (30.0758, 103.8485),
    "宜宾": (28.7577, 104.6309),
    "广安": (30.4555, 106.6333),
    "达州": (31.2142, 107.4941),
    "雅安": (29.9850, 103.0017),
    "巴中": (31.8678, 106.7530),
    "资阳": (30.1320, 104.6276),
    # ... 省份内若干地级市略（你可按需补充） ...

    # 贵州
    "贵阳": (26.6470, 106.6302),
    "六盘水": (26.5919, 104.8526),
    "遵义": (27.7252, 106.9270),
    "安顺": (26.2450, 105.9322),
    "铜仁": (27.6749, 109.2019),
    "毕节": (27.3320, 105.3338),
    "黔西南": (25.0920, 104.8964),
    "黔东南": (26.5830, 107.9739),
    "黔南": (26.2592, 107.5185),

    # 云南
    "昆明": (24.8797, 102.8332),
    "曲靖": (25.4898, 103.7965),
    "玉溪": (24.3508, 102.5439),
    "保山": (25.1205, 99.1770),
    "昭通": (27.3398, 103.7175),
    "丽江": (26.8550, 100.2260),
    "普洱": (22.8256, 100.9740),
    "临沧": (23.8856, 100.0869),
    "楚雄": (25.0329, 101.5456),
    "红河": (23.3756, 103.3849),
    "文山": (23.4030, 104.2440),
    "西双版纳": (21.9716, 100.7600),
    "大理": (25.5890, 100.2257),
    "德宏": (24.4367, 98.5895),
    "怒江": (25.8500, 98.8546),
    "迪庆": (27.8266, 99.7024),

    # 西藏
    "拉萨": (29.6520, 91.1721),
    "日喀则": (29.2670, 88.8800),
    "昌都": (31.1376, 97.1786),
    "林芝": (29.6508, 94.3620),
    "那曲": (31.4760, 92.0606),
    "阿里": (32.5031, 80.1034),

    # 陕西
    "西安": (34.3416, 108.9398),
    "铜川": (34.9127, 108.9799),
    "宝鸡": (34.3655, 107.2370),
    "咸阳": (34.3296, 108.7071),
    "渭南": (34.4995, 109.5029),
    "延安": (36.6034, 109.4890),
    "汉中": (33.0776, 107.0286),
    "榆林": (38.2794, 109.7453),
    "安康": (32.7044, 109.0293),
    "商洛": (33.8683, 109.9342),

    # 甘肃
    "兰州": (36.0565, 103.8342),
    "嘉峪关": (39.8020, 98.2890),
    "金昌": (38.5201, 102.1879),
    "白银": (36.5457, 104.1738),
    "天水": (34.5800, 105.7249),
    "武威": (37.9288, 102.6329),
    "张掖": (38.9256, 100.4550),
    "平凉": (35.5436, 106.6846),
    "酒泉": (39.7442, 98.5106),
    "庆阳": (35.7097, 107.6442),
    "定西": (35.5796, 104.6266),
    "陇南": (33.4000, 104.9290),
    "临夏": (35.6012, 103.2155),
    "甘南": (34.9838, 102.9116),

    # 青海
    "西宁": (36.6171, 101.7782),
    "海东": (36.5025, 102.1033),
    "海北": (36.9597, 100.9010),
    "黄南": (35.5190, 102.0191),
    "海南州": (35.5105, 100.6197),
    "果洛": (34.4736, 100.2421),
    "玉树": (33.0067, 97.0086),
    "海西": (37.3763, 97.3699),

    # 宁夏
    "银川": (38.4872, 106.2309),
    "石嘴山": (38.9896, 106.3762),
    "吴忠": (37.9972, 106.1980),
    "固原": (36.0045, 106.2853),
    "中卫": (37.5009, 105.1968),

    # 新疆（常用地级市）
    "乌鲁木齐": (43.8256, 87.6169),
    "克拉玛依": (45.5790, 84.8898),
    "吐鲁番": (42.9511, 89.1895),
    "哈密": (42.8339, 93.5132),
    "昌吉": (44.0140, 87.3016),
    "博尔塔拉": (44.9036, 82.0747),
    "巴音郭楞": (41.7641, 86.1528),
    "阿克苏": (41.1671, 80.2696),
    "喀什": (39.4704, 75.9898),
    "和田": (37.1112, 79.9231),
    "伊犁": (43.9219, 81.3306),
    "塔城": (46.7587, 82.9855),
    "阿勒泰": (47.8486, 88.1404),
    "石河子": (44.3167, 86.0419),
    "五家渠": (44.1674, 87.5270),

    # 港澳台（常用）
    "香港": (22.3193, 114.1694),
    "澳门": (22.1987, 113.5439),
    "台北": (25.0330, 121.5654),
    "高雄": (22.6273, 120.3014),

    # 常见地级市补充（若需更多可继续扩充）
    "温州": (27.9949, 120.6994),
    "嘉兴": (30.7461, 120.7550),
    "绍兴": (30.0024, 120.5925),
    "金华": (29.0791, 119.6474),
    "泉州": (24.8739, 118.6758),
    "漳州": (24.5180, 117.6474),
    "珠海": (22.2707, 113.5767),
    "汕头": (23.3535, 116.6819),
    "邵阳": (27.2389, 111.4680),
    "株洲": (27.8270, 113.1410),
    "岳阳": (29.3703, 113.1335),
    "柳州": (24.3144, 109.4222),
    "桂林": (25.2736, 110.2901),
    "南宁": (22.8170, 108.3669),
    "海口": (20.0440, 110.1999),
    "三亚": (18.2528, 109.5119),
    "兰州": (36.0565, 103.8342),
    "西宁": (36.6171, 101.7782),
    "银川": (38.4872, 106.2309),
    "乌鲁木齐": (43.8256, 87.6169)
}

# ========== 基础：干支、甲子表 ==========
tiangan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
dizhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
GZS_LIST = [tiangan[i%10] + dizhi[i%12] for i in range(60)]

def ganzhi_list():
    return GZS_LIST

# 五行（按天干/地支）与颜色
WUXING_OF_GAN = {
    "甲":"木","乙":"木",
    "丙":"火","丁":"火",
    "戊":"土","己":"土",
    "庚":"金","辛":"金",
    "壬":"水","癸":"水"
}
WUXING_OF_DZ = {
    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火",
    "午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"
}
WUXING_COLOR = {
    "木": "#2e7d32",
    "火": "#d32f2f",
    "土": "#c19a6b",
    "金": "#ffd700",
    "水": "#1565c0"
}

# ========== 合/冲 规则（你之前的规则） ==========
gan_he = {"甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壳":"壬","壬":"丁","戊":"癸","癸":"戊"}
# NOTE: 保留你原始的 gan_chong（已删除戊/己冲）
gan_chong = {"甲":"庚","庚":"甲","乙":"辛","辛":"乙","丙":"壬","壬":"丙","丁":"癸","癸":"丁"}
zhi_he = {"子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午"}
zhi_chong = {dz: dizhi[(i+6)%12] for i, dz in enumerate(dizhi)}

def zhi_next(z): return dizhi[(dizhi.index(z)+1)%12]
def zhi_prev(z): return dizhi[(dizhi.index(z)-1)%12]

def unique_list(seq):
    seen=set(); out=[]
    for s in seq:
        if s not in seen:
            seen.add(s); out.append(s)
    return out

def calc_jixiong(gz):
    if not gz or len(gz) < 2:
        return {"吉":[], "凶":[]}
    tg, dz = gz[0], gz[1]
    res = {"吉":[], "凶":[]}
    tg_he = gan_he.get(tg, "")
    dz_he = zhi_he.get(dz, "")
    tg_ch = gan_chong.get(tg, "")
    dz_ch = zhi_chong.get(dz, "")
    if tg_he and dz_he:
        shuang_he = tg_he + dz_he
        jin_yi = tg_he + zhi_next(dz_he)
        res["吉"].extend([shuang_he, jin_yi])
    if tg_ch and dz_ch:
        shuang_ch = tg_ch + dz_ch
        tui_yi = tg_ch + zhi_prev(dz_ch)
        res["凶"].extend([shuang_ch, tui_yi])
    return res

def analyze_bazi(year_zhu, month_zhu, day_zhu, time_zhu):
    pillars = [p for p in (year_zhu, month_zhu, day_zhu) if p]
    if time_zhu and str(time_zhu).strip() and str(time_zhu).strip().lower() not in ["不要","不要时","不知道"]:
        pillars.append(time_zhu)
    all_ji=[]; all_xiong=[]
    for p in pillars:
        r = calc_jixiong(p)
        all_ji.extend(r["吉"]); all_xiong.extend(r["凶"])
    return unique_list(all_ji), unique_list(all_xiong)

# ========== 八字推算：锚点日法 & 月柱/时柱规则 ==========
ANCHOR_DATE = date(1984,1,1)
ANCHOR_GZ = "甲午"
ANCHOR_INDEX = GZS_LIST.index(ANCHOR_GZ)

def day_ganzhi_by_anchor(y,m,d,h=None):
    if h is not None and h >= 23:
        target = date(y,m,d) + timedelta(days=1)
    else:
        target = date(y,m,d)
    delta = (target - ANCHOR_DATE).days
    idx = (ANCHOR_INDEX + delta) % 60
    return GZS_LIST[idx]

# --------- 这里是替换后的节气（立春）计算函数，尝试兼容 sxtwl 不同版本 ---------
def get_li_chun_datetime(year):
    """
    返回指定年份的“立春”时刻（本函数尽力尝试使用 sxtwl 的多种可能接口）。
    若环境没有安装 sxtwl 或无法正确调用，将回退到近似值：year-02-04 00:00。
    """
    try:
        import sxtwl
    except Exception:
        # sxtwl 不可用 -> 使用近似值，避免抛错
        return datetime.datetime(year, 2, 4, 0, 0)

    # Try various APIs that different sxtwl versions might expose
    try:
        # 1) 常见：sxtwl.getJieQiJD(yq) 或 sxtwl.getJieQiJD(year*100 + qi_index)
        if hasattr(sxtwl, "getJieQiJD"):
            try:
                jd = sxtwl.getJieQiJD(year * 100 + 3)  # 3 通常为立春（部分版本）
                if jd:
                    if hasattr(sxtwl, "JD2DD"):
                        dd = sxtwl.JD2DD(jd + 0.5)
                        y = dd // 10000
                        m = (dd % 10000) // 100
                        d = dd % 100
                        return datetime.datetime(int(y), int(m), int(d), 0, 0)
            except Exception:
                pass

        # 2) 有些版本把 getJieQi 等放到模块属性名不同或类中，尝试 Lunar 类（若存在）
        if hasattr(sxtwl, "Lunar"):
            try:
                lunar = sxtwl.Lunar()
                if hasattr(lunar, "getJieQiJD"):
                    jd = lunar.getJieQiJD(year * 100 + 3)
                    if jd and hasattr(sxtwl, "JD2DD"):
                        dd = sxtwl.JD2DD(jd + 0.5)
                        y = dd // 10000
                        m = (dd % 10000) // 100
                        d = dd % 100
                        return datetime.datetime(int(y), int(m), int(d), 0, 0)
            except Exception:
                pass

        # 3) 有些版本使用 sxtwl.getJQ 或者 sxtwl.getJieQi 等，尝试这些名称
        for fn_name in ("getJQ", "getJieQi", "getJieQiByYear", "jieqi"):
            if hasattr(sxtwl, fn_name):
                try:
                    fn = getattr(sxtwl, fn_name)
                    # 某些函数可能返回浮点儒略日或日期元组
                    res = fn(year)
                    # 如果返回 dict/列表/tuple，尝试从中找立春（关键字/位置可能不同）
                    # 这里做较宽松的尝试：若返回值是数值，视作儒略日
                    if isinstance(res, (int, float)):
                        if hasattr(sxtwl, "JD2DD"):
                            dd = sxtwl.JD2DD(res + 0.5)
                            y = dd // 10000
                            m = (dd % 10000) // 100
                            d = dd % 100
                            return datetime.datetime(int(y), int(m), int(d), 0, 0)
                    # 若返回复合结构，尝试检索包含立春信息（按经验此处难以通用）
                except Exception:
                    continue

    except Exception:
        # 若上面任何一步内部报错，统一回退
        pass

    # 最后回退：近似值（2月4日）
    return datetime.datetime(year, 2, 4, 0, 0)

# year_ganzhi 使用 get_li_chun_datetime
def year_ganzhi(year, month, day, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute)
    lichun = get_li_chun_datetime(year)
    adj_year = year if dt >= lichun else year-1
    return GZS_LIST[(adj_year - 1984) % 60], adj_year

# 近似节气划分月支（寅月起）
JIEQI = [
    (2,4,"寅"), (3,6,"卯"), (4,5,"辰"), (5,6,"巳"), (6,6,"午"),
    (7,7,"未"), (8,7,"申"), (9,7,"酉"), (10,8,"戌"), (11,7,"亥"),
    (12,7,"子"), (1,6,"丑"),
]
def get_month_branch(year, month, day):
    bd = date(year, month, day)
    for i,(m,d,branch) in enumerate(JIEQI):
        dt = date(year if m != 1 else year+1, m, d)
        dt_next = date(year if JIEQI[(i+1)%12][0] != 1 else year+1, JIEQI[(i+1)%12][0], JIEQI[(i+1)%12][1])
        if dt <= bd < dt_next:
            return branch
    return "寅"

def month_stem_by_fihu_dun(year_tg, month_branch):
    if year_tg in ("甲","己"): first = "丙"
    elif year_tg in ("乙","庚"): first = "戊"
    elif year_tg in ("丙","辛"): first = "庚"
    elif year_tg in ("丁","壬"): first = "壬"
    elif year_tg in ("戊","癸"): first = "甲"
    else: first = "丙"
    start_idx = tiangan.index(first)
    offset = (dizhi.index(month_branch) - dizhi.index("寅")) % 12
    tg_idx = (start_idx + offset) % 10
    return tiangan[tg_idx] + month_branch

def get_hour_branch_by_minute(hour, minute):
    if hour is None:
        return None
    tot = hour*60 + (minute or 0)
    if tot >= 23*60 or tot < 1*60:
        return "子", 0
    intervals = [
        (1*60, 3*60, "丑"),
        (3*60, 5*60, "寅"),
        (5*60, 7*60, "卯"),
        (7*60, 9*60, "辰"),
        (9*60, 11*60, "巳"),
        (11*60, 13*60, "午"),
        (13*60, 15*60, "未"),
        (15*60, 17*60, "申"),
        (17*60, 19*60, "酉"),
        (19*60, 21*60, "戌"),
        (21*60, 23*60, "亥"),
    ]
    for i,(s,e,name) in enumerate(intervals):
        if s <= tot < e:
            return name, i+1
    return "子", 0

def time_ganzhi_by_rule(day_gz, hour, minute):
    if hour is None or hour < 0:
        return "不知道"
    branch, idx = get_hour_branch_by_minute(hour, minute)
    day_gan = day_gz[0]
    if day_gan in ("甲","己"): start = tiangan.index("甲")
    elif day_gan in ("乙","庚"): start = tiangan.index("丙")
    elif day_gan in ("丙","辛"): start = tiangan.index("戊")
    elif day_gan in ("丁","壬"): start = tiangan.index("庚")
    elif day_gan in ("戊","癸"): start = tiangan.index("壬")
    else: start = 0
    tg_idx = (start + idx) % 10
    return tiangan[tg_idx] + branch

def year_ganzhi_map(start=1900, end=2100):
    base = 1984
    return {y: GZS_LIST[(y-base) % 60] for y in range(start, end+1)}

def color_of_gan(gan_ch):
    el = WUXING_OF_GAN.get(gan_ch, "土")
    return WUXING_COLOR.get(el, "#000000")
def color_of_dz(dz_ch):
    el = WUXING_OF_DZ.get(dz_ch, "土")
    return WUXING_COLOR.get(el, "#000000")

def render_four_pillars_two_rows(year_p, month_p, day_p, hour_p):
    pillars = [year_p, month_p, day_p, hour_p]
    pillars = [p if p and len(p) == 2 else "  " for p in pillars]
    tiangan_row = [p[0] for p in pillars]
    dizhi_row = [p[1] for p in pillars]

    html = "<div style='display:flex;justify-content:center;margin-bottom:10px;'>"
    for tg in tiangan_row:
        c = color_of_gan(tg)
        html += f"<div style='width:60px;text-align:center;font-size:32px;font-weight:700;color:{c};margin:0 8px'>{tg}</div>"
    html += "</div>"

    html += "<div style='display:flex;justify-content:center;'>"
    for dz in dizhi_row:
        c = color_of_dz(dz)
        html += f"<div style='width:60px;text-align:center;font-size:32px;font-weight:700;color:{c};margin:0 8px'>{dz}</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def show_jixiong(ji_list, xiong_list, birth_year):
    current_year = datetime.datetime.now().year
    start = birth_year
    end = 2100
    ymap = year_ganzhi_map(start, end)

    order_key = lambda x: GZS_LIST.index(x) if x in GZS_LIST else 999

    st.subheader("🎉 吉年")
    if not ji_list:
        st.info("无吉年（按当前规则）")
    else:
        for gz in sorted(ji_list, key=order_key):
            years = [y for y,g in ymap.items() if g == gz]
            if not years: continue
            years.sort()
            past = [y for y in years if y <= current_year]
            future = [y for y in years if y > current_year]
            parts = []
            for y in past:
                parts.append(f"{y}年")
            for y in future:
                parts.append(f"<b>{y}年★</b>")
            st.markdown(
                f"<div style='padding:8px;border-left:4px solid #2e7d32;background:#f1fbf1;border-radius:6px;margin-bottom:6px;color:#145214'><b>{gz}</b>: {'，'.join(parts)}</div>",
                unsafe_allow_html=True
            )

    st.subheader("☠️ 凶年")
    if not xiong_list:
        st.info("无凶年（按当前规则）")
    else:
        for gz in sorted(xiong_list, key=order_key):
            years = [y for y,g in ymap.items() if g == gz]
            if not years: continue
            years.sort()
            past = [y for y in years if y <= current_year]
            future = [y for y in years if y > current_year]
            parts = []
            for y in past:
                parts.append(f"{y}年")
            for y in future:
                parts.append(f"<b>{y}年★</b>")
            st.markdown(
                f"<div style='padding:8px;border-left:4px solid #8b0000;background:#fff6f6;border-radius:6px;margin-bottom:6px;color:#5b0000'><b>{gz}</b>: {'，'.join(parts)}</div>",
                unsafe_allow_html=True
            )

# --------- 城市查找（用嵌入 CITY_COORDS，支持多种容错匹配） -------------
def normalize_city_name(s):
    if not s:
        return ""
    s = s.strip()
    # remove common suffixes/whitespace
    for suf in ["市", "省", "自治区", "自治州", "地区", "盟", "特别行政区", "区", "县"]:
        if s.endswith(suf):
            s = s[:-len(suf)]
    return s.strip()

def find_city_coords(input_city):
    if not input_city:
        return None
    s = str(input_city).strip()
    s_norm = normalize_city_name(s)
    # direct lookups
    if s in CITY_COORDS:
        return CITY_COORDS[s]
    if s_norm in CITY_COORDS:
        return CITY_COORDS[s_norm]
    # try with/without 市
    if s + "市" in CITY_COORDS:
        return CITY_COORDS[s + "市"]
    if s_norm + "市" in CITY_COORDS:
        return CITY_COORDS[s_norm + "市"]
    # case-insensitive keys (though keys in Chinese typically same)
    for k,v in CITY_COORDS.items():
        if s == k or s_norm == k:
            return v
    # fuzzy contains
    for k,v in CITY_COORDS.items():
        if s in k or k in s or s_norm in k or k in s_norm:
            return v
    return None

def calc_true_solar_time_correction(longitude):
    # correction in hours relative to standard meridian (东经120度)
    standard_meridian = 120.0
    correction_hours = (longitude - standard_meridian) / 15.0
    return correction_hours

def corrected_hour_minute(hour, minute, longitude):
    correction_hours = calc_true_solar_time_correction(longitude)
    total_minutes = hour * 60 + minute + correction_hours * 60
    total_minutes = total_minutes % (24 * 60)
    adj_hour = int(total_minutes // 60)
    adj_min = int(total_minutes % 60)
    return adj_hour, adj_min

# ========== 大运函数（保持你原有逻辑，仅妥善集成） ==========
def is_strict_double_he(gz1, gz2):
    gan_he_pairs = [("甲","己"),("己","甲"),("乙","庚"),("庚","乙"),
                    ("丙","辛"),("辛","丙"),("丁","壬"),("壬","丁"),
                    ("戊","癸"),("癸","戊")]
    dz_he_pairs = [("子","丑"),("丑","子"),("寅","亥"),("亥","寅"),
                   ("卯","戌"),("戌","卯"),("辰","酉"),("酉","辰"),
                   ("巳","申"),("申","巳"),("午","未"),("未","午")]
    if not gz1 or not gz2 or len(gz1) < 2 or len(gz2) < 2:
        return False
    gan1, dz1 = gz1[0], gz1[1]
    gan2, dz2 = gz2[0], gz2[1]
    return (gan1, gan2) in gan_he_pairs and (dz1, dz2) in dz_he_pairs

def is_strict_double_chong(gz1, gz2):
    dz_chong_pairs = [("子","午"),("午","子"),
                      ("丑","未"),("未","丑"),
                      ("寅","申"),("申","寅"),
                      ("卯","酉"),("酉","卯"),
                      ("辰","戌"),("戌","辰"),
                      ("巳","亥"),("亥","巳")]
    if not gz1 or not gz2 or len(gz1) < 2 or len(gz2) < 2:
        return False
    dz1, dz2 = gz1[1], gz2[1]
    return (dz1, dz2) in dz_chong_pairs

def generate_dayun_list(year_gan, gender, month_pillar, forward=True, steps=8):
    if month_pillar not in GZS_LIST:
        base_index = 0
    else:
        base_index = GZS_LIST.index(month_pillar)
    result = []
    for i in range(steps):
        idx = (base_index + i + 1) % 60 if forward else (base_index - (i+1)) % 60
        result.append(GZS_LIST[idx])
    return result

def calc_qiyun_age_by_terms(birth_date, gender, year_gan, solar_terms_dates):
    yang_gans = ["甲","丙","戊","庚","壬"]
    is_yang_year = year_gan in yang_gans
    if (is_yang_year and gender == "男") or (not is_yang_year and gender == "女"):
        forward = True
    else:
        forward = False

    terms_sorted = sorted(solar_terms_dates)
    if forward:
        next_terms = [d for d in terms_sorted if d > birth_date]
        if not next_terms:
            next_term = terms_sorted[0].replace(year=birth_date.year+1)
        else:
            next_term = next_terms[0]
        delta_days = (next_term - birth_date).days
    else:
        prev_terms = [d for d in terms_sorted if d <= birth_date]
        if not prev_terms:
            prev_term = terms_sorted[-1].replace(year=birth_date.year-1)
        else:
            prev_term = prev_terms[-1]
        delta_days = (birth_date - prev_term).days

    years = int(delta_days // 3)
    rem = delta_days % 3
    months = int((rem / 3.0) * 12)
    return forward, years, months

def show_dayun_two_rows(dayun_list, start_age, birth_year, ji_list, xiong_list, year_p, month_p, day_p, hour_p):
    labels = []
    years = []
    for i, gz in enumerate(dayun_list):
        seg_start = birth_year + start_age + i*10
        seg_end = seg_start + 9
        label = gz
        if any(is_strict_double_he(gz, p) for p in [year_p, month_p, day_p, hour_p] if p and len(p)==2):
            label += "（双合）"
            if gz not in ji_list: ji_list.append(gz)
        if any(is_strict_double_chong(gz, p) for p in [year_p, month_p, day_p, hour_p] if p and len(p)==2):
            label += "（双冲）"
            if gz not in xiong_list: xiong_list.append(gz)
        labels.append(label)
        years.append(f"{seg_start}-{seg_end}")
    html_upper = "<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px;'>"
    for lab in labels:
        html_upper += f"<div style='padding:6px 10px;border-radius:6px;background:#f0f7ff;font-weight:700'>{lab}</div>"
    html_upper += "</div>"
    html_lower = "<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;'>"
    for yr in years:
        html_lower += f"<div style='padding:5px 8px;border-radius:6px;background:#fff9e6;color:#333'>{yr}</div>"
    html_lower += "</div>"
    st.markdown(html_upper + html_lower, unsafe_allow_html=True)

# ========== Streamlit 页面 ==========
st.set_page_config(page_title="流年吉凶", layout="centered")

# 居中美化标题
st.markdown(
    "<h1 style='text-align:center; color:#2e7d32; font-weight:900;'>🌟 流年吉凶 🌟</h1>",
    unsafe_allow_html=True
)

# 主布局三栏：左侧模式选择+附加选项，右侧输入
col1, col3 = st.columns([4, 6])

with col1:
    mode = st.radio("", ["阳历生日", "四柱八字"], horizontal=True)

    if mode == "阳历生日":
        c1, c2 = st.columns(2)
        with c1:
            unknown_time = st.checkbox("时辰未知", value=False)
        with c2:
            use_true_solar = st.checkbox("真太阳时修正", value=False)
    else:
        unknown_time = False
        use_true_solar = False

with col3:
    if mode == "阳历生日":
        col31, col32, col33 = st.columns(3)
        with col31:
            byear = st.number_input("出生年", min_value=1900, max_value=2100, value=1990, step=1)
        with col32:
            bmonth = st.number_input("出生月", min_value=1, max_value=12, value=5, step=1)
        with col33:
            bday = st.number_input("出生日", min_value=1, max_value=31, value=18, step=1)

        if not unknown_time:
            bhour = st.number_input("小时", min_value=0, max_value=23, value=8, step=1)
            bmin = st.number_input("分钟", min_value=0, max_value=59, value=0, step=1)
        else:
            bhour = -1
            bmin = 0

        city_input = None
        if use_true_solar and not unknown_time:
            city_input = st.text_input("出生城市", value="北京")

    else:
        nianzhu = st.text_input("年柱", max_chars=2)
        yuezhu = st.text_input("月柱", max_chars=2)
        rizhu = st.text_input("日柱", max_chars=2)
        shizhu = st.text_input("时柱", max_chars=2)
        start_year = st.number_input("出生年份", min_value=1600, max_value=2100, value=1990, step=1)

# 查询按钮放底部居中
st.markdown("<br>", unsafe_allow_html=True)
query_trigger = st.button("🔍 查询吉凶", use_container_width=True)

# 按钮触发计算放这里
if mode == "阳历生日" and query_trigger:
    if bhour != -1 and use_true_solar:
        coords = find_city_coords(city_input)
        if coords is None:
            st.warning(f"未找到城市“{city_input}”经纬度，默认使用东经120度，建议采用临近城市")
            lon = 120.0
        else:
            lon = coords[1]
        adj_hour, adj_min = corrected_hour_minute(bhour, bmin, lon)
    else:
        adj_hour, adj_min = bhour, bmin

    hour_val = None if bhour == -1 else adj_hour
    min_val = None if bhour == -1 else adj_min

    try:
        year_p, adj_year = year_ganzhi(byear, bmonth, bday, hour_val or 0, min_val or 0)
        day_p = day_ganzhi_by_anchor(byear, bmonth, bday, hour_val)
        mb = get_month_branch(byear, bmonth, bday)
        month_p = month_stem_by_fihu_dun(year_p[0], mb)
        hour_p = "不知道" if hour_val is None else time_ganzhi_by_rule(day_p, hour_val, min_val or 0)

        st.markdown("## 四柱八字")
        render_four_pillars_two_rows(year_p, month_p, day_p, hour_p)

        ji, xiong = analyze_bazi(year_p, month_p, day_p, hour_p)

        # 改为左右两栏显示吉凶流年
        col_ji, col_xiong = st.columns(2)

        with col_ji:
            st.subheader("🎉 吉年")
            if not ji:
                st.info("无吉年（按当前规则）")
            else:
                order_key = lambda x: GZS_LIST.index(x) if x in GZS_LIST else 999
                current_year = datetime.datetime.now().year
                start = byear
                end = 2100
                ymap = year_ganzhi_map(start, end)
                for gz in sorted(ji, key=order_key):
                    years = [y for y,g in ymap.items() if g == gz]
                    if not years:
                        continue
                    years.sort()
                    past = [y for y in years if y <= current_year]
                    future = [y for y in years if y > current_year]
                    parts = []
                    for y in past:
                        parts.append(f"{y}年")
                    for y in future:
                        parts.append(f"<b>{y}年★</b>")
                    st.markdown(
                        f"<div style='padding:8px;border-left:4px solid #2e7d32;background:#f1fbf1;border-radius:6px;margin-bottom:6px;color:#145214'><b>{gz}</b>: {'，'.join(parts)}</div>",
                        unsafe_allow_html=True
                    )
        with col_xiong:
            st.subheader("☠️ 凶年")
            if not xiong:
                st.info("无凶年（按当前规则）")
            else:
                order_key = lambda x: GZS_LIST.index(x) if x in GZS_LIST else 999
                current_year = datetime.datetime.now().year
                start = byear
                end = 2100
                ymap = year_ganzhi_map(start, end)
                for gz in sorted(xiong, key=order_key):
                    years = [y for y,g in ymap.items() if g == gz]
                    if not years:
                        continue
                    years.sort()
                    past = [y for y in years if y <= current_year]
                    future = [y for y in years if y > current_year]
                    parts = []
                    for y in past:
                        parts.append(f"{y}年")
                    for y in future:
                        parts.append(f"<b>{y}年★</b>")
                    st.markdown(
                        f"<div style='padding:8px;border-left:4px solid #8b0000;background:#fff6f6;border-radius:6px;margin-bottom:6px;color:#5b0000'><b>{gz}</b>: {'，'.join(parts)}</div>",
                        unsafe_allow_html=True
                    )

    except Exception as e:
        st.error(f"计算出错：{e}")

elif mode == "四柱八字" and query_trigger:
    try:
        ji, xiong = analyze_bazi(nianzhu.strip(), yuezhu.strip(), rizhu.strip(), shizhu.strip())
        st.markdown("## 你输入的四柱")
        render_four_pillars_two_rows(nianzhu.strip() or "  ", yuezhu.strip() or "  ", rizhu.strip() or "  ", shizhu.strip() or "  ")

        st.markdown("---")

        # 左右两栏展示吉凶流年
        col_ji, col_xiong = st.columns(2)
        with col_ji:
            st.subheader("🎉 吉年")
            if not ji:
                st.info("无吉年（按当前规则）")
            else:
                order_key = lambda x: GZS_LIST.index(x) if x in GZS_LIST else 999
                current_year = datetime.datetime.now().year
                start = int(start_year)
                end = 2100
                ymap = year_ganzhi_map(start, end)
                for gz in sorted(ji, key=order_key):
                    years = [y for y,g in ymap.items() if g == gz]
                    if not years:
                        continue
                    years.sort()
                    past = [y for y in years if y <= current_year]
                    future = [y for y in years if y > current_year]
                    parts = []
                    for y in past:
                        parts.append(f"{y}年")
                    for y in future:
                        parts.append(f"<b>{y}年★</b>")
                    st.markdown(
                        f"<div style='padding:8px;border-left:4px solid #2e7d32;background:#f1fbf1;border-radius:6px;margin-bottom:6px;color:#145214'><b>{gz}</b>: {'，'.join(parts)}</div>",
                        unsafe_allow_html=True
                    )
        with col_xiong:
            st.subheader("☠️ 凶年")
            if not xiong:
                st.info("无凶年（按当前规则）")
            else:
                order_key = lambda x: GZS_LIST.index(x) if x in GZS_LIST else 999
                current_year = datetime.datetime.now().year
                start = int(start_year)
                end = 2100
                ymap = year_ganzhi_map(start, end)
                for gz in sorted(xiong, key=order_key):
                    years = [y for y,g in ymap.items() if g == gz]
                    if not years:
                        continue
                    years.sort()
                    past = [y for y in years if y <= current_year]
                    future = [y for y in years if y > current_year]
                    parts = []
                    for y in past:
                        parts.append(f"{y}年")
                    for y in future:
                        parts.append(f"<b>{y}年★</b>")
                    st.markdown(
                        f"<div style='padding:8px;border-left:4px solid #8b0000;background:#fff6f6;border-radius:6px;margin-bottom:6px;color:#5b0000'><b>{gz}</b>: {'，'.join(parts)}</div>",
                        unsafe_allow_html=True
                    )

    except Exception as e:
        st.error(f"计算出错：{e}")
