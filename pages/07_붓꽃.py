
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃(Iris) 품종 예측 프로그램")

st.write(
    "꽃의 크기를 입력하거나 원하는 속성 2개를 선택하여 "
    "머신러닝으로 붓꽃의 품종을 예측해 보세요!"
)

st.divider()


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    script_folder = Path(__file__).resolve().parent

    # 검색할 폴더
    search_folders = [
        script_folder,
        script_folder.parent,
        script_folder.parent.parent,
        Path.cwd()
    ]

    # 중복 폴더 제거
    search_folders = list(dict.fromkeys(search_folders))

    file_path = None

    # 1차: 지정된 폴더에서 검색
    for folder in search_folders:

        candidate = folder / "Iris.csv"

        if candidate.is_file():
            file_path = candidate
            break

    # 2차: 프로젝트 폴더 내부까지 검색
    if file_path is None:

        for folder in search_folders[:3]:

            if not folder.is_dir():
                continue

            try:
                for candidate in folder.rglob("*"):

                    if (
                        candidate.is_file()
                        and candidate.name.lower() == "iris.csv"
                        and not any(
                            part.startswith(".")
                            or part in ["venv", ".venv", "__pycache__"]
                            for part in candidate.parts
                        )
                    ):
                        file_path = candidate
                        break

            except (PermissionError, OSError):
                continue

            if file_path is not None:
                break

    # CSV 파일이 발견된 경우
    if file_path is not None:

        encodings = [
            "cp949",
            "utf-8-sig",
            "utf-8"
        ]

        last_error = None

        for encoding in encodings:

            try:
                df = pd.read_csv(
                    file_path,
                    encoding=encoding
                )

                # 컬럼 이름 정리
                df.columns = (
                    df.columns
                    .astype(str)
                    .str.strip()
                )

                return df, f"CSV 파일 사용: {file_path}"

            except UnicodeDecodeError as e:
                last_error = e

        raise ValueError(
            f"CSV 인코딩을 확인할 수 없습니다: {last_error}"
        )

    # ======================================
    # CSV 파일이 없으면 내장 데이터 사용
    # ======================================

    iris = load_iris()

    df = pd.DataFrame(
        iris.data,
        columns=[
            "꽃받침 길이",
            "꽃받침 너비",
            "꽃잎 길이",
            "꽃잎 너비"
        ]
    )

    species = [
        "Iris-setosa",
        "Iris-versicolor",
        "Iris-virginica"
    ]

    df["품종"] = [
        species[i] for i in iris.target
    ]

    return df, "Scikit-learn 내장 Iris 데이터 사용"


try:

    df, data_source = load_data()

    st.success(f"데이터 불러오기 완료! ({data_source})")

except Exception as e:

    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# ==========================================
# 3. 데이터 정리
# ==========================================

all_features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"

required_columns = all_features + [target]

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


# 숫자형 변환
for col in all_features:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df[target] = df[target].astype(str).str.strip()

df = df.dropna(
    subset=required_columns
).copy()

if len(df) < 10:

    st.error("학습에 사용할 데이터가 부족합니다.")
    st.stop()

if df[target].nunique() < 2:

    st.error("두 종류 이상의 품종 데이터가 필요합니다.")
    st.stop()


# ==========================================
# 4. 품종 이름
# ==========================================

species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}


# ==========================================
# 5. 알고리즘 설명
# ==========================================

algorithm_info = {

    "서포트 벡터 머신 (SVM)": """
**작동 원리**

SVM은 데이터를 가장 잘 구분할 수 있는 경계선을 찾는 알고리즘입니다.

서로 다른 품종 사이의 간격을 최대한 넓히는 방향으로 학습합니다.

이번 프로그램에서는 RBF 커널을 사용하여
곡선 형태의 경계도 학습할 수 있도록 했습니다.
""",

    "랜덤 포레스트 (Random Forest)": """
**작동 원리**

랜덤 포레스트는 여러 개의 의사결정나무를 만드는 알고리즘입니다.

각 나무가 독립적으로 품종을 예측한 후,
가장 많은 나무가 선택한 품종을 최종 결과로 결정합니다.

여러 나무의 결과를 종합한다는 특징이 있습니다.
""",

    "K-최근접 이웃 (KNN)": """
**작동 원리**

KNN은 새로운 데이터와 가까운 기존 데이터들을 찾아
품종을 예측하는 알고리즘입니다.

이번 프로그램에서는 가장 가까운 데이터 5개를 확인합니다.

주변 데이터 중 가장 많이 등장하는 품종을
최종 예측 결과로 선택합니다.
"""
}


# ==========================================
# 6. 알고리즘 모델 생성
# ==========================================

def make_model(algorithm):

    if algorithm == "서포트 벡터 머신 (SVM)":

        return Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(kernel="rbf"))
        ])

    elif algorithm == "랜덤 포레스트 (Random Forest)":

        return RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )

    elif algorithm == "K-최근접 이웃 (KNN)":

        return Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(
                n_neighbors=5
            ))
        ])


# ==========================================
# 7. 모델 학습
# ==========================================

def train_model(features, algorithm):

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = make_model(algorithm)

    model.fit(
        X_train,
        y_train
    )

    test_prediction = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        test_prediction
    )

    # 전체 데이터로 최종 모델 학습
    model.fit(X, y)

    return model, accuracy


# ==========================================
# 8. 공통 예측 화면
# ==========================================

def prediction_page(features, page_title):

    st.subheader(page_title)

    model, accuracy = train_model(
        features,
        selected_algorithm
    )

    # 입력값 범위
    min1 = float(df[features[0]].min())
    max1 = float(df[features[0]].max())

    min2 = float(df[features[1]].min())
    max2 = float(df[features[1]].max())

    # --------------------------------------
    # 사용자 입력
    # --------------------------------------

    st.markdown("### ✏️ 꽃의 크기 입력하기")

    st.info(
        f"""
📏 입력 가능한 범위

- {features[0]}: {min1:.1f} ~ {max1:.1f} cm
- {features[1]}: {min2:.1f} ~ {max2:.1f} cm
"""
    )

    col1, col2 = st.columns(2)

    with col1:

        value1 = st.number_input(
            f"{features[0]} (cm)",
            min_value=min1,
            max_value=max1,
            value=float(df[features[0]].median()),
            step=0.1,
            format="%.1f",
            key=f"{page_title}_input1"
        )

    with col2:

        value2 = st.number_input(
            f"{features[1]} (cm)",
            min_value=min2,
            max_value=max2,
            value=float(df[features[1]].median()),
            step=0.1,
            format="%.1f",
            key=f"{page_title}_input2"
        )

    # --------------------------------------
    # 품종 예측
    # --------------------------------------

    input_data = pd.DataFrame(
        [[value1, value2]],
        columns=features
    )

    prediction = model.predict(input_data)[0]

    result_name = species_names.get(
        prediction,
        prediction
    )

    st.markdown("### 🔍 품종 예측 결과")

    st.success(
        f"🌸 예측된 붓꽃 품종: {result_name}"
    )

    result1, result2, result3 = st.columns(3)

    result1.metric(
        features[0],
        f"{value1:.1f} cm"
    )

    result2.metric(
        features[1],
        f"{value2:.1f} cm"
    )

    result3.metric(
        "예측 정확도",
        f"{accuracy * 100:.2f}%"
    )

    # --------------------------------------
    # 산점도
    # --------------------------------------

    st.divider()

    st.markdown("### 📊 품종별 크기 비교 그래프")

    fig = px.scatter(
        df,
        x=features[0],
        y=features[1],
        color=target,
        hover_data=[target],
        title=f"{features[0]}과 {features[1]} 비교"
    )

    # 사용자 입력값 초록색 별
    fig.add_trace(
        go.Scatter(
            x=[value1],
            y=[value2],
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
        xaxis_title=features[0] + " (cm)",
        yaxis_title=features[1] + " (cm)",
        legend_title="품종"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------
    # 그래프 아래 알고리즘 설명
    # --------------------------------------

    st.markdown("### 🤖 알고리즘 작동 원리")

    st.info(
        f"선택한 알고리즘: {selected_algorithm}"
    )

    st.markdown(
        algorithm_info[selected_algorithm]
    )

    st.caption(
        f"전체 데이터 {len(df)}개 중 "
        f"학습용 80%, 테스트용 20%로 평가했습니다."
    )


# ==========================================
# 9. 알고리즘 선택
# ==========================================

st.subheader("🤖 머신러닝 알고리즘 선택")

selected_algorithm = st.selectbox(
    "사용할 알고리즘을 선택하세요.",
    [
        "서포트 벡터 머신 (SVM)",
        "랜덤 포레스트 (Random Forest)",
        "K-최근접 이웃 (KNN)"
    ]
)


# ==========================================
# 10. 탭 만들기
# ==========================================

tab1, tab2 = st.tabs([
    "🌷 꽃잎으로 품종 예측",
    "🔬 원하는 속성 2개로 예측"
])


# ==========================================
# 탭 1. 꽃잎 길이 + 꽃잎 너비
# ==========================================

with tab1:

    prediction_page(
        ["꽃잎 길이", "꽃잎 너비"],
        "꽃잎 크기로 품종 예측하기"
    )


# ==========================================
# 탭 2. 원하는 속성 2개 선택
# ==========================================

with tab2:

    st.subheader("🔬 예측에 사용할 속성 선택")

    st.write(
        "아래 네 가지 속성 중 두 가지를 선택하세요."
    )

    col1, col2 = st.columns(2)

    with col1:

        feature1 = st.selectbox(
            "첫 번째 속성",
            all_features,
            index=0,
            key="feature1"
        )

    remaining_features = [
        f for f in all_features
        if f != feature1
    ]

    with col2:

        feature2 = st.selectbox(
            "두 번째 속성",
            remaining_features,
            index=0,
            key="feature2"
        )

    st.success(
        f"선택된 속성: {feature1} + {feature2}"
    )

    prediction_page(
        [feature1, feature2],
        "선택한 속성으로 품종 예측하기"
    )


# ==========================================
# 11. 데이터 정보
# ==========================================

st.divider()

with st.expander("📚 Iris 데이터 확인하기"):

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


# ==========================================
# 12. 마무리
# ==========================================

st.divider()

st.caption(
    "🌸 Iris Machine Learning Project | "
    "Pandas + Scikit-learn + Plotly + Streamlit"
)
