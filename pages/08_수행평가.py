import re
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="카카오 초콜릿 데이터 분석",
    page_icon="🍫",
    layout="wide"
)

st.title("🍫 카카오 초콜릿 데이터 분석")
st.caption("초콜릿 회사, 카카오 함량, 평점, 원산지를 분석합니다.")


# --------------------------------------------------
# 2. CSV 파일 불러오기
# --------------------------------------------------
DATA_FILE = Path(__file__).parent / "flavors_of_cacao.csv"

COLUMNS = [
    "회사",
    "세부 원산지",
    "참조 번호",
    "리뷰 연도",
    "카카오 함량",
    "회사 소재 국가",
    "평점",
    "카카오 종류",
    "원산지"
]

try:
    # 첨부된 CSV는 첫 번째 줄부터 데이터가 시작되는 형식입니다.
    df = pd.read_csv(DATA_FILE, header=None, encoding="utf-8-sig")

    if df.shape[1] != 9:
        st.error(
            f"CSV 열 개수가 9개가 아닙니다. 현재 {df.shape[1]}개입니다. "
            "파일 형식을 확인해 주세요."
        )
        st.stop()

    df.columns = COLUMNS

except FileNotFoundError:
    st.error(
        "flavors_of_cacao.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 CSV 파일을 넣어 주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------------------------
# 3. 데이터 정리
# --------------------------------------------------
df = df.copy()

text_columns = [
    "회사",
    "세부 원산지",
    "회사 소재 국가",
    "카카오 종류",
    "원산지"
]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()

df = df.replace(
    {
        "": pd.NA,
        "nan": pd.NA,
        "NaN": pd.NA,
        "\xa0": pd.NA
    }
)

df["회사"] = df["회사"].fillna("회사명 없음")

df["참조 번호"] = pd.to_numeric(df["참조 번호"], errors="coerce")
df["리뷰 연도"] = pd.to_numeric(df["리뷰 연도"], errors="coerce")
df["평점"] = pd.to_numeric(df["평점"], errors="coerce")

df["카카오 함량"] = (
    df["카카오 함량"]
    .astype("string")
    .str.replace("%", "", regex=False)
)

df["카카오 함량"] = pd.to_numeric(
    df["카카오 함량"],
    errors="coerce"
)


# --------------------------------------------------
# 4. 회사 이름의 한글 발음
# --------------------------------------------------
# 자주 등장하는 회사 이름은 발음을 직접 지정합니다.
# 표기는 공식 발음이 아니라 한글로 읽는 법의 근사치입니다.
COMPANY_PRONUNCIATIONS = {
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


def approximate_korean_pronunciation(name):
    """
    회사 이름을 한글로 읽는 근사 표기로 변환합니다.
    사전에 없는 이름은 영문 철자를 기준으로 대략 변환합니다.
    """

    name = str(name).strip()

    if not name:
        return ""

    # 사전에 등록된 회사 이름
    if name in COMPANY_PRONUNCIATIONS:
        return COMPANY_PRONUNCIATIONS[name]

    # 대소문자 차이를 무시한 검색
    pronunciation_lower = {
        key.lower(): value
        for key, value in COMPANY_PRONUNCIATIONS.items()
    }

    if name.lower() in pronunciation_lower:
        return pronunciation_lower[name.lower()]

    # 영문이 아닌 이름은 그대로 반환
    if not re.search(r"[A-Za-z]", name):
        return name

    # 간단한 철자 기반 근사 변환
    text = name.lower()

    replacements = [
        ("tion", "션"),
        ("sion", "션"),
        ("tch", "치"),
        ("ch", "치"),
        ("sh", "쉬"),
        ("ph", "프"),
        ("th", "스"),
        ("ck", "크"),
        ("qu", "퀴"),
        ("wh", "우"),
        ("wr", "르"),
        ("ng", "ㅇ"),
        ("oo", "우"),
        ("ee", "이"),
        ("ea", "이"),
        ("ai", "에이"),
        ("ay", "에이"),
        ("ou", "아우"),
        ("ow", "오"),
        ("oi", "오이"),
        ("oy", "오이"),
        ("er", "어"),
        ("ir", "어"),
        ("ur", "어"),
        ("ar", "아"),
        ("or", "오"),
        ("igh", "아이"),
        ("a", "아"),
        ("e", "에"),
        ("i", "이"),
        ("o", "오"),
        ("u", "우"),
        ("b", "브"),
        ("c", "크"),
        ("d", "드"),
        ("f", "프"),
        ("g", "그"),
        ("h", "흐"),
        ("j", "즈"),
        ("k", "크"),
        ("l", "르"),
        ("m", "므"),
        ("n", "느"),
        ("p", "프"),
        ("q", "크"),
        ("r", "르"),
        ("s", "스"),
        ("t", "트"),
        ("v", "브"),
        ("w", "우"),
        ("x", "엑스"),
        ("y", "이"),
        ("z", "즈")
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()
    return text if text else name


def company_display_name(name):
    """영문 회사명 옆에 한글 발음을 표시합니다."""

    if pd.isna(name):
        return "회사명 없음"

    name = str(name).strip()
    pronunciation = approximate_korean_pronunciation(name)

    return f"{name} ({pronunciation})"


df["회사 표시명"] = df["회사"].apply(company_display_name)


# --------------------------------------------------
# 5. 화면에서 분석 조건 선택
# --------------------------------------------------
st.subheader("🔎 분석 조건 선택")

all_years = sorted(
    df["리뷰 연도"].dropna().astype(int).unique().tolist()
)

all_companies = sorted(
    df["회사 표시명"].dropna().unique().tolist()
)

all_origins = sorted(
    df["원산지"].dropna().astype(str).unique().tolist()
)

col1, col2 = st.columns(2)

with col1:
    selected_years = st.multiselect(
        "리뷰 연도",
        options=all_years,
        default=all_years
    )

    selected_companies = st.multiselect(
        "회사 이름",
        options=all_companies,
        default=all_companies
    )

with col2:
    selected_origins = st.multiselect(
        "카카오 원산지",
        options=all_origins,
        default=all_origins
    )

    valid_cocoa = df["카카오 함량"].dropna()

    cocoa_min = int(valid_cocoa.min()) if not valid_cocoa.empty else 0
    cocoa_max = int(valid_cocoa.max()) if not valid_cocoa.empty else 100

    cocoa_range = st.slider(
        "카카오 함량 범위 (%)",
        min_value=cocoa_min,
        max_value=cocoa_max,
        value=(cocoa_min, cocoa_max)
    )

valid_ratings = df["평점"].dropna()

rating_min = float(valid_ratings.min()) if not valid_ratings.empty else 0.0
rating_max = float(valid_ratings.max()) if not valid_ratings.empty else 5.0

rating_range = st.slider(
    "평점 범위",
    min_value=rating_min,
    max_value=rating_max,
    value=(rating_min, rating_max),
    step=0.25
)


# --------------------------------------------------
# 6. 선택한 조건으로 데이터 필터링
# --------------------------------------------------
filtered = df.copy()

if selected_years:
    filtered = filtered[
        filtered["리뷰 연도"].isin(selected_years)
    ]
else:
    filtered = filtered.iloc[0:0]

if selected_companies:
    filtered = filtered[
        filtered["회사 표시명"].isin(selected_companies)
    ]
else:
    filtered = filtered.iloc[0:0]

if selected_origins:
    filtered = filtered[
        filtered["원산지"].astype(str).isin(selected_origins)
    ]
else:
    filtered = filtered.iloc[0:0]

filtered = filtered[
    filtered["카카오 함량"].between(
        cocoa_range[0],
        cocoa_range[1]
    )
]

filtered = filtered[
    filtered["평점"].between(
        rating_range[0],
        rating_range[1]
    )
]


# --------------------------------------------------
# 7. 데이터 요약
# --------------------------------------------------
st.divider()
st.subheader("📊 데이터 요약")

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "선택된 초콜릿 수",
    f"{len(filtered):,}개"
)

if not filtered.empty:
    metric2.metric(
        "평균 평점",
        f"{filtered['평점'].mean():.2f} / 5"
    )

    metric3.metric(
        "평균 카카오 함량",
        f"{filtered['카카오 함량'].mean():.1f}%"
    )
else:
    metric2.metric("평균 평점", "-")
    metric3.metric("평균 카카오 함량", "-")


# --------------------------------------------------
# 8. 그래프 및 데이터 표
# --------------------------------------------------
if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "카카오 함량",
        "평점 분석",
        "회사별 분석",
        "원산지 분석",
        "전체 데이터"
    ]
)


# 카카오 함량 그래프
with tab1:
    st.subheader("카카오 함량별 초콜릿 수")

    cocoa_counts = (
        filtered["카카오 함량"]
        .value_counts()
        .sort_index()
        .rename_axis("카카오 함량 (%)")
        .reset_index(name="초콜릿 수")
    )

    st.bar_chart(
        cocoa_counts,
        x="카카오 함량 (%)",
        y="초콜릿 수"
    )

    st.caption("카카오 함량이 같은 초콜릿이 몇 개 있는지 보여줍니다.")


# 평점 그래프
with tab2:
    st.subheader("평점별 초콜릿 수")

    rating_counts = (
        filtered["평점"]
        .value_counts()
        .sort_index()
        .rename_axis("평점")
        .reset_index(name="초콜릿 수")
    )

    st.bar_chart(
        rating_counts,
        x="평점",
        y="초콜릿 수"
    )

    st.caption("각 평점에 해당하는 초콜릿 수를 비교합니다.")


# 회사별 그래프
with tab3:
    st.subheader("회사별 평균 평점")

    company_ratings = (
        filtered.groupby("회사 표시명", as_index=False)
        .agg(
            평균_평점=("평점", "mean"),
            초콜릿_수=("평점", "count")
        )
        .sort_values("평균_평점", ascending=False)
    )

    st.bar_chart(
        company_ratings.head(20),
        x="회사 표시명",
        y="평균_평점"
    )

    st.caption("평균 평점이 높은 회사 중 상위 20개를 표시합니다.")

    st.dataframe(
        company_ratings.rename(
            columns={
                "회사 표시명": "회사 이름 (한글 발음)",
                "평균_평점": "평균 평점",
                "초콜릿_수": "초콜릿 수"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# 원산지 그래프
with tab4:
    st.subheader("원산지별 초콜릿 수")

    origin_counts = (
        filtered["원산지"]
        .fillna("정보 없음")
        .value_counts()
        .rename_axis("원산지")
        .reset_index(name="초콜릿 수")
    )

    st.bar_chart(
        origin_counts.head(20),
        x="원산지",
        y="초콜릿 수"
    )

    st.caption("데이터가 많은 원산지 상위 20개를 표시합니다.")


# 전체 데이터 표
with tab5:
    st.subheader("선택된 전체 데이터")

    display_df = filtered[
        [
            "회사 표시명",
            "세부 원산지",
            "리뷰 연도",
            "카카오 함량",
            "회사 소재 국가",
            "평점",
            "카카오 종류",
            "원산지"
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "회사 표시명": "회사 이름 (한글 발음)",
            "카카오 함량": "카카오 함량 (%)",
            "원산지": "카카오 원산지"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="선택한 데이터 CSV로 다운로드",
        data=display_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="filtered_flavors_of_cacao.csv",
        mime="text/csv"
    )
