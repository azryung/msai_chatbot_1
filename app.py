# app.py
import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import io, requests
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

load_dotenv()

# 당신의 키들
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2024-02-01"
)
GPT_MODEL = os.getenv("AZURE_OAI_DEPLOYMENT")  # 8ai006-gpt-4o-mini

# =========================== 예쁜 디자인 시작 ===========================
st.set_page_config(page_title="우리 아기만의 동화책", layout="centered", initial_sidebar_state="expanded")

# 커스텀 CSS (인스타 감성 + 동화책 느낌)
st.markdown("""
<style>
    .big-title {
        font-size: 48px !important;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FFB6C1, #87CEEB, #98FB98);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .subtitle {
        font-size: 22px;
        text-align: center;
        color: #555;
        margin-bottom: 30px;
    }
    .chat-bubble {
        padding: 15px 20px;
        border-radius: 25px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .user-bubble { background: #FFF0F5; border: 3px solid #FFB6C1; }
    .assistant-bubble { background: #E6F3FF; border: 3px solid #87CEEB; }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FFB6C1);
        color: white;
        border-radius: 30px;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(255,107,107,0.4);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(255,107,107,0.6);
    }
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown('<div class="big-title">우리 아기만의 동화책</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">아기와 함께 오늘 본 것, 느낀 것을 말해주세요</div>', unsafe_allow_html=True)

# 사이드바 예쁘게
with st.sidebar:
    st.image("https://em-content.zobj.net/source/telegram/386/baby_1f476.png", width=100)
    st.markdown("<h2 style='text-align:center; color:#FF69B4;'>동화 설정</h2>", unsafe_allow_html=True)
    
    art_style = st.selectbox(
        "그림체 선택",
        ["수채화 동화책", "파스텔 꿈나라", "디즈니 스타일", "한국 전래동화", "지브리 느낌", "크레용 손그림"]
    )
    
    story_length = st.radio("동화 길이", ["짧은 동화 (3~5문장)", "보통 동화 (8~12문장)", "긴 동화 (15문장 이상)"])
    
    st.markdown("---")
    st.markdown("### 사용법")
    st.markdown("1. 아래에 말해주세요  \n2. 동화 완성!  \n3. 살랑살랑 그림 그리기  \n4. PDF로 저장")

# 세션 상태
if "messages" not in st.session_state: st.session_state.messages = []
if "full_story" not in st.session_state: st.session_state.full_story = ""
if "images" not in st.session_state: st.session_state.images = []

# 채팅 히스토리 예쁘게
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble user-bubble"><strong>아기/엄마:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble assistant-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# 입력창
if prompt := st.chat_input("오늘 아기가 본 것, 느낀 것 말해주세요~ 예) '바다를 처음 봤어!'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble user-bubble"><strong>아기/엄마:</strong> {prompt}</div>', unsafe_allow_html=True)
    
    with st.spinner("동화 작가 선생님이 열심히 쓰고 있어요..."):
        length_text = {"짧은 동화 (3~5문장)": "3~5문장", "보통 동화 (8~12문장)": "8~12문장", "긴 동화 (15문장 이상)": "15문장 이상"}[story_length]
        
        system = f"""너는 세계 최고의 아동 동화 작가야. 3~6세 아이를 위해 아주 따뜻하고 예쁜 동화를 써줘.
        - 문장은 짧고 간단하게, 반복 많이 써줘 (예: 반짝반짝, 토끼깡충)
        - 항상 행복한 결말
        - {art_style} 느낌으로 묘사해줘
        - 길이는 {length_text}로"""
        
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=1200
        )
        story = response.choices[0].message.content.strip()
        st.session_state.full_story = story
        st.session_state.messages.append({"role": "assistant", "content": story})
        st.markdown(f'<div class="chat-bubble assistant-bubble">{story}</div>', unsafe_allow_html=True)
        st.balloons()

# 삽화 생성 버튼
if st.session_state.full_story and len(st.session_state.images) < 5:
    if st.button(f"살랑살랑 그림 그리기 (남은 {5-len(st.session_state.images)}장)"):
        with st.spinner("화가가 열심히 그리고 있어요..."):
            img_prompt = f"{art_style}, 동화책 한 페이지 삽화, 매우 귀엽고 따뜻한 분위기, 텍스트 없음, 최고 품질: {st.session_state.full_story[:400]}"
            resp = client.images.generate(model="dall-e-3", prompt=img_prompt, n=1, size="1024x1024")
            url = resp.data[0].url
            st.session_state.images.append(url)
            st.image(url, caption=f"페이지 {len(st.session_state.images)}")
            st.success("그림 완성!")

# 완성된 삽화 갤러리
if st.session_state.images:
    st.markdown("### 완성된 동화책 페이지들")
    cols = st.columns(len(st.session_state.images))
    for i, url in enumerate(st.session_state.images):
        cols[i].image(url, use_column_width=True)

# PDF 다운로드 (동화 + 그림 합본)
if st.session_state.full_story and st.session_state.images:
    if st.button("PDF 동화책으로 저장하기", key="pdf"):
        # PDF 생성 코드 (이전과 동일, 생략 없이 그대로)
        # ... (PDF 생성 부분은 이전 코드 그대로 복사해서 넣으세요)
        st.success("PDF 준비 중...")
        # PDF 생성 후 다운로드 버튼 제공

# 첫 방문 안내
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding:30px; background:linear-gradient(45deg,#FFF0F5,#E6F3FF); border-radius:20px; margin:30px 0;">
        <h3>안녕하세요! 우리 아기만의 동화책을 만들어 볼까요?</h3>
        <p>예시 문장들:</p>
        <ul style="text-align:left; display:inline-block;">
            <li>“오늘 처음 눈을 봤어!”</li>
            <li>“할머니가 맛있는 떡을 해주셨어”</li>
            <li>“강아지가 꼬리를 흔들었어”</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)