import pandas as pd
import streamlit as st

# --- 데이터 불러오기 ---
df = pd.read_csv(
    r"C:/theBoram4Jo/새 폴더/Total 물품 낙찰 결과_군_분류_군수품_2종4종분류_추가.csv",
    encoding="cp949"
)

st.set_page_config(page_title="군수품 관리 대시보드", layout="wide")
st.title("군수품 관리 대시보드")

# --- 사이드바 필터 ---
st.sidebar.header("조회 조건")

# 대분류 (종)
종목록 = ["전체", "1종(식량류)", "2종(일반물자류)", "3종(유류)", "4종(건설자재류)", 
         "5종(탄약류)", "6종(복지매장)", "7종(장비류)", "8종(의무)", "9종(수리부속/공구류)", "10종(기타)"]
선택종 = st.sidebar.selectbox("대분류(종)", 종목록)

# 군 구분
군목록 = ["전체", "육군", "해군", "공군", "해병", "국방부직할"]
선택군 = st.sidebar.selectbox("군 구분", 군목록)

# 연도구분
연도 = ["전체", "2016", "2017", "2018", "2019", 
         "2020", "2021", "2022", "2023", "2024", "2025"]
선택연도 = st.sidebar.selectbox("연도", 연도)

# 검색어
검색어 = st.sidebar.text_input("검색어 (입찰명)")

# --- 필터 적용 ---
filtered_df = df.copy()

# 종 필터
if 선택종 != "전체" and "군수품분류" in df.columns:
    filtered_df = filtered_df[filtered_df["군수품분류"] == 선택종]

# 군 구분 필터
if 선택군 != "전체" and "군 분류" in df.columns:
    filtered_df = filtered_df[filtered_df["군 분류"].str.contains(선택군, na=False)]

# 연도 필터
if 선택연도 != "전체" and "개찰일시" in df.columns:
    filtered_df = filtered_df[filtered_df["개찰일시"].astype(str).str[:4] == str(선택연도)]


# 검색어 필터
if 검색어 and "입찰명" in df.columns:
    filtered_df = filtered_df[filtered_df["입찰명"].str.contains(검색어, na=False)]

# --- 메인화면 ---
st.subheader("조회 결과")
st.dataframe(filtered_df, use_container_width=True)

# --- 상세정보 ---
st.subheader("상세 정보")
if not filtered_df.empty:
    선택행 = st.selectbox("확인할 행 선택", filtered_df.index)
    st.json(filtered_df.loc[선택행].to_dict())
else:
    st.info("조건에 맞는 데이터가 없습니다.")

# --- 통계 요약 ---
st.subheader("통계 요약")
if "군수품분류" in filtered_df.columns:
    summary = filtered_df["군수품분류"].value_counts()
    st.bar_chart(summary)
