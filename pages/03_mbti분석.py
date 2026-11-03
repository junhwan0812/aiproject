
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="세계 MBTI 탐험",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 세계 MBTI 탐험")
st.markdown(
    "국가를 선택하고 해당 국가의 **16가지 MBTI 유형 비율**을 확인해 보세요!"
)

# CSV 파일은 app.py와 같은 폴더에 있어야 합니다.
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"


# ==========================================
# 2. CSV 데이터 불러오기
# ==========================================
@st.cache_data
def load_data(file_path):
    # UTF-8 형식으로 읽고, 실패하면 다른 인코딩으로 시도합니다.
    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="cp949")

    # 열 이름의 불필요한 공백 제거
    data.columns = data.columns.str.strip()

    if "Country" not in data.columns:
        raise ValueError(
            "CSV 파일에 'Country' 열이 없습니다."
        )

    # 국가 이름 정리
    data["Country"] = data["Country"].astype(str).str.strip()
    data = data[
        (data["Country"] != "") &
        (data["Country"].str.lower() != "nan")
    ]

    # Country를 제외한 나머지 열을 MBTI 열로 사용
    mbti_columns = [
        column for column in data.columns
        if column != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 열은 16개여야 합니다. "
            f"현재 {len(mbti_columns)}개입니다."
        )

    # MBTI 데이터가 숫자인지 확인
    for column in mbti_columns:
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        )

    if data[mbti_columns].isna().any().any():
        raise ValueError(
            "MBTI 데이터에 비어 있거나 숫자가 아닌 값이 있습니다."
        )

    return data, mbti_columns


# ==========================================
# 3. 데이터 오류 확인
# ==========================================
try:
    if not DATA_FILE.exists():
        st.error(
            "CSV 파일을 찾을 수 없습니다.\n\n"
            "countriesMBTI_16types.csv 파일을 "
            "app.py와 같은 폴더에 넣어 주세요."
        )
        st.stop()

    df, mbti_columns = load_data(DATA_FILE)

except Exception as error:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()


# ==========================================
# 4. 국가 선택 메뉴
# ==========================================
countries = sorted(df["Country"].unique().tolist())

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요",
    options=countries,
    index=default_index
)

# 선택한 국가의 데이터 한 행 가져오기
country_data = df.loc[
    df["Country"] == selected_country
].iloc[0]


# ==========================================
# 5. MBTI 비율 계산 및 정렬
# ==========================================
rates = country_data[mbti_columns].astype(float)

# 원본 데이터가 0~1 사이의 비율이라면
# 100을 곱해 백분율(%)로 변환합니다.
rates = rates * 100

# 높은 비율부터 낮은 비율 순서로 정렬
rates = rates.sort_values(ascending=False)

# 가장 높은 MBTI 유형과 비율
top_mbti = rates.index[0]
top_rate = rates.iloc[0]


# ==========================================
# 6. 파란색 그라데이션 만들기
# ==========================================
def hex_to_rgb(hex_color):
    """HEX 색상을 RGB 숫자로 변환합니다."""
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    """RGB 숫자를 HEX 색상으로 변환합니다."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def make_blue_gradient(count):
    """진한 파란색에서 연한 파란색으로 색상을 생성합니다."""
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

        colors.append(rgb_to_hex(rgb))

    return colors


# 1위는 초록색, 나머지 15개는 파란색 그라데이션
blue_colors = make_blue_gradient(len(rates) - 1)

bar_colors = ["#16A34A"] + blue_colors


# ==========================================
# 7. 핵심 통계 표시
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🌍 선택한 국가",
        value=selected_country
    )

with col2:
    st.metric(
        label="🏆 비율 1위 MBTI",
        value=top_mbti
    )

with col3:
    st.metric(
        label="📊 1위 비율",
        value=f"{top_rate:.2f}%"
    )

st.divider()


# ==========================================
# 8. 막대그래프 만들기
# ==========================================
st.subheader(f"📊 {selected_country}의 MBTI 비율")

fig = go.Figure(
    data=[
        go.Bar(
            # 가로 막대그래프
            x=rates.values,
            y=rates.index,
            orientation="h",

            # 막대별 색상
            marker=dict(
                color=bar_colors,
                line=dict(
                    color="rgba(0,0,0,0)",
                    width=0
                )
            ),

            # 막대 끝에 비율 표시
            text=[
                f"{value:.2f}%"
                for value in rates.values
            ],
            textposition="outside",

            # 마우스를 올렸을 때 표시할 정보
            hovertemplate=(
                "<b>%{y}</b><br>"
                "비율: %{x:.2f}%"
                "<extra></extra>"
            )
        )
    ]
)

# 그래프 모양과 축 설정
fig.update_layout(
    height=650,

    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",

    # 가장 높은 비율이 맨 위에 오도록 설정
    yaxis=dict(
        autorange="reversed"
    ),

    # 가로축이 0부터 시작하도록 설정
    xaxis=dict(
        rangemode="tozero"
    ),

    # 배경을 투명하게 설정
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",

    # 그래프 여백
    margin=dict(
        l=30,
        r=65,
        t=25,
        b=45
    ),

    font=dict(size=13),
    showlegend=False
)

# Streamlit 화면에 그래프 표시
st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "🟢 초록색은 비율 1위 MBTI입니다. "
    "🔵 나머지는 진한 파란색부터 연한 파란색까지 "
    "그라데이션으로 표시됩니다."
)


# ==========================================
# 9. MBTI 순위표
# ==========================================
with st.expander("📋 MBTI 비율 순위표 보기"):

    ranking = pd.DataFrame({
        "순위": range(1, len(rates) + 1),
        "MBTI 유형": rates.index,
        "비율(%)": rates.values
    })

    ranking["비율(%)"] = ranking["비율(%)"].round(2)

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 10. 데이터 안내
# ==========================================
st.divider()

st.caption(
    "※ 이 웹 앱은 제공된 CSV 데이터의 비율에 100을 곱해 "
    "백분율로 표시합니다. 데이터의 출처와 조사 방법에 따라 "
    "해석에 한계가 있을 수 있으며, 국가 전체 국민의 성격을 "
    "확정적으로 나타내는 자료는 아닙니다."
)
