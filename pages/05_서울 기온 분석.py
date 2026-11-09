
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================
st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 분석 대시보드")
st.write("서울의 기온 변화를 다양한 그래프로 분석해 보세요!")

# ==========================================
# 2. CSV 파일 찾기
# ==========================================
def find_csv_file():
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent

    possible_paths = [
        project_root / "temperature(1).csv",
        project_root / "temperature.csv",
        Path.cwd() / "temperature(1).csv",
        Path.cwd() / "temperature.csv"
    ]

    for path in possible_paths:
        if path.is_file():
            return path

    return None


# ==========================================
# 3. CSV 파일 읽기
# ==========================================
@st.cache_data
def load_data(csv_path):
    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                csv_path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")


csv_file = find_csv_file()

if csv_file is None:
    st.error("temperature(1).csv 파일을 찾을 수 없습니다.")
    st.write("현재 파이썬 파일 위치:")
    st.code(str(Path(__file__).resolve()))
    st.write("CSV 파일이 있어야 하는 위치:")
    st.code(str(Path(__file__).resolve().parent.parent))
    st.stop()

try:
    df = load_data(str(csv_file))

except Exception as error:
    st.error(f"CSV 파일 읽기 오류: {error}")
    st.stop()


# ==========================================
# 4. 필요한 열 확인
# ==========================================
required_columns = [
    "일시",
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "CSV 파일에 필요한 열이 없습니다: "
        + ", ".join(missing_columns)
    )
    st.write(list(df.columns))
    st.stop()


# ==========================================
# 5. 날짜에서 연도와 월 추출
# ==========================================
month_numbers = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}


def parse_year_month(
    date_value,
    previous_year=None,
    previous_month=None
):
    try:
        month_text, year_text = str(date_value).strip().split("-")

        month = month_numbers[month_text.title()]
        year_suffix = int(year_text)

        if previous_year is None:
            year = 1900 + year_suffix

        else:
            year = (
                previous_year // 100
            ) * 100 + year_suffix

            if year < previous_year:
                year += 100

            elif (
                year == previous_year
                and previous_month is not None
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

for date_value in df["일시"]:

    year, month = parse_year_month(
        date_value,
        previous_year,
        previous_month
    )

    years.append(year)
    months.append(month)

    if year is not None and month is not None:
        previous_year = year
        previous_month = month

df["연도"] = years
df["월"] = months


# ==========================================
# 6. 기온 데이터 숫자로 변환
# ==========================================
temperature_columns = [
    "평균기온(℃)",
    "최고기온(℃)",
    "최저기온(℃)"
]

for column in temperature_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

valid_df = df.dropna(
    subset=["연도", "월"]
).copy()

valid_df["연도"] = valid_df["연도"].astype(int)
valid_df["월"] = valid_df["월"].astype(int)

available_years = sorted(
    valid_df["연도"].unique().tolist()
)

if not available_years:
    st.error("분석할 날짜 데이터가 없습니다.")
    st.stop()


# ==========================================
# 기능 1. 월별 평균기온 그래프
# ==========================================
st.header("1. 서울의 월별 평균기온")

selected_year = st.selectbox(
    "📅 평균기온을 확인할 연도를 선택하세요.",
    available_years,
    index=len(available_years) - 1,
    key="monthly_average_year"
)

monthly_avg_df = valid_df[
    (valid_df["연도"] == selected_year)
    & (valid_df["평균기온(℃)"].notna())
].sort_values("월")

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=monthly_avg_df["월"],
        y=monthly_avg_df["평균기온(℃)"],
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#16A085",
            width=3
        ),
        marker=dict(size=8),
        connectgaps=False,
        hovertemplate=(
            "%{x}월<br>"
            "평균기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

fig1.update_layout(
    title=f"{selected_year}년 서울의 월별 평균기온",
    xaxis_title="월",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified",
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=[
            f"{month}월"
            for month in range(1, 13)
        ]
    ),
    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif"
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

if monthly_avg_df.empty:
    st.info("선택한 연도의 평균기온 데이터가 없습니다.")


# ==========================================
# 기능 2. 연도별 최고기온과 최저기온
# ==========================================
st.divider()

st.header("2. 연도별 최고기온과 최저기온")

selected_month_name = st.selectbox(
    "📅 비교할 월을 선택하세요.",
    list(month_names.values()),
    index=0,
    key="annual_extreme_month"
)

selected_month = next(
    number
    for number, name in month_names.items()
    if name == selected_month_name
)

month_df = valid_df[
    valid_df["월"] == selected_month
].sort_values("연도")

high_df = month_df.dropna(
    subset=["최고기온(℃)"]
)

low_df = month_df.dropna(
    subset=["최저기온(℃)"]
)

fig2 = go.Figure()

# 최고기온 - 빨간색
fig2.add_trace(
    go.Scatter(
        x=high_df["연도"],
        y=high_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="red",
            width=3
        ),
        marker=dict(size=6),
        hovertemplate=(
            "%{x}년<br>"
            "최고기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

# 최저기온 - 파란색
fig2.add_trace(
    go.Scatter(
        x=low_df["연도"],
        y=low_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="blue",
            width=3
        ),
        marker=dict(size=6),
        hovertemplate=(
            "%{x}년<br>"
            "최저기온: %{y:.1f}℃"
            "<extra></extra>"
        )
    )
)

fig2.update_layout(
    title=f"{selected_month_name} 연도별 최고기온과 최저기온",
    xaxis_title="연도",
    yaxis_title="온도 (℃)",
    legend_title="기온 구분",
    template="plotly_white",
    hovermode="x unified",
    font=dict(
        family="Malgun Gothic, AppleGothic, sans-serif"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

if month_df.empty:
    st.info("선택한 월의 기온 데이터가 없습니다.")


# ==========================================
# 기능 3. 두 연도의 월별 평균기온 비교
# ==========================================
st.divider()

st.header("3. 두 연도의 월별 평균기온 비교")

if len(available_years) >= 2:

    col1, col2 = st.columns(2)

    with col1:
        year1 = st.selectbox(
            "첫 번째 연도",
            available_years,
            index=len(available_years) - 2,
            key="compare_year_1"
        )

    second_year_options = [
        year for year in available_years
        if year != year1
    ]

    default_second_index = 0

    if available_years[-1] in second_year_options:
        default_second_index = second_year_options.index(
            available_years[-1]
        )

    with col2:
        year2 = st.selectbox(
            "두 번째 연도",
            second_year_options,
            index=default_second_index,
            key="compare_year_2"
        )

    compare_df = valid_df[
        (valid_df["연도"].isin([year1, year2]))
        & (valid_df["평균기온(℃)"].notna())
    ].copy()

    fig3 = go.Figure()

    for year, color in [
        (year1, "red"),
        (year2, "blue")
    ]:

        one_year_df = compare_df[
            compare_df["연도"] == year
        ].sort_values("월")

        fig3.add_trace(
            go.Scatter(
                x=one_year_df["월"],
                y=one_year_df["평균기온(℃)"],
                mode="lines+markers",
                name=f"{year}년",
                line=dict(
                    color=color,
                    width=3
                ),
                marker=dict(size=8),
                connectgaps=False,
                hovertemplate=(
                    f"{year}년<br>"
                    "%{x}월<br>"
                    "평균기온: %{y:.1f}℃"
                    "<extra></extra>"
                )
            )
        )

    fig3.update_layout(
        title=f"{year1}년과 {year2}년 서울 월별 평균기온 비교",
        xaxis_title="월",
        yaxis_title="평균기온 (℃)",
        legend_title="비교 연도",
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=[
                f"{month}월"
                for month in range(1, 13)
            ]
        ),
        font=dict(
            family="Malgun Gothic, AppleGothic, sans-serif"
        )
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

else:
    st.info("두 연도를 비교하려면 최소 2개 연도가 필요합니다.")


# ==========================================
# 7. 데이터 안내
# ==========================================
st.divider()

missing_average = int(
    df["평균기온(℃)"].isna().sum()
)

missing_high = int(
    df["최고기온(℃)"].isna().sum()
)

missing_low = int(
    df["최저기온(℃)"].isna().sum()
)

st.caption(
    f"데이터 파일: {csv_file.name} | "
    f"전체 행: {len(df):,}개 | "
    f"평균기온 결측: {missing_average:,}개 | "
    f"최고기온 결측: {missing_high:,}개 | "
    f"최저기온 결측: {missing_low:,}개"
)
