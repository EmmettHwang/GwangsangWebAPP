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
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #fff; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; font-family: sans-serif; padding: 20px;">
                <h1 style="color: #d32f2f;">⛔️ 접속 불가</h1>
                <p>카카오톡/인스타그램에서는 카메라가 안 열리오.<br>우측 상단 점 3개(...)를 눌러 <b>[다른 브라우저로 열기]</b>를 하시오.</p>
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
    st.stop()

# --- 5. [핵심] 장군신 자동 로테이션 시스템 ---
def get_all_available_models():
    """사용 가능한 모든 장군신 목록 가져오기"""
    try:
        all_models = []
        for model_info in genai.list_models():
            if 'generateContent' in model_info.supported_generation_methods:
                all_models.append(model_info.name)
        return all_models
    except:
        # API 호출 실패 시 수동 백업 리스트
        return [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-1.5-pro-latest',
            'gemini-2.0-flash-exp',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]

def try_model_with_image(model_name, prompt, image):
    """특정 장군신으로 관상 시도"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image])
        return response, None  # 성공
    except Exception as e:
        error_msg = str(e)
        # 429 에러 (할당량 초과) 또는 다른 에러 반환
        if "429" in error_msg or "quota" in error_msg.lower():
            return None, "quota_exceeded"
        elif "404" in error_msg or "not found" in error_msg.lower():
            return None, "model_not_found"
        else:
            return None, error_msg

# --- 6. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

# --- 7. 화면 구성 ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.write("---")

input_method = st.radio(
    "사진 준비 방식을 선택하시오:",
    ("📸 직접 촬영", "📂 앨범 선택"),
    horizontal=True
)

if input_method == "📸 직접 촬영":
    camera_image = st.camera_input("촬영", label_visibility="collapsed")
    if camera_image: 
        st.session_state.final_image = camera_image
elif input_method == "📂 앨범 선택":
    uploaded_file = st.file_uploader("업로드", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    if uploaded_file: 
        st.session_state.final_image = uploaded_file

# --- 8. 분석 및 실행 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="선택된 얼굴", use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # ---------------------------------------------------------
            # 1단계: 사용 가능한 모든 장군신 명단 가져오기
            # ---------------------------------------------------------
            status_text.markdown("### 📡 당직 서는 장군신을 찾는 중이오...")
            progress_bar.progress(5)
            
            available_models = get_all_available_models()
            
            if not available_models:
                st.error("⚠️ 장군신 명단을 불러올 수 없소. 네트워크를 확인하시오.")
                st.stop()

            # ---------------------------------------------------------
            # 2단계: 얼굴 부위별 분석 애니메이션
            # ---------------------------------------------------------
            analysis_steps = [
                "1단계: 이마의 넓이와 초년운 측정 중...",
                "2단계: 눈썹의 기세와 형제운 분석 중...",
                "3단계: 코의 높이와 재물운 계산 중...",
                "4단계: 입술의 모양과 말년운 확인 중...",
                "5단계: 얼굴의 전체적인 조화(오행) 분석 중..."
            ]
            
            for i, step in enumerate(analysis_steps):
                status_text.markdown(f"### 🔍 {step}")
                progress_bar.progress(5 + (i + 1) * 15)
                time.sleep(1.0)

            # ---------------------------------------------------------
            # 3단계: 장군신 순차 소환 (할당량 초과 시 자동 교체)
            # ---------------------------------------------------------
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
            
            image = Image.open(st.session_state.final_image)
            response = None
            successful_model = None
            tried_models = []
            
            for model_name in available_models:
                display_name = model_name.replace('models/', '').replace('gemini-', '').upper()
                
                status_text.markdown(f"### ⚡ **{display_name}** 장군신 소환 중...")
                progress_bar.progress(85)
                
                response, error = try_model_with_image(model_name, prompt, image)
                tried_models.append(model_name)
                
                if response is not None:
                    # ✅ 성공!
                    successful_model = display_name
                    break
                else:
                    # ❌ 실패 - 다음 장군신으로
                    if error == "quota_exceeded":
                        status_text.markdown(f"### 💤 {display_name} 장군신이 휴식 중이오... 다른 장군신 찾는 중...")
                        time.sleep(0.8)
                    elif error == "model_not_found":
                        continue  # 조용히 다음으로
                    else:
                        continue  # 기타 에러도 다음으로
            
            # ---------------------------------------------------------
            # 4단계: 결과 확인
            # ---------------------------------------------------------
            if response is None:
                st.error("⚠️ 모든 장군신이 휴식 중이거나 소환할 수 없소.")
                st.info(f"💡 시도한 장군신: {len(tried_models)}명")
                st.warning("잠시 후 다시 시도하시거나, 다른 시간대에 찾아주시오.")
                st.stop()
            
            # ---------------------------------------------------------
            # 5단계: 성공적인 감정서 출력
            # ---------------------------------------------------------
            status_text.markdown(f"### ✅ **{successful_model}** 장군신이 감정서를 작성했소!")
            progress_bar.progress(100)
            time.sleep(1.0)
            
            progress_bar.empty()
            status_text.empty()
            
            st.write("---")
            st.subheader(f"📜 아솔의 관상 풀이 (by {successful_model} 장군신)")
            st.markdown(response.text)
            st.balloons()

        except Exception as e:
            st.error(f"예기치 못한 에러가 났소. (내용: {e})")
            st.info("💡 네트워크 연결을 확인하거나, 잠시 후 다시 시도해주시오.")