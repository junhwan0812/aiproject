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

st.title("🍫 초콜릿 한눈에 알아보기")

st.write(
    "초콜릿을 잘 몰라도 괜찮아요! "
    "원하는 조건을 선택하면 초콜릿의 특징과 평가 결과를 "
    "쉽게 알아볼 수 있어요."
)

# ==================================================
# 2. 기본 설명
# ==================================================

with st.expander("🍫 초콜릿 데이터 알아보기", expanded=True):

    st.markdown("""
    | 용어 | 쉬운 설명 |
    |---|---|
    | 카카오 함량 | 초콜릿에 카카오 성분이 얼마나 들어 있는지 나타낸 비율 |
    | 평점 | 초콜릿을 평가한 사람이 매긴 점수. 5점에 가까울수록 높은 평가 |
    | 제조 회사 | 초콜릿을 만든 회사 |
    | 카카오콩 원산지 | 초콜릿을 만드는 데 사용한 카카오콩이 재배된 지역 |
    """)

    st.caption(
        "예를 들어 카카오 함량이 70%라면 "
        "초콜릿의 카카오 성분 비율이 70%라는 뜻이에요."
    )

# ==================================================
# 3. 한글 번역 사전
# ==================================================

국가번역 = {
      "Panama": "파나마",
    "Belize": "벨리즈",
    "St. Vincent": "세인트빈센트",
    "St. Vincent and the Grenadines": "세인트빈센트 그레나딘",
    "Grenadines": "그레나딘",
    "Principe": "프린시페",
    "Sao Tome and Principe": "상투메 프린시페",
    "São Tomé": "상투메",
    "Côte d’Ivoire": "코트디부아르",
    "Cote d'Ivoire": "코트디부아르",
    "Ivory coast": "코트디부아르",
    "Congo, the": "콩고",
    "Democratic Republic of the Congo": "콩고민주공화국",
    "Republic of the Congo": "콩고공화국",
    "Czechia": "체코",
    "The Netherlands": "네덜란드",
    "Republic of Korea": "대한민국",
    "Korea, Republic of": "대한민국",
    "United States of America": "미국",
    "United States of America (U.S.A.)": "미국",
    "U.S.": "미국",
    "England": "잉글랜드",
    "Caribbean": "카리브해 지역",
    "Africa": "아프리카",
    "South America": "남아메리카",
    "Central America": "중앙아메리카",
    "Asia": "아시아",
    "Oceania": "오세아니아",
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
    if pd.isna(value):
        return "정보 없음"

    value = str(value).strip()

    if value in dictionary:
        return dictionary[value]

    for eng, kor in sorted(
        dictionary.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        value = value.replace(eng, kor)

    return value


# ==================================================
# 4. CSV 파일 불러오기
# ==================================================

@st.cache_data
def load_data():

    파일명 = "flavors_of_cacao.csv"

    # CSV 파일에 열 이름이 있는 경우
    df = pd.read_csv(
        파일명,
        encoding="utf-8-sig"
    )

    # 원본 열 이름을 소문자로 정리
    원본열이름 = [
        str(col).strip().lower()
        for col in df.columns
    ]

    # 원본 CSV의 영문 열 이름
    영문열이름 = {
        "company": "회사",
        "specific bean origin or bar name": "제품/원산지명",
        "ref": "참조번호",
        "review date": "평가연도",
        "cocoa percent": "카카오함량",
        "company location": "회사국가",
        "rating": "평점",
        "bean type": "콩종류",
        "broad bean origin": "콩원산지"
    }

    # 열 이름이 없는 CSV도 처리
    if "company" not in 원본열이름:

        df = pd.read_csv(
            파일명,
            header=None,
            encoding="utf-8-sig"
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
            "콩원산지"
        ]

    else:

        df.columns = [
            영문열이름.get(
                str(col).strip().lower(),
                str(col).strip()
            )
            for col in df.columns
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
        "flavors_of_cacao.csv 파일을 찾을 수 없어요. "
        "app.py와 같은 폴더에 CSV 파일을 넣어 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했어요: {e}")
    st.stop()


# ==================================================
# 5. 한글 표시용 데이터 만들기
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
# 6. 페이지 안에서 조건 선택
# ==================================================

st.header("🔎 원하는 조건 선택하기")

st.write(
    "아래에서 관심 있는 조건을 선택해 보세요. "
    "선택한 조건에 맞는 초콜릿만 분석할 수 있어요."
)

with st.container(border=True):

    st.subheader("1. 어떤 초콜릿을 살펴볼까요?")

    col1, col2, col3 = st.columns(3)

    연도목록 = sorted(
        df_kr["평가연도"].dropna().unique()
    )

    회사목록 = sorted(
        df_kr["회사"].dropna().unique()
    )

    원산지목록 = sorted(
        df_kr["콩원산지"].dropna().unique()
    )

    with col1:
        선택연도 = st.multiselect(
            "📅 평가 연도",
            연도목록,
            default=연도목록,
            help="초콜릿을 평가한 연도를 선택해요."
        )

    with col2:
        선택회사 = st.multiselect(
            "🏭 제조 회사",
            회사목록,
            default=회사목록,
            help="초콜릿을 만든 회사를 선택해요."
        )

    with col3:
        선택원산지 = st.multiselect(
            "🌍 카카오콩 원산지",
            원산지목록,
            default=원산지목록,
            help="카카오콩이 재배된 지역을 선택해요."
        )

    st.subheader("2. 어떤 초콜릿을 비교할까요?")

    col4, col5 = st.columns(2)

    with col4:
        함량범위 = st.slider(
            "🍫 카카오 함량",
            min_value=0,
            max_value=100,
            value=(0, 100),
            help="카카오 성분의 비율을 선택해요."
        )

    with col5:
        평점범위 = st.slider(
            "⭐ 평점",
            min_value=1.0,
            max_value=5.0,
            value=(1.0, 5.0),
            step=0.25,
            help="초콜릿 평가 점수의 범위를 선택해요."
        )

    st.caption(
        "처음에는 모든 초콜릿이 선택되어 있어요. "
        "특정 조건만 보고 싶다면 원하는 항목만 선택하면 돼요."
    )

    초기화 = st.button(
        "🔄 모든 조건 초기화",
        use_container_width=True
    )

    if 초기화:
        st.rerun()


# ==================================================
# 7. 선택한 조건 적용
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
# 8. 기본 통계
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

st.caption(
    "위 숫자는 방금 선택한 조건에 해당하는 초콜릿의 분석 결과예요."
)


# ==================================================
# 9. 분석 메뉴
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
        "점 하나가 초콜릿 한 종류를 뜻해요. "
        "점이 어디에 모여 있는지 살펴보세요."
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
        "상관관계는 두 항목이 함께 변하는 정도를 나타내요. "
        "카카오 함량이 평점을 직접 결정한다는 뜻은 아니에요."
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
            "더 많은 회사를 선택해 주세요."
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

    st.markdown("### 원산지별 평가 수")

    st.write(
        "어떤 원산지의 초콜릿이 데이터에 많이 포함되어 있는지 살펴봐요."
    )

    st.bar_chart(
        원산지별평점.head(15),
        x="카카오콩 원산지",
        y="평가 수",
        x_label="카카오콩 원산지",
        y_label="평가 수"
    )

    st.markdown("### 원산지별 평균 평점")

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
