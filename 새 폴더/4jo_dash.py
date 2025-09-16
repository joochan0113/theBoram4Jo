import pandas as pd
import streamlit as st
import altair as alt
import colorsys
import plotly.express as px
def style_dataframe(df: pd.DataFrame):
    return df.style.set_table_styles(
        [
            {"selector": "thead th",
             "props": [("background-color", "#2E86C1"), ("color", "white"), ("font-weight", "bold")]},
            {"selector": "tbody tr:nth-child(even)",
             "props": [("background-color", "#F2F4F4")]},
            {"selector": "tbody tr:hover",
             "props": [("background-color", "#D6EAF8")]}
        ]
    )



# --- 데이터 불러오기 ---
df = pd.read_csv(
    r"C:/theBoram4Jo/새 폴더/군_분류_군수품_분류_완료.csv",
    encoding="cp949"
)

from streamlit_option_menu import option_menu

# --- 필터 적용 ---
filtered_df = df.copy()





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
        ["메인", "부대별", "연도별", "종 별", "지역별"],
        icons=["house", "building", "calendar", "box", "map"],
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

st.title("BORAM-IV : MSA")

if 선택 == "메인":
    st.subheader("🏠 메인")

    # 검색어 입력 (1개 컬럼)
    col1 = st.columns(1)[0]
    with col1:
        검색어 = st.text_input("검색어 (입찰명)")

    # 검색어 필터
    if 검색어 and "입찰명" in df.columns:
        filtered_df = filtered_df[filtered_df["입찰명"].str.contains(검색어, na=False)]

    #####  메인화면 
    st.subheader("Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 건수", len(filtered_df))
    with col2:
        if "낙찰금액" in filtered_df.columns:
            st.metric("총 낙찰금액", f"{filtered_df['낙찰금액'].sum():} 원")
    with col3:
        if "낙찰률" in filtered_df.columns:
            st.metric("평균 낙찰률", f"{filtered_df['낙찰률'].mean():.2f} %")

    if "개찰일시" in filtered_df.columns and "낙찰금액" in filtered_df.columns:
        temp = filtered_df.copy()
        temp["연도"] = temp["개찰일시"].astype(str).str[:4]
        year_summary = temp.groupby("연도")["낙찰금액"].sum()
        st.subheader("연도별 낙찰금액 추이")
        st.line_chart(year_summary)


    with st.expander("상세 데이터 보기"):
        st.dataframe(filtered_df, use_container_width=True)


    st.subheader("상세 정보")
    if not filtered_df.empty:
        선택행 = st.selectbox("확인할 행 선택", filtered_df.index)
        st.json(filtered_df.loc[선택행].to_dict())
    else:
        st.info("조건에 맞는 데이터가 없습니다.")

elif 선택 == "부대별":
    st.subheader("🏢 부대별")
    col1, col2, col3, col4, col5, col6= st.columns([1, 1, 1, 1, 1, 1])
    군목록 = ["육군", "해군", "공군", "해병", "국방부직할", "기타"]
    cols = st.columns(len(군목록))
    
    선택군 = {}

    for i, 군 in enumerate(군목록):
        with cols[i]:
            선택군[군] = st.toggle(군, value=False, key=f"toggle_{군}")

    # 선택된 군만 필터링 (True인 것만 추출)
    선택된군 = [군 for 군, 상태 in 선택군.items() if 상태]
    if 선택된군 and "군 분류" in df.columns:
        filtered_df = filtered_df[filtered_df["군 분류"].isin(선택된군)]

    st.write("### 📊 조회 결과")
    st.dataframe(filtered_df, use_container_width=True, height=500)
    if not filtered_df.empty:
        st.bar_chart(filtered_df["군수품분류"].value_counts())
    else:
        st.info("조건에 맞는 데이터가 없습니다.")

elif 선택 == "연도별":
    st.subheader("📅 연도별")

    연도목록 = ["2016", "2017", "2018", "2019", 
                "2020", "2021", "2022", "2023", "2024", "2025"]
    선택연도 = {}

    cols1 = st.columns(5)
    for i, 연도 in enumerate(연도목록[:5]):
        with cols1[i]:
            선택연도[연도] = st.toggle(연도, value=False, key=f"toggle_{연도}")

    cols2 = st.columns(5)
    for i, 연도 in enumerate(연도목록[5:]):
        with cols2[i]:
            선택연도[연도] = st.toggle(연도, value=False, key=f"toggle_{연도}")

    선택된연도 = [연도 for 연도, 상태 in 선택연도.items() if 상태]

    if 선택된연도 and "개찰일시" in df.columns:
        filtered_df = filtered_df[filtered_df["개찰일시"].astype(str).str[:4].isin(선택된연도)]

    filtered_df.rename(columns=lambda x: x.strip(), inplace=True)
    filtered_df['연도'] = filtered_df['개찰일시'].astype(str).str[:4]
    filtered_df['낙찰금액'] = pd.to_numeric(filtered_df['낙찰금액'], errors='coerce')

    col1, empty2, col2, empty3 = st.columns([5, 1,4, 1])
    with col1:
        st.subheader("조회 결과")
        st.dataframe(filtered_df, use_container_width=True)
    with col2:
        st.subheader("연도별 건수")
        if "연도" in filtered_df.columns:
            year_counts = filtered_df["연도"].value_counts().sort_index()
            st.bar_chart(year_counts, use_container_width=True)

    if not filtered_df.empty and "연도" in filtered_df.columns and "군수품분류" in filtered_df.columns:
        grouped = (
            filtered_df.groupby(['연도', '군수품분류'], as_index=False)['낙찰금액']
            .sum()
        )
        grouped['총낙찰금액'] = grouped.groupby('연도')['낙찰금액'].transform('sum')
        grouped['비율'] = grouped['낙찰금액'] / grouped['총낙찰금액']

        col3, empty5, col4, empty6 = st.columns([5, 1,4, 1])
        with col3:
            st.subheader("Debug: Grouped Data")
            st.dataframe(grouped, use_container_width=True)
        with col4:
            if not grouped.empty:
                fig = px.bar(
                    grouped,
                    x='연도',
                    y='비율',
                    color='군수품분류',
                    text=grouped['비율'].apply(lambda x: f"{x:.0%}"),
                    title='연도별 군수품분류 낙찰금액 비율',
                    labels={'연도': '연도', '비율': '비율'}
                )
                fig.update_layout(barmode='stack', yaxis=dict(tickformat=".0%"))
                st.plotly_chart(fig, use_container_width=True)


elif 선택 == "종 별":
    st.subheader("📦 종 별")
    col1, col2 = st.columns(2)
##### 상단 분류


    # 대분류 (종)
    with col1:
        종목록 = ["전체", "1종", "2종", "3종", "4종", 
                "5종", "6종", "7종", "8종", "9종", "10종"]
        선택종 = st.selectbox("종 분류", 종목록)

    # --- 중분류 (세부항목) ---
    # with col2:
    #     if 선택종 == "1종":
    #         중분류 = ["전체", "주식", "부식", "후식","증식/특식","특수식량"]

    #     elif 선택종 == "2종":
    #         중분류 = ["전체", "피복류", "병참물자", "화생방 물자", "통신 물자", "공병 물자", "기타 물자류"]

    #     elif 선택종 == "3종":
    #         중분류 = ["전체", "일반유류", "항공류", "윤활유", "화공약품류", "고체연료", "가스류", "유류포장재료"]

    #     elif 선택종 == "4종":
    #         중분류 = ["전체", "건축자재", "축성자재"]

    #     elif 선택종 == "5종":
    #         중분류 = ["전체", "지상탄약", "해상탄약", "항공탄약", "탄피/원자재류"]

    #     elif 선택종 == "6종":
    #         중분류 = ["전체", "복지매장 판매품"]

    #     elif 선택종 == "7종":
    #         중분류 = ["전체", "화력", "특수무기", "기동", "항공", "함정", "통신전자", "일반장비", "정밀측정"]

    #     elif 선택종 == "8종":
    #         중분류 = ["전체", "의무장비", "의무수리부속", "의무물자", "의약품류"]

    #     elif 선택종 == "9종":
    #         중분류 = ["전체", "화력", "특수무기", "기동", "항공", "함정", "통신전자", "일반장비", "정밀측정", "정비자재", "유도탄", "공구류"]

    #     elif 선택종 == "10종":
    #         중분류 = ["전체", "기타 물자류"]

    #     else: 중분류 = ["전체"]

    #     세부항목 = st.selectbox("세부항목", 중분류)

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

elif 선택 == "지역별":
    st.subheader("🗺️ 지역별")
    col1, col2 = st.columns(2)

    with col1:
        선택업체 = st.selectbox("입찰업체", ["경기도", "서울특별시", "충청도"])

    with col2:
        선택부대 = st.selectbox("부대", ["육군", "공군"])






