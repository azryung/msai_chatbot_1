# wine_data.py (업그레이드 버전)

def get_wine_database():
    return [
        {
            "name": "빌라 엠 (Villa M)",
            "type": "화이트 스파클링",
            "price": 25000,
            "description": "달콤하고 가벼운 스파클링 와인. 술을 못 하는 사람, 디저트 와인, 달달한 맛"
        },
        {
            "name": "1865 까베르네 소비뇽",
            "type": "레드",
            "price": 45000,
            "description": "묵직한 바디감, 드라이한 맛, 고기나 스테이크와 어울림, 선물용"
        },
        {
            "name": "몬테스 알파 샤도네이",
            "type": "화이트",
            "price": 38000,
            "description": "바닐라 향, 드라이하지만 부드러움, 크림 파스타나 해산물"
        }
        # 여기에 나중에 와인을 더 추가하면 됩니다.
    ]

def search_wine_info(user_text):
    wines = get_wine_database()
    found_items = []
    
    # [업그레이드] 이제 이름뿐만 아니라 '설명'이나 '타입'도 검사합니다.
    keywords = user_text.split() # 사용자의 말을 띄어쓰기 단위로 쪼갭니다.
    
    for wine in wines:
        # 1. 이름으로 찾기 (기존 기능)
        if wine["name"] in user_text:
            found_items.append(wine)
            continue # 찾았으면 다음 와인으로 넘어감

        # 2. 키워드로 찾기 (새로운 기능)
        # 예: 사용자가 "달달한 거"라고 하면, 설명(description)에 "달달"이 있는지 확인
        for word in keywords:
            if len(word) >= 2: # "술", "맛" 같은 너무 짧은 단어는 제외
                if word in wine["description"] or word in wine["type"]:
                    found_items.append(wine)
                    break # 하나라도 키워드가 맞으면 목록에 추가

    # 검색 결과를 예쁘게 포장해서 돌려줍니다.
    if not found_items:
        return ""
        
    result_text = ""
    for item in found_items:
        result_text += f"\n- 이름: {item['name']}\n- 타입: {item['type']}\n- 가격: {item['price']}원\n- 특징: {item['description']}\n"
    
    return result_text