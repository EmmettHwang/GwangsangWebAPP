import streamlit as st
from PIL import Image
# streamlit 라이브러리를 이용해서 간단한 웹앱을 만들어 봅니다. 
# html, css, javascript 같은 복잡한 언어를 몰라도 됩니다!


# 1. 페이지 기본 설정 (페이지 제목, 아이콘 등)
st.set_page_config(page_title="관상가 양반", page_icon="🧙‍♂️")

# 2. 화면 타이틀
st.title("운명을 읽어주는 AI 관상가 🧙‍♂️")
st.write("당신의 사진을 올려주세요. AI가 관상을 분석해 드립니다.")

# 3. 파일 업로더 만들기 (jpg, png 파일만 허용)
uploaded_file = st.file_uploader("관상을 볼 사진을 선택하세요", type=['jpg', 'jpeg', 'png'])

# 4. 만약 사용자가 파일을 올렸다면? -> 화면에 보여주기
if uploaded_file is not None:
    # 파일을 이미지로 변환
    image = Image.open(uploaded_file)
    
    # 이미지를 화면에 출력 
    # use_container_width=True 옵션은 모바일에서 사진이 화면 밖으로 삐져나가는 걸 막아줍니다.
    st.image(image, caption='업로드된 사진', use_container_width=True)
    
    # 5. 분석 버튼 만들기
    if st.button("관상 분석 시작하기"):
        st.write("⏳ AI가 당신의 얼굴을 분석하고 있습니다...")
        # --- 여기(AI 분석 로직)는 다음 단계에서 채워 넣을 예정입니다 ---
        st.success("분석 기능은 5단계에서 연결됩니다!")