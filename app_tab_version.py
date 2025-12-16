import streamlit as st
from PIL import Image
import google.generativeai as genai

# --- 1. 기본 설정 (페이지 아이콘 및 제목) ---
st.set_page_config(
    page_title="관상가 양반",
    page_icon="🧙‍♂️",
    layout="centered"
)

# [스타일 꾸미기] 버튼 모양과 헤더를 조금 더 예쁘게 다듬는 CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        background-color: #FF4B4B;
        color: white;
    }
    .main-header {
        text-align: center; 
        font-family: 'Helvetica', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API 키 연결 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키가 설정되지 않았습니다. secrets.toml 파일을 확인해주세요.")

# --- 3. 헤더 영역 ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 운명을 읽는 AI 관상가</h1>", unsafe_allow_html=True)
st.write("---")
st.info("당신의 얼굴에 숨겨진 천기(天機)를 읽어드립니다. 아래에서 사진을 선택하시오.")

# --- 4. 이미지 입력 (탭 구조로 변경하여 깔끔하게 정리) ---
# 탭을 사용하여 '파일 업로드'와 '카메라'를 분리했습니다.
tab1, tab2 = st.tabs(["📂 앨범에서 선택", "📸 카메라로 촬영"])

final_image = None

with tab1:
    uploaded_file = st.file_uploader("얼굴이 잘 나온 사진을 올려주시오", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        final_image = uploaded_file

# ... (앞부분 코드는 동일) ...

with tab2:
    st.write("### 📸 실시간 촬영")
    st.write("아래 체크박스를 누르면 카메라가 켜집니다.")

    # [수정 1] 세션 상태를 활용해 카메라 켜짐 상태를 확실하게 잡음 (버그 수정)
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False

    def toggle_camera():
        st.session_state.camera_on = not st.session_state.camera_on

    # on_change를 사용하여 체크박스 상태가 바뀔 때 즉시 반응하도록 함
    enable_camera = st.checkbox("카메라 켜기", value=st.session_state.camera_on, on_change=toggle_camera)

    if enable_camera:
        # [수정 2] 카메라가 뜨기 전에 안심시키는 메시지 출력 (프로그레스바 대체)
        msg_placeholder = st.empty() # 빈 공간을 미리 만듦
        msg_placeholder.info("🚀 카메라 모듈을 예열 중입니다... (2~3초 정도 걸립니다)")
        
        # [수정 3] key 값을 부여하여 위젯이 깜빡이거나 초기화되는 것 방지
        camera_image = st.camera_input("얼굴을 들이대시오", label_visibility="visible", key="camera_widget")
        
        # 카메라가 로딩되어 화면에 뜨면(사용자가 볼 수 있는 상태), 로딩 메시지를 지움
        if camera_image:
             msg_placeholder.empty() # 메시지 삭제
             final_image = camera_image
        else:
             # 아직 사진을 안 찍었어도 카메라는 떴을 테니 메시지 변경
             msg_placeholder.success("카메라가 준비되었습니다! 촬영 버튼을 누르세요.")

# ... (뒷부분 분석 로직 동일) ...

# --- 5. 분석 로직 ---
if final_image:
    # 이미지를 중앙에 정렬하여 보여줌
    st.write("---")
    st.markdown("### 🧐 선택된 얼굴")
    
    img = Image.open(final_image)
    st.image(img, use_container_width=True)

    # 분석 버튼
    if st.button("🔮 관상 보기 (운명 확인)"):
        with st.spinner("하늘의 기운을 읽고 있습니다... 잠시만 기다리시오..."):
            try:
                # 1) 모델 설정 (gemini-2.5는 아직 없으므로 1.5-flash로 수정)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 2) 프롬프트 (사극 톤 유지)
                prompt = """
                당신은 조선 시대부터 전해져 내려오는 전설적인 관상가입니다. 
                이 사진의 인물을 보고 다음 내용을 바탕으로 관상을 아주 상세하고 재미있게 봐주세요.
                말투는 사극 톤("~하오", "~이오", "~니라")을 사용하세요.
                
                목차:
                1. 전체적인 인상과 기운
                2. 초년, 중년, 말년의 운세 흐름
                3. 재물운 (곳간이 찰 상인가?)
                4. 연애 및 대인관계
                5. 피해야 할 것과 행운의 조언
                
                무조건 좋은 말만 하지 말고, 재미를 위해 따끔한 조언이나 팩트 폭격도 섞어서 
                아주 신비롭고 도사처럼 말해주세요.
                """
                
                # 3) AI에게 요청
                response = model.generate_content([prompt, img])
                
                # 4) 결과 출력
                st.write("---")
                st.success("관상 분석이 완료되었소!")
                st.subheader("📜 도사의 감정 결과")
                st.markdown(response.text)
                st.balloons() 

            except Exception as e:
                st.error(f"에러가 발생했소. 사진을 다시 확인해보시오. \n(에러 내용: {e})")
else:
    # 사진이 없을 때 빈 공간 확보
    st.write("")