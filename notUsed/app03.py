# app03.py은 streamlit을 이용한 간단한 웹앱입니다.
# 카메라를 이용해 사진을 찍거나 파일을 업로드하여 이미지를 입력받고,
# AI가 관상을 분석하는 기능을 구현할 준비를 합니다. 

import streamlit as st
from PIL import Image


st.set_page_config(page_title="관상가 양반", page_icon="🧙‍♂️")

st.title("운명을 읽어주는 AI 관상가 🧙‍♂️")
st.write("사진을 찍거나 앨범에서 골라주세요. AI가 관상을 봐드립니다.")

# --- 1. 이미지 가져오기 (카메라 vs 파일 업로드) ---

# 방법 1: 카메라로 직접 찍기
camera_image = st.camera_input("📸 카메라로 내 얼굴 찍기")

# 방법 2: 파일 업로드하기
uploaded_file = st.file_uploader("📂 또는 앨범에서 사진 선택", type=['jpg', 'jpeg', 'png'])

# 사용자가 입력한 이미지가 있는지 확인하는 변수
final_image = None

# 카메라로 찍은 게 있으면 그걸 우선 사용
if camera_image is not None:
    final_image = camera_image
    st.write("✅ 카메라 사진을 사용합니다.")

# 카메라 사진은 없는데 파일 업로드가 있으면 그걸 사용
elif uploaded_file is not None:
    final_image = uploaded_file
    st.write("✅ 업로드된 파일을 사용합니다.")

# --- 2. 이미지가 확보되었다면 화면에 보여주고 분석 버튼 표시 ---
if final_image is not None:
    # 이미지 파일 열기
    image = Image.open(final_image)
    
    # 화면에 보여주기 (모바일 대응을 위해 use_container_width=True 사용)
    st.image(image, caption='선택된 사진', use_container_width=True)
    
    # 3. 분석 버튼
    if st.button("관상 분석 시작하기"):
        st.write("⏳ AI가 당신의 얼굴을 요리조리 뜯어보고 있습니다...")
        # --- 여기에 나중에 AI 연결 코드가 들어갑니다 ---
        st.success("아직 AI 연결 전입니다! (다음 단계에서 진행)")
else:
    st.info("👆 위에서 사진을 찍거나 파일을 올려주세요.")