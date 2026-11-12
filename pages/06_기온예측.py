
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import re
from sklearn.linear_model import LinearRegression

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 월별 평균기온 예측 ",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측 ")
st.markdown("""
과거 서울의 평균기온 데이터를 분석하여
미래의 월별 평균기온을 예측해 보세요! 🔮
""")

st.divider()


# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "temperature.csv"


# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    if not CSV_PATH.exists():
        return None

    # 한글 CSV 인코딩 처리
    try:
        data = pd.read_csv(
            CSV_PATH,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        data = pd.read_csv(
            CSV_PATH,
            encoding="utf-8-sig"
        )

    return data


df = load_data()

if df is None:
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다.\n\n"
        "CSV 파일이 pages 폴더의 상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()


# ==========================================
# 4. 데이터 정리
# ==========================================

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.stop()

df = df[required_columns].copy()


# 날짜에서 연도와 월 추출
def parse_date(value):

    match = re.match(
        r"^\s*([A-Za-z]{3})-(\d{2})\s*$",
        str(value)
    )

    if not match:
        return pd.Series([None, None])

    month_text = match.group(1).title()
    short_year = int(match.group(2))

    try:
        month = datetime.strptime(
            month_text,
            "%b"
        ).month
    except ValueError:
        return pd.Series([None, None])

    # 이 CSV 파일은 2007~2026년 데이터
    year = 2000 + short_year

    return pd.Series([year, month])


df[["연도", "월"]] = df["일시"].apply(parse_date)

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["연도", "월", "평균기온(℃)"]
)

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# 같은 연도와 월의 데이터가 여러 개라면 평균 계산
df = df.groupby(
    ["연도", "월"],
    as_index=False
)["평균기온(℃)"].mean()

df = df.sort_values("연도")


# ==========================================
# 5. 사용자 입력
# ==========================================

st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "📅 예측할 월을 선택하세요",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:

    selected_year = st.number_input(
        "🔮 예측할 연도를 입력하세요",
        min_value=2007,
        max_value=2200,
        value=2030,
        step=1
    )

selected_year = int(selected_year)

st.info(
    f"선택한 예측 기간: {selected_year}년 {selected_month}월"
)


# ==========================================
# 6. 선택한 월의 데이터 추출
# ==========================================

month_data = df[
    df["월"] == selected_month
].copy()

month_data = month_data.sort_values("연도")

if len(month_data) < 2:

    st.error(
        "선택한 월의 과거 데이터가 부족합니다."
    )
    st.stop()


# ==========================================
# 7. 선형회귀 모델 학습
# ==========================================

X = month_data[["연도"]]
y = month_data["평균기온(℃)"]

model = LinearRegression()

model.fit(X, y)


# ==========================================
# 8. 미래 평균기온 예측
# ==========================================

prediction = model.predict(
    pd.DataFrame({
        "연도": [selected_year]
    })
)[0]

# 회귀식의 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r_squared = model.score(X, y)


# ==========================================
# 9. 예측 결과 출력
# ==========================================

st.divider()

st.subheader("🤖 AI 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 연도",
        f"{selected_year}년"
    )

with col2:
    st.metric(
        "예측 월",
        f"{selected_month}월"
    )

with col3:
    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )

if selected_year > month_data["연도"].max():

    st.success(
        f"🎯 AI가 예측한 {selected_year}년 "
        f"{selected_month}월의 평균기온은 "
        f"{prediction:.2f}℃입니다!"
    )

elif selected_year < month_data["연도"].min():

    st.warning(
        "현재 데이터보다 이전 연도를 예측한 결과입니다."
    )

else:

    st.info(
        "선택한 연도는 과거 데이터 범위에 포함됩니다. "
        "해당 연도의 실제 기온과 회귀 예측값을 비교해 보세요."
    )


# ==========================================
# 10. 기온 변화 그래프
# ==========================================

st.divider()

st.subheader(
    f"📈 {selected_month}월 연도별 평균기온 변화 그래프"
)

fig = go.Figure()


# 과거 실제 평균기온
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["평균기온(℃)"],
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(
            color="#3498db",
            width=2
        ),
        marker=dict(size=7)
    )
)


# 회귀 추세선
trend_years = sorted(
    set(
        month_data["연도"].tolist()
        + [selected_year]
    )
)

trend_values = model.predict(
    pd.DataFrame({
        "연도": trend_years
    })
)

fig.add_trace(
    go.Scatter(
        x=trend_years,
        y=trend_values,
        mode="lines",
        name="선형회귀 추세선",
        line=dict(
            color="orange",
            width=3,
            dash="dash"
        )
    )
)


# 미래 예측 기온
fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[prediction],
        mode="markers+text",
        name="AI 예측 평균기온",
        marker=dict(
            color="red",
            size=16,
            symbol="star"
        ),
        text=[f"{prediction:.2f}℃"],
        textposition="top center"
    )
)


# 그래프 디자인
fig.update_layout(
    title=f"{selected_month}월 평균기온 분석 및 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    legend_title="그래프 구분"
)

fig.update_xaxes(
    dtick=2
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 11. 회귀분석 정보
# ==========================================

st.subheader("📊 선형회귀 분석 정보")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "회귀식의 기울기",
        f"{slope:.4f}"
    )

    st.caption(
        "연도가 1년 증가할 때 예상되는 평균기온의 변화량입니다."
    )

with col2:

    st.metric(
        "결정계수 (R²)",
        f"{r_squared:.4f}"
    )

    st.caption(
        "모델이 과거 기온 데이터의 변동을 얼마나 설명하는지 나타냅니다."
    )


# ==========================================
# 12. 선형회귀 알고리즘 설명
# ==========================================

st.divider()

st.subheader("📚 선형회귀 알고리즘이란?")

st.markdown("""
선형회귀(Linear Regression)는 과거 데이터를 분석하여
두 변수 사이의 관계를 하나의 직선으로 나타내는
머신러닝 알고리즘입니다.

이번 프로그램에서는 과거의 연도와 평균기온을 분석하여
미래의 평균기온을 예측합니다.
""")

st.latex(r"y = ax + b")

st.markdown("""
**각 기호의 의미**

- **y** : 예측하려는 평균기온
- **x** : 예측하려는 연도
- **a** : 기울기 (연도에 따른 기온 변화량)
- **b** : 절편 (직선의 시작 위치를 결정하는 값)

### 🧠 선형회귀의 작동 과정

1. **데이터 수집**: CSV 파일에서 과거 평균기온을 가져옵니다.
2. **데이터 선택**: 사용자가 선택한 월의 기온 데이터만 추출합니다.
3. **모델 학습**: 연도와 평균기온 사이의 관계를 분석합니다.
4. **직선 생성**: 실제 데이터와의 오차 제곱합이 작아지는 직선을 찾습니다.
5. **미래 예측**: 사용자가 입력한 연도를 직선에 대입하여 평균기온을 계산합니다.

### 📌 이번 프로그램의 특징

1월을 선택하면 과거 모든 1월의 평균기온을 분석하고,
7월을 선택하면 과거 모든 7월의 평균기온을 분석합니다.

따라서 계절별 기온 특성을 고려하여 각각 다른 회귀 모델을 학습합니다.
""")

st.latex(
    r"\text{예측 기온} = "
    r"\text{기울기} \times \text{연도} + \text{절편}"
)

st.warning("""
⚠️ 주의사항

이 프로그램은 과거 기온의 선형적인 변화 추세를 이용한 통계적 예측입니다.
실제 미래의 기온을 정확하게 예보하는 것은 아닙니다.
특히 먼 미래를 예측할수록 오차가 커질 수 있습니다.
""")


# ==========================================
# 13. 하단 안내
# ==========================================

st.divider()

st.caption(
    "🌡️ 서울 평균기온 AI 예측 프로그램 | "
    "Linear Regression | Python & Streamlit"
)
