# -*- coding: utf-8 -*-
import datetime
from datetime import date, timedelta
import streamlit as st
import math

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

def get_li_chun_datetime(year):
    return datetime.datetime(year,2,4,0,0)

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

# ----------- 全国市级城市经纬度示例（简略） -------------
# 你若放 city_coords.py 文件，可用 from city_coords import city_coords
city_coords = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "成都": (30.5728, 104.0668),
    # ... 建议替换为完整 city_coords.py 导入 ...
}

def find_city_coords(input_city):
    if not input_city:
        return None
    city = input_city.strip()
    if city in city_coords:
        return city_coords[city]
    if city.endswith("市"):
        if city in city_coords:
            return city_coords[city]
        short = city[:-1]
        if short in city_coords:
            return city_coords[short]
    city_with_shi = city + "市"
    if city_with_shi in city_coords:
        return city_coords[city_with_shi]
    # 模糊匹配
    for c in city_coords.keys():
        if city in c or c in city:
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

# ========== 大运相关函数（你提供 / 优化） ==========
def is_strict_double_he(gz1, gz2):
    gan_he_pairs = [("甲","己"),("己","甲"),("乙","庚"),("庚","乙"),
                    ("丙","辛"),("辛","丙"),("丁","壬"),("壬","丁"),("戊","癸"),("癸","戊")]
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
    """
    显示大运（两行）：上行为大运干支+吉/凶标记，下行为对应年份区间。
    规则：
      - 仍会检测大运与八字是否严格双合/双冲；
      - 如果严格双合则把该大运加入 ji_list；严格双冲则加入 xiong_list；
      - 显示时不再写“（双合）/（双冲）”，而是根据最终的 ji_list/xiong_list 标注“吉”或“凶”；
      - 标注优先逻辑：若同时在 ji_list 与 xiong_list 则显示“吉/凶”，仅在 ji_list 则“吉”，仅在 xiong_list 则“凶”，都没有则不显示。
    """
    labels = []
    years = []
    for i, gz in enumerate(dayun_list):
        seg_start = birth_year + start_age + i*10
        seg_end = seg_start + 9

        # 检测严格双合/双冲并加入吉凶列表（不在标签中直接显示双合/双冲）
        has_he = any(is_strict_double_he(gz, p) for p in [year_p, month_p, day_p, hour_p] if p and len(p)==2)
        has_chong = any(is_strict_double_chong(gz, p) for p in [year_p, month_p, day_p, hour_p] if p and len(p)==2)
        if has_he and gz not in ji_list:
            ji_list.append(gz)
        if has_chong and gz not in xiong_list:
            xiong_list.append(gz)

        # 根据最终吉凶列表决定标签状态
        is_j = gz in ji_list
        is_x = gz in xiong_list
        if is_j and not is_x:
            status_html = "<span style='display:inline-block;padding:2px 6px;border-radius:4px;background:#e8f6ea;color:#145214;margin-left:8px;font-weight:700'>吉</span>"
        elif is_x and not is_j:
            status_html = "<span style='display:inline-block;padding:2px 6px;border-radius:4px;background:#fff0f0;color:#8b0000;margin-left:8px;font-weight:700'>凶</span>"
        elif is_j and is_x:
            status_html = "<span style='display:inline-block;padding:2px 6px;border-radius:4px;background:#fff8e6;color:#8b4513;margin-left:8px;font-weight:700'>吉/凶</span>"
        else:
            status_html = ""

        # 构建标签（干支 + 状态）
        label_html = f"<div style='padding:6px 10px;border-radius:6px;background:#f0f7ff;font-weight:700;display:inline-flex;align-items:center'>{gz}{status_html}</div>"
        labels.append(label_html)
        years.append(f"{seg_start}-{seg_end}")

    # render two rows: labels then years
    html_upper = "<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px;'>"
    for lab in labels:
        html_upper += lab
    html_upper += "</div>"
    html_lower = "<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;'>"
    for yr in years:
        html_lower += f"<div style='padding:5px 8px;border-radius:6px;background:#fff9e6;color:#333'>{yr}</div>"
    html_lower += "</div>"
    st.markdown(html_upper + html_lower, unsafe_allow_html=True)

# ========== Streamlit 页面 ==========
st.set_page_config(page_title="流年吉凶", layout="centered")
# UI: "请选择" + radio on same row
col_a, col_b = st.columns([1,3])
with col_a:
    st.markdown("**请选择**")
with col_b:
    mode = st.radio("", ["阳历生日", "四柱八字"], horizontal=True)

# 阳历或四柱输入区域
if mode == "阳历生日":
    col1, col2 = st.columns([2,1])
    with col1:
        byear = st.number_input("出生年", min_value=1900, max_value=2100, value=1990, step=1)
        bmonth = st.number_input("出生月（数字）", min_value=1, max_value=12, value=5, step=1)
        bday = st.number_input("出生日", min_value=1, max_value=31, value=18, step=1)
    with col2:
        unknown_time = st.checkbox("时辰未知（跳过时柱）", value=False)
        use_true_solar = st.checkbox("使用真太阳时修正", value=False)
        if not unknown_time:
            bhour = st.number_input("小时（0-23）", min_value=0, max_value=23, value=8, step=1)
            bmin = st.number_input("分钟（0-59）", min_value=0, max_value=59, value=0, step=1)
        else:
            bhour = -1
            bmin = 0
    # city input shown only if use_true_solar checked
    city_input = None
    if use_true_solar and not unknown_time:
        city_input = st.text_input("输入城市名称（用于真太阳时修正）", value="北京")

    # 性别选择单独一行（保留原有功能不变）
    gender = st.selectbox("性别", ["男", "女"], index=0)

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

            # -------- 大运计算 ----------
            birth_date = datetime.date(byear, bmonth, bday)
            # 简化：构建当年（与相邻）的节气近似日期列表（按 24 节气近似）
            year = birth_date.year
            # JIEQI_COMPLETE 是近似24节气的元组列表 (month, day)
            JIEQI_COMPLETE = [
                (1,6),(1,20),(2,4),(2,19),(3,6),(3,21),(4,5),(4,20),
                (5,6),(5,21),(6,6),(6,21),(7,7),(7,22),(8,7),(8,23),
                (9,8),(9,23),(10,8),(10,23),(11,7),(11,22),(12,7),(12,22)
            ]
            solar_terms = []
            # build list including prev and next year terms for edge cases
            for y in (year-1, year, year+1):
                for m,d in JIEQI_COMPLETE:
                    try:
                        solar_terms.append(datetime.date(y, m, d))
                    except Exception:
                        pass

            forward, start_age, start_months = calc_qiyun_age_by_terms(birth_date, gender, year_p[0], solar_terms)
            dayun_list = generate_dayun_list(year_p[0], gender, month_p, forward=forward, steps=8)
            # compute birth-year-based start (round down months; we use birth_year + start_age)
            start_year_dayun = byear + start_age

            # show dayun (two rows)
            st.markdown("## 大运排盘")
            show_dayun_two_rows(dayun_list, start_age, byear, ji, xiong, year_p, month_p, day_p, hour_p)

            # after adding any dayun-based ji/xiong, show full 吉凶
            st.markdown("---")
            show_jixiong(ji, xiong, byear)

        except Exception as e:
            st.error(f"计算出错：{e}")

else:
    st.markdown("请直接输入四柱八字（例如：庚午、辛巳），时柱可填“不知道”以跳过。")
    nianzhu = st.text_input("年柱", max_chars=2)
    yuezhu = st.text_input("月柱", max_chars=2)
    rizhu = st.text_input("日柱", max_chars=2)
    shizhu = st.text_input("时柱", max_chars=2)
    start_year = st.number_input("用于列出吉凶年份的起始年（例如出生年）", min_value=1600, max_value=2100, value=1990, step=1)

    if st.button("分析吉凶"):
        try:
            ji, xiong = analyze_bazi(nianzhu.strip(), yuezhu.strip(), rizhu.strip(), shizhu.strip())
            st.markdown("## 你输入的四柱")
            render_four_pillars_two_rows(nianzhu.strip() or "  ", yuezhu.strip() or "  ", rizhu.strip() or "  ", shizhu.strip() or "  ")
            st.markdown("---")
            show_jixiong(ji, xiong, int(start_year))
        except Exception as e:
            st.error(f"计算出错：{e}")
