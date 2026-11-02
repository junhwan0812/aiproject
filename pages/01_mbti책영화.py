
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="MBTI 책 & 영화 추천 🎬",
    page_icon="📚",
    layout="centered"
)

# MBTI별 추천 데이터
recommendations = {
    "NT": {
        "books": [
            ("어스시의 마법사", "어슐러 K. 르 귄",
             "마법과 지혜, 성장에 관한 깊이 있는 판타지!"),
            ("황금나침반", "필립 풀먼",
             "상상력 넘치는 세계와 흥미진진한 모험!")
        ],
        "movies": [
            ("던전 앤 드래곤: 도적들의 명예", 2023,
             "개성 넘치는 모험가들의 유쾌한 판타지 모험!"),
            ("스즈메의 문단속", 2022,
             "신비로운 문과 재난을 둘러싼 아름다운 애니메이션!")
        ]
    },

    "NF": {
        "books": [
            ("해리 포터와 마법사의 돌", "J.K. 롤링",
             "마법 학교에서 펼쳐지는 우정과 성장 이야기!"),
            ("모모", "미하엘 엔데",
             "시간의 소중함과 삶의 의미를 생각하게 하는 판타지!")
        ],
        "movies": [
            ("말레피센트", 2014,
             "잠자는 숲속의 공주를 새로운 시선으로 바라본 이야기!"),
            ("바다의 노래", 2014,
             "전설 속 존재들과 가족의 사랑을 그린 감성 애니메이션!")
        ]
    },

    "SJ": {
        "books": [
            ("나니아 연대기: 사자와 마녀와 옷장",
             "C.S. 루이스",
             "신비로운 나라 나니아에서 펼쳐지는 모험!"),
            ("호빗", "J.R.R. 톨킨",
             "평범한 호빗이 떠나는 특별한 모험!")
        ],
        "movies": [
            ("호빗: 뜻밖의 여정", 2012,
             "드넓은 중간계에서 펼쳐지는 대모험!"),
            ("드래곤 길들이기", 2010,
             "용과 소년의 우정과 성장을 그린 애니메이션!")
        ]
    },

    "SP": {
        "books": [
            ("퍼시 잭슨과 번개 도둑", "릭 라이어던",
             "그리스 신화와 현대 세계가 만난 신나는 모험!"),
            ("시간의 주름", "매들렌 렝글",
             "시간과 공간을 넘나드는 신비로운 여행!")
        ],
        "movies": [
            ("신비한 동물사전", 2016,
             "마법 생물들이 가득한 환상적인 세계!"),
            ("늑대아이", 2012,
             "특별한 가족의 사랑과 성장을 그린 애니메이션!")
        ]
    }
}

# MBTI 유형
mbti_types = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

# MBTI별 추천 그룹
# NT: 분석적 성향
# NF: 이상적 성향
# SJ: 안정적 성향
# SP: 자유로운 성향
group_names = {
    "NT": "🧠 논리적인 탐험가",
    "NF": "💖 감성적인 이야기꾼",
    "SJ": "🛡️ 든든한 모험가",
    "SP": "⚡ 자유로운 도전자"
}

# 화면 디자인
st.title("📚 MBTI별 책 & 영화 추천 🎬")

st.subheader("나에게 어울리는 판타지 세계는? ✨")

st.write(
    "나의 MBTI를 선택하면 성향에 어울리는 "
    "책과 영화를 추천해 줄게!"
)

st.info("💡 MBTI 추천은 재미를 위한 콘텐츠야!")

# MBTI 선택
selected_mbti = st.selectbox(
    "🧩 나의 MBTI를 선택해 줘!",
    mbti_types,
    index=None,
    placeholder="MBTI를 선택해 주세요."
)

# 추천 버튼
if st.button("✨ 추천받기!", use_container_width=True):

    if selected_mbti is None:
        st.warning("먼저 MBTI를 선택해 줘! 😊")

    else:
        # MBTI 앞의 두 글자로 추천 그룹 구분
        group = selected_mbti[2:4]

        # NT, NF, SJ, SP 그룹으로 변환
        if group == "TJ" or group == "TP":
            category = "NT"
        elif group == "FJ" or group == "FP":
            category = "NF"
        else:
            category = "SJ" if selected_mbti[0] == "I" else "SP"

        # ISTP, ISFP, ESTP, ESFP는 SP 그룹
        if selected_mbti[1] == "S" and selected_mbti[2] in ["T", "F"]:
            category = "SP" if selected_mbti[0] == "E" else "SJ"

        # 일부 유형 보정
        if selected_mbti in ["ISTP", "ISFP"]:
            category = "SP"

        data = recommendations[category]

        st.divider()

        st.success(
            f"🎉 {selected_mbti} 유형의 추천 결과!"
        )

        st.header(group_names[category])

        st.write(
            "너의 성향에 어울리는 판타지 작품을 준비했어!"
        )

        # 책 추천
        st.header("📚 너에게 추천하는 판타지 책 2권")

        for i, book in enumerate(data["books"], 1):
            with st.container(border=True):
                st.subheader(f"📖 {i}. {book[0]}")
                st.write(f"✍️ 작가: {book[1]}")
                st.write(f"💬 {book[2]}")

        # 영화 추천
        st.header("🎬 너에게 추천하는 영화 2편")

        for i, movie in enumerate(data["movies"], 1):
            with st.container(border=True):
                st.subheader(f"🍿 {i}. {movie[0]}")
                st.write(f"📅 개봉 연도: {movie[1]}년")
                st.write(f"💬 {movie[2]}")

        st.divider()

        st.balloons()

        st.success(
            "오늘의 추천은 여기까지! "
            "마음에 드는 작품을 골라 즐겨 봐! 💕"
        )

# 하단 문구
st.divider()

st.caption(
    "📚 MBTI Fantasy Recommendation | "
    "나만의 판타지 세계를 찾아보자! ✨"
)

