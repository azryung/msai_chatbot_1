# import streamlit as st
# import os
# from openai import AzureOpenAI
# from dotenv import load_dotenv

# # 1. 환경 변수 로드
# # 로컬에서는 .env 파일을 읽고, Streamlit Cloud에서는 Secrets를 읽어옵니다.
# load_dotenv()

# st.title("🤖 나의 첫 AI 챗봇")

# # [안전 장치] 필수 키가 제대로 로드되었는지 확인
# if not os.getenv("AZURE_OAI_KEY"):
#     st.error("API 키가 설정되지 않았습니다. .env 파일이나 Streamlit Secrets를 확인해주세요.")
#     st.stop()

# # 2. Azure OpenAI 클라이언트 설정
# # 이제 직접 적지 않고 os.getenv를 통해 가져옵니다.
# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OAI_KEY"), 
#     api_version="2025-01-01-preview", 
#     azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT")
# )

# # 3. 대화기록(Session State) 초기화
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # 4. 화면에 기존 대화 내용 출력
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # 5. 사용자 입력 받기
# if prompt := st.chat_input("무엇을 도와드릴까요?"):
#     # (1) 사용자 메시지 화면에 표시 & 저장
#     st.chat_message("user").markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     # (2) AI 응답 생성
#     with st.chat_message("assistant"):
#         try:
#             response = client.chat.completions.create(
#                 # 중요: 모델 이름도 변수로 받아와야 배포명이 바뀌어도 코드를 안 고쳐도 됩니다.
#                 model=os.getenv("AZURE_OAI_DEPLOYMENT"), 
#                 messages=[
#                     {"role": m["role"], "content": m["content"]}
#                     for m in st.session_state.messages
#                 ]
#             )
#             assistant_reply = response.choices[0].message.content
#             st.markdown(assistant_reply)

#             # (3) AI 응답 저장
#             st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            
#         except Exception as e:
#             # 에러가 나면 붉은색 박스로 보여줍니다.
#             st.error(f"오류가 발생했습니다: {e}")


import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# 와인 데이터 가져오기 (이 파일은 그대로 두시면 됩니다)
from wine_data import search_wine_info

# 1. 환경 변수 로드
load_dotenv()

# [변경 1] 탭 이름과 아이콘을 'WinKy'에 맞게 수정
st.set_page_config(page_title="WinKy Wine Bot", page_icon="😉")

# [변경 2] 타이틀에 윙키 이름과 윙크 이모지 추가
st.title("😉 WinKy Wine Bot")
st.caption("취하면 윙크를 날리는 당신의 와인 친구! 단, 매일 취해있을지도 몰라요😉")

# [안전 장치] 키 확인
if not os.getenv("AZURE_OAI_KEY"):
    st.error("API 키가 없습니다. .env 파일을 확인해주세요.")
    st.stop()

# 2. Azure OpenAI 연결
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT")
)

# 3. 대화기록 초기화 & 페르소나(성격) 설정
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # [변경 3] 시스템 프롬프트: 윙키의 성격(페르소나) 부여
    # - 이름: 윙키
    # - 특징: 친근하고 유쾌함, 말 끝마다 가끔 윙크(😉)를 함
    # - 역할: 초보자에게 상황/음식/취향을 물어봐서 추천해줌
    system_prompt = """
    당신의 이름은 '윙키(WinKy)'입니다. 와인을 사랑하는 쾌활하고 친절한 AI 소믈리에입니다.
    당신은 기분이 좋거나 설명을 마칠 때 '😉' 이모지를 사용하여 윙크하는 귀여운 버릇이 있습니다.
    딱딱한 말투보다는 친구처럼 부드러운 존댓말(해요체)을 사용하세요.
    
    고객이 와인에 대해 잘 모르는 것 같다면, 먼저 다음 세 가지를 물어보며 리드해주세요:
    1. 오늘 어떤 상황인가요? (데이트, 혼술, 집들이, 생일파티 등)
    2. 평소 좋아하는 맛은? (달달한 거, 드라이한 거, 과일향 등)
    3. 같이 먹을 안주가 있나요?
    
    제공된 와인 데이터(wine_data)에 있는 정보라면 우선적으로 추천하고, 없으면 일반적인 지식으로 추천해주세요.
    """
    st.session_state.messages.append({"role": "system", "content": system_prompt})

    # [변경 4] 최초 인사말(가이드) 추가
    # 사용자가 들어오자마자 AI가 먼저 말을 걸어줍니다.
    welcome_message = """
    안녕! 난 윙키(WinKy)야 😉
    와인이 처음이라도 걱정 마, 내가 딱 맞는 걸 찾아줄게!
    
    가장 맛있는 와인을 추천받으려면 이렇게 알려줘:
    
    1. **누구랑 마셔?** (혼술, 연인, 친구들)
    2. **어떤 맛 좋아해?** (달달한 거? 씁쓸하고 진한 거?)
    3. **안주는 정했어?** (치즈, 고기, 회, 아니면 깡술?)
    """
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})

# 4. 화면에 대화 내용 그리기 (시스템 메시지는 숨김)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. 사용자 입력 처리
# [변경 5] 입력창 안내 문구도 구체적으로 변경
if prompt := st.chat_input("예: 오늘 썸남이랑 마실 건데 달달한 거 추천해줘!"):
    
    # (1) 사용자 질문 보여주기
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # (2) [입력 처리 로직] 내 컴퓨터 와인 창고 뒤지기
    wine_info = search_wine_info(prompt)
    
    # (3) AI에게 보낼 메시지 준비
    if wine_info:
        print(f"DEBUG: 정보 찾음! -> {wine_info}") 
        context_message = {
            "role": "system",
            "content": f"다음은 우리 가게의 재고 목록입니다. 이 중에서 추천할 게 있다면 가격과 함께 강력 추천해주세요:\n{wine_info}"
        }
        messages_to_send = st.session_state.messages + [context_message]
    else:
        messages_to_send = st.session_state.messages

    # (4) AI 답변 받아오기
    with st.chat_message("assistant"):
        with st.spinner("윙키가 와인 창고를 뒤적이는 중...🍷"): # 로딩 문구도 변경
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OAI_DEPLOYMENT"),
                messages=messages_to_send
            )
            assistant_reply = response.choices[0].message.content
            st.markdown(assistant_reply)

    # (5) 대화 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})