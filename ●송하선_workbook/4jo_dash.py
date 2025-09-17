# pip install streamlit_option_menu 설치 후 실행!

import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import colorsys
import plotly.express as px
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import re

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
    r"C:/Users/user\Desktop/새 폴더/군_분류_군수품_분류_완료.csv",
    encoding="cp949"
) # 자기 경로에 맞는 거로 반드시 수정 !

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
    unsafe_allow_html=True
)

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
        unsafe_allow_html=True
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
    <style>
    /* 사이드바 전체 폭 */
    section[data-testid="stSidebar"] {
        width: 350px !important;   
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    선택 = option_menu(
        "CATEGORY",
        ["메인", "부대별", "연도별", "종 별", "업체별"],
        icons=["house", "building", "calendar", "box", "shop"],
        menu_icon="list",
        default_index=0
    )

st.sidebar.markdown("""
    <hr style="margin-top:50px; margin-bottom:10px">
    <p style="font-size:13px; color:gray; text-align:center;">
    <b>출처:</b> 방위사업청 공개데이터<br>
    <b>제작:</b> <b>BORAM-IV</b><br>
    <b>Version 1.0</b>
    </p>
""", unsafe_allow_html=True)

df["낙찰금액"] = (
    df["낙찰금액"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("원", "", regex=False)
    .str.strip()
    .replace(["None", ""], "0")
)
df["낙찰금액"] = pd.to_numeric(df["낙찰금액"], errors="coerce").fillna(0)

if "낙찰률" in df.columns:
    df["낙찰률"] = (
        df["낙찰률"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace(["None", ""], "0")
    )
    df["낙찰률"] = pd.to_numeric(df["낙찰률"], errors="coerce").fillna(0)
st.title("BORAM-IV : MSA")

if 선택 == "메인":
    st.subheader("🏠 메인")

    검색어 = st.text_input("검색어 (입찰명)")

    if 검색어 and "입찰명" in df.columns:
        filtered_df = filtered_df[filtered_df["입찰명"].str.contains(검색어, na=False)]
    else:
        filtered_df = df.copy()

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

    # 상단 3개 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(widget_box("총 건수", f"{len(df):,}", "📊"), unsafe_allow_html=True)
    with col2:
        total_amount = int(df["낙찰금액"].sum() / 100000000)
        st.markdown(widget_box("총 낙찰금액", f"{total_amount:,} 억원", "💰"), unsafe_allow_html=True)
    with col3:
        avg_rate = df["낙찰률"].mean()
        st.markdown(widget_box("평균 낙찰률", f"{avg_rate:.2f} %", "📈"), unsafe_allow_html=True)

    # 중단 뉴스/날씨
    col4, col5 = st.columns([2,1])

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

        rss_url = "https://news.google.com/rss/search?q=방산"
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


    with col5:
        st.markdown("<div class='widget-box'><div class='widget-title'>🌦️ 오늘의 날씨</div>", unsafe_allow_html=True)
        try:
            weather = requests.get("https://wttr.in/Seoul?format=%C+%t").text

            # 날씨 아이콘 가져오기 (wttr.in의 이모지 대신 fontawesome 아이콘 사용)
            weather_card = f"""
            <div style="display:flex; align-items:center; margin:10px 0; padding:10px; 
                        border-radius:10px; background:white; box-shadow:2px 2px 6px rgba(0,0,0,0.1);">
                <div style="font-size:32px; margin-right:15px;">⛅</div>
                <div>
                    <div style="font-weight:bold; font-size:16px; color:#111;">서울</div>
                    <div style="font-size:14px; color:gray;">{weather}</div>
                </div>
            </div>
            """
            st.markdown(weather_card, unsafe_allow_html=True)

        except:
            st.markdown("날씨 정보를 불러올 수 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 하단 상위 업체 차트
    if "낙찰자(상호)" in df.columns:
        top_vendor = df["낙찰자(상호)"].value_counts().head(5).reset_index()
        top_vendor.columns = ["업체", "건수"]
        fig = px.bar(
            top_vendor,
            x="업체",
            y="건수",
            text="건수",
            color="업체",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition="outside")
        st.markdown("<div style='padding:20px; border-radius:20px; background-color:white; box-shadow:2px 2px 8px rgba(0,0,0,0.15); margin:10px;'><div style='font-size:14px; color:gray;'>🏆 상위 낙찰 업체</div>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    


elif 선택 == "부대별":
    st.subheader("🏢 부대별")

    군목록 = ["육군", "해군", "공군", "해병", "국방부직할", "기타"]

    선택된군 = st.multiselect(
        "군 선택",
        options=군목록,
        default=[]  # 기본 선택 없음
    )

    if 선택된군 and "군 분류" in df.columns:
        filtered_df = filtered_df[filtered_df["군 분류"].isin(선택된군)]

    st.write("### 📊 조회 결과")
    if not filtered_df.empty:
        st.write("### 종별 입찰 수")
        st.bar_chart(filtered_df["군수품분류"].value_counts())
    else:
        st.info("조건에 맞는 데이터가 없습니다.")
    if "군 분류" in filtered_df.columns:
            unit_counts = filtered_df["군 분류"].value_counts().reset_index()
            unit_counts.columns = ["군 분류", "건수"]
            fig2 = px.bar(unit_counts, x="군 분류", y="건수", text="건수",
                          color="군 분류", color_discrete_sequence=px.colors.qualitative.Pastel)
            card_box("군별 입찰 현황", fig2)

elif 선택 == "연도별":
    st.subheader("📅 연도별")
    import datetime

# 개찰일시를 datetime으로 확실히 변환
    df['개찰일시'] = pd.to_datetime(df['개찰일시'], errors='coerce')

    date_range = st.date_input(
        "기간 선택",
        value=[datetime.date(2016, 1, 1), datetime.date(2024, 12, 31)],
        min_value=datetime.date(2016, 1, 1),
        max_value=datetime.date(2025, 12, 31)   # 2025년까지 선택 허용
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[
            (df["개찰일시"].dt.date >= start_date) &
            (df["개찰일시"].dt.date <= end_date)
        ]
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
    .replace("None", "")
    )
    filtered_df['낙찰금액'] = pd.to_numeric(filtered_df['낙찰금액'], errors='coerce')

    col1, empty2, col2, empty3 = st.columns([5, 1, 4, 1])
    with col1:
        if "연도" in filtered_df.columns:
            year_total = filtered_df.groupby("연도")["낙찰금액"].sum().reset_index()
            fig1 = px.line(year_total, x="연도", y="낙찰금액",
                           color_discrete_sequence=px.colors.qualitative.Pastel, markers=True)
            card_box("입찰 추세", fig1)


    with col2:
        st.subheader("연도별 건수")
        if not filtered_df.empty and "연도" in filtered_df.columns:
            year_counts = filtered_df["연도"].value_counts().sort_index()
            st.bar_chart(year_counts, use_container_width=True)

    if not filtered_df.empty and "연도" in filtered_df.columns and "군수품분류" in filtered_df.columns:
        grouped = (
            filtered_df.groupby(['연도', '군수품분류'], as_index=False)['낙찰금액']
            .sum()
        )
        grouped['총낙찰금액'] = grouped.groupby('연도')['낙찰금액'].transform('sum')
        grouped['비율'] = grouped['낙찰금액'] / grouped['총낙찰금액']

        col3, empty5, col4, empty6 = st.columns([5, 1, 4, 1])
        with col3:
            filtered_df['연도'] = filtered_df['개찰일시'].dt.year.astype(str)
            if "연도" in filtered_df.columns:
                year_total = filtered_df.groupby("연도")["낙찰금액"].sum().reset_index()
                fig3 = px.pie(year_total, names="연도", values="낙찰금액", hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
                card_box("연도별 낙찰 총액", fig3)    
        with col4:
            fig = px.bar(
                grouped,
                x='연도',
                y='비율',
                color='군수품분류',
                text=grouped['비율'].apply(lambda x: f"{x:.0%}"),
                title='연도별 낙찰금액 비율',
                labels={'연도': '연도', '비율': '비율'}
            )
            fig.update_layout(barmode='stack', yaxis=dict(tickformat=".0%"))
            st.plotly_chart(fig, use_container_width=True)

        year_total = (
            filtered_df.groupby('연도', as_index=False)['낙찰금액']
            .sum()
            .rename(columns={'낙찰금액': '연도별총낙찰금액'})
        )
        year_total['전체비율'] = year_total['연도별총낙찰금액'] / year_total['연도별총낙찰금액'].sum()

        col5, empty7, col6, empty8 = st.columns([5, 1, 4, 1])
        with col5:
            if "낙찰률" in filtered_df.columns and "연도" in filtered_df.columns:
                year_avg = filtered_df.groupby("연도")["낙찰률"].mean().reset_index()
                year_avg["낙찰률"] = year_avg["낙찰률"] / 100
                fig6 = px.line(year_avg, x="연도", y="낙찰률", markers=True,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
                fig6.update_traces(text=year_avg["낙찰률"].apply(lambda x: f"{x:.2%}"))
                fig6.update_layout(yaxis_tickformat=".0%")
                card_box("연도별 평균 낙찰률", fig6)
        with col6:
            fig2 = px.pie(
                year_total,
                names='연도',
                values='연도별총낙찰금액',
                title='연도별 총 낙찰금액 비율',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_traces(textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)

elif 선택 == "종 별":
    st.subheader("📦 종 별")
    col1, col2 = st.columns(2)
##### 상단 분류


    # 대분류 (종)
    with col1:
        종목록 = ["전체", "1종", "2종", "3종", "4종", 
                "5종", "6종", "7종", "8종", "9종", "10종"]
        선택종 = st.selectbox("종 분류", 종목록)

 # 종 필터
    if 선택종 != "전체" and "군수품분류" in df.columns:
        filtered_df = filtered_df[df["군수품분류"].astype(str).str[:2] == 선택종]

    # # 중분류 (세부항목) 필터
    # if 세부항목 != "전체" and "군수품분류" in df.columns:
    #     filtered_df = filtered_df[
    #         filtered_df["군수품분류"].str.replace(" ", "").str.contains(세부항목.replace(" ", ""), na=False)
    #     ]
    st.write("### 📊 조회 결과")
    st.dataframe(filtered_df, use_container_width=True, height=500)

    # 군수품 분류별 건수 막대그래프
    def lighten_color(hex_color, factor):
            """hex -> 더 밝게"""
            hex_color = hex_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            l = min(1, l + factor) 
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

        # main color
    base_colors = {
            "1종": "#d62728",       
            "2종": "#ff7f0e",
            "3종": "#ffff00",
            "4종": "#bcbd22",       
            "5종": "#00ff00",       
            "6종": "#17becf",       
            "7종": "#1f77b4",       
            "8종": "#e377c2",
            "9종": "#9467bd",
            "10종": "#ff00ff"
        }

    if 선택종 == "전체":
            temp = filtered_df.copy()
            temp["대분류"] = temp["군수품분류"].str.extract(r'(\d+종)')
            temp["중분류"] = temp["군수품분류"]

            summary = temp.groupby(["대분류", "중분류"]).size().reset_index(name="건수")

            color_map = {}
            for 종 in summary["대분류"].unique():
                sub_items = summary[summary["대분류"] == 종]["중분류"].unique()
                n = len(sub_items)
                for i, 항목 in enumerate(sorted(sub_items)):
                    # 위로 갈수록 옅어지도록 factor 계산 (0.0=진함, 0.4=옅음)
                    factor = (i / max(1, n-1)) * 0.4
                    color_map[항목] = lighten_color(base_colors[종], factor)

            chart = (
                alt.Chart(summary)
                .mark_bar()
                .encode(
                    x=alt.X("대분류:N", title="종 분류", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("건수:Q", title="건수"),
                    color=alt.Color("중분류:N",
                                    scale=alt.Scale(domain=list(color_map.keys()),
                                                    range=list(color_map.values())),
                                    legend=alt.Legend(title="세부 항목")),
                    tooltip=["대분류", "중분류", "건수"]
                )
                .properties(width=800, height=500)
            )

            st.altair_chart(chart, use_container_width=True)

    else:

            summary = filtered_df["군수품분류"].value_counts().reset_index()
            summary.columns = ["군수품분류", "건수"]

            chart = (
                alt.Chart(summary)
                .mark_bar()
                .encode(
                    x=alt.X("군수품분류:N", sort="-y", title="세부 항목", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("건수:Q", title="건수"),
                    tooltip=["군수품분류", "건수"]
                )
                .properties(width=600, height=400)
            )

            st.altair_chart(chart, use_container_width=True)

elif 선택 == "업체별":
    st.subheader("🏪 업체별")

    st.markdown("---")
    col1, col2= st.columns(2)
    with col1:
        if "낙찰자(상호)" in filtered_df.columns:
            top_vendor = (
                filtered_df["낙찰자(상호)"]
                .value_counts()
                .head()
                .reset_index()
            )
            top_vendor.columns = ["낙찰자(상호)", "건수"]

            # ✅ 전체 평균 (모든 업체 기준)
            overall_mean = filtered_df["낙찰자(상호)"].value_counts().mean()

            # ✅ 막대 그래프
            fig4 = px.bar(
                top_vendor,
                x="낙찰자(상호)",
                y="건수",
                color="낙찰자(상호)",
                text="건수",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            # ✅ 전체 평균선 추가
            fig4.add_hline(
                y=overall_mean,
                line_dash="solid",
                line_color="red",
                line_width=2,
                annotation_text=f"전체 평균 {overall_mean:.1f}",
                annotation_position="top left"
            )

            # ✅ 그래프 꾸미기
            fig4.update_traces(textposition="outside")
            fig4.update_layout(showlegend=False)

            card_box("상위 낙찰 업체", fig4)

    with col2:
        if "발주기관" in filtered_df.columns:
            top_org = filtered_df["발주기관"].value_counts().head(5).reset_index()
            top_org.columns = ["발주기관", "건수"]
            fig5 = px.pie(top_org, names="발주기관", values="건수", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig5.update_traces(textinfo="percent+label")
            card_box("상위 발주기관", fig5)



#     def parse_address(addr):
#         if pd.isna(addr):
#             return None, None
#         parts = re.split(r"\s+", str(addr))
#         if len(parts) >= 2:
#             return parts[0], parts[1]
#         elif len(parts) == 1:
#             return parts[0], None
#         return None, None
    

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         업체대분류 = st.selectbox(
#         "입찰업체(대분류)",
# ['서울특별시', '부산직할시', '부산광역시' ,'대구광역시' ,'인천광역시'
#  '광주광역시', '대전광역시', '울산광역시' ,'세종특별자치시', '경기도', '강원도' , '충청북도'
#  '충청남도', '전라북도' ,'전라남도', '경상북도', '경상남도' ,'제주특별자치도', '강원특별자치도', '전북특별자치도']
#     )

#     소분류_매핑 = {
#  "강원특별자치도": ["강릉시","동해시","삼척시","속초시","원주시","춘천시","태백시",
#                 "고성군","양구군","양양군","영월군","인제군","정선군","철원군","평창군","홍천군","화천군","횡성군"],

#  "경기도": ["가평군","고양시","과천시","광명시","광주시","구리시","군포시","김포시",
#           "남양주시","동두천시","부천시","성남시","수원시","시흥시","안산시","안성시",
#           "안양시","양주시","양평군","여주시","연천군","오산시","용인시","의왕시",
#           "의정부시","이천시","파주시","평택시","포천시","하남시","화성시"],

#  "경상남도": ["거제시","김해시","밀양시","사천시","양산시","진주시","창원시","통영시",
#            "거창군","고성군","남해군","산청군","의령군","창녕군","하동군","함안군","함양군","합천군"],

#  "경상북도": ["경산시","경주시","구미시","김천시","문경시","상주시","안동시","영주시","영천시",
#            "포항시","고령군","군위군","봉화군","성주군","영덕군","영양군","예천군","울릉군",
#            "울진군","의성군","청도군","청송군","칠곡군"],

#  "광주광역시": ["광산구","남구","동구","북구","서구"],

#  "대구광역시": ["남구","달서구","달성군","동구","북구","서구","수성구","중구"],

#  "대전광역시": ["대덕구","동구","서구","유성구","중구"],

#  "부산광역시": ["강서구","금정구","기장군","남구","동구","동래구","부산진구","북구",
#             "사상구","사하구","서구","수영구","연제구","영도구","중구","해운대구"],

#  "서울특별시": ["강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구",
#             "노원구","도봉구","동대문구","동작구","마포구","서대문구","서초구","성동구",
#             "성북구","송파구","양천구","영등포구","용산구","은평구","종로구","중구","중랑구"],

#  "세종특별자치시": ["세종시"],

#  "울산광역시": ["남구","동구","북구","울주군","중구"],

#  "인천광역시": ["강화군","계양구","남동구","동구","미추홀구","부평구","서구","연수구","옹진군","중구"],

#  "전라남도": ["광양시","나주시","목포시","순천시","여수시","강진군","고흥군","곡성군","구례군",
#            "담양군","무안군","보성군","신안군","영광군","영암군","완도군","장성군","장흥군",
#            "진도군","함평군","해남군","화순군"],

#  "전북특별자치도": ["군산시","김제시","남원시","익산시","전주시","정읍시","고창군","무주군",
#                 "부안군","순창군","완주군","임실군","장수군","진안군"],

#  "제주특별자치도": ["서귀포시","제주시"],

#  "충청남도": ["계룡시","공주시","논산시","보령시","서산시","아산시","천안시","당진시",
#            "금산군","부여군","서천군","예산군","청양군","태안군","홍성군"],

#  "충청북도": ["제천시","청주시","충주시","괴산군","단양군","보은군","영동군","옥천군",
#            "음성군","진천군","증평군"]
# }


#     with col2:
#         가능한소분류 = 소분류_매핑.get(업체대분류, [])
#         업체소분류 = st.selectbox("세부지역(소분류)", 가능한소분류 if 가능한소분류 else ["(소분류 없음)"])

#     with col3:
#         선택부대 = st.selectbox("부대", ["육군", "공군"])

#     df = pd.read_csv("군_분류_군수품_분류_완료.csv", encoding="cp949")
#     df[["시도", "시군구"]] = df["낙찰자(주소)"].apply(lambda x: pd.Series(parse_address(x)))

#     sido_mapping = {
#         "서울": "서울특별시", "서울시": "서울특별시", "용산구": "서울특별시", "강남구": "서울특별시",
#         "전북특별자치도": "전라북도", "전북": "전라북도",
#         "강원특별자치도": "강원도", "강원": "강원도",
#         "충북": "충청북도", "충남": "충청남도",
#         "경북": "경상북도", "경남": "경상남도",
#         "전남": "전라남도",
#         "부산": "부산광역시", "대구": "대구광역시", "광주": "광주광역시",
#         "대전": "대전광역시", "울산": "울산광역시",
#         "세종": "세종특별자치시", "제주": "제주특별자치도"
#     }
#     df["시도"] = df["시도"].replace(sido_mapping)

#     sido_counts = df.groupby("시도").size().reset_index(name="count")
#     sigungu_counts = df.groupby(["시도", "시군구"]).size().reset_index(name="count")

#     coords = {
#         "서울특별시": [37.5665, 126.9780], "경기도": [37.4138, 127.5183],
#         "부산광역시": [35.1796, 129.0756], "대구광역시": [35.8714, 128.6014],
#         "광주광역시": [35.1595, 126.8526], "대전광역시": [36.3504, 127.3845],
#         "울산광역시": [35.5384, 129.3114], "강원도": [37.8228, 128.1555],
#         "충청북도": [36.6357, 127.4914], "충청남도": [36.5184, 126.8],
#         "전라북도": [35.7175, 127.153], "전라남도": [34.8679, 126.991],
#         "경상북도": [36.4919, 128.8889], "경상남도": [35.4606, 128.2132],
#         "제주특별자치도": [33.489, 126.498]
#     }

#     st.title("입찰업체 지도")

#     m = folium.Map(location=[36.5, 127.8], zoom_start=7)

#     for _, row in sido_counts.iterrows():
#         sido, count = row["시도"], row["count"]
#         if sido in coords:
#             lat, lon = coords[sido]

#             radius = np.sqrt(count) * 2  
#             if count < 5000:
#                 color = "#a6cee3"   # 연한 파랑
#             elif count < 15000:
#                 color = "#1f78b4"   # 중간 파랑
#             else:
#                 color = "#08306b"   # 진한 남색
            
#             min_val = sido_counts["count"].min()   # 762
#             max_val = sido_counts["count"].max()   # 20800

#             def scale_radius(count, min_val, max_val, min_r=10, max_r=30):
#                 norm = (count - min_val) / (max_val - min_val)  # 0 ~ 1 사이로 변환
#                 return min_r + norm * (max_r - min_r)

#             folium.CircleMarker(
#                 location=[lat, lon],
#                 radius = scale_radius(count, min_val, max_val),
#                 color="white",       
#                 weight=1,            
#                 fill=True,
#                 fill_color=color,    
#                 fill_opacity=0.6,
#                 popup=f"{sido}: {count}건"
#             ).add_to(m)

#     # 2단계: 특정 시/도 선택 (시군구는 좌표 없으므로 일단 제외하거나 준비되면 추가)
#     selected_sido = st.selectbox("시/도를 선택하세요", sido_counts["시도"].unique())


#     st_folium(m, width=700, height=500)






