
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# -----------------------------------
# 1. 페이지 설정
# -----------------------------------
st.set_page_config(
    page_title="서울시 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("🏙️ 서울시 연령별 인구 분석")
st.write("서울시의 연령별 인구와 자치구별 인구 순위를 분석해 보세요!")

st.divider()

# -----------------------------------
# 2. CSV 파일 불러오기
# -----------------------------------
@st.cache_data
def load_data():

    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    for encoding in encodings:
        try:
            return pd.read_csv(
                "population.csv",
                encoding=encoding,
                thousands=","
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")

try:
    df = load_data()

except FileNotFoundError:
    st.error("population.csv 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()

# -----------------------------------
# 3. 행정구역 이름 정리
# -----------------------------------
df["행정구역"] = (
    df["행정구역"]
    .astype(str)
    .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
    .str.strip()
)

regions = df["행정구역"].tolist()

# -----------------------------------
# 4. 분석 조건 선택
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
         "2023년", "2024년", "2025년"],
        index=5
    )

# -----------------------------------
# 5. 연령대 목록
# -----------------------------------
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

# -----------------------------------
# 6. 기존 기능: 연령별 인구 분석
# -----------------------------------
st.divider()
st.header("📈 1. 행정구역별 연령 인구 분석")

st.caption(
    "선택한 행정구역의 연령대별 인구를 꺾은선 그래프로 보여줍니다."
)

column_names = [
    prefix + age for age in age_columns
]

missing_columns = [
    col for col in column_names
    if col not in df.columns
]

if missing_columns:
    st.error("선택한 조건의 데이터 컬럼이 없습니다.")
    st.stop()

region_data = df[
    df["행정구역"] == selected_region
]

if region_data.empty:
    st.error("행정구역 데이터를 찾을 수 없습니다.")
    st.stop()

population = pd.to_numeric(
    region_data.iloc[0][column_names],
    errors="coerce"
).fillna(0)

chart_df = pd.DataFrame({
    "연령대": age_columns,
    "인구수": population.values
})

total_population = int(chart_df["인구수"].sum())

max_age = chart_df.loc[
    chart_df["인구수"].idxmax(),
    "연령대"
]

max_population = int(chart_df["인구수"].max())

# 주요 정보
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "연령별 인구 합계",
        f"{total_population:,}명"
    )

with col2:
    st.metric(
        "인구가 가장 많은 연령",
        max_age
    )

with col3:
    st.metric(
        "해당 연령 인구",
        f"{max_population:,}명"
    )

# 꺾은선 그래프
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
        gridcolor="lightgray"
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
    height=550
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------------
# 7. 새로운 기능: 연령대별 자치구 순위
# -----------------------------------
st.divider()

st.header("🏆 2. 연령대별 인구가 가장 많은 자치구")

st.write(
    "원하는 연령대를 선택하면 서울시 25개 자치구의 "
    "인구를 비교하여 순위별로 보여줍니다."
)

# 연령대 선택
selected_age = st.selectbox(
    "🎂 분석할 연령대 선택",
    age_columns,
    index=2
)

# 선택한 연령대의 컬럼명
target_column = prefix + selected_age

if target_column not in df.columns:
    st.error("선택한 연령대의 데이터가 없습니다.")
    st.stop()

# 서울특별시 전체 행 제외
district_df = df[
    df["행정구역"] != "서울특별시"
].copy()

# 자치구별 인구 추출
district_df["인구수"] = pd.to_numeric(
    district_df[target_column],
    errors="coerce"
).fillna(0)

# 인구가 많은 순서대로 정렬
district_df = district_df.sort_values(
    by="인구수",
    ascending=False
).reset_index(drop=True)

# 순위 만들기
district_df["순위"] = range(
    1,
    len(district_df) + 1
)

# -----------------------------------
# 8. 1위 자치구 정보 표시
# -----------------------------------
if len(district_df) > 0:

    first_district = district_df.iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🥇 인구 1위 자치구",
            first_district["행정구역"]
        )

    with col2:
        st.metric(
            "해당 연령대 인구",
            f"{int(first_district['인구수']):,}명"
        )

    with col3:
        st.metric(
            "비교 자치구 수",
            f"{len(district_df)}개"
        )

# -----------------------------------
# 9. 자치구별 가로 막대그래프
# -----------------------------------
bar_fig = go.Figure()

bar_fig.add_trace(
    go.Bar(
        x=district_df["인구수"],
        y=district_df["행정구역"],
        orientation="h",
        marker=dict(
            color="blue"
        ),
        text=district_df["인구수"].apply(
            lambda x: f"{int(x):,}명"
        ),
        textposition="outside",
        hovertemplate=(
            "자치구: %{y}<br>"
            "인구수: %{x:,.0f}명"
            "<extra></extra>"
        )
    )
)

bar_fig.update_layout(
    title=dict(
        text=(
            f"{selected_year} "
            f"{selected_gender} "
            f"{selected_age} 자치구별 인구 순위"
        ),
        x=0.5
    ),

    xaxis=dict(
        title="인구 수 (명)",
        showgrid=True,
        gridcolor="lightgray",
        tickformat=",d"
    ),

    yaxis=dict(
        title="행정구역",
        autorange="reversed"
    ),

    font=dict(
        family="Malgun Gothic, AppleGothic, NanumGothic, sans-serif",
        size=12
    ),

    plot_bgcolor="white",
    paper_bgcolor="white",
    height=750,
    margin=dict(
        l=100,
        r=80,
        t=80,
        b=60
    )
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)

# -----------------------------------
# 10. 자치구별 순위 표
# -----------------------------------
with st.expander("📋 자치구별 인구 순위 상세 보기"):

    ranking_df = district_df[
        ["순위", "행정구역", "인구수"]
    ].copy()

    ranking_df["인구수"] = ranking_df[
        "인구수"
    ].map(lambda x: f"{int(x):,}명")

    st.dataframe(
        ranking_df,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------
# 11. 기존 연령별 데이터 표
# -----------------------------------
with st.expander("📊 선택한 행정구역의 연령별 상세 데이터"):

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
# 12. 하단 안내
# -----------------------------------
st.divider()

st.caption(
    "📊 서울시 인구 통계 분석 | "
    "데이터 출처: population.csv"
)
