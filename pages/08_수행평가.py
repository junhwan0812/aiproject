import streamlit as st
import pandas as pd

# ==================================================
# 1. 페이지 설정
# ==================================================

st.set_page_config(
    page_title="초콜릿 한눈에 알아보기",
    page_icon="🍫",
    layout="wide"
)

# ==================================================
# 2. 앱 제목과 소개
# ==================================================

st.title("🍫 초콜릿, 한눈에 알아보기")

st.write(
    "초콜릿을 잘 몰라도 괜찮아요! "
    "이 앱에서는 초콜릿의 카카오 함량, 평점, 제조 회사, "
    "카카오콩 원산지를 쉽고 재미있게 살펴볼 수 있어요."
)

st.info(
    "이 앱은 실제 초콜릿 평가 데이터를 이용해 "
    "어떤 초콜릿이 높은 평가를 받았는지 알아보는 분석 앱입니다."
)

# ==================================================
# 3. 용어 설명
# ==================================================

with st.expander("🍫 초콜릿 데이터, 먼저 알아보기", expanded=True):

    st.markdown("""
    ### 카카오 함량이란?

    초콜릿에 카카오 성분이 얼마나 들어 있는지를 백분율(%)로 나타낸 값이에요.

    예를 들어 카카오 함량이 70%라면 초콜릿의 70%가 카카오 성분이라는 뜻이에요.
    일반적으로 카카오 함량이 높을수록 쓴맛이 강하게 느껴질 수 있어요.

    ### 평점이란?

    초콜릿을 평가한 사람이 매긴 점수예요. 이 데이터에서는 1점부터 5점까지의 점수를 사용해요.

    - 1점: 낮은 평가
    - 3점: 중간 정도의 평가
    - 5점: 높은 평가

    ### 카카오콩 원산지란?

    초콜릿을 만드는 데 사용한 카카오콩이 재배된 지역을 말해요.

    카카오콩은 재배 지역에 따라 향과 맛이 달라질 수 있어요.
    """)

# ==================================================
# 4. 한글 번역 사전
# ==================================================

국가번역 = {
    "France": "프랑스",
    "U.S.A.": "미국",
    "U.S.A": "미국",
    "United States": "미국",
    "U.K.": "영국",
    "United Kingdom": "영국",
    "South Korea": "대한민국",
    "Japan": "일본",
    "Italy": "이탈리아",
    "Germany": "독일",
    "Belgium": "벨기에",
    "Switzerland": "스위스",
    "Netherlands": "네덜란드",
    "Spain": "스페인",
    "Portugal": "포르투갈",
    "Austria": "오스트리아",
    "Canada": "캐나다",
    "Australia": "호주",
    "New Zealand": "뉴질랜드",
    "Brazil": "브라질",
    "Peru": "페루",
    "Ecuador": "에콰도르",
    "Venezuela": "베네수엘라",
    "Colombia": "콜롬비아",
    "Bolivia": "볼리비아",
    "Argentina": "아르헨티나",
    "Chile": "칠레",
    "Mexico": "멕시코",
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
    "Grenada": "그레나다",
    "St. Lucia": "세인트루시아",
    "Ghana": "가나",
    "Madagascar": "마다가스카르",
    "Ivory Coast": "코트디부아르",
    "Nigeria": "나이지리아",
    "Tanzania": "탄자니아",
    "Uganda": "우간다",
    "Cameroon": "카메룬",
    "Congo": "콩고",
    "Sao Tome": "상투메",
    "Sao Tome & Principe": "상투메 프린시페",
    "Togo": "토고",
    "Liberia": "라이베리아",
    "South Africa": "남아프리카공화국",
    "Vietnam": "베트남",
    "India": "인도",
    "Indonesia": "인도네시아",
    "Malaysia": "말레이시아",
    "Philippines": "필리핀",
    "Papua New Guinea": "파푸아뉴기니",
    "Fiji": "피지",
    "Samoa": "사모아",
    "Solomon Islands": "솔로몬제도",
    "Vanuatu": "바누아투",
    "China": "중국",
    "Singapore": "싱가포르",
    "Russia": "러시아",
    "Ireland": "아일랜드",
    "Denmark": "덴마크",
    "Sweden": "스웨덴",
    "Finland": "핀란드",
    "Norway": "노르웨이",
    "Poland": "폴란드",
    "Hungary": "헝가리",
    "Czech Republic": "체코",
    "Lithuania": "리투아니아",
    "Iceland": "아이슬란드",
    "Israel": "이스라엘",
    "Scotland": "스코틀랜드",
    "Wales": "웨일스",
    "Martinique": "마르티니크",
    "Suriname": "수리남",
    "Burma": "미얀마",
    "Niacragua": "니카라과",
    "Eucador": "에콰도르",
    "Sao Tome & Principe": "상투메 프린시페"
}

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
    "EET": "EET"
}

열이름번역 = {
    "회사": "제조 회사",
    "제품/원산지명": "제품명 또는 세부 원산지",
    "참조번호": "참조 번호",
    "평가연도": "평가 연도",
    "카카오함량": "카카오 함량(%)",
    "회사국가": "제조 회사 국가",
    "평점": "평점",
    "콩종류": "카카오콩 종류",
    "콩원산지": "카카오콩 원산지"
}


def 번역하기(value, dictionary):
    """번역 사전에 있는 표현을 한글로 바꾸고, 없는 표현은 원본 유지"""
    if pd.isna(value):
        return "정보 없음"

    value = str(value).strip()

    if value in dictionary:
        return dictionary[value]

    # 원산지에 여러 지역이 들어 있는 경우도 번역
    for eng, kor in sorted(
        dictionary.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        value = value.replace(eng, kor)

    return value


# ==================================================
# 5. CSV 파일 불러오기
# ==================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "flavors_of_cacao.csv",
        header=None,
        encoding="utf-8"
    )

    # 실제 CSV 파일의 열 순서
    df.columns = [
        "회사",
        "제품/원산지명",
        "참조번호",
        "평가연도",
        "카카오함량",
        "회사국가",
        "평점",
        "콩종류",
        "콩원산지"
    ]

    # 빈칸 정리
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

    # 분석에 필요한 값이 없는 행 제거
    df = df.dropna(
        subset=["평가연도", "카카오함량", "평점"]
    )

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "수행평가.csv 파일을 찾을 수 없어요. "
        "app.py와 같은 폴더에 CSV 파일을 넣어 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했어요: {e}")
    st.stop()


# ==================================================
# 6. 한글 표시용 데이터 만들기
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
df_kr["제품/원산지명"] = (
    df_kr["제품/원산지명"].fillna("정보 없음")
)


# ==================================================
# 7. 사이드바 필터
# ==================================================

st.sidebar.header("🔎 원하는 조건 선택하기")

st.sidebar.write(
    "조건을 바꾸면 아래 그래프와 분석 결과도 자동으로 바뀌어요."
)

연도목록 = sorted(
    df_kr["평가연도"].dropna().unique()
)

선택연도 = st.sidebar.multiselect(
    "📅 평가 연도",
    연도목록,
    default=연도목록
)

회사목록 = sorted(
    df_kr["회사"].dropna().unique()
)

선택회사 = st.sidebar.multiselect(
    "🏭 제조 회사",
    회사목록,
    default=회사목록
)

원산지목록 = sorted(
    df_kr["콩원산지"].dropna().unique()
)

선택원산지 = st.sidebar.multiselect(
    "🌍 카카오콩 원산지",
    원산지목록,
    default=원산지목록
)

함량범위 = st.sidebar.slider(
    "🍫 카카오 함량(%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

평점범위 = st.sidebar.slider(
    "⭐ 평점",
    min_value=1.0,
    max_value=5.0,
    value=(1.0, 5.0),
    step=0.25
)

# 필터 적용
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

if filtered.empty:
    st.warning(
        "선택한 조건에 맞는 초콜릿이 없어요. "
        "왼쪽의 필터를 조금 넓혀 보세요."
    )
    st.stop()


# ==================================================
# 8. 데이터 요약
# ==================================================

st.header("📊 지금 선택한 초콜릿 살펴보기")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "평가된 초콜릿",
    f"{len(filtered):,}개"
)

col2.metric(
    "평균 평점",
    f"{filtered['평점'].mean():.2f} / 5점"
)

col3.metric(
    "평균 카카오 함량",
    f"{filtered['카카오함량'].mean():.1f}%"
)

col4.metric(
    "가장 높은 평점",
    f"{filtered['평점'].max():.2f}점"
)

st.caption(
    "위 숫자는 왼쪽에서 선택한 조건에 해당하는 초콜릿만 분석한 결과예요."
)


# ==================================================
# 9. 메뉴 구성
# ==================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍫 카카오 함량",
    "⭐ 평점",
    "🏭 제조 회사",
    "🌍 원산지",
    "📋 전체 데이터"
])


# ==================================================
# 10. 카카오 함량 분석
# ==================================================

with tab1:

    st.subheader("카카오 함량이 높으면 평점도 높을까요?")

    st.write(
        "카카오 함량은 초콜릿에 들어 있는 카카오 성분의 비율이에요. "
        "아래 그래프에서 점 하나는 초콜릿 한 종류를 뜻해요."
    )

    st.scatter_chart(
        filtered,
        x="카카오함량",
        y="평점",
        x_label="카카오 함량(%)",
        y_label="평점(5점 만점)"
    )

    상관계수 = filtered["카카오함량"].corr(
        filtered["평점"]
    )

    st.markdown("### 📖 그래프 읽는 방법")

    st.markdown("""
    - 점이 오른쪽 위로 모이면 카카오 함량이 높을수록 평점도 높아지는 경향이에요.
    - 점이 오른쪽 아래로 모이면 카카오 함량이 높을수록 평점이 낮아지는 경향이에요.
    - 점이 여기저기 흩어져 있으면 두 항목의 관계가 뚜렷하지 않다는 뜻이에요.
    """)

    st.markdown("### 🔍 분석 결과")

    if pd.isna(상관계수):
        st.info("현재 선택한 데이터로는 두 항목의 관계를 계산하기 어려워요.")

    elif 상관계수 >= 0.5:
        st.success(
            f"상관계수는 {상관계수:.2f}예요. "
            "카카오 함량이 높을수록 평점도 높아지는 경향이 비교적 뚜렷해요."
        )

    elif 상관계수 >= 0.2:
        st.info(
            f"상관계수는 {상관계수:.2f}예요. "
            "카카오 함량이 높을수록 평점이 높아지는 약한 경향이 있어요."
        )

    elif 상관계수 <= -0.5:
        st.info(
            f"상관계수는 {상관계수:.2f}예요. "
            "카카오 함량이 높을수록 평점이 낮아지는 경향이 비교적 뚜렷해요."
        )

    elif 상관계수 <= -0.2:
        st.info(
            f"상관계수는 {상관계수:.2f}예요. "
            "카카오 함량이 높을수록 평점이 낮아지는 약한 경향이 있어요."
        )

    else:
        st.info(
            f"상관계수는 {상관계수:.2f}예요. "
            "카카오 함량과 평점 사이의 뚜렷한 관계가 나타나지 않아요."
        )

    st.caption(
        "주의: 상관관계는 두 항목이 함께 변하는 정도를 나타내요. "
        "카카오 함량이 평점을 직접 결정한다는 뜻은 아니에요."
    )

    st.markdown("### 카카오 함량 구간별 평균 평점")

    st.write(
        "카카오 함량을 몇 개의 구간으로 나누고, "
        "각 구간의 평균 평점을 비교해요."
    )

    filtered["카카오구간"] = pd.cut(
        filtered["카카오함량"],
        bins=[0, 60, 70, 75, 80, 101],
        labels=[
            "60% 이하",
            "60~70%",
            "70~75%",
            "75~80%",
            "80% 초과"
        ],
        include_lowest=True
    )

    함량별평점 = (
        filtered.groupby(
            "카카오구간",
            observed=False
        )["평점"]
        .agg(["mean", "count"])
        .reset_index()
    )

    함량별평점.columns = [
        "카카오 함량 구간",
        "평균 평점",
        "평가 수"
    ]

    st.bar_chart(
        함량별평점,
        x="카카오 함량 구간",
        y="평균 평점",
        x_label="카카오 함량 구간",
        y_label="평균 평점"
    )

    st.dataframe(
        함량별평점.round(2),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 11. 평점 분석
# ==================================================

with tab2:

    st.subheader("사람들은 초콜릿에 몇 점을 주었을까요?")

    st.write(
        "평점은 초콜릿을 평가한 사람이 매긴 점수예요. "
        "점수가 높을수록 좋은 평가를 받았다는 뜻이에요."
    )

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
        y="평가 수",
        x_label="평점",
        y_label="평가 수"
    )

    가장많은평점 = 평점분포.loc[
        평점분포["평가 수"].idxmax(),
        "평점"
    ]

    st.info(
        f"현재 선택한 데이터에서 가장 많이 나온 평점은 "
        f"{가장많은평점}점이에요."
    )

    st.markdown("### 📖 평점 구간별 의미")

    st.markdown("""
    | 평점 | 쉽게 이해하기 |
    |---|---|
    | 1~2점 | 상대적으로 낮은 평가 |
    | 3점 | 중간 정도의 평가 |
    | 4점 | 높은 평가 |
    | 5점 | 매우 높은 평가 |
    """)

    st.caption(
        "평점은 사람들의 평가 결과이므로 모든 사람의 취향을 대표하지는 않아요."
    )


# ==================================================
# 12. 제조 회사 분석
# ==================================================

with tab3:

    st.subheader("어떤 회사의 초콜릿이 높은 평가를 받았을까요?")

    st.write(
        "제조 회사별로 평균 평점을 비교해요. "
        "평가 수가 너무 적으면 결과가 달라질 수 있으므로 "
        "평가가 10개 이상인 회사만 비교해요."
    )

    회사별평점 = (
        filtered.groupby("회사")["평점"]
        .agg(["mean", "count"])
        .reset_index()
    )

    회사별평점.columns = [
        "제조 회사",
        "평균 평점",
        "평가 수"
    ]

    회사별평점 = 회사별평점[
        회사별평점["평가 수"] >= 10
    ]

    회사별평점 = 회사별평점.sort_values(
        "평균 평점",
        ascending=False
    )

    if 회사별평점.empty:

        st.warning(
            "평가가 10개 이상인 회사가 없어요. "
            "왼쪽에서 더 많은 회사를 선택해 주세요."
        )

    else:

        st.bar_chart(
            회사별평점.head(15),
            x="제조 회사",
            y="평균 평점",
            x_label="제조 회사",
            y_label="평균 평점"
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
# 13. 원산지 분석
# ==================================================

with tab4:

    st.subheader("카카오콩은 어느 나라에서 왔을까요?")

    st.write(
        "카카오콩 원산지는 초콜릿을 만드는 데 사용한 "
        "카카오콩이 재배된 지역을 뜻해요."
    )

    st.markdown("### 원산지별 평가 수")

    st.write(
        "어떤 원산지의 초콜릿이 데이터에 많이 포함되어 있는지 살펴봐요."
    )

    원산지별평점 = (
        filtered.groupby("콩원산지")["평점"]
        .agg(["mean", "count"])
        .reset_index()
    )

    원산지별평점.columns = [
        "카카오콩 원산지",
        "평균 평점",
        "평가 수"
    ]

    원산지별평점 = 원산지별평점.sort_values(
        "평가 수",
        ascending=False
    )

    st.bar_chart(
        원산지별평점.head(15),
        x="카카오콩 원산지",
        y="평가 수",
        x_label="카카오콩 원산지",
        y_label="평가 수"
    )

    st.markdown("### 원산지별 평균 평점")

    st.write(
        "원산지에 따라 평균 평점이 어떻게 달라지는지 비교해요."
    )

    원산지평점순 = 원산지별평점.sort_values(
        "평균 평점",
        ascending=False
    )

    st.bar_chart(
        원산지평점순.head(15),
        x="카카오콩 원산지",
        y="평균 평점",
        x_label="카카오콩 원산지",
        y_label="평균 평점"
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
# 14. 전체 데이터
# ==================================================

with tab5:

    st.subheader("한글로 번역된 초콜릿 데이터")

    st.write(
        "현재 선택한 조건에 해당하는 초콜릿의 정보를 확인할 수 있어요."
    )

    보여줄데이터 = filtered.rename(
        columns=열이름번역
    )

    st.dataframe(
        보여줄데이터,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 📥 데이터 다운로드")

    st.write(
        "한글로 번역된 데이터를 CSV 파일로 저장할 수 있어요. "
        "다운로드한 파일은 엑셀에서도 열 수 있어요."
    )

    csv_data = 보여줄데이터.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="한글 데이터 다운로드",
        data=csv_data,
        file_name="초콜릿_한글_데이터.csv",
        mime="text/csv"
    )


# ==================================================
# 15. 마무리 설명
# ==================================================

st.divider()

st.markdown("### 💡 분석을 마치며")

st.write(
    "초콜릿의 평점은 카카오 함량뿐만 아니라 "
    "제조 회사, 카카오콩의 종류와 원산지 등 "
    "여러 요소와 관련이 있을 수 있어요."
)

st.write(
    "그래프를 비교하면서 어떤 특징이 나타나는지 살펴보세요. "
    "데이터에서 발견한 관계가 반드시 원인과 결과를 의미하는 것은 아니에요."
)
