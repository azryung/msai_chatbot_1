# wine_data.py (데이터 확장 버전)

def get_wine_database():
    return [
        {
            "name": "빌라 엠 (Villa M)",
            "type": "화이트 스파클링",
            "price": 25000,
            "description": "달콤하고 가벼운 스파클링 와인. 술을 못 하는 사람, 디저트 와인, 달달한 맛, 여자친구 선물"
        },
        {
            "name": "1865 까베르네 소비뇽",
            "type": "레드",
            "price": 45000,
            "description": "국민 와인, 묵직한 바디감, 드라이한 맛, 골프 선물, 스테이크나 고기랑 잘 어울림"
        },
        {
            "name": "몬테스 알파 샤도네이",
            "type": "화이트",
            "price": 38000,
            "description": "바닐라 향, 드라이하지만 부드러움, 크림 파스타나 해산물, 연어랑 추천"
        },
        {
            "name": "모스카토 다스티 (3대장)",
            "type": "화이트 스파클링",
            "price": 30000,
            "description": "청포도 향이 터지는 달달한 와인. 케이크나 과일이랑 먹기 좋음. 파티용"
        },
        {
            "name": "캔달 잭슨 빈트너스 리저브",
            "type": "화이트",
            "price": 55000,
            "description": "오바마가 사랑한 와인. 버터 같은 풍미, 오크 향, 랍스터나 대게랑 먹으면 환상적"
        },
        {
            "name": "디아블로 까베르네 소비뇽",
            "type": "레드",
            "price": 12900,
            "description": "가성비 편의점 와인. 1초에 1병씩 팔림. 데일리 와인, 삼겹살이나 피자랑 막 먹기 좋음"
        },
        {
            "name": "클라우디 베이 소비뇽 블랑",
            "type": "화이트",
            "price": 48000,
            "description": "뉴질랜드 쇼블의 교과서. 상큼한 풀내음과 라임향. 회, 초밥, 샐러드랑 최고"
        },
        {
            "name": "몰리두커 더 복서",
            "type": "레드",
            "price": 49000,
            "description": "호주 쉬라즈. 알콜 도수가 높고 잼처럼 진득한 과일맛. 초콜릿 향. 진한 거 좋아하는 사람 추천"
        },
        {
            "name": "파이퍼 하이직 뀌베 브뤼",
            "type": "샴페인",
            "price": 65000,
            "description": "마릴린 먼로가 아침마다 마신 샴페인. 빵 굽는 냄새, 버블이 섬세함. 기념일이나 축하할 때 추천"
        },
        {
            "name": "콥케 파인 루비 포트",
            "type": "주정강화(포트)",
            "price": 28000,
            "description": "도수가 19.5도로 높고 엄청 달달함. 자기 전에 한 잔씩 마시는 와인. 초콜릿이나 치즈랑 찰떡"
        }
    ]

def search_wine_info(user_text):
    wines = get_wine_database()
    found_items = []
    
    # 띄어쓰기 기준으로 단어를 쪼갭니다 (예: "달달한 레드 추천" -> ["달달한", "레드", "추천"])
    keywords = user_text.split()
    
    for wine in wines:
        # 1. 이름이 포함되어 있으면 무조건 추가
        if wine["name"] in user_text:
            found_items.append(wine)
            continue

        # 2. 설명(description)이나 타입(type)에 키워드가 있는지 확인
        for word in keywords:
            # "추천", "좀", "있는" 같은 의미 없는 단어는 무시 (2글자 이상만 검색)
            if len(word) >= 2 and word not in ["추천", "와인", "있는", "주세요"]:
                if word in wine["description"] or word in wine["type"]:
                    found_items.append(wine)
                    break 

    if not found_items:
        return ""
        
    result_text = ""
    for item in found_items:
        result_text += f"\n- 이름: {item['name']}\n- 타입: {item['type']}\n- 가격: {item['price']}원\n- 특징: {item['description']}\n"
    
    return result_text