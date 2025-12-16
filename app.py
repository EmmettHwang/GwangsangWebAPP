import streamlit as st
from PIL import Image
import google.generativeai as genai

# --- 1. 기본 설정 및 주소창 숨기기(PWA) 설정 ---
st.set_page_config(
    page_title="관상가 아솔",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. [핵심] 인앱 브라우저 감지 및 차단 스크립트 ---
# 카카오톡이나 인스타로 열면 "크롬으로 여시오"라고 경고창을 띄우고 내용을 가립니다.
st.components.v1.html("""
<script>
    var userAgent = navigator.userAgent.toLowerCase();
    var isInApp = userAgent.indexOf("kakao") > -1 || userAgent.indexOf("instagram") > -1 || userAgent.indexOf("line") > -1;
    
    if (isInApp) {
        // 인앱 브라우저라면 내용을 다 덮어버리고 안내문을 띄움
        document.body.innerHTML = `
            <div style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background-color: #fff; z-index: 9999; display: flex;
                flex-direction: column; justify-content: center; align-items: center;
                text-align: center; font-family: sans-serif; padding: 20px;">
                <h1 style="color: #d32f2f;">⛔️ 접속 불가</h1>
                <p style="font-size: 18px; line-height: 1.6;">
                    죄송하오. <b>카카오톡/인스타그램</b>에서는<br>
                    카메라가 열리지 않소.<br><br>
                    화면 우측 상단(또는 하단)의 <b>점 3개(...)</b>를 누르고<br>
                    <b>[다른 브라우저로 열기]</b>를 선택하시오.
                </p>
            </div>
        `;
    }
</script>
""", height=0)

# --- 3. 스타일 꾸미기 (주소창 숨기는 메타태그 포함) ---
st.markdown("""
    <style>
    /* 1. 버튼 디자인 */
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        background-color: #7D5A5A;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px;
    }
    
    /* 2. 라디오 버튼 가로 배치 */
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 15px;
    }
    
    /* 3. 헤더 폰트 */
    .main-header {
        text-align: center; 
        font-family: 'Helvetica', sans-serif;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. API 키 연결 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키가 설정되지 않았습니다.")

# --- 5. 세션 상태 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

# --- 6. 헤더 영역 ---
st.markdown("<h1 class='main-header'>🧙‍♂️관상가아솔</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>당신의 얼굴에 숨겨진 운명을 꿰뚫어 봅니다.</p>", unsafe_allow_html=True)

# 🚀 주소창 없애는 팁 안내 (사용자가 직접 해야 함)
with st.expander("📲 앱처럼 주소창 없이 쓰는 법"):
    st.markdown("""
    1. 브라우저 메뉴(점 3개) 클릭
    2. **[홈 화면에 추가]** 또는 **[앱 설치]** 선택
    3. 바탕화면에 생긴 아이콘으로 실행하면 **주소창 없이** 실행됩니다!
    """)

st.write("---")

# --- 7. 이미지 입력 (라디오 버튼) ---
input_method = st.radio(
    "사진 준비 방식을 선택하시오:",
    ("📸 직접 촬영", "📂 앨범 선택"),
    horizontal=True,
    index=0
)

st.write("") 

if input_method == "📸 직접 촬영":
    # 카메라 위젯
    camera_image = st.camera_input("얼굴을 들이대시오", label_visibility="collapsed")
    if camera_image:
        st.session_state.final_image = camera_image
        st.success("사진이 찍혔소!")

elif input_method == "📂 앨범 선택":
    # 파일 업로드
    uploaded_file = st.file_uploader("파일 업로드", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    if uploaded_file:
        st.session_state.final_image = uploaded_file
        st.success("사진을 잘 받았소!")

# --- 8. 분석 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.subheader("🧐 아솔이 보고 있는 얼굴")
    
    img = Image.open(st.session_state.final_image)
    st.image(img, use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기"):
        with st.spinner("아솔이 천기를 읽고 있소이다..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """
                당신의 이름은 '아솔'입니다. 조선 팔도에서 가장 용한 전설적인 관상가입니다.
                이 사진의 인물을 보고 다음 내용을 바탕으로 관상을 아주 상세하고 재미있게 봐주세요.
                말투는 위엄 있으면서도 친근한 사극 톤("~하오", "~이오", "~니라", "보시오")을 사용하세요.
                자신을 지칭할 때는 '나 아솔은~' 또는 '이 아솔이 보기에~'라고 하세요.
                
                [아솔의 감정서]
                1. 🎭 인상 총평 (초년, 중년, 말년의 기운)
                2. 💰 재물운 (곳간이 가득 찰 상인가?)
                3. ❤️ 연애 및 애정운 (도화살이 있는가?)
                4. 🍀 아솔의 특별 처방 (행운의 조언과 주의할 점)
                
                무조건 좋은 말만 하지 말고, 재미를 위해 따끔한 팩트 폭격도 섞어서 
                아주 신통방통하게 말해주세요.
                """
                
                response = model.generate_content([prompt, img])
                
                st.write("---")
                st.subheader("📜 아솔의 관상 풀이")
                st.markdown(response.text)
                st.balloons() 

            except Exception as e:
                st.error(f"에러가 났소. (내용: {e})")