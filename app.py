# app.py - 우리 아기만의 완벽한 AI 동화책 (최종 에러 수정 버전)
import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import io
import requests
import tempfile
import azure.cognitiveservices.speech as speechsdk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import time

# .env 로드
load_dotenv()

# Azure OpenAI 설정
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OAI_KEY"),
    api_version="2024-02-01"
)
GPT_MODEL = os.getenv("AZURE_OAI_DEPLOYMENT", "8ai006-gpt-4o-mini")

# DALL·E 전용 클라이언트 (새로 추가!)
dalle_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_DALLE_ENDPOINT"),
    api_key=os.getenv("AZURE_DALLE_KEY"),
    api_version="2024-02-01"
)

# 페이지 설정 & 예쁜 디자인 (나눔고딕 느낌으로 변경: sans-serif 폰트 사용)
st.set_page_config(page_title="우리 아기만의 동화책", layout="centered")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    .big-title {font-size: 50px !important; font-weight: bold; text-align: center;
                background: linear-gradient(90deg, #FFB6C1, #87CEEB, #98FB98);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-family: 'Noto Sans KR', sans-serif; /* 나눔고딕 느낌의 무료 온라인 서체 */}
    .stButton>button {background: linear-gradient(45deg, #FF6B6B, #FFB6C1); color: white;
                      border-radius: 30px; height: 60px; font-size: 18px; font-weight: bold;
                      font-family: 'Noto Sans KR', sans-serif;}
    body {font-family: 'Noto Sans KR', sans-serif;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">우리 아기만의 동화책</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:20px; color:#555;'>아기 목소리로 말하면 바로 동화책이 만들어져요</p>", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.image("https://em-content.zobj.net/source/telegram/386/baby_1f476.png", width=100)
    st.markdown("### 동화 설정")
    art_style = st.selectbox("그림체", [
        "수채화 동화책", "파스텔 꿈나라", "디즈니 스타일", "한국 전래동화", "지브리 느낌", "크레용 손그림"
    ])
    story_length = st.radio("동화 길이", ["짧은 동화 (3~5문장)", "보통 동화 (8~12문장)", "긴 동화 (15문장 이상)"])
    
    st.markdown("### 낭독 목소리")
    voice_choice = st.selectbox("누가 읽어줄까?", [
        "ko-KR-SunHiNeural → 귀여운 여자아이 (최고 추천!)",
        "ko-KR-InJoonNeural → 씩씩한 남자아이",
        "ko-KR-HyunsuNeural → 따뜻한 할아버지",
        "ko-KR-SeoYunNeural → 부드러운 엄마",
        "ko-KR-SoonBokNeural → 귀여운 할머니"
    ], index=0)
    TTS_VOICE = voice_choice.split(" → ")[0]

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_story" not in st.session_state:
    st.session_state.full_story = ""
if "images" not in st.session_state:
    st.session_state.images = []

# ====== 1. 마이크 녹음 + 파일 업로드 ======
col1, col2 = st.columns(2)
with col1:
    st.markdown("**마이크로 바로 말하기**")
    audio_bytes = st.audio_input("마이크 누르고 말해주세요!", key="mic")
with col2:
    st.markdown("**또는 파일 업로드**")
    uploaded_file = st.file_uploader("", type=["wav", "mp3", "m4a", "webm"], key="file")

# ====== 2. 음성 → 텍스트 → 동화 생성 ======
if audio_bytes or uploaded_file:
    audio_data = audio_bytes if audio_bytes else uploaded_file.read()
    st.audio(audio_data, format='audio/wav')

    with st.spinner("아기 목소리 듣고 있어요..."):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(audio_data if isinstance(audio_data, bytes) else audio_data.getvalue())
        temp_file_path = temp_file.name
        temp_file.close()

        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        speech_config.speech_recognition_language = "ko-KR"
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                                audio_config=speechsdk.audio.AudioConfig(filename=temp_file_path))
        
        result = recognizer.recognize_once()

        # ===== 안전하게 임시파일 삭제 (윈도우 에러 방지) =====
        try:
            os.unlink(temp_file_path)
        except PermissionError:
            time.sleep(0.5)
            try:
                os.unlink(temp_file_path)
            except:
                pass
        except:
            pass
        # =================================================

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            prompt = result.text.strip()
            if not prompt.endswith(("!", "?", ".", "요", "다", "어", "야")):
                prompt += "."
            st.success(f"인식 성공! → {prompt}")

            # 동화 생성
            with st.chat_message("user"):
                st.markdown(f"**아기 목소리:** {prompt}")
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("동화 작가 선생님이 쓰고 있어요..."):
                    length_map = {"짧은 동화 (3~5문장)": "3~5문장", "보통 동화 (8~12문장)": "8~12문장", "긴 동화 (15문장 이상)": "15문장 이상"}
                    system = f"""너는 세계 최고의 아동 동화 작가야. 3~6세 아이를 위한 따뜻한 동화를 써줘.
                    - 문장은 아주 짧고 간단하게, 반복 많이 써줘
                    - 항상 행복한 결말
                    - {art_style} 느낌으로 묘사
                    - 길이는 {length_map[story_length]}로"""
                    
                    response = client.chat.completions.create(
                        model=GPT_MODEL,
                        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                        temperature=0.9, max_tokens=1200
                    )
                    story = response.choices[0].message.content.strip()
                    st.session_state.full_story = story
                    st.session_state.messages.append({"role": "assistant", "content": story})
                    st.markdown(story)
                    st.balloons()

        else:
            st.error("목소리를 잘 못 알아들었어요. 조금 더 크게 말해볼까요?")

# ====== 3. 삽화 생성 (최대 5장) ======
if st.session_state.full_story and len(st.session_state.images) < 5:
    if st.button(f"살랑살랑 그림 그리기 (남은 {5-len(st.session_state.images)}장)"):
        with st.spinner("화가가 열심히 그리고 있어요..."):
            img_prompt = f"{art_style}, 동화책 한 페이지 삽화, 매우 귀엽고 따뜻한 분위기, 텍스트 없음, 최고 품질: {st.session_state.full_story[:400]}"
            
            resp = dalle_client.images.generate(
                model=os.getenv("AZURE_DALLE_DEPLOYMENT"),
                prompt=img_prompt,
                n=1,
                size="1024x1024"
            )
            url = resp.data[0].url
            st.session_state.images.append(url)
            st.image(url, caption=f"페이지 {len(st.session_state.images)}")
            st.success("그림 완성!")

# 완성된 삽화 보기
if st.session_state.images:
    st.markdown("### 완성된 동화책 페이지들")
    cols = st.columns(len(st.session_state.images))
    for i, url in enumerate(st.session_state.images):
        cols[i].image(url, use_column_width=True)

# ====== 4. 아기 목소리로 낭독 + PDF ======
if st.session_state.full_story and st.session_state.images:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("아기 목소리로 읽어주기", use_container_width=True):
            with st.spinner("목소리 준비 중..."):
                speech_config = speechsdk.SpeechConfig(
                    subscription=os.getenv("AZURE_SPEECH_KEY"),
                    region=os.getenv("AZURE_SPEECH_REGION")
                )
                speech_config.speech_synthesis_voice_name = TTS_VOICE
                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_wav.name)
                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                
                text = st.session_state.full_story.replace("**", "").replace("#", "")
                result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    st.audio(temp_wav.name, format="audio/wav")
                    with open(temp_wav.name, "rb") as f:
                        st.download_button("음성 저장하기", f, "우리아기_동화_낭독.wav", "audio/wav")
                    
                    # ===== 안전하게 임시파일 삭제 (윈도우 에러 방지) =====
                    try:
                        os.unlink(temp_wav.name)
                    except PermissionError:
                        time.sleep(0.5)
                        try:
                            os.unlink(temp_wav.name)
                        except:
                            pass
                    except:
                        pass
                    # =================================================
                else:
                    st.error("낭독 실패")

    with c2:
        if st.button("PDF 동화책으로 저장하기", use_container_width=True):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 28)
            c.drawCentredString(width/2, height-100, "우리 아기만의 동화책")
            if st.session_state.images:
                img_data = requests.get(st.session_state.images[0]).content
                img = ImageReader(io.BytesIO(img_data))
                c.drawImage(img, 50, height-450, width=500, preserveAspectRatio=True)
            c.showPage()
            
            y = height - 100
            for line in st.session_state.full_story.split("\n"):
                if y < 150:
                    c.showPage()
                    y = height - 100
                c.setFont("Helvetica", 18)
                c.drawString(100, y, line.strip()[:80])
                y -= 40
            c.save()
            buffer.seek(0)
            st.download_button("PDF 다운로드!", buffer, "우리아기_동화책.pdf", "application/pdf")
            st.balloons()

# 첫 방문 안내
if not st.session_state.messages and not st.session_state.full_story:
    st.markdown("""
    <div style="text-align:center; padding:40px; background:linear-gradient(45deg,#FFF0F5,#E6F3FF); border-radius:20px;">
        <h3>마이크 버튼 누르고 아기 목소리로 말해보세요!</h3>
        <p>예: "오늘 눈 왔어!" "할머니 만났어!" "강아지가 꼬리 흔들었어!"</p>
    </div>
    """, unsafe_allow_html=True)