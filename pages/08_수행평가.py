import re
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# 1. 페이지 설정
# =========================================================

st.set_page_config(
    page_title="초콜릿 한눈에 알아보기",
    page_icon="🍫",
    layout="wide"
)

st.title("🍫 초콜릿, 한눈에 알아보기")
st.write(
    "초콜릿을 잘 몰라도 괜찮아요! "
    "카카오 함량, 평점, 제조 회사, 카카오콩 원산지를 "
    "그래프와 함께 쉽고 재미있게 살펴봐요."
)

st.info(
    "📌 이 앱은 초콜릿 평가 데이터를 분석합니다. "
    "필터를 선택하면 그래프와 분석 결과가 자동으로 바뀝니다."
)


# =========================================================
# 2. 용어 설명
# =========================================================

with st.expander("🍫 초콜릿 데이터, 먼저 알아보기", expanded=False):
    st.markdown("""
    **카카오 함량이란?**  
    초콜릿에 들어 있는 카카오 성분의 비율을 백분율(%)로 나타낸 값이에요.
    카카오 함량이 높을수록 쓴맛이 강하게 느껴질 수 있어요.

    **평점이란?**  
    초콜릿을 평가한 사람이 매긴 점수예요. 이 데이터에서는 1점부터 5점까지 사용해요.

    **카카오콩 원산지란?**  
    초콜릿을 만드는 데 사용한 카카오콩이 재배된 지역을 말해요.
    카카오콩은 재배 지역에 따라 향과 맛이 달라질 수 있어요.
    """)


# =========================================================
# 3. 한글 번역 사전
# =========================================================

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
    "Eucador": "에콰도르"
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
    """번역 사전에 있는 표현을 한글로 바꾸고, 없는 표현은 원본을 유지합니다."""
    if pd.isna(value):
        return "정보 없음"

    value = str(value).strip()

    if value in dictionary:
        return dictionary[value]

    # 원산지처럼 여러 지역이 들어 있는 값도 번역합니다.
    for eng, kor in sorted(
        dictionary.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        value = value.replace(eng, kor)

    return value


# =========================================================
# 4. 회사 이름 한글 발음
# =========================================================

# 자주 나오는 회사명은 읽는 법을 직접 지정합니다.
# 공식 발음이 아니라 한글로 읽기 위한 근사 표기입니다.
회사발음사전 = {
    "A. Morin": "에이 모랭",
    "A. Le Comptoir": "에이 르 콩투아르",
    "A. M. Chocolat": "에이엠 쇼콜라",
    "Amano": "아마노",
    "Bonnat": "보나",
    "Callebaut": "칼리바우트",
    "Dandelion": "댄덜라이언",
    "Domori": "도모리",
    "Guittard": "기타드",
    "Lindt": "린트",
    "Michel Cluizel": "미셸 클뤼젤",
    "Valrhona": "발로나",
    "Soma": "소마",
    "TCHO": "티초",
    "Theo": "테오",
    "Rogue": "로그",
    "Pralus": "프랄뤼",
    "Pacari": "파카리",
    "Marou": "마루",
    "Fruition": "프루이션",
    "Felchlin": "펠클린",
    "El Rey": "엘 레이",
    "Duffy's": "더피스",
    "Cacao Barry": "카카오 배리",
    "Baker's": "베이커스",
    "Artisan du Chocolat": "아티잔 뒤 쇼콜라",
    "Amedei": "아메데이",
    "Askinosie": "아스키노시",
    "Benoit Nihant": "브누아 니앙",
    "Blanxart": "블랑샤르",
    "Cacaosuyo": "카카오수요",
    "Chocovic": "초코빅",
    "Chocolat Madagascar": "쇼콜라 마다가스카르",
    "Chocolaterie Robert": "쇼콜라트리 로베르",
    "Coppeneur": "코페너",
    "Dick Taylor": "딕 테일러",
    "Dole": "돌",
    "Fresco": "프레스코",
    "Friis Holm": "프리스 홀름",
    "Georgia Ramon": "조지아 라몬",
    "Hummingbird": "허밍버드",
    "Jordis": "조디스",
    "Kah Kow": "카 카우",
    "Kakao": "카카오",
    "La Maison du Chocolat": "라 메종 뒤 쇼콜라",
    "Madre": "마드레",
    "Mast Brothers": "마스트 브라더스",
    "Mellow": "멜로",
    "Menakao": "메나카오",
    "Mindo": "민도",
    "Naive": "나이브",
    "Original Beans": "오리지널 빈스",
    "Pump Street": "펌프 스트리트",
    "Raaka": "라아카",
    "Ritual": "리추얼",
    "Ritter Sport": "리터 스포트",
    "Scharffen Berger": "샤펜 버거",
    "Solstice": "솔스티스",
    "Taza": "타자",
    "Theobroma": "테오브로마",
    "Willie's Cacao": "윌리스 카카오",
    "Zotter": "초터"
}


def 회사발음변환(회사명):
    """영문 회사명을 한글로 읽는 근사 표기로 변환합니다."""

    if pd.isna(회사명):
        return "정보 없음"

    회사명 = str(회사명).strip()

    if not 회사명:
        return "정보 없음"

    if 회사명 in 회사발음사전:
        return 회사발음사전[회사명]

    # 대소문자 차이만 있는 이름도 사전에서 찾습니다.
    발음사전_소문자 = {
        key.lower(): value
        for key, value in 회사발음사전.items()
    }

    if 회사명.lower() in 발음사전_소문자:
        return 발음사전_소문자[회사명.lower()]

    # 영문이 아닌 회사명은 원문 그대로 표시합니다.
    if not re.search(r"[A-Za-z]", 회사명):
        return 회사명

    # 사전에 없는 이름은 영문 철자를 기준으로 대략 변환합니다.
    # 실제 영어·프랑스어·스페인어 등의 발음을 정확히 분석하는 기능은 아닙니다.
    변환표 = [
        ("tion", "션"), ("sion", "션"),
        ("tch", "치"), ("ch", "치"), ("sh", "쉬"),
        ("ph", "프"), ("th", "스"), ("ck", "크"),
        ("qu", "퀴"), ("wh", "우"), ("wr", "르"),
        ("ng", "ㅇ"), ("oo", "우"), ("ee", "이"),
        ("ea", "이"), ("ai", "에이"), ("ay", "에이"),
        ("ou", "아우"), ("ow", "오"), ("oi", "오이"),
        ("oy", "오이"), ("er", "어"), ("ir", "어"),
        ("ur", "어"), ("ar", "아"), ("or", "오"),
        ("igh", "아이"),
        ("a", "아"), ("e", "에"), ("i", "이"),
        ("o", "오"), ("u", "우"), ("b", "브"),
        ("c", "크"), ("d", "드"), ("f", "프"),
        ("g", "그"), ("h", "흐"), ("j", "즈"),
        ("k", "크"), ("l", "르"), ("m", "므"),
        ("n", "느"), ("p", "프"), ("q", "크"),
        ("r", "르"), ("s", "스"), ("t", "트"),
        ("v", "브"), ("w", "우"), ("x", "엑스"),
        ("y", "이"), ("z", "즈")
    ]

    변환된이름 = 회사명.lower()

    for 영문, 한글 in 변환표:
        변환된이름 = 변환된이름.replace(영문, 한글)

    return re.sub(r"\s+", " ", 변환된이름).strip()


def 회사표시명(회사명):
    """영문 원본 이름 옆에 한글 발음을 표시합니다."""
    if pd.isna(회사명):
        return "정보 없음"

    회사명 = str(회사명).strip()
    발음 = 회사발음변환(회사명)

    return f"{회사명} ({발음})"


# =========================================================
# 5. CSV 파일 불러오기
# =========================================================

DATA_FILE = Path(__file__).parent / "수행평가.csv"


@st.cache_data
def load_data(file_path):
    """CSV 파일을 불러오고 분석에 필요한 자료형으로 변환합니다."""

    data = pd.read_csv(
        file_path,
        header=None,
        encoding="utf-8-sig"
    )

    if data.shape[1] != 9:
        raise ValueError(
            f"CSV 열 개수가 9개가 아닙니다. 현재 {data.shape[1]}개입니다."
        )

    data.columns = [
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

    # 공백만 있는 셀을 결측값으로 처리합니다.
    data = data.replace(r"^\s*$", pd.NA, regex=True)

    # 문자열 앞뒤 공백을 정리합니다.
    for col in [
        "회사",
        "제품/원산지명",
        "회사국가",
        "콩종류",
        "콩원산지"
    ]:
        data[col] = data[col].astype("string").str.strip()

    # 숫자 데이터 변환
    data["참조번호"] = pd.to_numeric(
        data["참조번호"],
        errors="coerce"
    )

    data["평가연도"] = pd.to_numeric(
        data["평가연도"],
        errors="coerce"
    )

    data["평점"] = pd.to_numeric(
        data["평점"],
        errors="coerce"
    )

    data["카카오함량"] = pd.to_numeric(
        data["카카오함량"]
        .astype("string")
        .str.replace("%", "", regex=False),
        errors="coerce"
    )

    # 분석에 필요한 값이 없는 행은 제외합니다.
    data = data.dropna(
        subset=["평가연도", "카카오함량", "평점"]
    )

    return data


try:
    df = load_data(str(DATA_FILE))

except FileNotFoundError:
    st.error(
        "📂 flavors_of_cacao.csv 파일을 찾을 수 없어요. "
        "app.py와 같은 폴더에 CSV 파일을 넣어 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"⚠️ 데이터를 불러오는 중 오류가 발생했어요: {e}")
    st.stop()


# =========================================================
# 6. 한글 표시용 데이터 만들기
# =========================================================

df_kr = df.copy()

df_kr["회사"] = df_kr["회사"].fillna("정보 없음")
df_kr["회사 표시명"] = df_kr["회사"].apply(회사표시명)

df_kr["제품/원산지명"] = (
    df_kr["제품/원산지명"].fillna("정보 없음")
)

df_kr["회사국가"] = df_kr["회사국가"].apply(
    lambda x: 번역하기(x, 국가번역)
)

df_kr["콩원산지"] = df_kr["콩원산지"].apply(
    lambda x: 번역하기(x, 국가번역)
)

df_kr["콩종류"] = df_kr["콩종류"].apply(
    lambda x: 번역하기(x, 콩종류번역)
)


# =========================================================
# 7. 화면에서 분석 조건 선택
# =========================================================

st.header("🔎 분석 조건 선택하기")
st.caption("아래 조건을 바꾸면 요약 정보와 그래프가 자동으로 바뀝니다.")

연도목록 = sorted(
    df_kr["평가연도"].dropna().astype(int).unique().tolist()
)

회사목록 = sorted(
    df_kr["회사 표시명"].dropna().unique().tolist()
)

원산지목록 = sorted(
    df_kr["콩원산지"].dropna().unique().tolist()
)

필터1, 필터2 = st.columns(2)

with 필터1:
    선택연도 = st.multiselect(
        "📅 평가 연도",
        options=연도목록,
        default=연도목록,
        help="분석할 평가 연도를 선택하세요."
    )

    선택회사 = st.multiselect(
        "🏭 제조 회사",
        options=회사목록,
        default=회사목록,
        help="영문 회사 이름 옆에 한글로 읽는 법을 표시합니다."
    )

with 필터2:
    선택원산지 = st.multiselect(
        "🌍 카카오콩 원산지",
        options=원산지목록,
        default=원산지목록
    )

    함량범위 = st.slider(
        "🍫 카카오 함량 범위(%)",
        min_value=0,
        max_value=100,
        value=(0, 100)
    )

평점범위 = st.slider(
    "⭐ 평점 범위",
    min_value=1.0,
    max_value=5.0,
    value=(1.0, 5.0),
    step=0.25
)


# =========================================================
# 8. 필터 적용
# =========================================================

filtered = df_kr[
    df_kr["평가연도"].isin(선택연도)
    & df_kr["회사 표시명"].isin(선택회사)
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
        "🔍 선택한 조건에 맞는 초콜릿이 없어요. "
        "필터 조건을 조금 넓혀 보세요."
    )
    st.stop()


# =========================================================
# 9. 데이터 요약
# =========================================================

st.divider()
st.header("📊 지금 선택한 초콜릿 살펴보기")

요약1, 요약2, 요약3, 요약4 = st.columns(4)

요약1.metric(
    "🍫 평가된 초콜릿",
    f"{len(filtered):,}개"
)

요약2.metric(
    "⭐ 평균 평점",
    f"{filtered['평점'].mean():.2f} / 5점"
)

요약3.metric(
    "🍫 평균 카카오 함량",
    f"{filtered['카카오함량'].mean():.1f}%"
)

요약4.metric(
    "🏆 가장 높은 평점",
    f"{filtered['평점'].max():.2f}점"
)

st.caption(
    "위 숫자는 선택한 조건에 해당하는 초콜릿만 분석한 결과예요."
)


# =========================================================
# 10. 메뉴 구성
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍫 카카오 함량",
    "⭐ 평점",
    "🏭 제조 회사",
    "🌍 원산지",
    "📋 전체 데이터"
])


# =========================================================
# 11. 카카오 함량 분석
# =========================================================

with tab1:
    st.subheader("🍫 카카오 함량이 높으면 평점도 높을까요?")

    st.write(
        "아래 그래프에서 점 하나는 초콜릿 한 종류를 뜻해요. "
        "점들이 어떻게 모여 있는지 살펴보세요."
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

    with st.expander("📖 그래프 읽는 방법"):
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

    st.markdown("### 📊 카카오 함량 구간별 평균 평점")

    구간데이터 = filtered.copy()

    구간데이터["카카오구간"] = pd.cut(
        구간데이터["카카오함량"],
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
        구간데이터.groupby(
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


# =========================================================
# 12. 평점 분석
# =========================================================

with tab2:
    st.subheader("⭐ 사람들은 초콜릿에 몇 점을 주었을까요?")

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

    st.success(
        f"현재 선택한 데이터에서 가장 많이 나온 평점은 "
        f"{가장많은평점}점이에요."
    )

    with st.expander("📖 평점 구간별 의미"):
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


# =========================================================
# 13. 제조 회사 분석
# =========================================================

with tab3:
    st.subheader("🏭 어떤 회사의 초콜릿이 높은 평가를 받았을까요?")

    st.write(
        "회사별 평균 평점을 비교해요. "
        "평가 수가 너무 적으면 결과가 달라질 수 있으므로 "
        "평가가 10개 이상인 회사만 비교해요."
    )

    회사별평점 = (
        filtered.groupby("회사 표시명")["평점"]
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
            "필터에서 더 많은 회사를 선택해 주세요."
        )

    else:
        st.markdown("### 🏆 평균 평점이 높은 회사")

        st.bar_chart(
            회사별평점.head(15),
            x="제조 회사",
            y="평균 평점",
            x_label="제조 회사 (영문 이름과 한글 발음)",
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


# =========================================================
# 14. 원산지 분석
# =========================================================

with tab4:
    st.subheader("🌍 카카오콩은 어느 나라에서 왔을까요?")

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

    st.markdown("### 📊 원산지별 평가 수")

    st.bar_chart(
        원산지별평점.head(15),
        x="카카오콩 원산지",
        y="평가 수",
        x_label="카카오콩 원산지",
        y_label="평가 수"
    )

    st.markdown("### ⭐ 원산지별 평균 평점")

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


# =========================================================
# 15. 전체 데이터 및 다운로드
# =========================================================

with tab5:
    st.subheader("📋 한글로 표시된 초콜릿 데이터")

    st.write(
        "현재 선택한 조건에 해당하는 초콜릿의 정보를 확인할 수 있어요. "
        "제조 회사 이름은 영문 원본과 한글 발음을 함께 표시합니다."
    )

    보여줄데이터 = filtered.rename(
        columns=열이름번역
    )

    # 분석용 회사 표시명도 표에 포함합니다.
    보여줄데이터 = 보여줄데이터.copy()
    보여줄데이터["회사 이름 (한글 발음)"] = filtered["회사 표시명"]

    st.dataframe(
        보여줄데이터,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### 📥 데이터 다운로드")

    st.write(
        "한글로 표시된 데이터를 CSV 파일로 저장할 수 있어요. "
        "다운로드한 파일은 엑셀에서도 열 수 있습니다."
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


# =========================================================
# 16. 마무리 설명
# =========================================================

st.divider()

st.subheader("💡 분석을 마치며")

st.write(
    "초콜릿의 평점은 카카오 함량뿐만 아니라 제조 회사, "
    "카카오콩의 종류와 원산지 등 여러 요소와 관련이 있을 수 있어요."
)

st.write(
    "그래프를 비교하면서 어떤 특징이 나타나는지 살펴보세요. "
    "데이터에서 발견한 관계가 반드시 원인과 결과를 의미하는 것은 아니에요."
)
