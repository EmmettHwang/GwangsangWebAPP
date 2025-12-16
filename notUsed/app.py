import streamlit as st
# 아주 간단한 예제입니다.
# steamlit 라이브러리가 무엇인지 설명 하기 위한 용도입니다.

# 제목 넣기
st.title("운명을 읽어주는 AI 관상가 🧙‍♂️")

# 텍스트 넣기
st.write("당신의 사진을 올려주세요. 관상을 봐드립니다.")

# 버튼 만들기
if st.button("내 관상을확인하기"):
    st.success("버튼이 눌렸습니다! (아직 기능은 없어요)")