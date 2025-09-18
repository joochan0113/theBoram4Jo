# 실행 전 아래 코드 실행해서 설치!
# pip install pandas streamlit altair numpy folium plotly streamlit-folium

import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import colorsys
import folium
import plotly.express as px
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import re
import time
import base64

#글꼴.. 
with open("C:/theBoram4Jo/●송하선_workbook/MaplestoryFont_TTF/Maplestory Light.ttf", "rb") as f:
    font_data = f.read()
encoded_font = base64.b64encode(font_data).decode()


st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'MapleStoryLight';
        src: url(data:font/ttf;base64,{encoded_font}) format('truetype');
    }}
    html, body, [class*="css"], *  {{
        font-family: 'MapleStoryLight', sans-serif !important;
    }}
    [data-testid="stExpander"] svg {{
        font-family: inherit !important;
    }}


    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>

    div[data-testid="stVerticalBlock"] div:has(> div > .stExpander) {
        min-height: 110px; }
    </style>
""", unsafe_allow_html=True)

def get_news_image(url):
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image:
                return og_image["content"]
        except:
            return None
        return None

df = pd.read_csv(
    r"C:/theBoram4Jo/●송하선_workbook/BID_Address.csv",
    encoding="cp949") 
# 자기 경로에 맞는 거로 반드시 수정 !

from streamlit_option_menu import option_menu

filtered_df = df.copy()

# 대시보드 여백 주려고 수정했음
st.markdown(
    """
    <style>
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True)

# 위젯이 이뻐서 넣었음
def widget_box(title, value, icon=""):
        return f"""
        <div style="
            padding:20px; 
            border-radius:20px; 
            background-color:white; 
            box-shadow:2px 2px 8px rgba(0,0,0,0.15); 
            margin:10px;
        ">
            <div style="font-size:14px; color:gray;">{icon} {title}</div>
            <div style="font-size:24px; font-weight:bold;">{value}</div>
        </div>
        """

# 카드박스 형태로 만들기 위함
def card_box(title, fig):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 10px; 
            padding: 15px; 
            margin: 5px; 
            background-color: white;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        ">
            <h4 style="margin-bottom:15px;">{title}</h4>
        </div>
        """,
        unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

선택 = option_menu(
    None,
    ["메인", "부대별", "연도별", "종 별", "업체별"],
    icons=["house", "building", "calendar", "box", "shop"],
    menu_icon="list",
    default_index=0,
    orientation="horizontal")


df["낙찰금액"] = (
    df["낙찰금액"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("원", "", regex=False)
    .str.strip()
    .replace(["None", ""], "0"))
df["낙찰금액"] = pd.to_numeric(df["낙찰금액"], errors="coerce").fillna(0)

if "낙찰률" in df.columns:
    df["낙찰률"] = (
        df["낙찰률"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace(["None", ""], "0"))
    df["낙찰률"] = pd.to_numeric(df["낙찰률"], errors="coerce").fillna(0)
st.title("BORAM-IV : MSA")

if 선택 == "메인":
    검색어 = st.text_input("검색어 (입찰명)")
    
    if 검색어 and "입찰명" in df.columns:
        filtered_df = filtered_df[filtered_df["입찰명"].str.contains(검색어, na=False)]

        st.markdown(f"{검색어} 관련 최근 입찰 10개")

        if not filtered_df.empty:
            mini_table2 = filtered_df.sort_values(
                by="개찰일시", ascending=False).head(10)[["개찰일시", "입찰명", "낙찰업체상호","발주기관", "낙찰금액"]]

            mini_table2["낙찰금액"] = mini_table2["낙찰금액"].apply(lambda x: f"{int(x):,} 원")

            st.dataframe(mini_table2, use_container_width=True, height=300)
        else:
            st.info("데이터가 없습니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(widget_box("총 건수", f"{len(df):,}", "📊"), unsafe_allow_html=True)
    with col2:
        total_amount = int(df["낙찰금액"].sum() / 100000000)
        st.markdown(widget_box("총 낙찰금액", f"{total_amount:,} 억원", "💰"), unsafe_allow_html=True)
    with col3:
        if "낙찰률" in filtered_df.columns:
            avg_rate = filtered_df["낙찰률"].mean()
            std_rate = filtered_df["낙찰률"].std()
        else:
            avg_rate, std_rate = 0, 0

        st.markdown(
            widget_box(
                "평균 낙찰률",
                f"""{avg_rate:.2f} % <span style="font-size:14px; color:gray;">(±{std_rate:.2f} %)</span>""",
                "📈"),unsafe_allow_html=True)

    col4, col6 = st.columns([1,1])

    with col4:
        st.markdown("<div class='widget-box'><div class='widget-title'>📰 국방/방산 최신 뉴스</div>", unsafe_allow_html=True)

        import feedparser, requests
        from bs4 import BeautifulSoup

        def get_news_image(url):
            try:
                res = requests.get(url, timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")
                og_image = soup.find("meta", property="og:image")
                if og_image:
                    return og_image["content"]
            except:
                return None
            return None

        rss_url = "https://news.google.com/rss/search?q=입찰"
        feed = feedparser.parse(rss_url)

        if feed.entries:
            for e in feed.entries[:3]:
                img_url = get_news_image(e.link)
                if img_url:
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; margin:10px 0; padding:10px; border-radius:10px; background:white; box-shadow:2px 2px 6px rgba(0,0,0,0.1);">
                        <img src="{img_url}" style="width:80px; height:60px; object-fit:cover; margin-right:15px; border-radius:8px;">
                        <div>
                            <a href="{e.link}" target="_blank" style="text-decoration:none; font-weight:bold; color:#111;">{e.title}</a>
                            <div style="font-size:12px; color:gray;">{getattr(e, 'published', '')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"- [{e.title}]({e.link})")
        else:
            st.markdown("뉴스를 불러올 수 없습니다.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <style>
        [data-testid="stExpander"] summary svg {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
        row1 = st.columns(3)
        row2 = st.columns(3)
        row3 = st.columns(3)

        with row1[0]:
            st.markdown("1종 (식량류)")
            st.markdown("주식: 양곡류, 잡곡류\n부식: 수육류, 어패류, 소채류, 두채류 등\n후식: 우유, 주스류, 과일 등\n특수식량: 전투식량, 특전식량 등")

        with row1[1]:
            st.markdown("2종 (일반물자류)")
            st.markdown("피복류: 기본/특수피복류\n병참물자: 부대비품, 기구류, 장구류\n화생방물자: 탐지/보호/치료/연막 등")

        with row1[2]:
            st.markdown("3종 (유류)")
            st.markdown("일반유류: 경유, 휘발유 등\n항공류: 제트유, 항공휘발유\n윤활유: 엔진오일, 기어오일 등")

        with row2[0]:
            st.markdown("4종 (건설자재류)")
            st.markdown("목재, 철재, 시멘트, 장판/벽지, 수도·전기자재 등")

        with row2[1]:
            st.markdown("5종 (탄약류)")
            st.markdown("지상탄약: 소구경탄, 박격포탄, 포병탄 등\n해상탄약: 함포탄, 기뢰, 폭뢰 등\n항공탄약: 유도탄, 폭탄류 등")

        with row2[2]:
            st.markdown("6종 (복지매장 판매품)")
            st.markdown("군 복지매장에서 판매되는 계통 물자")

        with row3[0]:
            st.markdown("7종 (장비류)")
            st.markdown("화력, 특수무기, 기동, 항공, 함정, 통신전자, 일반장비, 정밀측정장비 등")

        with row3[1]:
            st.markdown("8종 (의무 장비/물자류)")
            st.markdown("의무 장비, 의무수리부속, 의무물자, 의약품류")

        with row3[2]:
            st.markdown("9종 (수리부속/공구류) /10종")
            st.markdown("9종: 화력·특수무기·기동·항공·함정·통신전자 장비 수리부속, 정비자재, 유도탄 부속, 공구류\n\n10종: 1~9종에 속하지 않는 물자")

    col5, col6 = st.columns(2)

    unit_summary = df.groupby("발주기관").agg(
        건수=("발주기관", "count"),
        총낙찰금액=("낙찰금액", "sum")
    ).reset_index()

    vendor_summary = df.groupby("낙찰업체상호").agg(
        건수=("낙찰업체상호", "count"),
        총낙찰금액=("낙찰금액", "sum")
    ).reset_index()

    with col5:
        unit_placeholder = st.empty()
    with col6:
        vendor_placeholder = st.empty()

    # col6, 7 갱신!
    i = 0
    while True:
        unit = unit_summary.iloc[i % len(unit_summary)]
        unit_html = f"""
        <div style="padding:20px; border-radius:20px; background-color:white;
                    box-shadow:2px 2px 8px rgba(0,0,0,0.15); margin:10px;">
            <div style="font-size:14px; color:gray;">🏢 발주기관</div>
            <div style="font-size:20px; font-weight:bold;">{unit['발주기관']}</div>
            <div style="font-size:14px;">건수: {unit['건수']:,}</div>
            <div style="font-size:14px;">총 낙찰금액: {int(unit['총낙찰금액']/1e8):,} 억원</div>
        </div>
        """
        unit_placeholder.markdown(unit_html, unsafe_allow_html=True)

        vendor = vendor_summary.iloc[i % len(vendor_summary)]
        vendor_html = f"""
        <div style="padding:20px; border-radius:20px; background-color:white;
                    box-shadow:2px 2px 8px rgba(0,0,0,0.15); margin:10px;">
            <div style="font-size:14px; color:gray;">🏆 낙찰업체</div>
            <div style="font-size:20px; font-weight:bold;">{vendor['낙찰업체상호']}</div>
            <div style="font-size:14px;">건수: {vendor['건수']:,}</div>
            <div style="font-size:14px;">총 낙찰금액: {int(vendor['총낙찰금액']/1e8):,} 억원</div>
        </div>
        """
        vendor_placeholder.markdown(vendor_html, unsafe_allow_html=True)
        i += 1
        time.sleep(3)

elif 선택 == "부대별":
    col_title, col_year, empty1 = st.columns([1.5, 2, 0.2])  
        
    with col_title:
            st.subheader("🏢 부대별")

    with col_year:
        if "개찰일시" in df.columns:
            df["연도"] = df["개찰일시"].astype(str).str[:4]
            연도목록 = sorted(df["연도"].dropna().unique())

            연도목록_num = sorted([int(y) for y in 연도목록 if y.isnumeric()])

            선택연도범위 = st.slider(
                "연도 범위 선택",
                min_value=min(연도목록_num),
                max_value=max(연도목록_num),
                value=(min(연도목록_num), max(연도목록_num)),
                step=1)

    col1, col2 = st.columns(2)
    with col1:
        군목록 = ["육군", "해군", "공군", "해병", "국방부직할", "기타"]
        선택된군 = st.multiselect("군 선택", options=군목록, default=[])


    with col2:
        세부선택군 = []
        if 선택된군:
            세부분류 = df[df["군 분류"].isin(선택된군)]["발주기관"].unique()

            if len(세부분류) > 0:
                options = ["전체"] + list(세부분류)
                세부선택군 = st.multiselect("세부 부대 선택", options=options)

    final_df = df.copy()

    if 선택된군 and "군 분류" in df.columns:
        final_df = final_df[final_df["군 분류"].isin(선택된군)]

    if 세부선택군:
        if "전체" in 세부선택군:
       
            final_df = final_df[final_df["군 분류"].isin(선택된군)]
        else:
            final_df = final_df[final_df["발주기관"].isin(세부선택군)]
    if "개찰일시" in final_df.columns:
        final_df["연도"] = pd.to_datetime(final_df["개찰일시"], errors="coerce").dt.year
        final_df = final_df[
            (final_df["연도"] >= 선택연도범위[0]) &
            (final_df["연도"] <= 선택연도범위[1])
        ]

    if not final_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(widget_box("선택 군 총 건수", f"{len(final_df):,}", "📊"), unsafe_allow_html=True)
        with col2:
            total_amount = int(pd.to_numeric(
                final_df["낙찰금액"].astype(str)
                .str.replace(",", "").str.replace("원", ""),
                errors="coerce"
            ).sum() / 1e8)
            st.markdown(widget_box("선택 군 총 낙찰금액", f"{total_amount:,} 억원", "💰"), unsafe_allow_html=True)
        with col3:
            if "낙찰률" in final_df.columns:
                avg_rate = final_df["낙찰률"].mean()
                std_rate = final_df["낙찰률"].std()
            else:
                avg_rate, std_rate = 0, 0

            st.markdown(
                widget_box(
                    "평균 낙찰률",
                    f"""{avg_rate:.2f} % <span style="font-size:14px; color:gray;">(±{std_rate:.2f} %)</span>""",
                    "📈"
                ),
                unsafe_allow_html=True
            )


        if "카테고리" in final_df.columns:
            counts = final_df["카테고리"].value_counts().reset_index()
            counts.columns = ["카테고리", "건수"]

            order = ["1종", "2종", "3종", "4종", "5종",
                    "6종", "7종", "8종", "9종", "10종", "미분류"]

            counts["카테고리"] = pd.Categorical(counts["카테고리"], categories=order, ordered=True)
            counts = counts.sort_values("카테고리")

            fig1 = px.bar(
                counts,
                x="카테고리",
                y="건수",
                text="건수",
                color="카테고리",
                category_orders={"카테고리": order},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            card_box("군수품 카테고리별 입찰 수", fig1)


        col1, col3, col2 = st.columns(3)
        with col1:
            if "개찰일시" in final_df.columns:
                final_df["연도"] = pd.to_datetime(final_df["개찰일시"], errors="coerce").dt.year
                yearly = final_df.groupby("연도").size().reset_index(name="건수")
                fig2 = px.line(yearly, x="연도", y="건수", markers=True)
                card_box("부대별 연간 입찰건수 추세", fig2)

        with col3:
            if "개찰일시" in final_df.columns and "낙찰금액" in final_df.columns:
                final_df["연도"] = pd.to_datetime(final_df["개찰일시"], errors="coerce").dt.year

                yearly_amount = (
                    final_df.groupby("연도")["낙찰금액"]
                    .sum()
                    .reset_index(name="총낙찰금액"))

                fig_amount = px.line(
                    yearly_amount,
                    x="연도",
                    y="총낙찰금액",
                    markers=True,
                    labels={"총낙찰금액": "총 낙찰금액"})
                fig_amount.update_yaxes(tickformat=",")
                card_box("부대별 연간 낙찰금액 추세", fig_amount)
        with col2:
            if "발주기관" in final_df.columns:
                top_org = final_df["발주기관"].value_counts().head(10).reset_index()
                top_org.columns = ["발주기관", "건수"]
                fig5 = px.pie(top_org, names="발주기관", values="건수", hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
                fig5.update_traces(textinfo="percent+label")
                card_box("선택 부대 중 최다 발주 비율", fig5)
    else:
        st.info("조건에 맞는 데이터가 없습니다.")


elif 선택 == "연도별":
    st.subheader("📅 연도별")
    import datetime

    df['개찰일시'] = pd.to_datetime(df['개찰일시'], errors='coerce')

    df['연도'] = df['개찰일시'].dt.year.astype(int)

    선택연도목록 = st.multiselect(
        "연도 선택",
        options=sorted(df['연도'].dropna().unique()),
        default=sorted(df['연도'].dropna().unique())  )

    if 선택연도목록:
        filtered_df = df[df['연도'].isin(선택연도목록)].copy()
    else:
        filtered_df = df.copy()


    filtered_df.rename(columns=lambda x: x.strip(), inplace=True)
    filtered_df['연도'] = filtered_df['개찰일시'].dt.year.astype(str)
    filtered_df['낙찰금액'] = (
        filtered_df['낙찰금액']
        .astype(str)
        .str.replace(",", "")
        .str.replace("원", "")
        .str.strip()
        .replace("None", ""))
    filtered_df['낙찰금액'] = pd.to_numeric(filtered_df['낙찰금액'], errors='coerce')

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if "연도" in filtered_df.columns:
            year_total = filtered_df.groupby("연도")["낙찰금액"].sum().reset_index()
            fig1 = px.line(year_total, x="연도", y="낙찰금액",
                           color_discrete_sequence=px.colors.qualitative.Pastel, markers=True)
            card_box("연도별 낙찰금액", fig1)

    with col2:
        if not filtered_df.empty and "연도" in filtered_df.columns:
            year_counts = (filtered_df["연도"].value_counts().sort_index().reset_index())
            year_counts.columns = ["연도", "건수"]

            fig2 = px.line(year_counts,x="연도", y="건수",text="건수",markers=True,
                title=None,color_discrete_sequence=px.colors.qualitative.Bold)
            fig2.update_traces(textposition='top center')

            card_box("연도별 낙찰 건수", fig2)

    with col3:
            if "낙찰률" in filtered_df.columns and "연도" in filtered_df.columns:
                year_avg = filtered_df.groupby("연도")["낙찰률"].mean().reset_index()
                year_avg["낙찰률"] = year_avg["낙찰률"] / 100
                fig6 = px.line(year_avg, x="연도", y="낙찰률", markers=True,
                            color_discrete_sequence=px.colors.qualitative.Dark24)
                fig6.update_traces(text=year_avg["낙찰률"].apply(lambda x: f"{x:.2%}"))
                fig6.update_layout(yaxis_tickformat=".0%")
                card_box("연도별 평균 낙찰률", fig6)        

    if not filtered_df.empty and "연도" in filtered_df.columns and "카테고리" in filtered_df.columns:
        grouped = (filtered_df.groupby(['연도', '카테고리'], as_index=False)['낙찰금액']
            .sum())
        grouped['총낙찰금액'] = grouped.groupby('연도')['낙찰금액'].transform('sum')
        grouped['비율'] = grouped['낙찰금액'] / grouped['총낙찰금액']

        col3, empty1, col4,  = st.columns([2, 1, 2])
        with col3:
            fig2 = px.pie(
                year_total,
                names='연도',
                values='낙찰금액', 
                color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_traces(textinfo='percent+label')
            card_box("연도별 낙찰금액 비율", fig2)  

        valid_categories = [f"{i}종" for i in range(1, 11)]

        df_expanded = (filtered_df.assign(카테고리=filtered_df["카테고리"].astype(str).str.split(","))
            .explode("카테고리") )
        df_expanded["카테고리"] = df_expanded["카테고리"].str.strip() 
        df_expanded = df_expanded[df_expanded["카테고리"].isin(valid_categories)].copy()

        df_expanded["카테고리"] = pd.Categorical(
            df_expanded["카테고리"],
            categories=valid_categories,
            ordered=True)
        grouped = (df_expanded.groupby(['연도', '카테고리'], as_index=False)['낙찰금액']
            .sum())
        grouped['총낙찰금액'] = grouped.groupby('연도')['낙찰금액'].transform('sum')
        grouped['비율'] = grouped['낙찰금액'] / grouped['총낙찰금액']

        with col4:
            fig = px.bar(
                grouped,
                x='연도',
                y='비율',
                color='카테고리',
                category_orders={"카테고리": valid_categories}, 
                text=grouped['비율'].apply(lambda x: f"{x:.0%}"),
                title=None,
                labels={'연도': '연도', '비율': '비율'},
                color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                barmode='stack',
                yaxis=dict(tickformat=".0%"),
                legend_title_text="카테고리")

            card_box("연간 종별 낙찰금액 추이", fig)

 
elif 선택 == "종 별":
    st.subheader("📦 종 별")
    col1, = st.columns(1)

    with col1:
        종목록 = ["전체", "1종(식량류)", "2종(일반물자류)", "3종(유류)", "4종(건설자재류)", 
                 "5종(탄약류)", "6종(복지매장 판매품)", "7종(장비류)", "8종(의무 장비/물자류)", "9종(수리부속/공구류)", "10종(기타)"]
        선택종 = st.selectbox("종 분류", 종목록)

    if 선택종 != "전체" and "카테고리" in df.columns:
        selected_category_num = 선택종.split("종")[0]
        filtered_df = filtered_df[filtered_df["카테고리"].astype(str).str.startswith(selected_category_num)]

    filtered_df["낙찰금액"] = (
        filtered_df["낙찰금액"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False)
        .str.strip()
        .replace(["None", ""], "0"))
    filtered_df["낙찰금액"] = pd.to_numeric(filtered_df["낙찰금액"], errors="coerce").fillna(0)

    if "낙찰률" in filtered_df.columns:
        filtered_df["낙찰률"] = (
            filtered_df["낙찰률"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
            .replace(["None", ""], "0"))
        filtered_df["낙찰률"] = pd.to_numeric(filtered_df["낙찰률"], errors="coerce").fillna(0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(widget_box("선택 종 총 건수", f"{len(filtered_df):,}", "📊"), unsafe_allow_html=True)

    with col2:
        total_amount = int(filtered_df["낙찰금액"].sum() / 100000000) 
        st.markdown(widget_box("선택 종 총 낙찰금액", f"{total_amount:,} 억원", "💰"), unsafe_allow_html=True)

    with col3:
        if "낙찰률" in filtered_df.columns:
            avg_rate = filtered_df["낙찰률"].mean()
            std_rate = filtered_df["낙찰률"].std()
        else:
            avg_rate, std_rate = 0, 0

        st.markdown(
            widget_box(
                "평균 낙찰률",
                f"""{avg_rate:.2f} % <span style="font-size:14px; color:gray;">(±{std_rate:.2f} %)</span>""",
                "📈"
            ),
            unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if "발주기관" in filtered_df.columns:
            top_org = (
                filtered_df.groupby("발주기관")
                .size()
                .nlargest(10)
                .reset_index(name="낙찰건수"))

            fig_org = px.bar(
                top_org, x="발주기관", y="낙찰건수", text="낙찰건수",
                title=f"{선택종} 발주기관 Top 10",
                color="발주기관",
                color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_org.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            st.plotly_chart(fig_org, use_container_width=True)

    with col2:
        if "낙찰업체상호" in filtered_df.columns:

            top_vendor = (
                filtered_df.groupby("낙찰업체상호")
                .size()
                .nlargest(10)
                .reset_index(name="낙찰건수"))

            fig_vendor = px.bar(
                top_vendor, x="낙찰업체상호", y="낙찰건수", text="낙찰건수",
                title=f"{선택종} 업체 Top 10",
                color="낙찰업체상호",
                color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_vendor.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            st.plotly_chart(fig_vendor, use_container_width=True)

    st.markdown(f"{선택종} 최근 낙찰 내역")

    if not filtered_df.empty:
        mini_table = filtered_df.sort_values(
            by="개찰일시", ascending=False
        ).head(20)[["개찰일시", "입찰명", "낙찰업체상호", "낙찰금액"]]

        mini_table["낙찰금액"] = mini_table["낙찰금액"].apply(lambda x: f"{int(x):,} 원")

        st.dataframe(mini_table, use_container_width=True, height=300)
    else:
        st.info("데이터가 없습니다.")


#업체별 시작
elif 선택 == "업체별":
    st.subheader("🏪 업체별")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        업체대분류 = st.selectbox(
        "도/광역시/특별시",
        ["전체"] + [
            '서울특별시', '부산광역시', '대구광역시', '인천광역시',
            '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
            '경기도', '강원도', '충청북도', '충청남도',
            '전라북도', '전라남도', '경상북도', '경상남도',
            '제주특별자치도', '강원특별자치도', '전북특별자치도'])

    소분류_매핑 = {
        "강원특별자치도": ["강릉시","동해시","삼척시","속초시","원주시","춘천시","태백시",
                        "고성군","양구군","양양군","영월군","인제군","정선군","철원군","평창군","홍천군","화천군","횡성군"],
        "경기도": ["가평군","고양시","과천시","광명시","광주시","구리시","군포시","김포시",
                "남양주시","동두천시","부천시","성남시","수원시","시흥시","안산시","안성시",
                "안양시","양주시","양평군","여주시","연천군","오산시","용인시","의왕시",
                "의정부시","이천시","파주시","평택시","포천시","하남시","화성시"],
        "경상남도": ["거제시","김해시","밀양시","사천시","양산시","진주시","창원시","통영시",
                "거창군","고성군","남해군","산청군","의령군","창녕군","하동군","함안군","함양군","합천군"],
        "경상북도": ["경산시","경주시","구미시","김천시","문경시","상주시","안동시","영주시","영천시",
                "포항시","고령군","군위군","봉화군","성주군","영덕군","영양군","예천군","울릉군",
                "울진군","의성군","청도군","청송군","칠곡군"],
        "광주광역시": ["광산구","남구","동구","북구","서구"],
        "대구광역시": ["남구","달서구","달성군","동구","북구","서구","수성구","중구"],
        "대전광역시": ["대덕구","동구","서구","유성구","중구"],
        "부산광역시": ["강서구","금정구","기장군","남구","동구","동래구","부산진구","북구",
                    "사상구","사하구","서구","수영구","연제구","영도구","중구","해운대구"],
        "서울특별시": ["강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구",
                    "노원구","도봉구","동대문구","동작구","마포구","서대문구","서초구","성동구",
                    "성북구","송파구","양천구","영등포구","용산구","은평구","종로구","중구","중랑구"],
        "세종특별자치시": ["세종시"],
        "울산광역시": ["남구","동구","북구","울주군","중구"],
        "인천광역시": ["강화군","계양구","남동구","동구","미추홀구","부평구","서구","연수구","옹진군","중구"],
        "전라남도": ["광양시","나주시","목포시","순천시","여수시","강진군","고흥군","곡성군","구례군",
                "담양군","무안군","보성군","신안군","영광군","영암군","완도군","장성군","장흥군",
                "진도군","함평군","해남군","화순군"],
        "전북특별자치도": ["군산시","김제시","남원시","익산시","전주시","정읍시","고창군","무주군",
                        "부안군","순창군","완주군","임실군","장수군","진안군"],
        "제주특별자치도": ["서귀포시","제주시"],
        "충청남도": ["계룡시","공주시","논산시","보령시","서산시","아산시","천안시","당진시",
                "금산군","부여군","서천군","예산군","청양군","태안군","홍성군"],
        "충청북도": ["제천시","청주시","충주시","괴산군","단양군","보은군","영동군","옥천군",
                "음성군","진천군","증평군"]}


    with col2:
        가능한소분류 = 소분류_매핑.get(업체대분류, [])
        업체소분류 = st.selectbox(
            "세부지역(소분류)",
            ["전체"] + 가능한소분류 if 가능한소분류 else ["전체"])

    df_region = filtered_df.copy()

    if 업체대분류 and 업체대분류 != "전체":
        df_region = df_region[df_region["주소_대분류"] == 업체대분류]

    if 업체소분류 and 업체소분류 != "전체":
        df_region = df_region[df_region["주소_소분류"] == 업체소분류]

    if not df_region.empty:
        mini_table2 = (
            df_region.sort_values(by="개찰일시", ascending=False)
            [[ "입찰명", "낙찰업체상호","업체주소", "발주기관", "pick_keywords"]]
            .copy())


        st.dataframe(mini_table2, use_container_width=True, height=300)
    else:
        st.info(f"{업체대분류} {업체소분류} 지역에 해당하는 데이터가 없습니다.")    
        
    col1, col2= st.columns(2)
    with col1:
        if "낙찰업체상호" in filtered_df.columns:
            df_filtered_region = filtered_df.copy()

            if 업체대분류 and 업체대분류 != "전체":
                df_filtered_region = df_filtered_region[df_filtered_region["주소_대분류"] == 업체대분류]

            if 업체소분류 and 업체소분류 != "전체":
                df_filtered_region = df_filtered_region[df_filtered_region["주소_소분류"] == 업체소분류]

            if not df_filtered_region.empty:
                top_vendor = (
                    df_filtered_region["낙찰업체상호"]
                    .value_counts()
                    .head(10)
                    .reset_index())
                top_vendor.columns = ["낙찰업체상호", "건수"]

                overall_mean = df_filtered_region["낙찰업체상호"].value_counts().mean()

                fig4 = px.bar(
                    top_vendor,
                    x="낙찰업체상호",
                    y="건수",
                    color="낙찰업체상호",
                    text="건수",
                    color_discrete_sequence=px.colors.qualitative.Pastel)

                fig4.add_hline(
                    y=overall_mean,
                    line_dash="solid",
                    line_color="red",
                    line_width=2,
                    annotation_text=f"전체 평균 {overall_mean:.1f}",
                    annotation_position="top left")
                fig4.update_traces(textposition="outside")
                fig4.update_layout(showlegend=False)
                card_box(f"{업체대분류} | {업체소분류} 최다 낙찰 업체", fig4)
            else:
                st.info(f"{업체대분류} {업체소분류} 지역에는 데이터가 없습니다.")
            
    with col2:
        def parse_address(addr):
            if pd.isna(addr):
                return None, None
            parts = re.split(r"\s+", str(addr))
            if len(parts) >= 2:
                return parts[0], parts[1]
            elif len(parts) == 1:
                return parts[0], None
            return None, None

        df[["시도", "시군구"]] = df["업체주소"].apply(lambda x: pd.Series(parse_address(x)))

        sido_mapping = {
            "서울": "서울특별시", "서울시": "서울특별시", "용산구": "서울특별시", "강남구": "서울특별시",
            "전북특별자치도": "전라북도", "전북": "전라북도",
            "강원특별자치도": "강원도", "강원": "강원도",
            "충북": "충청북도", "충남": "충청남도",
            "경북": "경상북도", "경남": "경상남도",
            "전남": "전라남도",
            "부산": "부산광역시", "대구": "대구광역시", "광주": "광주광역시",
            "대전": "대전광역시", "울산": "울산광역시",
            "세종": "세종특별자치시", "제주": "제주특별자치도"}
        df["시도"] = df["시도"].replace(sido_mapping)

        sido_counts = df.groupby("시도").size().reset_index(name="count")


        coords = {
            "서울특별시": [37.5665, 126.9780], "경기도": [37.4138, 127.5183],
            "부산광역시": [35.1796, 129.0756], "대구광역시": [35.8714, 128.6014],
            "광주광역시": [35.1595, 126.8526], "대전광역시": [36.3504, 127.3845],
            "울산광역시": [35.5384, 129.3114], "강원도": [37.8228, 128.1555],
            "충청북도": [36.6357, 127.4914], "충청남도": [36.5184, 126.8],
            "전라북도": [35.7175, 127.153], "전라남도": [34.8679, 126.991],
            "경상북도": [36.4919, 128.8889], "경상남도": [35.4606, 128.2132],
            "제주특별자치도": [33.489, 126.498]}

        sido_counts["lat"] = sido_counts["시도"].map(lambda x: coords.get(x, [None, None])[0])
        sido_counts["lon"] = sido_counts["시도"].map(lambda x: coords.get(x, [None, None])[1])


        sido_counts = sido_counts.dropna(subset=["lat", "lon"])

        fig = px.scatter_mapbox(
        sido_counts,

        lat="lat",
        lon="lon",
        size="count",
        hover_name="시도",
        size_max=50,
        zoom=6,
        color="count",
        color_continuous_scale="reds",
        mapbox_style="carto-positron")

        fig.update_layout(
            mapbox=dict(
                center={"lat": 36.5, "lon": 127.8},
                zoom=5.7                        
            ),
            margin={"r":0,"t":0,"l":0,"b":0}       )
        card_box("전국 입찰업체 분포 현황", fig)




 

#여기부터 하단 메뉴
img_path = r"C:/theBoram4Jo/●송하선_workbook/보람4조.png"

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

base64_str = get_base64_image(img_path)

st.markdown("---")  

col1, col2 = st.columns([1.5,4])

with col1:
    st.markdown(
        f"""
        <img src="data:image/png;base64,{base64_str}" style="width:1000px;" />
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="font-size:18px; color:gray; text-align:left;">
        <b>출처:</b> 방위사업청 공개데이터 | 
        <b>제작:</b> BORAM-IV | 
        <b>Version 1.0</b><br>
        주소 : 없음  <br>
        대표전화 : 없음 <br> 팩스 : 없음
        </div>
        """,
        unsafe_allow_html=True
    )



