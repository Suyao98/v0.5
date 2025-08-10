# 在现有import后加：
import math

# 先在文件中适当位置添加大运辅助函数和数据：
def is_strict_double_he(gz1, gz2):
    # 严格双合：天干合+地支合（只考虑两字完全相合）
    # 天干合规则：甲己、乙庚、丙辛、丁壬、戊癸
    gan_he_pairs = [("甲","己"),("己","甲"),("乙","庚"),("庚","乙"),
                    ("丙","辛"),("辛","丙"),("丁","壬"),("壬","丁"),("戊","癸"),("癸","戊")]
    # 地支合规则，十二地支六合：子丑、寅亥、卯戌、辰酉、巳申、午未
    dz_he_pairs = [("子","丑"),("丑","子"),("寅","亥"),("亥","寅"),
                   ("卯","戌"),("戌","卯"),("辰","酉"),("酉","辰"),
                   ("巳","申"),("申","巳"),("午","未"),("未","午")]
    if len(gz1) != 2 or len(gz2) != 2:
        return False
    gan1, dz1 = gz1[0], gz1[1]
    gan2, dz2 = gz2[0], gz2[1]
    return ( (gan1, gan2) in gan_he_pairs ) and ( (dz1, dz2) in dz_he_pairs )

def is_strict_double_chong(gz1, gz2):
    # 严格双冲：只考虑地支相冲（干不考虑）
    dz_chong_pairs = [("子","午"),("午","子"),
                      ("丑","未"),("未","丑"),
                      ("寅","申"),("申","寅"),
                      ("卯","酉"),("酉","卯"),
                      ("辰","戌"),("戌","辰"),
                      ("巳","亥"),("亥","巳")]
    if len(gz1) != 2 or len(gz2) != 2:
        return False
    dz1, dz2 = gz1[1], gz2[1]
    return (dz1, dz2) in dz_chong_pairs

# 重新定义顺逆大运排列函数（结合你的规则）
def generate_dayun_list(year_gan, gender, month_pillar, forward=True, steps=8):
    # 参数说明：
    # year_gan: 年柱天干，如“甲”
    # gender: "男"或"女"
    # month_pillar: 月柱，如“丙寅”
    # forward: True为顺排，False逆排（根据阴阳男女性别决定）
    # steps: 大运数，默认8步
    # 参考六十甲子表
    base_index = GZS_LIST.index(month_pillar)
    result = []
    for i in range(steps):
        idx = (base_index + i) % 60 if forward else (base_index - i) % 60
        result.append(GZS_LIST[idx])
    return result

# 计算起运岁数和月份（含余数）
def calc_qiyun_age(birth_date, gender, year_gan, li_chun_date, solar_terms_dates):
    # 先确定顺逆
    # 阳年干
    yang_gans = ["甲","丙","戊","庚","壬"]
    yin_gans = ["乙","丁","己","辛","癸"]
    is_yang_year = year_gan in yang_gans
    # 顺排规则：
    # 男阳顺，女阴顺
    # 男阴逆，女阳逆
    if (is_yang_year and gender == "男") or (not is_yang_year and gender == "女"):
        forward = True
    else:
        forward = False

    # 找下个节气（顺排）或上个节气（逆排）
    # solar_terms_dates是有序列表（节气日期）
    # birth_date为datetime.date类型
    # 为简化示范，solar_terms_dates可用节气实际日期列表，需传入

    # 先过滤合适节气日期
    sorted_terms = sorted(solar_terms_dates)
    if forward:
        next_terms = [d for d in sorted_terms if d > birth_date]
        if not next_terms:
            # 年末后，取下一年第一个节气
            next_term = sorted_terms[0].replace(year=birth_date.year+1)
        else:
            next_term = next_terms[0]
        delta_days = (next_term - birth_date).days
    else:
        prev_terms = [d for d in sorted_terms if d <= birth_date]
        if not prev_terms:
            # 年初前，取上一年最后一个节气
            prev_term = sorted_terms[-1].replace(year=birth_date.year-1)
        else:
            prev_term = prev_terms[-1]
        delta_days = (birth_date - prev_term).days

    # 起运岁数 = 天数整除3，余数换算成月份（余数1天 = 4个月）
    years = delta_days // 3
    months = int((delta_days % 3) * 4 / 3)  # 0~4个月
    return forward, years, months

# 新增显示大运的函数
def show_dayun(dayun_list, start_age, start_year, ji_list, xiong_list, year_p, month_p, day_p, hour_p):
    st.subheader("🌓 大运")
    # 大运每步10年
    segments = []
    for i, gz in enumerate(dayun_list):
        start = start_year + start_age + i*10
        end = start + 9
        # 判断大运干支是否与八字有严格双合或双冲
        has_double_he = any(is_strict_double_he(gz, p) for p in [year_p, month_p, day_p, hour_p] if p and len(p)==2)
        has_double_chong = any(is_strict_double_chong(gz, p) for p in [year_p, month_p, day_p, hour_p] if p and len(p)==2)
        label = gz
        if has_double_he:
            label += "（双合）"
            if gz not in ji_list:
                ji_list.append(gz)
        if has_double_chong:
            label += "（双冲）"
            if gz not in xiong_list:
                xiong_list.append(gz)
        segments.append(f"{label} {start}-{end}年")
    # UI 一行显示
    st.markdown("<div style='display:flex; flex-wrap: wrap; gap:10px;'>"
                + "".join(f"<div style='padding:6px 12px; border-radius:6px; background:#e3f2fd; font-weight:600;'>{seg}</div>" for seg in segments)
                + "</div>", unsafe_allow_html=True)

# ------------ 修改按钮事件部分（阳历生日模式内的查询按钮） -----------

if mode == "阳历生日":
    # ...前面代码不变...

    if st.button("查询吉凶"):
        # 根据性别输入（你界面没，需加）
        gender = st.selectbox("性别", ["男", "女"])

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

            # 计算大运起运年龄及顺逆
            birth_date = datetime.date(byear, bmonth, bday)
            # 你这里需要提供节气列表，这里简单用立春节气
            lichun = get_li_chun_datetime(byear).date()
            # 这里只用立春模拟节气列表，理想是提前算出当年所有节气
            solar_terms = [lichun]

            # 起运计算
            forward, start_age, start_months = calc_qiyun_age(birth_date, gender, year_p[0], lichun, solar_terms)

            dayun_list = generate_dayun_list(year_p[0], gender, month_p, forward=forward, steps=8)

            # 计算起运年份（出生年 + 起运岁数）
            # 起运月份换算成岁后附加月份忽略，精确度够用
            start_year_dayun = byear + start_age

            show_jixiong(ji, xiong, byear)
            show_dayun(dayun_list, start_age, byear, ji, xiong, year_p, month_p, day_p, hour_p)

        except Exception as e:
            st.error(f"计算出错：{e}")
