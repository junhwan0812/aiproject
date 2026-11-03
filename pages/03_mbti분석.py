
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="세계 MBTI 탐험",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 세계 MBTI 탐험")
st.markdown(
    "국가를 선택하고 해당 국가의 **16가지 MBTI 유형 비율**을 알아보세요!"
)

st.divider()


# ==========================================
# 2. CSV 파일 위치 찾기
# ==========================================

FILE_NAME = "countriesMBTI_16types.csv"

possible_paths = [
    Path(__file__).parent / FILE_NAME,
    Path.cwd() / FILE_NAME,
    Path.cwd() / "data" / FILE_NAME
]

DATA_FILE = None

for path in possible_paths:
    if path.exists():
        DATA_FILE = path
        break


# ==========================================
# 3. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):

    try:
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            file_path,
            encoding="cp949"
        )

    # 열 이름 정리
    df.columns = df.columns.str.strip()

    # Country 열 확인
    if "Country" not in df.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    # 국가 이름 정리
    df["Country"] = df["Country"].astype(str).str.strip()

    df = df[
        (df["Country"] != "") &
        (df["Country"].str.lower() != "nan")
    ]

    # MBTI 열 확인
    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 열이 16개가 아닙니다. 현재 {len(mbti_columns)}개입니다."
        )

    # 숫자 데이터로 변환
    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    if df[mbti_columns].isna().any().any():
        raise ValueError(
            "MBTI 데이터에 비어 있거나 잘못된 값이 있습니다."
        )

    return df, mbti_columns


# ==========================================
# 4. 데이터 오류 확인
# ==========================================

if DATA_FILE is None:

    st.error(
        "❌ CSV 파일을 찾을 수 없습니다."
    )

    st.info(
        "app.py와 countriesMBTI_16types.csv를 "
        "같은 폴더에 넣어 주세요."
    )

    st.code(
        """
my_project/
│
├── app.py
├── requirements.txt
└── countriesMBTI_16types.csv
        """
    )

    st.stop()


try:

    df, mbti_columns = load_data(str(DATA_FILE))

except Exception as error:

    st.error(f"데이터 오류: {error}")
    st.stop()


# ==========================================
# 5. 데이터 기본 정보
# ==========================================

st.subheader("📌 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌍 전체 국가",
        f"{df['Country'].nunique()}개"
    )

with col2:
    st.metric(
        "🧠 MBTI 유형",
        "16개"
    )

with col3:
    st.metric(
        "📊 데이터 행",
        f"{len(df)}개"
    )


st.divider()


# ==========================================
# 6. 국가 선택
# ==========================================

st.subheader("🗺️ 국가 선택")

countries = sorted(
    df["Country"].unique().tolist()
)

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "분석하고 싶은 국가를 선택하세요!",
    countries,
    index=default_index
)


# 선택한 국가 데이터 가져오기

country_data = df[
    df["Country"] == selected_country
].iloc[0]


# ==========================================
# 7. MBTI 비율 계산
# ==========================================

rates = country_data[mbti_columns].astype(float)

# 원본 데이터는 0.0463 형식이므로
# 100을 곱해서 백분율로 변환

if rates.max() <= 1:
    rates = rates * 100

# 높은 비율부터 정렬

rates = rates.sort_values(
    ascending=False
)

# 가장 높은 MBTI

top_mbti = rates.index[0]
top_rate = rates.iloc[0]


# ==========================================
# 8. 파란색 그라데이션 함수
# ==========================================

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):

    return "#{:02X}{:02X}{:02X}".format(
        *rgb
    )


def make_blue_gradient(count):

    dark_blue = hex_to_rgb("#155EEF")
    light_blue = hex_to_rgb("#DCEBFF")

    if count <= 0:
        return []

    if count == 1:
        return ["#155EEF"]

    colors = []

    for i in range(count):

        ratio = i / (count - 1)

        rgb = tuple(
            round(
                dark_blue[channel] * (1 - ratio)
                + light_blue[channel] * ratio
            )
            for channel in range(3)
        )

        colors.append(
            rgb_to_hex(rgb)
        )

    return colors


# 1위는 초록색
# 나머지는 파란색 그라데이션

blue_colors = make_blue_gradient(
    len(rates) - 1
)

bar_colors = [
    "#16A34A"
] + blue_colors


# ==========================================
# 9. 핵심 결과 표시
# ==========================================

st.divider()

st.subheader(
    f"🏆 {selected_country}의 MBTI 분석 결과"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🥇 1위 MBTI",
        top_mbti
    )

with col2:

    st.metric(
        "📊 1위 비율",
        f"{top_rate:.2f}%"
    )

with col3:

    st.metric(
        "🧠 분석 유형",
        "16가지"
    )


# ==========================================
# 10. MBTI 막대그래프
# ==========================================

st.subheader("📊 MBTI 유형별 비율")

fig = go.Figure()

fig.add_trace(
    go.Bar(

        x=rates.values,

        y=rates.index,

        orientation="h",

        marker=dict(
            color=bar_colors
        ),

        text=[
            f"{value:.2f}%"
            for value in rates.values
        ],

        textposition="outside",

        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )
)


# 그래프 디자인

fig.update_layout(

    height=650,

    xaxis_title="MBTI 비율 (%)",

    yaxis_title="MBTI 유형",

    yaxis=dict(
        autorange="reversed"
    ),

    xaxis=dict(
        rangemode="tozero"
    ),

    plot_bgcolor="rgba(0,0,0,0)",

    paper_bgcolor="rgba(0,0,0,0)",

    margin=dict(
        l=30,
        r=70,
        t=30,
        b=50
    ),

    font=dict(
        size=13
    ),

    showlegend=False
)


# Streamlit 화면에 그래프 출력

st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    "🟢 초록색: 비율 1위 / "
    "🔵 파란색: 나머지 MBTI 유형"
)


# ==========================================
# 11. MBTI 순위표
# ==========================================

st.divider()

with st.expander("📋 MBTI 전체 순위 확인하기"):

    ranking = pd.DataFrame({

        "순위": range(
            1,
            len(rates) + 1
        ),

        "MBTI 유형": rates.index,

        "비율(%)": rates.values

    })

    ranking["비율(%)"] = (
        ranking["비율(%)"].round(2)
    )

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 12. 데이터 안내
# ==========================================

st.divider()

st.subheader("ℹ️ 데이터 안내")

st.write(
    f"""
    - 분석 국가: {len(countries)}개
    - MBTI 유형: 16개
    - 선택 국가: {selected_country}
    - 최고 비율 유형: {top_mbti}
    - 최고 비율: {top_rate:.2f}%
    """
)

st.caption(
    "※ 이 데이터는 제공된 CSV 자료를 시각화한 것입니다. "
    "실제 국가 전체 국민의 MBTI 분포를 확정적으로 나타내지는 않습니다."
)

st.success(
    "🌍 세계 MBTI 탐험을 이용해 주셔서 감사합니다!"
)
