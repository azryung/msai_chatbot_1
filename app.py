import streamlit as st
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# 1. 환경 변수 로드
# 로컬에서는 .env 파일을 읽고, Streamlit Cloud에서는 Secrets를 읽어옵니다.
load_dotenv()

st.title("🤖 나의 첫 AI 챗봇")

# [안전 장치] 필수 키가 제대로 로드되었는지 확인
if not os.getenv("AZURE_OAI_KEY"):
    st.error("API 키가 설정되지 않았습니다. .env 파일이나 Streamlit Secrets를 확인해주세요.")
    st.stop()

# 2. Azure OpenAI 클라이언트 설정
# 이제 직접 적지 않고 os.getenv를 통해 가져옵니다.
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OAI_KEY"), 
    api_version="2025-01-01-preview", 
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT")
)

# 3. 대화기록(Session State) 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 화면에 기존 대화 내용 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # (1) 사용자 메시지 화면에 표시 & 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # (2) AI 응답 생성
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                # 중요: 모델 이름도 변수로 받아와야 배포명이 바뀌어도 코드를 안 고쳐도 됩니다.
                model=os.getenv("AZURE_OAI_DEPLOYMENT"), 
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            assistant_reply = response.choices[0].message.content
            st.markdown(assistant_reply)

            # (3) AI 응답 저장
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            
        except Exception as e:
            # 에러가 나면 붉은색 박스로 보여줍니다.
            st.error(f"오류가 발생했습니다: {e}")