import streamlit as st
from PIL import Image
import google.generativeai as genai
import time

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="관상가 아솔",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. [필수] 인앱 브라우저 차단 ---
st.components.v1.html("""
<script>
    var userAgent = navigator.userAgent.toLowerCase();
    var isInApp = userAgent.indexOf("kakao") > -1 || userAgent.indexOf("instagram") > -1 || userAgent.indexOf("line") > -1;
    
    if (isInApp) {
        document.body.innerHTML = `
            <div style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background-color: #fff; z-index: 9999; display: flex;
                flex-direction: column; justify-content: center; align-items: center;
                text-align: center; font-family: sans-serif; padding: 20px;">
                <h1 style="color: #d32f2f;">⛔️ 접속 불가</h1>
                <p style="font-size: 18px; line-height: 1.6;">
                    죄송하오. <b>카카오톡/인스타그램</b>에서는 카메라가 안 열리오.<br>
                    우측 상단 점 3개(...)를 눌러 <b>[다른 브라우저로 열기]</b>를 하시오.
                </p>
            </div>
        `;
    }
</script>
""", height=0)

# --- 3. 스타일 꾸미기 ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; margin-top: 10px; background-color: #7D5A5A; color: white; font-weight: bold; border-radius: 10px; padding: 12px;
    }
    div.row-widget.stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    .main-header { text-align: center; font-family: 'Helvetica', sans-serif; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. API 키 연결 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오.")

# --- 5. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

# --- 6. 화면 구성 ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.write("---")

input_method = st.radio(
    "사진 준비 방식을 선택하시오:",
    ("📸 직접 촬영", "📂 앨범 선택"),
    horizontal=True
)

if input_method == "📸 직접 촬영":
    camera_image = st.camera_input("촬영", label_visibility="collapsed")
    if camera_image: st.session_state.final_image = camera_image
elif input_method == "📂 앨범 선택":
    uploaded_file = st.file_uploader("업로드", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    if uploaded_file: st.session_state.final_image = uploaded_file

# --- 7. 분석 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="선택된 얼굴", use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기"):
        try:
            # 1. 진행바와 문구 표시 공간 만들기
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 2. [수정됨] 분석 단계 (시간을 1.2초로 늘림)
            analysis_steps = [
                "1단계: 이마의 넓이와 초년운 측정 중...",
                "2단계: 눈썹의 기세와 형제운 분석 중...",
                "3단계: 코의 높이와 재물운 계산 중...",
                "4단계: 입술의 모양과 말년운 확인 중...",
                "5단계: 얼굴의 전체적인 조화(오행) 분석 중..."
            ]
            
            for i, step in enumerate(analysis_steps):
                status_text.markdown(f"### 🔍 {step}")
                progress_bar.progress((i + 1) * 15) # 게이지 천천히 채우기
                time.sleep(1.2) # ⏱️ 0.7초 -> 1.2초로 늘려서 휙 지나가지 않게 함

            # 3. [수정됨] 실제 AI 호출 시 멘트 변경
            status_text.markdown("### ✍️ 아솔이 감정서를 작성하고 있소... (잠시만!)")
            progress_bar.progress(90)
            
            # 스피너로 마지막 기다림 지루함 덜기
            with st.spinner("천기를 글로 옮기는 중이니 조금만 참으시오..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """
                당신의 이름은 '아솔'입니다. 조선 팔도에서 가장 용한 전설적인 관상가입니다.
                이 사진의 인물을 보고 다음 내용을 바탕으로 관상을 아주 상세하고 재미있게 봐주세요.
                말투는 위엄 있으면서도 친근한 사극 톤("~하오", "~이오")을 사용하세요.
                
                [아솔의 감정서]
                1. 🎭 인상 총평 (초년, 중년, 말년)
                2. 💰 재물운 (곳간이 찰 상인가?)
                3. ❤️ 연애 및 애정운 (도화살 유무)
                4. 🍀 아솔의 특별 처방 (조언)
                
                재미있게 팩트 폭격을 섞어서 신통방통하게 말해주세요.
                """
                
                response = model.generate_content([prompt, Image.open(st.session_state.final_image)])
            
            # 4. 완료 처리
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # 5. 결과 출력
            st.write("---")
            st.subheader("📜 아솔의 관상 풀이")
            st.markdown(response.text)
            st.balloons() 

        except Exception as e:
            st.error(f"에러가 났소. (내용: {e})")