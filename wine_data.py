# wine_data.py
# 여기가 우리의 "가짜 데이터베이스"입니다.

def get_wine_database():
    return [
        {
            "name": "빌라 엠 (Villa M)",
            "type": "화이트/스파클링",
            "price": 25000,
            "description": "달콤하고 가벼운 스파클링 와인. 술을 못 하는 사람에게 추천."
        },
        {
            "name": "1865 까베르네 소비뇽",
            "type": "레드",
            "price": 45000,
            "description": "한국에서 가장 유명한 칠레 와인. 골프 선물용으로 인기. 묵직한 바디감."
        },
        {
            "name": "몬테스 알파 샤도네이",
            "type": "화이트",
            "price": 38000,
            "description": "바닐라 향이 나는 칠레 화이트 와인. 해산물보다는 크림 파스타와 어울림."
        }
    ]

# 이게 아까 질문하신 "입력 처리 로직"의 핵심입니다.
# 사용자가 말한 문장에 우리 와인 이름이 있는지 찾아보는 함수입니다.
def search_wine_info(user_text):
    wines = get_wine_database()
    found_info = ""
    
    for wine in wines:
        # 사용자가 입력한 말에 와인 이름이 들어있다면?
        if wine["name"] in user_text or wine["name"].split("(")[0].strip() in user_text:
            found_info += f"\n- 이름: {wine['name']}\n- 가격: {wine['price']}원\n- 특징: {wine['description']}\n"
            
    return found_info