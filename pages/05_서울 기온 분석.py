temperature-project/
│
├── temperature.csv
│
├── app.py
│
└── pages/
    └── 01_월별_기온분석.py
    
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. Streamlit 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 연도별 최고기온과 최저기온을 비교합니다.")

# --------------------------------------------------
# 2. CSV 파일 읽기
# CSV 파일은 pages 폴더의 상위 폴더에 있음
# --------------------------------------------------
@st.cache_data
def load_data():

    file_path = (
        Path(__file__).resolve().parent.parent
        / "temperature(1).csv"
    )

    if not file_path.exists():
        return None

    try:
        data = pd.read_csv(
            file_path,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        data = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    return data


df = load_data()

if df is None:
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "pages 폴더의 상위 폴더에 CSV 파일을 넣어 주세요."
    )
    st.stop()

# --------------------------------------------------
# 3. 필요한 데이터 열 확인
# --------------------------------------------------
required_columns = [
    "일시",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.stop()

# --------------------------------------------------
# 4. 월 이름과 숫자 연결
# --------------------------------------------------
month_numbers = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

# --------------------------------------------------
# 5. 날짜에서 연도와 월 추출
# --------------------------------------------------
def convert_year_month(
    date_text,
    previous_year=None,
    previous_month=None
):

    try:
        month_text, year_text = str(date_text).strip().split("-")

        month = month_numbers[month_text]
        year_suffix = int(year_text)

        if previous_year is None:
            year = 1900 + year_suffix

        else:
            year = (
                previous_year // 100
            ) * 100 + year_suffix

            if year < previous_year or (
                year == previous_year
                and month <= previous_month
            ):
                year += 100

        return year, month

    except (ValueError, KeyError, AttributeError):
        return None, None


years = []
months = []

previous_year = None
previous_month = None

for date_text in df["일시"]:

    year, month = convert_year_month(
        date_text,
        previous_year,
        previous_month
    )

    years.append(year)
    months.append(month)

    if year is not None:
        previous_year = year
        previous_month = month

df["연도"] = years
df["월"] = months

# --------------------------------------------------
# 6. 기온 데이터 숫자로 변환
# --------------------------------------------------
df["최고기온(℃)"] = pd.to_numeric(
    df["최고기온(℃)"],
    errors="coerce"
)

df["최저기온(℃)"] = pd.to_numeric(
    df["최저기온(℃)"],
    errors="coerce"
)

# 결측치 제거
valid_df = df.dropna(
    subset=[
        "연도",
        "월",
        "최고기온(℃)",
        "최저기온(℃)"
    ]
).copy()

valid_df["연도"] = valid_df["연도"].astype(int)
valid_df["월"] = valid_df["월"].astype(int)

# --------------------------------------------------
# 7. 사용자가 분석할 월 선택
# --------------------------------------------------
selected_month_name = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    list(month_names.values()),
    index=0
)

selected_month = [
    month
    for month, name in month_names.items()
    if name == selected_month_name
][0]

# --------------------------------------------------
# 8. 선택한 월의 데이터 추출
# --------------------------------------------------
chart_df = valid_df[
    valid_df["월"] == selected_month
].sort_values("연도")

# --------------------------------------------------
# 9. 꺾은선 그래프 만들기
# --------------------------------------------------
if chart_df.empty:

    st.warning(
        "선택한 월에 표시할 기온 데이터가 없습니다."
    )

else:

    fig = go.Figure()

    # 최고기온 - 빨간색
    fig.add_trace(
        go.Scatter(
            x=chart_df["연도"],
            y=chart_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="red",
                width=3
            ),
            marker=dict(size=7),
            hovertemplate=(
                "%{x}년<br>"
                "최고기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # 최저기온 - 파란색
    fig.add_trace(
        go.Scatter(
            x=chart_df["연도"],
            y=chart_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="blue",
                width=3
            ),
            marker=dict(size=7),
            hovertemplate=(
                "%{x}년<br>"
                "최저기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # 그래프 제목과 축 설정
    fig.update_layout(

        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },

        xaxis_title="연도",

        yaxis_title="온도 (℃)",

        legend_title="기온 구분",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        hovermode="x unified",

        template="plotly_white",

        font=dict(
            family="Malgun Gothic, AppleGothic, sans-serif"
        ),

        xaxis=dict(
            tickmode="linear",
            dtick=5
        )
    )

    # 그래프 출력
    st.subheader(
        f"📊 {selected_month_name} 연도별 최고·최저기온"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # 10. 데이터 표 출력
    # --------------------------------------------------
    with st.expander("연도별 기온 데이터 보기"):

        display_df = chart_df[
            [
                "연도",
                "최고기온(℃)",
                "최저기온(℃)"
            ]
        ].copy()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

# --------------------------------------------------
# 11. 데이터 안내
# --------------------------------------------------
missing_count = df[
    ["최고기온(℃)", "최저기온(℃)"]
].isna().any(axis=1).sum()

st.caption(
    f"전체 데이터 {len(df):,}개 중 "
    f"기온 데이터가 없는 {missing_count:,}개는 "
    "그래프에서 제외했습니다."
)
