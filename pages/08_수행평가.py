import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="초콜릿 데이터 분석",
    page_icon="🍫",
    layout="wide"
)

st.title("🍫 초콜릿 데이터 분석")
st.write(
    "판다스를 이용해 초콜릿의 카카오 함량, "
    "평점, 제조 회사, 원산지 등을 분석하는 앱입니다."
)

# ==========================================
# 2. 한글 번역 사전
# ==========================================

국가번역 = {
    "France": "프랑스",
    "U.S.A.": "미국",
    "U.K.": "영국",
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
    "Principe": "프린시페",
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
    "Amsterdam": "암스테르담",
    "Niacragua": "니카라과",
    "Nicaragua": "니카라과",
    "Eucador": "에콰도르",
    "Domincan Republic": "도미니카공화국",
    "Australia": "호주"
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
    "제품/원산지명": "제품명",
    "참조번호": "참조 번호",
    "평가연도": "평가 연도",
    "카카오함량": "카카오 함량(%)",
    "회사국가": "제조 회사 국가",
    "평점": "평점",
    "콩종류": "카카오콩 종류",
    "콩원산지": "카카오콩 원산지"
}

# ==========================================
# 3. CSV 파일 불러오기
# ==========================================

@st.cache_data
def load_data():
    df = pd.read_csv(
        "flavors_of_cacao.csv",
        header=None,
        encoding="utf-8"
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

    # 빈칸 및 공백 정리
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df = df.replace("\u00a0", pd.NA)

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

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 수행평가.csv를 넣어 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# ==========================================
# 4. 한글 번역 함수
# ==========================================

def translate_country(value):
    if pd.isna(value):
        return "정보 없음"

    value = str(value).strip()

    # 국가명 전체가 일치하면 번역
    if value in 국가번역:
        return 국가번역[value]

    # 여러 국가가 포함된 원산지 번역
    for eng, kor in sorted(
        국가번역.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        value = value.replace(eng, kor)

    # 원산지 구분 기호 정리
    value = value.replace(",", ", ")
    value = value.replace("  ", " ")

    return value


def translate_bean(value):
    if pd.isna(value):
        return "정보 없음"

    value = str(value).strip()

    for eng, kor in sorted(
        콩종류번역.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        value = value.replace(eng, kor)

    return value


# 한글 표시용 데이터 생성
df_kr = df.copy()

df_kr["회사국가"] = df_kr["회사국가"].apply(
    translate_country
)

df_kr["콩원산지"] = df_kr["콩원산지"].apply(
    translate_country
)

df_kr["콩종류"] = df_kr["콩종류"].apply(
    translate_bean
)

df_kr["제품/원산지명"] = (
    df_kr["제품/원산지명"].fillna("정보 없음")
)

df_kr["회사"] = df_kr["회사"].fillna("정보 없음")

# ==========================================
# 5. 사이드바
# ==========================================

st.sidebar.header("🔎 데이터 필터")

연도목록 = sorted(
    df_kr["평가연도"].dropna().unique()
)

선택연도 = st.sidebar.multiselect(
    "평가 연도",
    연도목록,
    default=연도목록
)

회사목록 = sorted(
    df_kr["회사"].dropna().unique()
)

선택회사 = st.sidebar.multiselect(
    "제조 회사",
    회사목록,
    default=회사목록
)

함량범위 = st.sidebar.slider(
    "카카오 함량 범위(%)",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

평점범위 = st.sidebar.slider(
    "평점 범위",
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0),
    step=0.25
)

# 필터 적용
filtered = df_kr[
    df_kr["평가연도"].isin(선택연도)
    & df_kr["회사"].isin(선택회사)
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
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# ==========================================
# 6. 기본 통계
# ==========================================

st.header("📊 데이터 기본 정보")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "전체 평가 수",
    f"{len(filtered):,}개"
)

col2.metric(
    "평균 평점",
    f"{filtered['평점'].mean():.2f}점"
)

col3.metric(
    "평균 카카오 함량",
    f"{filtered['카카오함량'].mean():.1f}%"
)

col4.metric(
    "평점 최고값",
    f"{filtered['평점'].max():.2f}점"
)

st.caption(
    "현재 선택한 필터에 해당하는 데이터의 통계입니다."
)

# ==========================================
# 7. 데이터 미리보기
# ==========================================

st.header("📋 한글로 번역된 데이터")

st.dataframe(
    filtered.rename(columns=열이름번역),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 8. 카카오 함량별 평점 분석
# ==========================================

st.header("🍫 카카오 함량과 평점의 관계")

상관계수 = filtered[
    ["카카오함량", "평점"]
].corr().iloc[0, 1]

st.metric(
    "카카오 함량과 평점의 상관계수",
    f"{상관계수:.3f}"
)

st.caption(
    "상관계수는 -1에서 1 사이의 값입니다. "
    "1에 가까우면 양의 관계, -1에 가까우면 음의 관계를 뜻합니다. "
    "0에 가까우면 선형적인 관계가 약합니다."
)

st.scatter_chart(
    filtered,
    x="카카오함량",
    y="평점",
    x_label="카카오 함량(%)",
    y_label="평점"
)

# 카카오 함량 구간 생성
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

st.subheader("카카오 함량 구간별 평균 평점")

st.bar_chart(
    함량별평점,
    x="카카오 함량 구간",
    y="평균 평점",
    x_label="카카오 함량 구간",
    y_label="평균 평점"
)

st.dataframe(
    함량별평점.round(3),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 9. 연도별 평점 분석
# ==========================================

st.header("📅 평가 연도별 평균 평점")

연도별평점 = (
    filtered.groupby("평가연도")["평점"]
    .mean()
    .reset_index()
    .sort_values("평가연도")
)

st.line_chart(
    연도별평점,
    x="평가연도",
    y="평점",
    x_label="평가 연도",
    y_label="평균 평점"
)

# ==========================================
# 10. 제조 회사별 분석
# ==========================================

st.header("🏭 제조 회사별 평가")

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

회사별평점 = 회사별평점.sort_values(
    "평균 평점",
    ascending=False
)

st.subheader("제조 회사별 평균 평점")

st.bar_chart(
    회사별평점.head(15),
    x="제조 회사",
    y="평균 평점",
    x_label="제조 회사",
    y_label="평균 평점"
)

st.dataframe(
    회사별평점.round(3),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 11. 원산지별 분석
# ==========================================

st.header("🌍 카카오콩 원산지별 평가")

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

st.subheader("평가 수가 많은 원산지")

st.bar_chart(
    원산지별평점.head(15),
    x="카카오콩 원산지",
    y="평가 수",
    x_label="카카오콩 원산지",
    y_label="평가 수"
)

st.subheader("원산지별 평균 평점")

st.bar_chart(
    원산지별평점.head(15),
    x="카카오콩 원산지",
    y="평균 평점",
    x_label="카카오콩 원산지",
    y_label="평균 평점"
)

# ==========================================
# 12. 한글 CSV 다운로드
# ==========================================

st.header("📥 데이터 다운로드")

# 열 이름을 한글로 변경
download_df = filtered.rename(columns=열이름번역)

# UTF-8 BOM을 사용하여 엑셀에서 한글이 깨지지 않게 저장
csv_data = download_df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="한글로 번역된 CSV 다운로드",
    data=csv_data,
    file_name="초콜릿_분석_한글.csv",
    mime="text/csv"
)

st.success(
    "분석이 완료되었습니다. "
    "왼쪽 필터를 변경하면 그래프와 통계가 자동으로 바뀝니다."
)
