from pathlib import Path

import pandas as pd
import streamlit as st


# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="초콜릿 한눈에 알아보기",
    page_icon="🍫",
    layout="wide"
)

st.title("🍫 초콜릿 한눈에 알아보기")
st.write(
    "원하는 조건을 선택하면 초콜릿의 특징과 평가 결과를 "
    "쉽게 알아볼 수 있어요."
)


# ==================================================
# 2. 국가 이름 한글 번역 사전
# ==================================================

국가번역 = {
    "France": "프랑스",
    "U.S.A.": "미국",
    "U.S.A": "미국",
    "USA": "미국",
    "United States": "미국",
    "United States of America": "미국",
    "U.K.": "영국",
    "UK": "영국",
    "United Kingdom": "영국",
    "England": "잉글랜드",
    "Scotland": "스코틀랜드",
    "Wales": "웨일스",
    "Ireland": "아일랜드",
    "South Korea": "대한민국",
    "Korea": "대한민국",
    "Japan": "일본",
    "China": "중국",
    "Taiwan": "대만",
    "Hong Kong": "홍콩",
    "Singapore": "싱가포르",
    "India": "인도",
    "Indonesia": "인도네시아",
    "Malaysia": "말레이시아",
    "Philippines": "필리핀",
    "Vietnam": "베트남",
    "Thailand": "태국",
    "Australia": "호주",
    "New Zealand": "뉴질랜드",
    "Papua New Guinea": "파푸아뉴기니",
    "Fiji": "피지",
    "Samoa": "사모아",
    "Solomon Islands": "솔로몬제도",
    "Vanuatu": "바누아투",

    "Italy": "이탈리아",
    "Germany": "독일",
    "Belgium": "벨기에",
    "Switzerland": "스위스",
    "Netherlands": "네덜란드",
    "Spain": "스페인",
    "Portugal": "포르투갈",
    "Austria": "오스트리아",
    "Denmark": "덴마크",
    "Sweden": "스웨덴",
    "Finland": "핀란드",
    "Norway": "노르웨이",
    "Poland": "폴란드",
    "Hungary": "헝가리",
    "Czech Republic": "체코",
    "Czechia": "체코",
    "Lithuania": "리투아니아",
    "Iceland": "아이슬란드",
    "Russia": "러시아",
    "Greece": "그리스",
    "Turkey": "튀르키예",
    "Israel": "이스라엘",

    "Canada": "캐나다",
    "Mexico": "멕시코",
    "Brazil": "브라질",
    "Peru": "페루",
    "Ecuador": "에콰도르",
    "Venezuela": "베네수엘라",
    "Colombia": "콜롬비아",
    "Bolivia": "볼리비아",
    "Argentina": "아르헨티나",
    "Chile": "칠레",
    "Guatemala": "과테말라",
    "Honduras": "온두라스",
    "Nicaragua": "니카라과",
    "Costa Rica": "코스타리카",
    "El Salvador": "엘살바도르",
    "Dominican Republic": "도미니카공화국",
    "Domincan Republic": "도미니카공화국",
    "Dominican Rep.": "도미니카공화국",
    "Dom. Rep.": "도미니카공화국",
    "Cuba": "쿠바",
    "Jamaica": "자메이카",
    "Haiti": "아이티",
    "Puerto Rico": "푸에르토리코",
    "Trinidad": "트리니다드",
    "Tobago": "토바고",
    "Trinidad and Tobago": "트리니다드 토바고",
    "Grenada": "그레나다",
    "St. Lucia": "세인트루시아",
    "Martinique": "마르티니크",
    "Suriname": "수리남",

    "Ghana": "가나",
    "Madagascar": "마다가스카르",
    "Ivory Coast": "코트디부아르",
    "Côte d'Ivoire": "코트디부아르",
    "Nigeria": "나이지리아",
    "Tanzania": "탄자니아",
    "Uganda": "우간다",
    "Cameroon": "카메룬",
    "Congo": "콩고",
    "Sao Tome": "상투메",
    "Sao Tome & Principe": "상투메 프린시페",
    "São Tomé and Príncipe": "상투메 프린시페",
    "Togo": "토고",
    "Liberia": "라이베리아",
    "South Africa": "남아프리카공화국",
    "Burma": "미얀마",
    "Myanmar": "미얀마",
}


# ==================================================
# 3. 카카오콩 종류 한글 번역 사전
# ==================================================

콩종류번역 = {
    "Criollo": "크리올로",
    "Forastero": "포라스테로",
    "Trinitario": "트리니타리오",
    "Nacional": "나시오날",
    "Amazon": "아마존",
    "Amazon mix": "아마존 혼합",
    "Blend": "혼합",
    "Beniano": "베니아노",
    "CCN51": "CCN-51",
    "Matina": "마티나",
    "EET": "EET",
}


# ==================================================
# 4. 열 이름 번역 사전
# ==================================================

열이름번역 = {
    "회사": "제조 회사",
    "제품/원산지명": "제품명 또는 세부 원산지",
    "참조번호": "참조 번호",
    "평가연도": "평가 연도",
    "카카오함량": "카카오 함량(%)",
    "회사국가": "제조 회사 국가",
    "평점": "평점",
    "콩종류": "카카오콩 종류",
    "콩원산지": "카카오콩 원산지",
}


# ==================================================
# 5. 번역 함수
# ==================================================

def 번역하기(value, dictionary):
    if pd.isna(value):
        return "정보 없음"

    value = str(value).strip()

    if value in dictionary:
        return dictionary[value]

    return value


# ==================================================
# 6. CSV 파일 불러오기
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "flavors_of_cacao.csv"


@st.cache_data
def load_data():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}"
        )

    df = pd.read_csv(
        CSV_PATH,
        encoding="utf-8-sig"
    )

    원본열이름 = [
        str(col).strip().lower()
        for col in df.columns
    ]

    영문열이름 = {
        "company": "회사",
        "specific bean origin or bar name": "제품/원산지명",
        "ref": "참조번호",
        "review date": "평가연도",
        "cocoa percent": "카카오함량",
        "company location": "회사국가",
        "rating": "평점",
        "bean type": "콩종류",
        "broad bean origin": "콩원산지",
    }

    # 열 이름이 없는 CSV 파일도 처리
    if "company" not in 원본열이름:
        df = pd.read_csv(
            CSV_PATH,
            header=None,
            encoding="utf-8-sig"
        )

        if df.shape[1] != 9:
            raise ValueError(
                "CSV 파일은 9개의 열로 구성되어 있어야 합니다."
            )

        df.columns = [
            "회사",
            "제품/원산지명",
            "참조번호",
            "평가연도",
            "카카오함량",
            "회사국가",
            "평점",
            "콩종류",
            "콩원산지",
        ]

    else:
        df.columns = [
            영문열이름.get(
                str(col).strip().lower(),
                str(col).strip()
            )
            for col in df.columns
        ]

    # 빈 문자열을 결측값으로 처리
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # 숫자 데이터 변환
    df["평가연도"] = pd.to_numeric(
        df["평가연도"],
        errors="coerce"
    )

    df["평점"] = pd.to_numeric(
        df["평점"],
        errors="coerce"
    )

    df["카카오함량"] = pd.to_numeric(
        df["카카오함량"]
        .astype("string")
        .str.replace("%", "", regex=False),
        errors="coerce"
    )

    # 분석에 필요한 숫자 정보가 없는 행 제거
    df = df.dropna(
        subset=["평가연도", "카카오함량", "평점"]
    )

    return df


try:
    df = load_data()

except FileNotFoundError as e:
    st.error("📂 flavors_of_cacao.csv 파일을 찾을 수 없어요.")
    st.write("CSV 파일을 아래 위치에 넣어 주세요.")
    st.code(str(CSV_PATH))
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했어요: {e}")
    st.stop()


# ==================================================
# 7. 한글 표시용 데이터 만들기
# ==================================================

df_kr = df.copy()

df_kr["회사국가"] = df_kr["회사국가"].apply(
    lambda x: 번역하기(x, 국가번역)
)

df_kr["콩원산지"] = df_kr["콩원산지"].apply(
    lambda x: 번역하기(x, 국가번역)
)

df_kr["콩종류"] = df_kr["콩종류"].apply(
    lambda x: 번역하기(x, 콩종류번역)
)

df_kr["회사"] = df_kr["회사"].fillna("정보 없음")
df_kr["제품/원산지명"] = df_kr["제품/원산지명"].fillna("정보 없음")


# ==================================================
# 8. 데이터 설명
# ==================================================

with st.expander("📘 초콜릿 데이터 알아보기", expanded=True):
    st.markdown("""
    | 용어 | 쉬운 설명 |
    |---|---|
    | 카카오 함량 | 초콜릿에 카카오 성분이 얼마나 들어 있는지 나타낸 비율 |
    | 평점 | 초콜릿을 평가한 사람이 매긴 점수. 5점에 가까울수록 높은 평가 |
    | 제조 회사 | 초콜릿을 만든 회사 |
    | 제조 회사 국가 | 초콜릿 제조 회사가 있는 국가 |
    | 카카오콩 원산지 | 초콜릿에 사용한 카카오콩이 재배된 지역 |
    """)

    st.caption(
        "국가 이름은 가능한 경우 한글로 표시해요. "
        "번역 사전에 없는 이름은 원래 표기를 유지합니다."
    )


# ==================================================
# 9. 조건 선택
# ==================================================

st.header("🔎 원하는 조건 선택하기")

with st.container(border=True):
    col1, col2, col3 = st.columns(3)

    연도목록 = sorted(df_kr["평가연도"].dropna().unique())
    회사목록 = sorted(df_kr["회사"].dropna().unique())
    원산지목록 = sorted(df_kr["콩원산지"].dropna().unique())

    with col1:
        선택연도 = st.multiselect(
            "📅 평가 연도",
            연도목록,
            default=연도목록
        )

    with col2:
        선택회사 = st.multiselect(
            "🏭 제조 회사",
            회사목록,
            default=회사목록
        )

    with col3:
        선택원산지 = st.multiselect(
            "🌍 카카오콩 원산지",
            원산지목록,
            default=원산지목록
        )

    col4, col5 = st.columns(2)

    with col4:
        함량범위 = st.slider(
            "🍫 카카오 함량(%)",
            min_value=0,
            max_value=100,
            value=(0, 100)
        )

    with col5:
        평점범위 = st.slider(
            "⭐ 평점",
            min_value=1.0,
            max_value=5.0,
            value=(1.0, 5.0),
            step=0.25
        )

    st.caption(
        "처음에는 모든 항목이 선택되어 있어요. "
        "특정 조건만 보고 싶다면 원하는 항목을 선택하세요."
    )


# ==================================================
# 10. 선택 조건 적용
# ==================================================

filtered = df_kr[
    df_kr["평가연도"].isin(선택연도)
    & df_kr["회사"].isin(선택회사)
    & df_kr["콩원산지"].isin(선택원산지)
    & df_kr["카카오함량"].between(
        함량범위[0],
        함량범위[1]
    )
    & df_kr["평점"].between(
        평점범위[0],
        평점범위[1]
    )
].copy()

st.divider()
st.header("📊 선택한 조건의 분석 결과")

if filtered.empty:
    st.warning(
        "선택한 조건에 맞는 초콜릿이 없어요. "
        "조건을 조금 넓혀서 다시 선택해 주세요."
    )
    st.stop()


# ==================================================
# 11. 기본 통계
# ==================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🍫 평가된 초콜릿",
    f"{len(filtered):,}개"
)

col2.metric(
    "⭐ 평균 평점",
    f"{filtered['평점'].mean():.2f}점"
)

col3.metric(
    "카카오 함량 평균",
    f"{filtered['카카오함량'].mean():.1f}%"
)

col4.metric(
    "가장 높은 평점",
    f"{filtered['평점'].max():.2f}점"
)


# ==================================================
# 12. 분석 탭
# ==================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍫 카카오 함량",
    "⭐ 평점",
    "🏭 제조 회사",
    "🌍 원산지",
    "📋 전체 데이터",
])


# ==================================================
# 13. 카카오 함량 분석
# ==================================================

with tab1:
    st.subheader("카카오 함량과 평점의 관계")

    st.write(
        "점 하나가 초콜릿 한 종류를 뜻해요. "
        "점들이 어디에 모여 있는지 살펴보세요."
    )

    st.scatter_chart(
        filtered,
        x="카카오함량",
        y="평점"
    )

    상관계수 = filtered["카카오함량"].corr(filtered["평점"])

    if pd.isna(상관계수):
        st.info("현재 선택한 데이터로는 관계를 계산하기 어려워요.")
    elif 상관계수 >= 0.5:
        st.success(
            f"상관계수는 {상관계수:.2f}예요. "
            "두 항목 사이에 비교적 뚜렷한 양의 관계가 있어요."
        )
    elif 상관계수 <= -0.5:
        st.info(
            f"상관계수는 {상관계수:.2f}예요. "
            "두 항목 사이에 비교적 뚜렷한 음의 관계가 있어요."
        )
    else:
        st.info(
            f"상관계수는 {상관계수:.2f}예요. "
            "두 항목 사이의 관계가 약하거나 뚜렷하지 않아요."
        )

    st.caption(
        "상관관계가 있다고 해서 카카오 함량이 평점을 직접 결정한다는 뜻은 아니에요."
    )

    st.markdown("### 카카오 함량 구간별 평균 평점")

    filtered["카카오구간"] = pd.cut(
        filtered["카카오함량"],
        bins=[0, 60, 70, 75, 80, 101],
        labels=[
            "60% 이하",
            "60~70%",
            "70~75%",
            "75~80%",
            "80% 초과",
        ],
        include_lowest=True
    )

    함량별평점 = (
        filtered.groupby("카카오구간", observed=False)["평점"]
        .agg(["mean", "count"])
        .reset_index()
    )

    함량별평점.columns = [
        "카카오 함량 구간",
        "평균 평점",
        "평가 수",
    ]

    st.bar_chart(
        함량별평점,
        x="카카오 함량 구간",
        y="평균 평점"
    )

    st.dataframe(
        함량별평점.round(2),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 14. 평점 분석
# ==================================================

with tab2:
    st.subheader("사람들은 초콜릿에 몇 점을 주었을까요?")

    평점분포 = (
        filtered["평점"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    평점분포.columns = ["평점", "평가 수"]

    st.bar_chart(
        평점분포,
        x="평점",
        y="평가 수"
    )

    가장많은평점 = 평점분포.loc[
        평점분포["평가 수"].idxmax(),
        "평점"
    ]

    st.info(
        f"현재 선택한 데이터에서 가장 많이 나온 평점은 "
        f"{가장많은평점}점이에요."
    )


# ==================================================
# 15. 제조 회사 분석
# ==================================================

with tab3:
    st.subheader("회사별 평균 평점")

    회사별평점 = (
        filtered.groupby("회사")["평점"]
        .agg(["mean", "count"])
        .reset_index()
    )

    회사별평점.columns = ["제조 회사", "평균 평점", "평가 수"]

    회사별평점 = 회사별평점[
        회사별평점["평가 수"] >= 10
    ].sort_values(
        "평균 평점",
        ascending=False
    )

    if 회사별평점.empty:
        st.warning(
            "평가가 10개 이상인 회사가 없어요. "
            "더 많은 회사를 선택해 주세요."
        )
    else:
        st.bar_chart(
            회사별평점.head(15),
            x="제조 회사",
            y="평균 평점"
        )

        st.dataframe(
            회사별평점.round(2),
            use_container_width=True,
            hide_index=True
        )

        최고회사 = 회사별평점.iloc[0]

        st.success(
            f"현재 조건에서 가장 높은 평균 평점을 받은 회사는 "
            f"{최고회사['제조 회사']}예요. "
            f"평균 평점은 {최고회사['평균 평점']:.2f}점이에요."
        )


# ==================================================
# 16. 원산지 분석
# ==================================================

with tab4:
    st.subheader("카카오콩은 어느 나라에서 왔을까요?")

    원산지별평점 = (
        filtered.groupby("콩원산지")["평점"]
        .agg(["mean", "count"])
        .reset_index()
    )

    원산지별평점.columns = [
        "카카오콩 원산지",
        "평균 평점",
        "평가 수",
    ]

    원산지별평점 = 원산지별평점.sort_values(
        "평가 수",
        ascending=False
    )

    st.markdown("### 원산지별 평가 수")

    st.bar_chart(
        원산지별평점.head(15),
        x="카카오콩 원산지",
        y="평가 수"
    )

    st.markdown("### 원산지별 평균 평점")

    원산지평점순 = 원산지별평점.sort_values(
        "평균 평점",
        ascending=False
    )

    st.bar_chart(
        원산지평점순.head(15),
        x="카카오콩 원산지",
        y="평균 평점"
    )

    st.dataframe(
        원산지별평점.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "평가 수가 많다는 것은 데이터에 많이 포함되어 있다는 뜻이에요. "
        "반드시 품질이 더 좋다는 뜻은 아니에요."
    )


# ==================================================
# 17. 전체 데이터 및 다운로드
# ==================================================

with tab5:
    st.subheader("한글로 번역된 초콜릿 데이터")

    보여줄데이터 = filtered.rename(columns=열이름번역)

    st.dataframe(
        보여줄데이터,
        use_container_width=True,
        hide_index=True
    )

    csv_data = 보여줄데이터.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 한글 데이터 다운로드",
        data=csv_data,
        file_name="초콜릿_한글_데이터.csv",
        mime="text/csv"
    )


# ==================================================
# 18. 마무리 설명
# ==================================================

st.divider()
st.markdown("### 💡 분석을 마치며")

st.write(
    "초콜릿의 평점은 카카오 함량뿐만 아니라 제조 회사, "
    "카카오콩의 종류와 원산지 등 여러 요소와 관련이 있을 수 있어요."
)

st.write(
    "그래프를 비교하면서 어떤 특징이 나타나는지 살펴보세요. "
    "데이터에서 발견한 관계가 반드시 원인과 결과를 의미하는 것은 아니에요."
)
