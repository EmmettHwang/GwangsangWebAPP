import streamlit as st
from PIL import Image
import google.generativeai as genai

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="관상가 아솔",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 스타일 및 브라우저 차단 ---
st.components.v1.html("""
<script>
    var userAgent = navigator.userAgent.toLowerCase();
    var isInApp = userAgent.indexOf("kakao") > -1 || userAgent.indexOf("instagram") > -1 || userAgent.indexOf("line") > -1;
    if (isInApp) {
        document.body.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #fff; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; font-family: sans-serif;">
                <h1 style="color: #d32f2f;">⛔️ 접속 불가</h1>
                <p>카카오톡/인스타 브라우저에서는 작동하지 않소.<br><b>다른 브라우저(크롬/사파리)</b>로 여시오.</p>
            </div>
        `;
    }
</script>
""", height=0)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; margin-top: 10px; background-color: #7D5A5A; color: white; font-weight: bold; padding: 12px; border-radius: 10px;
    }
    div.row-widget.stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    .main-header { text-align: center; font-family: 'Helvetica', sans-serif; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 연결 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정이 안 되었소. secrets.toml을 확인하시오.")

# --- 4. 메인 화면 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.write("---")

input_method = st.radio("사진 준비:", ("📸 촬영", "📂 앨범"), horizontal=True)

if input_method == "📸 촬영":
    img = st.camera_input("촬영", label_visibility="collapsed")
    if img: st.session_state.final_image = img
else:
    img = st.file_uploader("업로드", type=['jpg','png'], label_visibility="collapsed")
    if img: st.session_state.final_image = img

# --- 5. 분석 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="선택된 얼굴", use_container_width=True)

    if st.button("🔮 관상 보기"):
        # 에러가 나면 즉시 보여주도록 try-except 강화
        try:
            with st.spinner("아솔이 천기를 읽고 있소... (최대 10초)"):
                # 모델 호출 (가장 안정적인 1.5-flash 사용)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 이미지 처리
                image_data = Image.open(st.session_state.final_image)

                prompt = """
                당신은 조선 최고의 관상가 '아솔'입니다. 
                이 사람의 [총평, 재물운, 애정운, 조언]을 사극 말투("~하오")로 재미있게 풀이하시오.
                """
                
                # 여기서 멈추는지 확인
                response = model.generate_content([prompt, image_data])
                
                st.write("---")
                st.subheader("📜 아솔의 감정서")
                st.markdown(response.text)
                st.balloons()
                
        except Exception as e:
            # 에러 발생 시 빨간 박스로 이유 출력
            st.error(f"⚠️ 에러가 발생했소!\n\n이유: {e}")
            st.warning("팁: API 키가 정확한지, 혹은 인터넷 연결을 확인하시오.")