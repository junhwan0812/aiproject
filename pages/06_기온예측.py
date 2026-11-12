
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import re

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 평균기온 AI 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울의 미래 평균기온 예측 AI")

st.markdown("""
과거 서울의 기온 데이터를 활용하여 미래의 평균기온을 예측합니다.

3가지 머신러닝 알고리즘을 비교하고
알고리즘에 따라 예측 결과가 어떻게 달라지는지 확인해 보세요! 🔮
""")

st.divider()


# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

# 기본 파일명은 temperature.csv
# temperature(2).csv도 자동으로 확인
CSV_CANDIDATES = [
    BASE_DIR / "temperature.csv",
    BASE_DIR / "temperature(2).csv"
]

CSV_PATH = next(
    (path for path in CSV_CANDIDATES if path.exists()),
    None
)


# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(file_path):

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


if CSV_PATH is None:

    st.error(
        "temperature.csv 파일을 찾을 수 없습니다.\n\n"
        "CSV 파일을 app.py가 들어 있는 pages 폴더의 "
        "상위 폴더에 넣어주세요."
    )

    st.stop()


df = load_data(str(CSV_PATH))


# ==========================================
# 4. 데이터 확인 및 정리
# ==========================================

required_columns = [
    "일시",
    "평균기온(℃)"
]

if not all(
    col in df.columns
    for col in required_columns
):

    st.error(
        "CSV 파일에 일시 또는 평균기온(℃) 열이 없습니다."
    )

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

    # CSV 데이터의 연도는 2007~2026년
    year = 2000 + short_year

    return pd.Series([year, month])


df[["연도", "월"]] = df["일시"].apply(parse_date)

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "연도",
        "월",
        "평균기온(℃)"
    ]
)

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

# 같은 연도와 월에 데이터가 중복되면 평균 계산
df = df.groupby(
    ["연도", "월"],
    as_index=False
)["평균기온(℃)"].mean()

df = df.sort_values("연도")


# ==========================================
# 5. 데이터 정보
# ==========================================

st.subheader("📂 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "데이터 시작 연도",
        f"{df['연도'].min()}년"
    )

with col2:

    st.metric(
        "데이터 마지막 연도",
        f"{df['연도'].max()}년"
    )

with col3:

    st.metric(
        "전체 데이터 수",
        f"{len(df)}개"
    )


# ==========================================
# 6. 사용자 입력
# ==========================================

st.divider()

st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "📅 예측할 월",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:

    selected_year = st.number_input(
        "🔮 예측할 연도",
        min_value=2007,
        max_value=2200,
        value=2030,
        step=1
    )

selected_year = int(selected_year)


# ==========================================
# 7. 회귀 알고리즘 선택
# ==========================================

st.subheader("🤖 회귀 알고리즘 선택")

algorithm_names = [
    "선형회귀 (Linear Regression)",
    "랜덤 포레스트 회귀 (Random Forest)",
    "그래디언트 부스팅 회귀 (Gradient Boosting)"
]

selected_algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    algorithm_names
)

st.info(
    f"📌 선택한 알고리즘: {selected_algorithm}"
)


# ==========================================
# 8. 선택한 월의 과거 데이터 추출
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


# 입력 데이터
X = month_data[["연도"]]

y = month_data["평균기온(℃)"]


# ==========================================
# 9. 세 가지 회귀 모델 생성
# ==========================================

models = {

    "선형회귀 (Linear Regression)": LinearRegression(),

    "랜덤 포레스트 회귀 (Random Forest)": RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42
    ),

    "그래디언트 부스팅 회귀 (Gradient Boosting)": GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.03,
        max_depth=2,
        random_state=42
    )
}


# ==========================================
# 10. 세 가지 모델 학습 및 예측
# ==========================================

prediction_results = {}

trained_models = {}

for name, model in models.items():

    # 모델 학습
    model.fit(X, y)

    trained_models[name] = model

    # 미래 평균기온 예측
    future_data = pd.DataFrame({
        "연도": [selected_year]
    })

    prediction = model.predict(
        future_data
    )[0]

    prediction_results[name] = prediction


# 선택한 알고리즘의 예측값
selected_prediction = prediction_results[
    selected_algorithm
]


# ==========================================
# 11. 선택한 알고리즘 예측 결과
# ==========================================

st.divider()

st.subheader("🎯 선택한 알고리즘의 예측 결과")

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
        f"{selected_prediction:.2f} ℃"
    )


if selected_year > month_data["연도"].max():

    st.success(
        f"🌟 {selected_year}년 {selected_month}월의 "
        f"예측 평균기온은 "
        f"{selected_prediction:.2f}℃입니다!"
    )

elif selected_year < month_data["연도"].min():

    st.warning(
        "현재 데이터보다 이전 연도를 예측한 결과입니다."
    )

else:

    st.info(
        "선택한 연도는 과거 데이터 범위에 포함됩니다."
    )


# ==========================================
# 12. 세 가지 알고리즘 예측값 비교
# ==========================================

st.divider()

st.subheader("⚖️ 알고리즘별 예측 결과 비교")

comparison_df = pd.DataFrame({

    "회귀 알고리즘": list(
        prediction_results.keys()
    ),

    "예측 평균기온(℃)": [
        round(value, 2)
        for value in prediction_results.values()
    ]

})

comparison_df["선택 여부"] = comparison_df[
    "회귀 알고리즘"
].apply(
    lambda x: "⭐ 선택한 알고리즘"
    if x == selected_algorithm
    else ""
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 13. 알고리즘별 예측값 막대그래프
# ==========================================

st.subheader("📊 알고리즘별 예측 기온 비교 그래프")

bar_fig = go.Figure()

bar_colors = [
    "#3498db",
    "#2ecc71",
    "#e67e22"
]

bar_fig.add_trace(
    go.Bar(
        x=[
            "선형회귀",
            "랜덤 포레스트",
            "그래디언트 부스팅"
        ],

        y=list(
            prediction_results.values()
        ),

        text=[
            f"{v:.2f}℃"
            for v in prediction_results.values()
        ],

        textposition="outside",

        marker_color=bar_colors
    )
)

bar_fig.update_layout(
    title=f"{selected_year}년 {selected_month}월 예측 평균기온",
    xaxis_title="회귀 알고리즘",
    yaxis_title="예측 평균기온 (℃)",
    template="plotly_white",
    height=450,
    showlegend=False
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)


# ==========================================
# 14. 과거 데이터와 선택 모델 추세선
# ==========================================

st.divider()

st.subheader("📈 과거 기온 및 선택 알고리즘 예측 그래프")

fig = go.Figure()

# 실제 기온
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
        marker=dict(size=6)
    )
)

# 선택한 알고리즘의 추세선
trend_years = sorted(
    set(
        month_data["연도"].tolist()
        + [selected_year]
    )
)

trend_X = pd.DataFrame({
    "연도": trend_years
})

trend_values = trained_models[
    selected_algorithm
].predict(trend_X)

fig.add_trace(
    go.Scatter(
        x=trend_years,
        y=trend_values,
        mode="lines",
        name="선택 알고리즘의 예측 추세",
        line=dict(
            color="orange",
            width=3,
            dash="dash"
        )
    )
)

# 선택한 알고리즘의 예측 지점
fig.add_trace(
    go.Scatter(
        x=[selected_year],
        y=[selected_prediction],
        mode="markers+text",
        name="선택 알고리즘 예측값",
        marker=dict(
            color="red",
            size=16,
            symbol="star"
        ),
        text=[
            f"{selected_prediction:.2f}℃"
        ],
        textposition="top center"
    )
)

fig.update_layout(
    title=f"{selected_month}월 평균기온 변화 및 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    height=550
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 15. 알고리즘별 특징 설명
# ==========================================

st.divider()

st.subheader("📚 회귀 알고리즘 알아보기")

# 선형회귀
with st.expander(
    "① 선형회귀 (Linear Regression)",
    expanded=True
):

    st.markdown("""
    **직선을 이용하여 미래 기온을 예측하는 알고리즘입니다.**

    과거 연도와 평균기온의 관계를 분석하여
    데이터의 전체적인 변화 추세를 직선으로 표현합니다.

    **특징**
    - 구조가 단순하고 이해하기 쉽습니다.
    - 연도에 따른 기온 상승 또는 하락 추세를 파악할 수 있습니다.
    - 학습한 연도보다 미래의 연도도 직선으로 예측할 수 있습니다.

    **예측 원리**
    """)

    st.latex(r"y = ax + b")

    st.markdown("""
    실제 기온과 예측 직선 사이의 오차 제곱합이
    작아지도록 기울기와 절편을 학습합니다.
    """)


# 랜덤 포레스트
with st.expander(
    "② 랜덤 포레스트 회귀 (Random Forest)"
):

    st.markdown("""
    **여러 개의 의사결정나무를 결합하는 알고리즘입니다.**

    여러 나무가 각각 예측한 결과를 평균 내어
    최종 예측값을 결정합니다.

    **특징**
    - 여러 의사결정나무를 사용합니다.
    - 복잡하고 비선형적인 데이터 관계를 학습할 수 있습니다.
    - 여러 모델의 결과를 결합하여 예측합니다.

    **이번 프로그램에서는**
    
    300개의 의사결정나무를 사용하도록 설정했습니다.

    **주의사항**

    학습 데이터의 연도 범위를 벗어나면
    새로운 장기 추세를 만들어내지 못합니다.
    따라서 먼 미래의 기온 예측에는 한계가 있습니다.
    """)


# 그래디언트 부스팅
with st.expander(
    "③ 그래디언트 부스팅 회귀 (Gradient Boosting)"
):

    st.markdown("""
    **이전 모델의 예측 오차를 보완하면서 학습하는 알고리즘입니다.**

    작은 의사결정나무를 순차적으로 학습시켜
    이전 모델이 놓친 부분을 개선합니다.

    **특징**
    - 여러 개의 작은 예측 모델을 순서대로 학습합니다.
    - 이전 모델의 오차를 줄이는 방향으로 개선합니다.
    - 복잡한 데이터 관계를 학습할 수 있습니다.

    **이번 프로그램에서는**

    200개의 작은 모델을 순차적으로 학습합니다.

    **주의사항**

    랜덤 포레스트와 마찬가지로 학습한 연도 범위 밖의
    미래 추세를 선형적으로 연장하지 못합니다.
    """)


# ==========================================
# 16. 알고리즘 비교 설명
# ==========================================

st.divider()

st.subheader("🧠 알고리즘에 따라 예측값이 다른 이유")

st.markdown("""
세 가지 알고리즘은 데이터를 학습하는 방법이 서로 다릅니다.

- **선형회귀**: 전체적인 직선 변화 추세를 학습합니다.
- **랜덤 포레스트**: 여러 의사결정나무의 예측을 평균 냅니다.
- **그래디언트 부스팅**: 이전 모델의 오차를 순차적으로 보완합니다.

따라서 동일한 과거 기온 데이터를 사용해도
서로 다른 예측 결과가 나올 수 있습니다.

특히 랜덤 포레스트와 그래디언트 부스팅은
학습한 데이터의 범위를 벗어난 미래 연도를 예측할 때
선형회귀와 다른 결과를 보일 수 있습니다.
""")

# 세 알고리즘 예측값의 차이
prediction_difference = (
    max(prediction_results.values())
    - min(prediction_results.values())
)

st.metric(
    "세 알고리즘의 예측값 최대 차이",
    f"{prediction_difference:.2f} ℃"
)

st.caption(
    "예측값의 차이는 알고리즘별 학습 방식의 차이에서 발생합니다."
)


# ==========================================
# 17. 최종 안내
# ==========================================

st.divider()

st.warning("""
⚠️ 예측 결과 이용 시 주의사항

이 프로그램은 과거 평균기온 데이터를 학습하여
통계적인 방법으로 미래의 기온을 예측합니다.

실제 기온은 기후 변화, 해양 현상, 대기 상태 등
다양한 요인의 영향을 받으므로 예측 결과가
실제 기온과 다를 수 있습니다.

특히 먼 미래의 예측값은 참고 자료로만 활용해 주세요.
""")

st.caption(
    "🌡️ 서울 평균기온 AI 예측 프로그램 | "
    "Linear Regression · Random Forest · Gradient Boosting"
)
