
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path

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
    page_title="붓꽃 품종 예측 프로그램",
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

    file_path = Path(__file__).resolve().parent / "Iris.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            "Iris.csv 파일이 app.py와 같은 폴더에 없습니다."
        )

    # 한글 인코딩 처리
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
    st.error("데이터 파일을 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()


# 사용할 컬럼
all_features = [
    "꽃받침 길이",
    "꽃받침 너비",
    "꽃잎 길이",
    "꽃잎 너비"
]

target = "품종"


# 필요한 컬럼 확인
required_columns = all_features + [target]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"CSV에 없는 컬럼: {missing_columns}")
    st.write("현재 컬럼:", df.columns.tolist())
    st.stop()


# 숫자형 데이터 변환
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
    st.error("학습할 데이터가 부족합니다.")
    st.stop()


# ==========================================
# 3. 품종 이름
# ==========================================

species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}


# ==========================================
# 4. 알고리즘 설명
# ==========================================

algorithm_info = {

    "서포트 벡터 머신 (SVM)": """
    **작동 원리**

    SVM은 데이터들을 가장 잘 구분할 수 있는 경계선을 찾는
    분류 알고리즘입니다.

    서로 다른 품종 사이의 간격을 최대한 넓히는 방향으로
    분류 기준을 학습합니다.

    이번 프로그램에서는 RBF 커널을 사용하여
    직선만으로 구분하기 어려운 데이터도 분류할 수 있습니다.
    """,

    "랜덤 포레스트 (Random Forest)": """
    **작동 원리**

    랜덤 포레스트는 여러 개의 의사결정나무를 만들어
    각각 품종을 예측하도록 하는 알고리즘입니다.

    여러 나무의 예측 결과를 종합하여
    가장 많은 선택을 받은 품종을 최종 결과로 결정합니다.

    여러 나무를 함께 사용하기 때문에
    하나의 나무에만 의존하는 문제를 줄일 수 있습니다.
    """,

    "K-최근접 이웃 (KNN)": """
    **작동 원리**

    KNN은 새롭게 입력된 데이터와 가까운 기존 데이터를
    찾아 품종을 예측하는 알고리즘입니다.

    이번 프로그램에서는 가장 가까운 데이터 5개를 확인합니다.

    주변 데이터 중 가장 많이 등장한 품종을
    새로운 데이터의 품종으로 예측합니다.
    """
}


# ==========================================
# 5. 머신러닝 모델 생성
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
# 6. 모델 학습 및 정확도 평가
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

    # 학습용 데이터 학습
    model.fit(X_train, y_train)

    # 테스트 데이터 예측
    test_prediction = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        test_prediction
    )

    # 전체 데이터로 최종 모델 학습
    model.fit(X, y)

    return model, accuracy


# ==========================================
# 7. 예측 화면 공통 함수
# ==========================================

def prediction_page(features, page_title):

    st.subheader(page_title)

    st.write(
        f"현재 선택된 속성: **{features[0]}**, **{features[1]}**"
    )

    # 모델 학습
    try:
        model, accuracy = train_model(
            features,
            selected_algorithm
        )

    except Exception as e:
        st.error("모델 학습 중 오류가 발생했습니다.")
        st.code(str(e))
        return

    # 입력 범위 계산
    col_min = float(df[features[0]].min())
    col_max = float(df[features[0]].max())

    row_min = float(df[features[1]].min())
    row_max = float(df[features[1]].max())

    # 데이터 입력
    st.markdown("### ✏️ 꽃의 크기 입력하기")

    st.info(
        f"""
        📏 입력 가능한 범위

        - {features[0]}: {col_min:.1f} ~ {col_max:.1f} cm
        - {features[1]}: {row_min:.1f} ~ {row_max:.1f} cm
        """
    )

    input_col1, input_col2 = st.columns(2)

    with input_col1:

        value1 = st.number_input(
            f"{features[0]} (cm)",
            min_value=col_min,
            max_value=col_max,
            value=float(df[features[0]].median()),
            step=0.1,
            format="%.1f",
            key=f"{page_title}_input1"
        )

    with input_col2:

        value2 = st.number_input(
            f"{features[1]} (cm)",
            min_value=row_min,
            max_value=row_max,
            value=float(df[features[1]].median()),
            step=0.1,
            format="%.1f",
            key=f"{page_title}_input2"
        )

    # 입력 데이터 생성
    input_data = pd.DataFrame(
        [[value1, value2]],
        columns=features
    )

    # 예측
    prediction = model.predict(input_data)[0]

    result_name = species_names.get(
        prediction,
        prediction
    )

    # 결과 표시
    st.markdown("### 🔍 품종 예측 결과")

    st.success(
        f"🌸 예측된 붓꽃 품종: {result_name}"
    )

    result_col1, result_col2, result_col3 = st.columns(3)

    result_col1.metric(
        "첫 번째 속성",
        f"{value1:.1f} cm"
    )

    result_col2.metric(
        "두 번째 속성",
        f"{value2:.1f} cm"
    )

    result_col3.metric(
        "테스트 정확도",
        f"{accuracy * 100:.2f}%"
    )

    # ======================================
    # 8. 산점도 그래프
    # ======================================

    st.divider()

    st.markdown("### 📊 품종별 크기 비교 그래프")

    st.write(
        "기존 붓꽃 데이터는 품종별로 표시하고, "
        "사용자가 입력한 데이터는 초록색 별로 표시합니다."
    )

    fig = px.scatter(
        df,
        x=features[0],
        y=features[1],
        color=target,
        hover_data=[target],
        labels={
            features[0]: features[0] + " (cm)",
            features[1]: features[1] + " (cm)"
        },
        title=f"{features[0]}과 {features[1]} 비교"
    )

    # 사용자 입력값 초록색 별 표시
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
        legend_title="붓꽃 품종"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # 9. 그래프 아래 알고리즘 원리 설명
    # ======================================

    st.markdown("### 🤖 선택한 알고리즘의 작동 원리")

    st.info(
        f"현재 사용 알고리즘: {selected_algorithm}"
    )

    st.markdown(
        algorithm_info[selected_algorithm]
    )

    st.caption(
        f"학습 데이터: {len(df)}개 / "
        f"테스트 데이터: {int(len(df) * 0.2)}개"
    )


# ==========================================
# 10. 알고리즘 선택
# ==========================================

st.subheader("🤖 머신러닝 알고리즘 선택")

st.write(
    "세 가지 분류 알고리즘 중 하나를 선택하세요. "
    "선택한 알고리즘은 아래 두 탭 모두에 적용됩니다."
)

selected_algorithm = st.selectbox(
    "사용할 알고리즘",
    [
        "서포트 벡터 머신 (SVM)",
        "랜덤 포레스트 (Random Forest)",
        "K-최근접 이웃 (KNN)"
    ]
)


# ==========================================
# 11. 두 가지 예측 탭
# ==========================================

tab1, tab2 = st.tabs([
    "🌷 꽃잎으로 품종 예측",
    "🔬 원하는 속성 2개로 예측"
])


# ==========================================
# 탭 1. 기존 꽃잎 예측
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
        "아래 네 가지 속성 중에서 "
        "품종을 예측하는 데 사용할 두 가지를 선택해 보세요."
    )

    option1, option2 = st.columns(2)

    with option1:

        feature1 = st.selectbox(
            "첫 번째 속성 선택",
            all_features,
            index=0,
            key="feature1"
        )

    # 첫 번째 속성과 중복되지 않는 항목만 선택
    remaining_features = [
        f for f in all_features
        if f != feature1
    ]

    with option2:

        feature2 = st.selectbox(
            "두 번째 속성 선택",
            remaining_features,
            index=0,
            key="feature2"
        )

    st.success(
        f"선택한 속성: {feature1} + {feature2}"
    )

    st.write(
        "선택한 두 가지 속성을 사용하여 "
        "새로운 머신러닝 모델을 학습하고 품종을 예측합니다."
    )

    prediction_page(
        [feature1, feature2],
        "선택한 두 가지 속성으로 품종 예측하기"
    )


# ==========================================
# 12. 데이터 정보
# ==========================================

st.divider()

with st.expander("📚 Iris 데이터 정보 확인하기"):

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
# 13. 마무리
# ==========================================

st.divider()

st.caption(
    "🌸 Iris Machine Learning Project | "
    "Pandas + Scikit-learn + Plotly + Streamlit"
)
