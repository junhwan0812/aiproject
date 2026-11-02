
import folium
from streamlit_folium import st_folium

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# --------------------------------
# 2. 관광지 데이터
# --------------------------------
PLACES = [
    {
        "rank": 1,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "desc": "화장품 쇼핑과 길거리 음식, 다양한 패션 매장을 즐길 수 있는 서울 대표 번화가입니다.",
        "tip": "저녁에 방문하면 다양한 길거리 음식을 즐길 수 있습니다."
    },
    {
        "rank": 2,
        "name": "남산서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "desc": "서울의 전경을 한눈에 감상할 수 있는 대표적인 전망 명소입니다.",
        "tip": "해 질 무렵 방문하면 아름다운 야경도 볼 수 있습니다."
    },
    {
        "rank": 3,
        "name": "코엑스·별마당도서관",
        "english": "COEX & Starfield Library",
        "lat": 37.5116,
        "lon": 127.0591,
        "category": "쇼핑·문화",
        "desc": "대형 쇼핑몰과 독특한 책장으로 유명한 별마당도서관이 있는 복합문화공간입니다.",
        "tip": "쇼핑과 문화 체험을 함께 즐겨 보세요."
    },
    {
        "rank": 4,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·전통문화",
        "desc": "조선 왕조의 법궁으로 아름다운 전통 건축과 한국의 역사를 만날 수 있습니다.",
        "tip": "한복 체험을 하며 궁궐을 둘러보는 것도 좋습니다."
    },
    {
        "rank": 5,
        "name": "홍대거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·공연",
        "desc": "거리 공연과 개성 있는 상점, 카페가 모여 있는 젊음의 거리입니다.",
        "tip": "주말에는 다양한 거리 공연을 구경해 보세요."
    },
    {
        "rank": 6,
        "name": "성수동",
        "english": "Seongsu-dong",
        "lat": 37.5445,
        "lon": 127.0560,
        "category": "카페·트렌드",
        "desc": "감각적인 카페와 편집숍, 팝업스토어로 유명한 트렌디한 지역입니다.",
        "tip": "골목마다 개성 있는 카페를 찾아보세요."
    },
    {
        "rank": 7,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·문화",
        "desc": "전통 한옥이 모여 있어 서울의 옛 모습을 느낄 수 있는 관광지입니다.",
        "tip": "실제 주민들이 거주하므로 조용히 관람해 주세요."
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·전시",
        "desc": "독특한 곡선형 건축물로 유명하며 다양한 전시와 행사가 열립니다.",
        "tip": "밤에는 아름다운 건축물의 야경을 감상해 보세요."
    },
    {
        "rank": 9,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·먹거리",
        "desc": "빈대떡과 김밥 등 다양한 한국 음식을 맛볼 수 있는 전통시장입니다.",
        "tip": "다양한 한국 전통 음식을 맛보세요."
    },
    {
        "rank": 10,
        "name": "강남거리",
        "english": "Gangnam",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "쇼핑·도시문화",
        "desc": "쇼핑과 맛집, 대형 상업시설이 모여 있는 서울의 대표적인 번화가입니다.",
        "tip": "강남역 주변과 지하상가를 함께 둘러보세요."
    }
]

# --------------------------------
# 3. 웹사이트 제목
# --------------------------------
st.title("🗺️ 서울 외국인 인기 관광지 TOP 10")
st.write(
    "서울을 방문하는 외국인 관광객을 위한 "
    "서울의 대표 관광지 10곳을 소개합니다! 🇰🇷"
)

st.info(
    "외국인 방문객 통계와 서울의 대표 관광지를 참고한 "
    "종합 추천 목록입니다. 공식 단일 순위는 아닙니다."
)

# --------------------------------
# 4. 관광지 종류 선택
# --------------------------------
categories = ["전체"] + sorted(
    set(place["category"] for place in PLACES)
)

selected_category = st.selectbox(
    "🔎 관광지 종류를 선택하세요",
    categories
)

if selected_category == "전체":
    visible_places = PLACES
else:
    visible_places = [
        place for place in PLACES
        if place["category"] == selected_category
    ]

# --------------------------------
# 5. 서울 지도 만들기
# --------------------------------
st.subheader("📍 서울 주요 관광지 지도")

seoul_map = folium.Map(
    location=[37.555, 126.985],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

# 관광지 마커 추가
for place in visible_places:

    popup_content = f"""
    <div style="width:230px;">
        <h3>{place['rank']}. {place['name']}</h3>
        <b>{place['english']}</b>
        <p>{place['desc']}</p>
        <p>분류: {place['category']}</p>
    </div>
    """

    folium.Marker(
        location=[
            place["lat"],
            place["lon"]
        ],

        tooltip=f"{place['rank']}. {place['name']}",

        popup=folium.Popup(
            popup_content,
            max_width=280
        ),

        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#e53935;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                text-align:center;
                line-height:26px;
                font-weight:bold;
                box-shadow:0 1px 5px #777;">
                {place['rank']}
            </div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    ).add_to(seoul_map)

# 지도 화면 출력
st_folium(
    seoul_map,
    width=None,
    height=580,
    returned_objects=[]
)

# --------------------------------
# 6. 관광지 설명
# --------------------------------
st.divider()

st.subheader("✨ 서울 관광지 TOP 10 소개")

st.write(
    "관광지를 선택해 간단한 설명과 여행 팁을 확인해 보세요!"
)

# 두 개씩 나누어 표시
for start in range(0, len(visible_places), 2):

    columns = st.columns(2)

    for column, place in zip(
        columns,
        visible_places[start:start + 2]
    ):

        with column:

            with st.container(border=True):

                st.markdown(
                    f"### {place['rank']}. {place['name']}"
                )

                st.caption(
                    f"{place['english']} · {place['category']}"
                )

                st.write(place["desc"])

                st.info(
                    f"💡 여행 팁: {place['tip']}"
                )

                google_maps_url = (
                    "https://www.google.com/maps/search/"
                    f"?api=1&query={place['lat']},{place['lon']}"
                )

                st.link_button(
                    "📍 Google 지도에서 위치 보기",
                    google_maps_url
                )

# --------------------------------
# 7. 하단 안내
# --------------------------------
st.divider()

st.markdown(
    """
    ### 🇰🇷 즐거운 서울 여행 되세요!

    서울의 다양한 문화와 음식, 역사와 현대적인
    매력을 경험해 보세요.

    자료 참고:
    - [Visit Seoul 공식 관광정보](https://english.visitseoul.net/)
    - [서울시 외국인 관광객 분석](https://english.seoul.go.kr/)
    """
)
