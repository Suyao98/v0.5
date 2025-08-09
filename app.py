# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import streamlit as st

# ---------- 干支、五行、颜色等基本数据 -----------

tiangan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
dizhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
GZS_LIST = [tiangan[i%10] + dizhi[i%12] for i in range(60)]

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

gan_he = {"甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壬":"丁","戊":"癸","癸":"戊"}
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

# --------- 八字推算函数 ----------

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

def get_li_chun_datetime(year):
    return datetime.datetime(year,2,4,0,0)

def year_ganzhi(year, month, day, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute)
    lichun = get_li_chun_datetime(year)
    adj_year = year if dt >= lichun else year-1
    return GZS_LIST[(adj_year - 1984) % 60], adj_year

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

# ----------- 全国市级城市经纬度示例 -------------
# 这里示例部分城市，建议你用更全数据替换
# city_coords.py

city_coords = {
    # 直辖市
    "北京": (39.9042, 116.4074),
    "天津": (39.0842, 117.2000),
    "上海": (31.2304, 121.4737),
    "重庆": (29.4316, 106.9123),

    # 黑龙江省
    "哈尔滨": (45.8038, 126.5349),
    "齐齐哈尔": (47.3543, 123.9170),
    "牡丹江": (44.5886, 129.6080),
    "佳木斯": (46.8096, 130.3616),
    "大庆": (46.5907, 125.1127),

    # 吉林省
    "长春": (43.8160, 125.3235),
    "吉林": (43.8378, 126.5490),
    "四平": (43.1700, 124.3490),
    "辽源": (42.9026, 125.1365),

    # 辽宁省
    "沈阳": (41.8057, 123.4315),
    "大连": (38.9140, 121.6147),
    "鞍山": (41.1106, 122.9946),
    "抚顺": (41.8750, 123.9572),

    # 内蒙古自治区
    "呼和浩特": (40.8426, 111.7491),
    "包头": (40.6571, 109.8404),
    "乌兰察布": (40.9946, 113.1217),

    # 河北省
    "石家庄": (38.0428, 114.5149),
    "唐山": (39.6306, 118.1803),
    "保定": (38.8799, 115.4646),

    # 山西省
    "太原": (37.8706, 112.5489),
    "大同": (40.0768, 113.3000),
    "运城": (35.0228, 111.0031),

    # 陕西省
    "西安": (34.3416, 108.9398),
    "宝鸡": (34.3655, 107.2370),
    "咸阳": (34.3296, 108.7071),

    # 河南省
    "郑州": (34.7466, 113.6254),
    "洛阳": (34.6574, 112.4355),
    "开封": (34.7970, 114.3075),

    # 山东省
    "济南": (36.6828, 117.0249),
    "青岛": (36.0671, 120.3826),
    "烟台": (37.4638, 121.4480),

    # 江苏省
    "南京": (32.0603, 118.7969),
    "无锡": (31.5744, 120.2886),
    "苏州": (31.2989, 120.5853),

    # 安徽省
    "合肥": (31.8206, 117.2272),
    "芜湖": (31.3529, 118.4335),
    "安庆": (30.5373, 117.0636),

    # 湖北省
    "武汉": (30.5928, 114.3055),
    "襄阳": (32.0084, 112.1224),
    "宜昌": (30.6910, 111.2867),

    # 江西省
    "南昌": (28.6820, 115.8579),
    "九江": (29.7058, 115.9998),
    "赣州": (25.8453, 114.9359),

    # 湖南省
    "长沙": (28.2282, 112.9388),
    "株洲": (27.8270, 113.1410),
    "湘潭": (27.8297, 112.9441),

    # 广东省
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "佛山": (23.0215, 113.1214),

    # 广西壮族自治区
    "南宁": (22.8170, 108.3669),
    "柳州": (24.3144, 109.4222),
    "桂林": (25.2736, 110.2901),

    # 海南省
    "海口": (20.0440, 110.1999),

    # 四川省
    "成都": (30.5728, 104.0668),
    "绵阳": (31.4675, 104.6796),
    "德阳": (31.1301, 104.3803),

    # 贵州省
    "贵阳": (26.6470, 106.6302),
    "遵义": (27.7252, 106.9270),

    # 云南省
    "昆明": (24.8797, 102.8332),
    "曲靖": (25.4898, 103.7965),

    # 西藏自治区
    "拉萨": (29.6520, 91.1721),

    # 青海省
    "西宁": (36.6171, 101.7782),

    # 宁夏回族自治区
    "银川": (38.4872, 106.2309),

    # 新疆维吾尔自治区
    "乌鲁木齐": (43.8256, 87.6169),
    
    # 其他地级市示例（如需要可补充）
    "邯郸": (36.6256, 114.5386),
    "沧州": (38.3044, 116.8388),
    "廊坊": (39.5186, 116.7036),
    "承德": (40.9763, 117.9392),
    "张家口": (40.8244, 114.8870),
    "秦皇岛": (39.9354, 119.5996),

    # ...你可以根据需求继续添加更多城市
}


def find_city_coords(input_city):
    city = input_city.strip()
    if not city:
        return None
    if city.endswith("市"):
        if city in city_coords:
            return city_coords[city]
    else:
        city_with_shi = city + "市"
        if city_with_shi in city_coords:
            return city_coords[city_with_shi]
        if city in city_coords:
            return city_coords[city]
    for c in city_coords.keys():
        if city in c:
            return city_coords[c]
    return None

def calc_true_solar_time_correction(longitude):
    standard_meridian = 120.0
    correction = (longitude - standard_meridian) / 15.0
    return correction

def corrected_hour_minute(hour, minute, longitude):
    correction = calc_true_solar_time_correction(longitude)
    total_minutes = hour * 60 + minute + correction * 60
    total_minutes = total_minutes % (24 * 60)
    adj_hour = int(total_minutes // 60)
    adj_min = int(total_minutes % 60)
    return adj_hour, adj_min

# ------------- Streamlit 界面 -------------

st.set_page_config(page_title="流年吉凶", layout="centered")
st.title("流年吉凶")

mode = st.radio("", ["阳历生日", "四柱八字"])

if mode == "阳历生日":
    col1, col2 = st.columns([2,1])
    with col1:
        byear = st.number_input("出生年", min_value=1900, max_value=2100, value=1990, step=1)
        bmonth = st.number_input("出生月（数字）", min_value=1, max_value=12, value=5, step=1)
        bday = st.number_input("出生日", min_value=1, max_value=31, value=18, step=1)
    with col2:
        unknown_time = st.checkbox("时辰未知（跳过时柱）", value=False)
        if not unknown_time:
            city_input = st.text_input("输入城市名称（如‘成都’）", value="北京")
            use_true_solar = st.checkbox("使用真太阳时修正", value=False)
            bhour = st.number_input("小时（0-23）", min_value=0, max_value=23, value=8, step=1)
            bmin = st.number_input("分钟（0-59）", min_value=0, max_value=59, value=0, step=1)
        else:
            bhour = -1
            bmin = 0
            use_true_solar = False

    # **新增 性别选择**
    gender = st.selectbox("性别", options=["男", "女"], index=0)

    if st.button("查询吉凶"):
        if bhour != -1 and use_true_solar:
            coords = find_city_coords(city_input)
            if coords is None:
                st.warning(f"未找到城市“{city_input}”经纬度，默认使用东经120度")
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
            st.markdown("---")
            show_jixiong(ji, xiong, byear)

            # --- 新增大运计算和展示 ---

            # 计算起运岁数
            birth_date = datetime.date(byear, bmonth, bday)

            def get_day_diff_to_next_jieqi(birth_date):
                # 这里简化，只以“清明”节气4月5日举例，建议用你已有节气函数替换
                jieqi_date = datetime.date(birth_date.year, 4, 5)
                if birth_date > jieqi_date:
                    jieqi_date = datetime.date(birth_date.year + 1, 4, 5)
                return (jieqi_date - birth_date).days

            def calc_start_age(birth_date, birth_hour=0):
                day_diff = get_day_diff_to_next_jieqi(birth_date)
                # 时辰换算，1时辰=10天，按小时折算为10/2=5天/小时的简易估算
                extra_days = birth_hour * 5
                total_days = day_diff + extra_days
                start_age = int(total_days // 3)
                return max(start_age, 0)

            def is_yang_gan(gan):
                return gan in ["甲", "丙", "戊", "庚", "壬"]

            def gen_dayun_list(month_pillar, gender):
                # 60甲子列表复用你代码里的GZS_LIST
                try:
                    start_idx = GZS_LIST.index(month_pillar)
                except ValueError:
                    return []

                year_gan = month_pillar[0]
                yang = is_yang_gan(year_gan)

                if yang:
                    direction = 1 if gender == "男" else -1
                else:
                    direction = -1 if gender == "男" else 1

                dayun = []
                idx = start_idx
                for _ in range(8):
                    idx = (idx + direction) % 60
                    dayun.append(GZS_LIST[idx])
                return dayun

            def format_dayun_ranges(start_age, dayun_list):
                res = []
                age = start_age
                for gz in dayun_list:
                    res.append(f"{age}-{age+9}岁：{gz}")
                    age += 10
                return res

            start_age = calc_start_age(birth_date, hour_val or 0)
            dayun_list = gen_dayun_list(month_p, gender)
            dayun_ranges = format_dayun_ranges(start_age, dayun_list)

            st.markdown("## 大运排盘")
            st.markdown(f"月柱（起运干支）: {month_p}")
            st.markdown(f"起运年龄：{start_age}岁")
            for item in dayun_ranges:
                st.markdown(item)

        except Exception as e:
            st.error(f"计算出错：{e}")

elif mode == "四柱八字":
    nianzhu = st.text_input("年柱", max_chars=2)
    yuezhu = st.text_input("月柱", max_chars=2)
    rizhu = st.text_input("日柱", max_chars=2)
    shizhu = st.text_input("时柱", max_chars=2)
    start_year = st.number_input("用于列出吉凶年份的起始年（例如出生年）", min_value=1600, max_value=2100, value=1990, step=1)

    if st.button("分析吉凶"):
        try:
            ji, xiong = analyze_bazi(nianzhu.strip(), yuezhu.strip(), rizhu.strip(), shizhu.strip())
            st.markdown("## 四柱八字")
            render_four_pillars_two_rows(nianzhu.strip() or "  ", yuezhu.strip() or "  ", rizhu.strip() or "  ", shizhu.strip() or "  ")
            st.markdown("---")
            show_jixiong(ji, xiong, int(start_year))
        except Exception as e:
            st.error(f"计算出错：{e}")
