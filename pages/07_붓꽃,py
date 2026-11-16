
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃(Iris) 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "머신러닝이 붓꽃의 품종을 예측합니다."
)

st.divider()


# =====================================
# 2. CSV 파일 불러오기
# =====================================
@st.cache_data
def load_data():

    # CSV 파일 위치 찾기
    current_folder = Path(__file__).resolve().parent

    possible_paths = [
        current_folder / "Iris.csv",
        current_folder.parent / "Iris.csv",
        Path.cwd() / "Iris.csv"
    ]

    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "Iris.csv 파일을 찾을 수 없습니다."
        )

    # 실제 파일의 한글 인코딩 처리
    df = pd.read_csv(
        file_path,
        encoding="cp949"
    )

    # 컬럼 이름 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터 파일을 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# =====================================
# 3. 데이터 확인 및 정리
# =====================================
features = ["꽃잎 길이", "꽃잎 너비"]
target = "품종"

# 필요한 컬럼 확인
required_columns = features + [target]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        f"CSV 파일에 필요한 컬럼이 없습니다: {missing_columns}"
    )
    st.write("현재 CSV 컬럼:", df.columns.tolist())
    st.stop()

# 숫자 데이터 변환
for col in features:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 결측치 제거
df = df.dropna(
    subset=required_columns
).copy()

# 품종 데이터 문자열 처리
df[target] = df[target].astype(str).str.strip()

if len(df) == 0:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

if df[target].nunique() < 2:
    st.error("분류하려면 두 종류 이상의 품종이 필요합니다.")
    st.stop()


# =====================================
# 4. 입력 범위 계산
# =====================================
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())


# =====================================
# 5. SVM 머신러닝 학습
# =====================================
X = df[features]
y = df[target]

try:

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # 표준화 + SVM
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(kernel="rbf"))
    ])

    # 학습
    model.fit(X_train, y_train)

    # 정확도 확인
    test_prediction = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        test_prediction
    )

    # 전체 데이터로 다시 학습
    model.fit(X, y)

except Exception as e:
    st.error("머신러닝 모델 학습 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# =====================================
# 6. 알고리즘 안내
# =====================================
with st.expander("🤖 사용된 알고리즘 알아보기"):

    st.markdown("""
    **서포트 벡터 머신(SVM)**

    - 분류 문제에 사용하는 머신러닝 알고리즘입니다.
    - 꽃잎 길이와 너비를 학습합니다.
    - RBF 커널을 사용하여 비선형적인 관계도 학습합니다.
    - StandardScaler로 입력 데이터의 크기를 표준화합니다.
    """)

    st.metric(
        "테스트 데이터 예측 정확도",
        f"{accuracy * 100:.2f}%"
    )


st.divider()


# =====================================
# 7. 사용자 입력
# =====================================
st.subheader("✏️ 꽃잎 크기 입력하기")

st.info(
    f"""
    📏 입력 가능한 데이터 범위

    - 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm
    - 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm
    """
)

col1, col2 = st.columns(2)

with col1:

    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=min(5.0, length_max),
        step=0.1,
        format="%.1f"
    )

with col2:

    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=min(1.5, width_max),
        step=0.1,
        format="%.1f"
    )


# =====================================
# 8. 품종 예측
# =====================================
input_data = pd.DataFrame(
    {
        "꽃잎 길이": [petal_length],
        "꽃잎 너비": [petal_width]
    }
)

prediction = model.predict(input_data)[0]

species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}

result_name = species_names.get(
    prediction,
    prediction
)

st.divider()

st.subheader("🔍 예측 결과")

st.success(
    f"🌸 예측된 붓꽃 품종: {result_name}"
)

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.metric(
        "꽃잎 길이",
        f"{petal_length:.1f} cm"
    )

with result_col2:
    st.metric(
        "꽃잎 너비",
        f"{petal_width:.1f} cm"
    )


# =====================================
# 9. 산점도 그래프
# =====================================
st.divider()

st.subheader("📊 붓꽃 품종별 꽃잎 크기 비교")

st.write(
    "기존 데이터는 품종별 색상으로 표시하고, "
    "사용자가 입력한 값은 초록색 별로 표시합니다."
)

fig = px.scatter(
    df,
    x="꽃잎 길이",
    y="꽃잎 너비",
    color="품종",
    title="붓꽃 품종별 꽃잎 크기 산점도",
    labels={
        "꽃잎 길이": "꽃잎 길이 (cm)",
        "꽃잎 너비": "꽃잎 너비 (cm)"
    }
)

# 사용자 입력값 표시
fig.add_trace(
    go.Scatter(
        x=[petal_length],
        y=[petal_width],
        mode="markers",
        name="사용자 입력값",
        marker=dict(
            symbol="star",
            size=24,
            color="green",
            line=dict(
                color="black",
                width=1
            )
        )
    )
)

fig.update_layout(
    height=550,
    xaxis_title="꽃잎 길이 (cm)",
    yaxis_title="꽃잎 너비 (cm)",
    legend_title="붓꽃 품종"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 10. 데이터 정보
# =====================================
with st.expander("📚 학습 데이터 확인하기"):

    st.write("전체 데이터 개수:", len(df))

    st.write("품종별 데이터 개수")

    st.dataframe(
        df[target].value_counts()
    )

    st.write("전체 데이터")

    st.dataframe(
        df,
        use_container_width=True
    )


# =====================================
# 11. 마무리
# =====================================
st.divider()

st.caption(
    "🌸 Iris 품종 예측 | "
    "Pandas + Scikit-learn + Plotly + Streamlit"
)
