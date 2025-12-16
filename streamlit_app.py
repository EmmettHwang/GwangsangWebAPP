import streamlit as st
from PIL import Image
import google.generativeai as genai
import cv2
import numpy as np
import mediapipe as mp

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="관상가 아솔",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 스타일 및 인앱 브라우저 차단 ---
st.components.v1.html("""
<script>
    var userAgent = navigator.userAgent.toLowerCase();
    var isInApp = userAgent.indexOf("kakao") > -1 || userAgent.indexOf("instagram") > -1 || userAgent.indexOf("line") > -1;
    if (isInApp) {
        document.body.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #fff; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; font-family: sans-serif; padding: 20px;">
                <h1 style="color: #d32f2f;">⛔️ 접속 불가</h1>
                <p>죄송하오. <b>카카오톡/인스타</b>에서는 카메라가 안 열리오.<br>우측 상단 점 3개(...)를 눌러 <b>[다른 브라우저로 열기]</b>를 하시오.</p>
            </div>
        `;
    }
</script>
""", height=0)

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; margin-top: 10px; background-color: #7D5A5A; color: white; font-weight: bold; border-radius: 10px; padding: 12px;
    }
    div.row-widget.stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    .main-header { text-align: center; font-family: 'Helvetica', sans-serif; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키가 설정되지 않았습니다.")

# --- 4. [신규] 얼굴에 메쉬(그물) 그리기 함수 ---
def draw_face_mesh(pil_image):
    # 1. 미디어파이프 설정
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # 2. 이미지를 numpy 배열로 변환 (OpenCV용)
    image_np = np.array(pil_image.convert('RGB'))
    
    # 3. 얼굴 그물 찾기
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:
        
        results = face_mesh.process(image_np)
        
        # 4. 그물 그리기
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 그물망(Tesselation) 그리기
                mp_drawing.draw_landmarks(
                    image=image_np,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
                
                # 눈/입술 윤곽선 강조
                mp_drawing.draw_landmarks(
                    image=image_np,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())
                    
    return Image.fromarray(image_np) # 다시 PIL 이미지로 변환해서 반환

# --- 5. UI 구성 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>당신의 얼굴에 숨겨진 운명을 꿰뚫어 봅니다.</p>", unsafe_allow_html=True)

input_method = st.radio("사진 준비 방식:", ("📸 직접 촬영", "📂 앨범 선택"), horizontal=True)
st.write("") 

if input_method == "📸 직접 촬영":
    camera_image = st.camera_input("촬영", label_visibility="collapsed")
    if camera_image:
        st.session_state.final_image = camera_image
elif input_method == "📂 앨범 선택":
    uploaded_file = st.file_uploader("업로드", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    if uploaded_file:
        st.session_state.final_image = uploaded_file

# --- 6. 분석 로직 (메쉬 애니메이션 효과 추가) ---
if st.session_state.final_image:
    st.write("---")
    
    # 원본 이미지 준비
    img = Image.open(st.session_state.final_image)
    
    # 화면에 보여줄 이미지 공간(placeholder)을 미리 만듭니다.
    image_placeholder = st.empty()
    image_placeholder.image(img, caption="선택된 얼굴", use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기"):
        try:
            # [효과 1] 메쉬 분석 중인 척하기
            with st.spinner("🔍 아솔이 얼굴의 골격을 분석하고 있소..."):
                mesh_img = draw_face_mesh(img)
                # [효과 2] 메쉬가 그려진 얼굴로 샥! 바꿔치기
                image_placeholder.image(mesh_img, caption="✅ 골격 및 이목구비 인식 완료", use_container_width=True)
            
            # [실제 분석] Gemini 호출
            with st.spinner("📜 운명의 두루마리를 펼치는 중..."):
                model = genai.GenerativeModel('gemini-2.5-flash') # 1.5-flash가 안정적임
                
                prompt = """
                당신의 이름은 '아솔'입니다. 조선 최고 관상가입니다.
                사진 속 인물의 관상을 봐주세요. 말투는 사극 톤("~하오", "보시오")입니다.
                
                [아솔의 감정서]
                1. 🎭 인상 총평
                2. 💰 재물운
                3. ❤️ 애정운
                4. 🍀 행운의 조언
                
                재미있게 팩트 폭격을 섞어서 말해주세요.
                """
                
                response = model.generate_content([prompt, img])
                
                st.write("---")
                st.subheader("📜 아솔의 관상 풀이")
                st.markdown(response.text)
                st.balloons() 

        except Exception as e:
            st.error(f"에러가 났소. (내용: {e})")