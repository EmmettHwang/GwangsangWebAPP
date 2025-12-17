import streamlit as st
from PIL import Image
import google.generativeai as genai
import time
import base64
import json

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="🧙‍♂️ 관상가 아솔 - 조선 팔도 최고의 관상",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 메타 태그 주입 ---
st.components.v1.html("""
<script>
(function() {
    var metaTags = [
        {property: 'og:type', content: 'website'},
        {property: 'og:title', content: '🧙‍♂️ 관상가 아솔 - 조선 팔도 최고의 관상'},
        {property: 'og:description', content: 'AI가 당신의 얼굴을 보고 초년운, 재물운, 애정운을 상세하게 풀어드립니다.'},
        {property: 'og:image', content: 'https://em-content.zobj.net/source/apple/391/mage_1f9d9.png'},
        {property: 'og:url', content: 'https://gwangsangapp-ryes95aziswadr3h9bhcug.streamlit.app/'},
        {name: 'twitter:card', content: 'summary_large_image'}
    ];
    
    try {
        var head = window.parent.document.head;
        metaTags.forEach(function(tag) {
            var meta = window.parent.document.createElement('meta');
            if (tag.property) meta.setAttribute('property', tag.property);
            else if (tag.name) meta.setAttribute('name', tag.name);
            meta.setAttribute('content', tag.content);
            head.appendChild(meta);
        });
    } catch(e) {}
})();
</script>
""", height=0)

# --- 3. 인앱 브라우저 차단 ---
st.components.v1.html("""
<script>
(function() {
    var ua = navigator.userAgent.toLowerCase();
    var inAppPatterns = ['kakao', 'instagram', 'line', 'fban', 'naver'];
    var isInApp = inAppPatterns.some(function(p) { return ua.indexOf(p) > -1; });
    
    if (isInApp && ua.indexOf('android') > -1) {
        var href = window.top.location.href || window.location.href;
        window.location.href = 'intent://' + href.replace(/https?:\\/\\//, '') + 
                              '#Intent;scheme=https;package=com.android.chrome;end';
    }
})();
</script>
""", height=1)

# --- 4. PWA 지원 ---
def add_pwa_support():
    manifest = {
        "name": "관상가 아솔",
        "short_name": "아솔",
        "description": "조선 팔도 최고의 관상가",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#7D5A5A",
        "orientation": "portrait",
        "icons": [{
            "src": "https://em-content.zobj.net/source/apple/391/mage_1f9d9.png",
            "sizes": "192x192",
            "type": "image/png"
        }]
    }
    manifest_json = json.dumps(manifest)
    pwa_html = f"""
    <link rel="manifest" href="data:application/json;base64,{base64.b64encode(manifest_json.encode()).decode()}">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#7D5A5A">
    """
    st.markdown(pwa_html, unsafe_allow_html=True)

add_pwa_support()

# --- 5. 스타일 ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        background-color: #7D5A5A;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 12px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #5D3A3A;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(125, 90, 90, 0.4);
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 15px;
    }
    .main-header {
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        color: #333;
    }
    .status-text {
        font-size: 16px;
        color: #666;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #7D5A5A;
    }
    .voice-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. API 키 설정 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오.")
    st.stop()

# --- 7. AI 분석 함수들 ---
def get_all_available_models():
    try:
        all_models = []
        for model_info in genai.list_models():
            if 'generateContent' in model_info.supported_generation_methods:
                all_models.append(model_info.name)
        return all_models
    except:
        return ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-2.0-flash-exp']

def analyze_basic_info(model_name, image):
    """성별, 나이, 추정 직업 1개 분석"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = """
이 사진을 보고 다음만 답변하세요:

1. 성별: 남성 또는 여성
2. 나이대: 10대, 20대 초반, 20대 후반, 30대 초반, 30대 후반, 40대 초반, 40대 후반, 50대 초반, 50대 후반, 60대 초반, 60대 후반, 70대, 80대 이상 중 하나
3. 추정 직업: 의상(70%)과 얼굴 관상(30%)을 보고 한 단어로 추정

형식:
성별: [남성/여성]
나이대: [나이대]
추정 직업: [한 단어]

예시:
성별: 여성
나이대: 30대 초반
추정 직업: 마케터
"""
        response = model.generate_content([prompt, image])
        return response.text, None
    except Exception as e:
        return None, str(e)

def analyze_suitable_jobs(model_name, image):
    """관상학으로 어울리는 직업 3개 분석"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = """
이 얼굴을 관상학적으로 분석하여 어울리는 직업 3개를 추천하세요.

관상 기준:
- 이마: 넓고 밝으면 → 교수, 연구원, 기획자, 컨설턴트
- 눈: 날카로우면 → 분석가, 개발자, 회계사, 과학자
- 코: 크고 단단하면 → 금융, 사업가, 영업, 투자가
- 입: 크고 표현력 좋으면 → 강사, 방송인, 마케터, 교육자
- 턱: 사각지고 강하면 → 경영인, 관리자, 공무원, CEO
- 귀: 크고 두꺼우면 → 전문직, 의사, 변호사, 교수

형식:
어울리는 직업: [직업1], [직업2], [직업3]

예시:
어울리는 직업: 교육, 컨설팅, 미디어
"""
        response = model.generate_content([prompt, image])
        return response.text, None
    except Exception as e:
        return None, str(e)

def try_model_with_image(model_name, prompt, image):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image])
        return response, None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return None, "quota_exceeded"
        elif "404" in error_msg:
            return None, "model_not_found"
        else:
            return None, error_msg

# --- 8. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'voice_input' not in st.session_state:
    st.session_state.voice_input = ""

# --- 9. 메인 UI ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 16px;'>조선 팔도를 떠돌며 수많은 관상을 봐온 전설의 관상가</p>", unsafe_allow_html=True)
st.write("---")

# 사진 입력
input_method = st.radio(
    "사진 준비 방식을 선택하시오:",
    ("📸 직접 촬영", "📂 앨범 선택"),
    horizontal=True
)

if input_method == "📸 직접 촬영":
    camera_image = st.camera_input("📸 얼굴을 화면에 담으시오", label_visibility="visible")
    if camera_image:
        st.session_state.final_image = camera_image
elif input_method == "📂 앨범 선택":
    uploaded_file = st.file_uploader("📂 사진을 선택하시오", type=['jpg', 'jpeg', 'png'], label_visibility="visible")
    if uploaded_file:
        st.session_state.final_image = uploaded_file

# --- 10. 관상 분석 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="✅ 선택된 얼굴", use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기", type="primary"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("<p class='status-text'>📡 당직 서는 장군신을 찾는 중...</p>", unsafe_allow_html=True)
            progress_bar.progress(3)
            
            available_models = get_all_available_models()
            image = Image.open(st.session_state.final_image)
            
            # 기본 정보 분석
            status_text.markdown("<p class='status-text'>🧐 얼굴 기본 정보 분석 중...</p>", unsafe_allow_html=True)
            progress_bar.progress(10)
            
            gender = ""
            age_range = ""
            estimated_job = ""
            
            if len(available_models) > 0:
                try:
                    basic_info, _ = analyze_basic_info(available_models[0], image)
                    if basic_info:
                        if "남성" in basic_info:
                            gender = "남성"
                        elif "여성" in basic_info:
                            gender = "여성"
                        
                        age_keywords = ["80대 이상", "70대", "60대 후반", "60대 초반", "50대 후반", "50대 초반",
                                      "40대 후반", "40대 초반", "30대 후반", "30대 초반", "20대 후반", "20대 초반", "10대"]
                        for age in age_keywords:
                            if age in basic_info:
                                age_range = age
                                break
                        
                        if "추정 직업:" in basic_info:
                            estimated_job = basic_info.split("추정 직업:")[1].strip().split("\n")[0].strip()
                except:
                    pass
            
            progress_bar.progress(20)
            
            # 분석 결과 표시
            if gender and age_range and estimated_job:
                st.success(f"### 👤 {gender} | {age_range} | 추정 직업: {estimated_job}")
                
                st.write("---")
                st.write("### 📝 추정 직업이 맞습니까?")
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    user_job = st.text_input(
                        "다르면 실제 직업을 입력해주세요",
                        value=estimated_job,
                        key="user_job_input",
                        placeholder="예: 개발자, 디자이너, 교사 등"
                    )
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("🎤", help="음성으로 입력", key="voice_btn"):
                        st.components.v1.html("""
                        <script>
                            if ('webkitSpeechRecognition' in window) {
                                const recognition = new webkitSpeechRecognition();
                                recognition.lang = 'ko-KR';
                                recognition.start();
                                
                                recognition.onresult = function(event) {
                                    const text = event.results[0][0].transcript;
                                    alert('음성 인식: ' + text + '\\n\\n위 입력창에 직접 입력해주세요.');
                                };
                                
                                recognition.onerror = function() {
                                    alert('음성 인식 실패. 직접 입력해주세요.');
                                };
                            } else {
                                alert('이 브라우저는 음성 인식을 지원하지 않습니다.');
                            }
                        </script>
                        """, height=0)
                
                final_job = user_job if user_job else estimated_job
                
                # 어울리는 직업 분석
                status_text.markdown("<p class='status-text'>✨ 관상으로 어울리는 직업 분석 중...</p>", unsafe_allow_html=True)
                progress_bar.progress(30)
                
                suitable_jobs = []
                try:
                    suitable_info, _ = analyze_suitable_jobs(available_models[0], image)
                    if suitable_info and "어울리는 직업:" in suitable_info:
                        job_line = suitable_info.split("어울리는 직업:")[1].strip().split("\n")[0]
                        suitable_jobs = [j.strip() for j in job_line.replace(",", " ").split() if j.strip()][:3]
                except:
                    pass
                
                if suitable_jobs:
                    st.info(f"✨ **관상으로 본 어울리는 직업군:** {', '.join(suitable_jobs)}")
                
                # 관상 분석 프로세스
                analysis_steps = [
                    "🔍 1단계: 이마의 넓이와 초년운 측정 중...",
                    "🔍 2단계: 눈썹의 기세와 형제운 분석 중...",
                    "🔍 3단계: 코의 높이와 재물운 계산 중...",
                    "🔍 4단계: 입술의 모양과 말년운 확인 중...",
                    "🔍 5단계: 얼굴의 전체적인 조화 분석 중..."
                ]
                
                for i, step in enumerate(analysis_steps):
                    status_text.markdown(f"<p class='status-text'>{step}</p>", unsafe_allow_html=True)
                    progress_bar.progress(30 + (i + 1) * 10)
                    time.sleep(0.8)
                
                # 직업 매칭 분석
                job_match_text = ""
                if final_job and suitable_jobs:
                    matching = any(final_job.lower() in job.lower() or job.lower() in final_job.lower() 
                                 for job in suitable_jobs)
                    if matching:
                        job_match_text = f"""

**🎉 직업운 특별 분석:**
오호! 현재 그대가 하고 있는 '{final_job}' 일이 
관상으로 본 어울리는 직업({', '.join(suitable_jobs)})과 잘 맞는구나!

그대는 운명의 길을 걷고 있소이다.
이 길을 계속 가면 큰 성취를 이룰 것이오.
얼굴에서 붉은 기운이 뿜어져 나오는군요! 
"""
                    else:
                        job_match_text = f"""

**💡 직업운 특별 분석:**
현재 '{final_job}' 일을 하고 계시는군요.
하지만 관상으로 보니 {', '.join(suitable_jobs)} 계열이 
그대의 타고난 운명과 더 잘 어울리는 것 같소.

현재 하시는 일도 나쁘지 않으나,
만약 새로운 길을 모색한다면 위 분야를 고려해보는 것도 좋겠구려.
얼굴에서 변화의 기운이 감지되는군요!
"""
                
                # AI 프롬프트
                prompt = f"""
당신의 이름은 '아솔'입니다. 조선 팔도에서 가장 용한 전설적인 관상가입니다.

**분석 대상 정보:**
- 성별: {gender}
- 나이대: {age_range}
- 현재 직업: {final_job}
- 어울리는 직업: {', '.join(suitable_jobs) if suitable_jobs else '미분석'}
{job_match_text}

위 정보를 바탕으로 {gender}의 {age_range} 시기에 맞는 관상을 **매우 상세하고 재미있게** 봐주세요.
말투는 위엄 있으면서도 친근한 사극 톤("~하오", "~이오", "~구려")을 사용하세요.

[아솔의 감정서 양식]

🎭 **인상 총평 및 삼정 분석**
- 첫인상과 전체적인 기운 (5-6문장)
- 상정(이마): 초년운(0-30세) 분석 (4문장)
- 중정(눈썹-코): 중년운(30-50세) 분석 (4문장)
- 하정(인중-턱): 말년운(50세 이후) 분석 (4문장)

💰 **재물운 및 사업운**
- 코로 보는 재물 축적 능력 (6문장)
- 광대뼈로 보는 리더십 (3문장)
- 돈을 버는 스타일 (4문장)
- 재물이 들어오는 시기
- 재테크 조언

❤️ **연애운 및 애정운**
- 눈매로 보는 이성운 (6문장)
- 입술로 보는 애정 표현 (3문장)
- 도화살 유무
- 결혼운과 배우자 특징 (4문장)

🏆 **직업운 및 적성**
- 학업 능력과 지적 수준 (3문장)
- 적합한 직업 5개 추천
- 승진운과 출세운 (4문장)
- 창업 적성

🍀 **건강운 및 주의사항**
- 현재 건강 상태 (2문장)
- 주의할 신체 부위
- 건강 관리 조언

👥 **대인관계 및 성격**
- 귀로 보는 복 (3문장)
- 성격 장점 5가지, 보완할 점 2가지
- 리더십과 인맥운

🔮 **아솔의 특별 처방**
- 개운 방향, 색상
- 주의할 시기
- 운을 높이는 습관 5가지
- 개운 음식, 장소

⭐ **종합 운세 평가 (별 5개 만점)**
- 재물운: ⭐⭐⭐⭐ (현실적으로 평가)
- 애정운: ⭐⭐⭐⭐
- 건강운: ⭐⭐⭐⭐⭐
- 직업운: ⭐⭐⭐⭐

**별점 기준:**
- ⭐⭐⭐ (3개): 보통, 평범
- ⭐⭐⭐⭐ (4개): 좋음, 긍정적
- ⭐⭐⭐⭐⭐ (5개): 매우 좋음
- 평균 3.5~4개 수준으로 현실적 평가

📜 **아솔의 한마디**
- 용기와 희망을 주는 말 (4-5문장)

**작성 지침:**
1. 각 항목 최소 4-5문장 상세 작성
2. 구체적인 나이, 시기 언급
3. 긍정 80% + 현실 조언 20%
4. 전체 분량 1200자 이상
5. 별점은 현실적으로 (평균 3.5~4개)
"""
                
                # 모델 시도
                status_text.markdown("<p class='status-text'>⚡ 장군신 소환 중...</p>", unsafe_allow_html=True)
                progress_bar.progress(85)
                
                response = None
                successful_model = None
                
                for model_name in available_models:
                    display_name = model_name.replace('models/', '').replace('gemini-', '').upper()
                    response, error = try_model_with_image(model_name, prompt, image)
                    
                    if response is not None:
                        successful_model = display_name
                        break
                    elif error == "quota_exceeded":
                        time.sleep(0.5)
                
                if response is None:
                    st.error("⚠️ 모든 장군신이 휴식 중입니다. 잠시 후 다시 시도해주세요.")
                    progress_bar.empty()
                    status_text.empty()
                    st.stop()
                
                status_text.markdown(f"<p class='status-text'>✅ {successful_model} 장군신이 감정서를 작성했소!</p>", unsafe_allow_html=True)
                progress_bar.progress(100)
                time.sleep(1.0)
                
                progress_bar.empty()
                status_text.empty()
                
                # 결과 표시
                st.write("---")
                st.subheader(f"📜 아솔의 관상 풀이")
                st.caption(f"*by {successful_model} 장군신*")
                st.markdown(response.text)
                
                # 복사 버튼
                result_text_escaped = response.text.replace('`', '').replace('"', '\\"').replace('\n', '\\n')
                st.components.v1.html(f"""
                <div style="margin: 30px 0; text-align: center;">
                    <button onclick="copyResult()" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 15px 40px;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                    ">📋 관상 결과 복사하기</button>
                    <div id="copy-msg" style="margin-top: 15px; color: #28a745; font-weight: bold; opacity: 0;"></div>
                </div>
                <script>
                    function copyResult() {{
                        var text = "📜 관상가 아솔의 감정서\\n\\n{result_text_escaped}";
                        if (navigator.clipboard) {{
                            navigator.clipboard.writeText(text).then(function() {{
                                var msg = document.getElementById('copy-msg');
                                msg.innerHTML = '✅ 복사 완료!';
                                msg.style.opacity = '1';
                                setTimeout(function() {{ msg.style.opacity = '0'; }}, 3000);
                            }});
                        }}
                    }}
                </script>
                """, height=120)
                
                st.balloons()

        except Exception as e:
            st.error(f"⚠️ 에러가 발생했소: {e}")

# --- 하단 푸터 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 <b>개인정보 보호:</b> 모든 사진은 분석 후 즉시 삭제됩니다.</p>
    <p>🎲 <b>엔터테인먼트:</b> 재미를 위한 서비스로 실제 운세와 무관합니다.</p>
    <p style="margin-top: 20px; color: #999; font-size: 12px;">
        🧙‍♂️ 관상가 아솔 © 2024 | Powered by Google Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
