
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import math

# -----------------------------------
# 1. 페이지 설정
# -----------------------------------
st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

# -----------------------------------
# 2. 제목
# -----------------------------------
st.title("🏙️ 서울시 연령별 인구 분석")
st.write("행정구역, 성별, 연도를 선택하여 인구 분포를 확인해 보세요!")

st.divider()

# -----------------------------------
# 3. CSV 파일 불러오기
# -----------------------------------
@st.cache_data
def load_data():

    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            data = pd.read_csv(
                "population.csv",
                encoding=encoding,
                thousands=","
            )
            return data

        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 파일의 인코딩을 확인해 주세요.")

try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "population.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 넣어 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# -----------------------------------
# 4. 행정구역 이름 정리
# -----------------------------------
df["행정구역"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)

regions = df["행정구역"].tolist()

# -----------------------------------
# 5. 선택 메뉴
# -----------------------------------
st.subheader("🔍 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_region = st.selectbox(
        "📍 행정구역",
        regions
    )

with col2:
    selected_gender = st.selectbox(
        "👤 성별",
        ["전체", "남성", "여성"]
    )

with col3:
    selected_year = st.selectbox(
        "📅 연도",
        ["2020년", "2021년", "2022년",
         "2023년", "2024년", "2025년"]
    )

st.divider()

# -----------------------------------
# 6. 연령별 데이터 가져오기
# -----------------------------------
gender_code = {
    "전체": "",
    "남성": "남_",
    "여성": "여_"
}

prefix = (
    selected_year
    + "_"
    + gender_code[selected_gender]
    + "거주자_"
)

age_columns = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

column_names = [
    prefix + age for age in age_columns
]

# 데이터에 필요한 컬럼이 있는지 확인
missing_columns = [
    col for col in column_names
    if col not in df.columns
]

if missing_columns:
    st.error(
        "선택한 조건에 해당하는 데이터 컬럼이 없습니다."
    )
    st.stop()

# 선택한 행정구역 데이터 찾기
region_data = df[
    df["행정구역"] == selected_region
]

if region_data.empty:
    st.error("선택한 행정구역 데이터를 찾을 수 없습니다.")
    st.stop()

# 선택한 행의 연령별 인구 데이터 추출
population = region_data.iloc[0][column_names]

population = pd.to_numeric(
    population,
    errors="coerce"
).fillna(0)

# -----------------------------------
# 7. 그래프 데이터 만들기
# -----------------------------------
chart_df = pd.DataFrame({
    "연령대": age_columns,
    "인구수": population.values
})

# 전체 인구 합계
total_population = int(chart_df["인구수"].sum())

# 가장 인구가 많은 연령대
max_age = chart_df.loc[
    chart_df["인구수"].idxmax(),
    "연령대"
]

max_population = int(
    chart_df["인구수"].max()
)

# -----------------------------------
# 8. 주요 정보 표시
# -----------------------------------
st.subheader("📌 인구 분석 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "총 연령별 인구",
        f"{total_population:,}명"
    )

with col2:
    st.metric(
        "인구가 가장 많은 연령대",
        max_age
    )

with col3:
    st.metric(
        "해당 연령대 인구",
        f"{max_population:,}명"
    )

st.divider()

# -----------------------------------
# 9. 파란색 꺾은선 그래프
# -----------------------------------
st.subheader("📈 연령별 인구 꺾은선 그래프")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["연령대"],
        y=chart_df["인구수"],
        mode="lines+markers",
        name="인구수",
        line=dict(
            color="blue",
            width=3
        ),
        marker=dict(
            color="blue",
            size=9
        ),
        hovertemplate=(
            "연령대: %{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

# 그래프 디자인
fig.update_layout(
    title=dict(
        text=(
            f"{selected_region} "
            f"{selected_year} "
            f"{selected_gender} 연령별 인구"
        ),
        x=0.5
    ),

    xaxis=dict(
        title="연령대",
        type="category",
        categoryorder="array",
        categoryarray=age_columns,
        showgrid=True,
        gridcolor="lightgray",
        tickangle=0
    ),

    yaxis=dict(
        title="인구 수 (명)",
        rangemode="tozero",
        showgrid=True,
        gridcolor="lightgray",
        tickmode="linear",
        dtick=100,
        tickformat=",d"
    ),

    font=dict(
        family="Malgun Gothic, AppleGothic, NanumGothic, sans-serif",
        size=13
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",

    hovermode="x unified",

    height=550,

    margin=dict(
        l=70,
        r=30,
        t=80,
        b=80
    )
)

# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------
# 10. 데이터 표 출력
# -----------------------------------
with st.expander("📋 연령별 상세 인구 데이터 보기"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].map(lambda x: f"{int(x):,}명")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------
# 11. 하단 안내
# -----------------------------------
st.divider()

st.caption(
    "📊 서울시 인구 통계 분석 | "
    "데이터 출처: 제공된 population.csv"
)
data = pd.read_csv(
    "population.csv",
    encoding="cp949",
    thousands=","
)
