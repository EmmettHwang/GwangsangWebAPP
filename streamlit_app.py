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

# --- 2. 메타 태그 주입 (Open Graph, Twitter Card) ---
st.components.v1.html("""
<script>
(function() {
    var metaTags = [
        {property: 'og:type', content: 'website'},
        {property: 'og:title', content: '🧙‍♂️ 관상가 아솔 - 조선 팔도 최고의 관상'},
        {property: 'og:description', content: 'AI가 당신의 얼굴을 보고 초년운, 재물운, 애정운을 상세하게 풀어드립니다. 지금 바로 관상을 봐보시오!'},
        {property: 'og:image', content: 'https://em-content.zobj.net/source/apple/391/mage_1f9d9.png'},
        {property: 'og:url', content: 'https://gwangsangapp-ryes95aziswadr3h9bhcug.streamlit.app/'},
        {property: 'og:site_name', content: '관상가 아솔'},
        {name: 'twitter:card', content: 'summary_large_image'},
        {name: 'twitter:title', content: '🧙‍♂️ 관상가 아솔'},
        {name: 'twitter:description', content: 'AI가 당신의 관상을 봐드립니다'},
        {name: 'twitter:image', content: 'https://em-content.zobj.net/source/apple/391/mage_1f9d9.png'},
        {name: 'description', content: 'AI 관상가 아솔이 당신의 얼굴을 보고 초년운, 재물운, 애정운을 재미있게 풀어드립니다.'},
        {name: 'keywords', content: '관상, AI관상, 관상보기, 얼굴운세, 무료관상, 아솔'},
        {name: 'author', content: '관상가 아솔'}
    ];
    
    try {
        var head = window.parent.document.head;
        metaTags.forEach(function(tag) {
            var meta = window.parent.document.createElement('meta');
            if (tag.property) {
                meta.setAttribute('property', tag.property);
            } else if (tag.name) {
                meta.setAttribute('name', tag.name);
            }
            meta.setAttribute('content', tag.content);
            head.appendChild(meta);
        });
    } catch(e) {
        console.log('메타 태그 주입 실패:', e);
    }
})();
</script>
""", height=0)

# --- 3. 인앱 브라우저 차단 (카카오톡, 인스타그램 등) ---
st.components.v1.html("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<script type="text/javascript">
(function() {
    'use strict';
    
    var ua = navigator.userAgent.toLowerCase();
    var href = window.top.location.href || window.location.href;
    
    // 인앱 브라우저 패턴
    var inAppPatterns = [
        'kakao',
        'kakaotalk',
        'instagram',
        'line',
        'fban',
        'fbav',
        'fb_iab',
        'naver',
        'snapchat',
        'twitter',
        'whatsapp',
        'telegram',
        'wechat',
        'band',
        'daum',
        'everytimeapp'
    ];
    
    var isInApp = false;
    for (var i = 0; i < inAppPatterns.length; i++) {
        if (ua.indexOf(inAppPatterns[i]) > -1) {
            isInApp = true;
            break;
        }
    }
    
    if (isInApp) {
        if (window.parent) {
            window.parent.postMessage({
                type: 'IN_APP_BROWSER_DETECTED',
                url: href,
                userAgent: ua
            }, '*');
        }
        
        if (ua.indexOf('android') > -1) {
            var intentUrl = 'intent://' + href.replace(/https?:\\/\\//, '') + 
                          '#Intent;scheme=https;package=com.android.chrome;end';
            
            try {
                window.top.location.href = intentUrl;
            } catch(e) {
                window.location.href = intentUrl;
            }
        }
    }
})();
</script>
</body>
</html>
""", height=1)

# --- 4. 인앱 브라우저 차단 화면 표시 ---
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data.type === 'IN_APP_BROWSER_DETECTED') {
        document.body.innerHTML = '';
        showBlockScreen(event.data.url, event.data.userAgent);
    }
});

function showBlockScreen(currentUrl, userAgent) {
    var isAndroid = userAgent.indexOf('android') > -1;
    
    document.body.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #FEE500 0%, #FFD700 100%);
            z-index: 999999;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden;
        ">
            <div style="
                background: white;
                padding: 40px 30px;
                border-radius: 20px;
                max-width: 400px;
                width: 100%;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            ">
                <div style="font-size: 80px; margin-bottom: 20px; animation: shake 0.5s infinite;">
                    ⛔
                </div>
                
                <h1 style="
                    color: #d32f2f;
                    font-size: 26px;
                    font-weight: bold;
                    margin: 0 0 15px 0;
                    line-height: 1.3;
                ">
                    앱 내부 브라우저에서는<br>사용할 수 없습니다
                </h1>
                
                <p style="
                    color: #666;
                    font-size: 17px;
                    line-height: 1.6;
                    margin: 0 0 30px 0;
                ">
                    카메라를 사용하려면<br>
                    <b style="color: #000;">Chrome 브라우저</b>로 열어주세요
                </p>
                
                <div style="
                    background: #f8f9fa;
                    padding: 25px 20px;
                    border-radius: 12px;
                    text-align: left;
                    margin-bottom: 25px;
                    border: 3px solid #dc3545;
                ">
                    <div style="
                        font-weight: bold;
                        color: #dc3545;
                        margin-bottom: 15px;
                        font-size: 16px;
                        text-align: center;
                    ">
                        👉 Chrome으로 여는 방법
                    </div>
                    <ol style="
                        margin: 0;
                        padding-left: 25px;
                        color: #333;
                        font-size: 15px;
                        line-height: 2;
                    ">
                        <li><b>우측 상단 점 3개 (⋮)</b> 클릭</li>
                        <li><b>"다른 브라우저로 열기"</b> 선택</li>
                        <li><b>"Chrome"</b> 선택</li>
                    </ol>
                </div>
                
                ${isAndroid ? `
                <button onclick="openInChrome()" style="
                    width: 100%;
                    background: #4285F4;
                    color: white;
                    border: none;
                    padding: 18px;
                    border-radius: 12px;
                    font-size: 17px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
                ">
                    🌐 Chrome에서 열기 (자동)
                </button>
                ` : ''}
                
                <button onclick="copyUrl()" style="
                    width: 100%;
                    background: #7D5A5A;
                    color: white;
                    border: none;
                    padding: 18px;
                    border-radius: 12px;
                    font-size: 17px;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(125, 90, 90, 0.3);
                ">
                    📋 주소 복사하기
                </button>
                
                <div id="msg" style="
                    color: #28a745;
                    font-weight: bold;
                    margin-top: 15px;
                    min-height: 25px;
                    font-size: 15px;
                "></div>
                
                <p style="
                    color: #999;
                    font-size: 13px;
                    margin: 25px 0 0 0;
                    line-height: 1.5;
                ">
                    💡 Safari나 Samsung Internet도 가능합니다
                </p>
            </div>
        </div>
        
        <style>
            @keyframes shake {
                0%, 100% { transform: rotate(0deg); }
                25% { transform: rotate(-5deg); }
                75% { transform: rotate(5deg); }
            }
            body {
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
            }
        </style>
        
        <script>
            function openInChrome() {
                var intentUrl = 'intent://' + '${currentUrl}'.replace(/https?:\\\\/\\\\//, '') + 
                              '#Intent;scheme=https;package=com.android.chrome;end';
                window.location.href = intentUrl;
                
                setTimeout(function() {
                    document.getElementById('msg').innerHTML = 
                        '⚠️ Chrome이 열리지 않으면<br><small>수동으로 메뉴에서 선택해주세요</small>';
                }, 2000);
            }
            
            function copyUrl() {
                var url = '${currentUrl}';
                var msg = document.getElementById('msg');
                
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(url).then(function() {
                        msg.innerHTML = '✅ 복사 완료!<br><small>Chrome을 열어서 붙여넣기 하세요</small>';
                    }).catch(function() {
                        fallbackCopy(url, msg);
                    });
                } else {
                    fallbackCopy(url, msg);
                }
            }
            
            function fallbackCopy(text, msgDiv) {
                var textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                
                try {
                    document.execCommand('copy');
                    msgDiv.innerHTML = '✅ 복사 완료!<br><small>Chrome을 열어서 붙여넣기 하세요</small>';
                } catch(e) {
                    msgDiv.innerHTML = '⚠️ 수동으로 주소창에서 복사해주세요';
                }
                
                document.body.removeChild(textarea);
            }
        </script>
    `;
}
</script>
""", unsafe_allow_html=True)

# --- 5. PWA 지원 ---
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
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#7D5A5A">
    """
    
    st.markdown(pwa_html, unsafe_allow_html=True)

add_pwa_support()

# --- 6. 스타일 ---
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
    /* 카메라/업로드 위젯 스타일 */
    [data-testid="stCameraInput"], [data-testid="stFileUploader"] {
        border: 2px dashed #7D5A5A;
        border-radius: 10px;
        padding: 20px;
    }
    /* 상태 텍스트 스타일 조정 */
    .status-text {
        font-size: 16px;
        color: #666;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #7D5A5A;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 7. API 키 설정 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오. `.streamlit/secrets.toml` 파일에 GOOGLE_API_KEY를 추가해야 합니다.")
    st.stop()

# --- 8. 장군신(AI 모델) 함수들 ---
def get_all_available_models():
    """사용 가능한 모든 Gemini 모델 목록 가져오기"""
    try:
        all_models = []
        for model_info in genai.list_models():
            if 'generateContent' in model_info.supported_generation_methods:
                all_models.append(model_info.name)
        return all_models
    except:
        return ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-2.0-flash-exp']

def analyze_face_info(model_name, image):
    """얼굴에서 성별, 나이대, 직업 분석 (관상학 + 의상 분석)"""
    try:
        model = genai.GenerativeModel(model_name)
        analysis_prompt = """
이 사진을 보고 다음 정보를 분석해주세요:

1. 성별: 남성 또는 여성

2. 추정 나이대: 10대, 20대 초반, 20대 후반, 30대 초반, 30대 후반, 40대 초반, 40대 후반, 50대 초반, 50대 후반, 60대 초반, 60대 후반, 70대, 80대 이상 중 하나

3. 현재 직업 추정 (70% 의상/분위기 + 30% 관상학):
   - 의상 분석 (70%): 정장, 캐주얼, 유니폼, 액세서리, 메이크업, 헤어스타일 등
   - 관상학 분석 (30%):
     * 이마: 넓고 밝으면 지적 직업 (교수, 연구원, 기획자)
     * 눈빛: 날카로우면 분석/전문직 (분석가, 회계사, 개발자)
     * 코: 크고 단단하면 재물 관련 (금융, 사업가, 영업)
     * 입: 크고 표현력 좋으면 소통 직업 (강사, 방송인, 마케터)
     * 턱: 사각지고 강하면 리더십 (경영인, 관리자, 공무원)
     * 귀: 크고 두껰우면 복 많은 직업 (안정적 직장, 전문직)
   - 위 분석을 종합하여 현재 직업 3가지 추정

4. 어울리는 직업 (100% 관상학):
   - 얼굴의 오행(금목수화토), 삼정(상중하정), 오관(이목구비이) 분석
   - 위 관상학적 특징으로 본 이 사람의 운명에 맞는 천직 직업 3가지

다음 형식으로만 답변해주세요:
성별: [남성/여성]
나이대: [구체적인 나이대]
현재 직업: [직업1], [직업2], [직업3]
어울리는 직업: [직업1], [직업2], [직업3]

예시:
성별: 여성
나이대: 20대 후반
현재 직업: 마케팅, 디자인, 기획
어울리는 직업: 교육, 컨설팅, 미디어
"""
        response = model.generate_content([analysis_prompt, image])
        return response.text, None
    except Exception as e:
        return None, str(e)

def try_model_with_image(model_name, prompt, image):
    """특정 모델로 이미지 분석 시도"""
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

# --- 9. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_model' not in st.session_state:
    st.session_state.last_model = None

# --- 10. 메인 UI ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 16px;'>조선 팔도를 떠돌며 수많은 관상을 봐온 전설의 관상가</p>", unsafe_allow_html=True)
st.write("---")

# 사진 입력 방식 선택
input_method = st.radio(
    "사진 준비 방식을 선택하시오:",
    ("📸 직접 촬영", "📂 앨범 선택"),
    horizontal=True
)

# 사진 입력
if input_method == "📸 직접 촬영":
    camera_image = st.camera_input("📸 얼굴을 화면에 담으시오", label_visibility="visible")
    if camera_image:
        st.session_state.final_image = camera_image
        
elif input_method == "📂 앨범 선택":
    uploaded_file = st.file_uploader("📂 사진을 선택하시오", type=['jpg', 'jpeg', 'png'], label_visibility="visible")
    if uploaded_file:
        st.session_state.final_image = uploaded_file

# --- 11. 관상 분석 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="✅ 선택된 얼굴", use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기", type="primary"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 1단계: 장군신 찾기
            status_text.markdown("<p class='status-text'>📡 당직 서는 장군신을 찾는 중이오...</p>", unsafe_allow_html=True)
            progress_bar.progress(3)
            
            available_models = get_all_available_models()
            
            # 2단계: 이미지 열기
            image = Image.open(st.session_state.final_image)
            
            # 3단계: 성별/나이/직업 분석
            status_text.markdown("<p class='status-text'>🧐 얼굴 기본 정보 분석 중 (성별, 나이, 직업)...</p>", unsafe_allow_html=True)
            progress_bar.progress(8)
            
            face_info = None
            gender = "사람"
            age_range = ""
            current_jobs = []
            suitable_jobs = []
            
            # 첫 번째 모델로 성별/나이/직업 분석 시도
            if len(available_models) > 0:
                try:
                    face_info, error = analyze_face_info(available_models[0], image)
                    if face_info:
                        # 성별 추출
                        if "남성" in face_info:
                            gender = "남성"
                        elif "여성" in face_info:
                            gender = "여성"
                        
                        # 나이대 추출 (더 세분화)
                        age_keywords = [
                            "80대 이상", "70대", 
                            "60대 후반", "60대 초반",
                            "50대 후반", "50대 초반",
                            "40대 후반", "40대 초반",
                            "30대 후반", "30대 초반",
                            "20대 후반", "20대 초반",
                            "10대"
                        ]
                        for age_keyword in age_keywords:
                            if age_keyword in face_info:
                                age_range = age_keyword
                                break
                        
                        # 현재 직엁 추출
                        if "현재 직업:" in face_info:
                            job_line = face_info.split("현재 직업:")[1].strip().split("\n")[0]
                            current_jobs = [j.strip() for j in job_line.replace(",", " ").split() if j.strip()]
                            current_jobs = current_jobs[:3]
                        
                        # 어울리는 직엁 추출
                        if "어울리는 직업:" in face_info:
                            suitable_line = face_info.split("어울리는 직업:")[1].strip().split("\n")[0]
                            suitable_jobs = [j.strip() for j in suitable_line.replace(",", " ").split() if j.strip()]
                            suitable_jobs = suitable_jobs[:3]
                except:
                    pass
            
            # 분석 결과 표시 (UI 개선)
            result_text = f"### 📊 기본 분석 결과\n\n"
            result_text += f"👤 **성별**: {gender}\n\n"
            if age_range:
                result_text += f"📅 **추정 나이**: {age_range}\n\n"
            
            if current_jobs:
                result_text += f"💼 **현재 직업 추정**: {', '.join(current_jobs)}"
            
            if suitable_jobs:
                result_text += f"\n\n✨ **어울리는 직업**: {', '.join(suitable_jobs)}"
                
                # 현재 직업과 어울리는 직업 비교
                if current_jobs and suitable_jobs:
                    # 겹치는 직업이 있는지 확인
                    matching = any(cj in suitable_jobs or sj in current_jobs 
                                 for cj in current_jobs for sj in suitable_jobs)
                    if matching:
                        result_text += "\n\n🎉 **오호! 그대는 운명에 맞게 살고 있구나!**"
                    else:
                        result_text += "\n\n💡 **홍미롭군요. 어울리는 분야로의 전환도 고려해보시오.**"
            
            if age_range or current_jobs or suitable_jobs:
                st.info(result_text)
                
                # 직업 입력 필드 추가
                st.write("---")
                st.markdown("### ✍️ 추정이 맞나요?")
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    user_job = st.text_input(
                        "실제 직업을 입력해주세요 (선택사항)",
                        placeholder="예: 개발자, 디자이너, 학생 등",
                        key="user_job_input"
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🎤", help="음성 입력 (준비 중)"):
                        st.info("음성 입력 기능은 곧 제공됩니다!")
                
                # 사용자가 직업을 입력한 경우
                if user_job:
                    st.session_state.user_actual_job = user_job
                    st.success(f"✅ 입력하신 직업: **{user_job}**")
            
            # 4단계: 관상 분석 프로세스 시뮬레이션
            analysis_steps = [
                "🔍 1단계: 이마의 넓이와 초년운 측정 중...",
                "🔍 2단계: 눈썹의 기세와 형제운 분석 중...",
                "🔍 3단계: 코의 높이와 재물운 계산 중...",
                "🔍 4단계: 입술의 모양과 말년운 확인 중...",
                "🔍 5단계: 얼굴의 전체적인 조화(오행) 분석 중..."
            ]
            
            for i, step in enumerate(analysis_steps):
                status_text.markdown(f"<p class='status-text'>{step}</p>", unsafe_allow_html=True)
                progress_bar.progress(8 + (i + 1) * 14)
                time.sleep(1.0)

            # 5단계: AI 프롬프트 (성별/나이/직업 정보 포함)
            gender_age_info = ""
            if gender and age_range:
                job_info = ""
                job_match_comment = ""
                
                if current_jobs:
                    job_info += f"\n- 추정 현재 직업: {', '.join(current_jobs)}"
                
                if suitable_jobs:
                    job_info += f"\n- 관상으로 본 어울리는 직업: {', '.join(suitable_jobs)}"
                    
                    # 사용자 입력 직업 확인 후 매칭 분석
                    actual_job = st.session_state.get('user_actual_job', '')
                    
                    if actual_job:
                        # 실제 직업과 어울리는 직업 비교
                        matching = any(sj.lower() in actual_job.lower() or actual_job.lower() in sj.lower() 
                                     for sj in suitable_jobs)
                        if matching:
                            job_match_comment = f"""

**운명 매칭 분석:**
오호라! 그대가 하고 계신 '{actual_job}' 일이 마침 어울리는 직업과 일치하는군요!
그대는 운명이 정한 길을 걷고 계십니다. 이 길을 계속 가면 큰 성취를 이룰 것이오.
그대의 얼굴에서 붉은 빛이 보이는군요! 하늘이 정한 길입니다!
"""
                        else:
                            job_match_comment = f"""

**운명 매칭 분석:**
흔, 현재 '{actual_job}' 일도 나쁘지 않으나, 관상으로 보니 그대는 {', '.join(suitable_jobs)} 같은 분야가 더 잘 맞는 것 같소.
현재 길에서 성실히 경험을 쌓으면서, 향후 이런 분야로 길을 틀어보는 것도 고려해보시오.
그대의 얼굴에서 변화의 기운이 보이는군요! 새로운 기회가 올 것이오.
"""
                    elif current_jobs:
                        # 사용자 입력 없으면 추정 직업으로 비교
                        matching = any(cj in suitable_jobs or sj in current_jobs 
                                     for cj in current_jobs for sj in suitable_jobs)
                        if matching:
                            job_match_comment = f"""

**운명 매칭 분석:**
현재 그대가 하고 있는 일({', '.join(current_jobs)})이 관상으로 본 어울리는 직업과 일치하는군요! 
오호! 그대는 운명에 맞게 살고 있습니다. 
이 길을 계속 가면 큰 성취를 이룰 것이오. 
그대의 얼굴에서 붉은 빛이 보이는군요!
"""
                        else:
                            job_match_comment = f"""

**운명 매칭 분석:**
홍, 현재 그대가 하고 있는 일({', '.join(current_jobs)})도 좋지만,
관상으로 보니 {', '.join(suitable_jobs)} 계열의 직업이 그대의 운명과 더 잘 맞는 것 같소.
향후 새로운 길을 모색한다면, 이 분야를 한 번 고려해보는 것도 좋겠구려.
그대의 얼굴에서 변화의 기운이 보이는군요!
"""
                
                gender_age_info = f"""

**분석 대상 정보:**
- 성별: {gender}
- 추정 나이대: {age_range}{job_info}{job_match_comment}

위 정보를 바탕으로 {gender}의 {age_range} 시기에 맞는 관상을 봐주세요.
예를 들어:
- {gender}의 특성에 맞는 연애운, 결혼운, 직업운 분석
- {age_range}에 맞는 현재와 미래 운세 예측
- {age_range} 시기에 주의할 점과 기회
- 직업 적성 분석 시 위 직업 정보 고려
"""
            
            prompt = f"""
당신의 이름은 '아솔'입니다. 조선 팔도에서 가장 용한 전설적인 관상가입니다.
이 사진의 인물을 보고 다음 내용을 바탕으로 관상을 **매우 상세하고 긍정적으로** 재미있게 봐주세요.
말투는 위엄 있으면서도 친근한 사극 톤("~하오", "~이오", "~구려", "~하옵니다")을 사용하세요.{gender_age_info}

[아솔의 감정서 양식]

🎭 **인상 총평 및 삼정(三停) 분석**
- **첫인상**: 이 사람의 첫인상과 전체적인 기운을 매우 긍정적으로 묘사 (최소 5-6문장)
  - 전체적인 얼굴 균형과 조화
  - 눈에 띄는 장점과 매력 포인트
  - 타고난 복과 기운
- **상정(上停, 이마 부분)**: 이마의 넓이, 높이, 굴곡으로 보는 초년운(0-30세) 매우 상세 분석 (5문장 이상)
  - 학업운과 지적 능력
  - 부모덕과 조상덕
  - 20대 운세의 흐름
- **중정(中停, 눈썹-코)**: 눈썹과 코의 형태로 보는 중년운(30-50세) 매우 상세 분석 (5문장 이상)
  - 재물운과 사업운
  - 배우자운과 가정운
  - 30-40대 전성기 예측
- **하정(下停, 인중-턱)**: 입과 턱의 형태로 보는 말년운(50세 이후) 상세 분석 (4문장 이상)
  - 자손운과 복록
  - 노년의 건강과 재물
  - 말년의 안정감

💰 **재물운 및 사업운**
- **코(재물궁)**: 코의 크기, 높이, 콧방울 상태로 보는 재물 축적 능력 (최소 6-7문장)
  - 코의 전체적인 형태 분석
  - 재물을 모으는 능력과 방식
  - 큰돈을 만질 시기
  - 투자 성향과 재테크 능력
  - 사업 수완
- **광대뼈**: 권력운과 리더십, 사회적 지위 분석 (3문장)
- **돈을 버는 스타일**: 투자형인지, 근면형인지, 사업형인지 매우 구체적으로 설명 (4문장)
- **재물이 들어오는 시기**: 20대, 30대, 40대, 50대별 재물운 상세 설명
- **재물 증식 방법**: 어떤 방식으로 돈을 불릴 수 있는지
- **주의할 점**: 재물 손실 가능성 (긍정적으로 조언)

❤️ **연애운 및 애정운**
- **눈매(처첩궁)**: 눈의 크기, 각도, 눈빛으로 보는 이성운 (최소 6-7문장)
  - 눈의 전체적인 인상
  - 이성에게 주는 매력
  - 연애 스타일과 패턴
  - 애정운이 강한 시기
  - 이성과의 궁합
- **입술**: 애정 표현 방식과 연애 스타일 (3문장)
- **도화살 유무**: 이성에게 인기가 많은 타입인지 구체적으로
- **이상형**: 어떤 스타일의 사람을 좋아하는지 자세히
- **결혼운**: 언제쯤 결혼할 가능성이 높은지, 결혼 후 생활
- **배우자의 특징**: 미래 배우자의 성격, 외모, 직업 특징 (4문장)
- **애정 관계 조언**: 연애를 잘하는 방법

🏆 **직업운 및 적성**
- **이마와 눈썹**: 학업 능력과 지적 수준 상세 분석 (3문장)
- **적합한 직업군**: 구체적인 직업 5-7가지 추천 + 이유
- **승진운과 출세운**: 조직에서의 성공 가능성 매우 상세히 (4문장)
- **창업 적성**: 사업가 기질, 어떤 사업이 잘 맞는지 (3문장)
- **재능과 특기**: 숨겨진 재능 발견
- **성공 시기**: 몇 살에 크게 성공할 가능성

🍀 **건강운 및 주의사항**
- **얼굴 색**: 현재 건강 상태 긍정적 분석 (2문장)
- **특정 부위**: 주의해야 할 신체 부위 (부드럽게 조언)
- **건강 관리 조언**: 구체적인 건강 관리법 3가지
- **장수와 복**: 전반적인 건강운

👥 **대인관계 및 성격**
- **귀**: 복과 장수, 재물 흡수력 (3문장)
- **눈썹**: 형제운, 친구운, 인복 (3문장)
- **입**: 말솜씨와 대인관계 능력 (3문장)
- **성격 특징**: 장점 5가지, 보완할 점 2가지 (각각 상세히)
- **리더십**: 사람을 이끄는 능력
- **인맥운**: 귀인을 만나는 운

🔮 **아솔의 특별 처방**
- **개운 방향**: 길한 방향 (동서남북 중) + 이유
- **개운 색상**: 도움이 되는 색깔 2-3가지 + 활용법
- **주의해야 할 시기**: 조심해야 할 나이나 시기 + 대처법
- **운을 높이는 습관**: 구체적인 행동 지침 5가지
- **부적 제안**: 몸에 지니면 좋을 물건이나 액세서리 3가지
- **개운 음식**: 먹으면 좋은 음식
- **개운 장소**: 가면 좋은 장소

⭐ **종합 운세 평가 (별 5개 만점)**
- 재물운: ⭐⭐⭐⭐ (별 개수로 표시, 평균 3.5~4개)
- 애정운: ⭐⭐⭐⭐ (별 개수로 표시, 평균 3.5~4개)
- 건강운: ⭐⭐⭐⭐ (별 개수로 표시, 평균 3.5~4개)
- 직업운: ⭐⭐⭐⭐ (별 개수로 표시, 평균 3.5~4개)
- 종합 평가: 한 줄 긍정적 요약

📜 **아솔의 한마디**
- 마지막으로 이 사람에게 용기와 희망을 주는 따뜻한 말 (4-5문장)
- 미래에 대한 긍정적 전망
- 응원의 메시지

**작성 지침:**
1. 각 항목마다 **최소 4-5문장 이상** 매우 상세하게 작성
2. 구체적인 나이, 시기, 숫자를 언급하여 신빙성 높이기
3. **긍정 80% + 현실적 조언 20%** 비율 유지 (현실적이면서 희망적으로)
4. **별점은 평균 3.5~4개** 주기 (최소 3개, 최대 5개)
5. 이모티콘 적절히 사용 (과하지 않게)
6. **굵게**, *이탤릭* 강조 문법 활용
7. 전체 분량: **최소 1200자 이상** 작성 (기존보다 50% 증가)
8. 재미있고 읽기 쉽게, 하지만 충분히 전문적으로
9. 사람들에게 희망과 용기를 주는 톤 유지
10. 단점보다는 보완 가능한 점으로 부드럽게 표현
"""
            
            # 6단계: 관상 분석 실행
            response = None
            successful_model = None
            
            for model_name in available_models:
                display_name = model_name.replace('models/', '').replace('gemini-', '').upper()
                status_text.markdown(f"<p class='status-text'>⚡ <strong>{display_name}</strong> 장군신 소환 중...</p>", unsafe_allow_html=True)
                progress_bar.progress(85)
                
                response, error = try_model_with_image(model_name, prompt, image)
                
                if response is not None:
                    successful_model = display_name
                    break
                elif error == "quota_exceeded":
                    status_text.markdown(f"<p class='status-text'>💤 {display_name} 장군신이 휴식 중... 다음 장군신 호출 중...</p>", unsafe_allow_html=True)
                    time.sleep(0.8)
            
            # 7단계: 결과 처리
            if response is None:
                st.error("⚠️ 모든 장군신이 휴식 중입니다. 잠시 후 다시 시도해주세요.")
                progress_bar.empty()
                status_text.empty()
                st.stop()
            
            status_text.markdown(f"<p class='status-text'>✅ <strong>{successful_model}</strong> 장군신이 감정서를 작성했소!</p>", unsafe_allow_html=True)
            progress_bar.progress(100)
            time.sleep(1.0)
            
            progress_bar.empty()
            status_text.empty()
            
            # 결과 저장
            st.session_state.last_result = response.text
            st.session_state.last_model = successful_model
            
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
                    transition: all 0.3s;
                    font-family: -apple-system, sans-serif;
                " onmouseover="this.style.transform='translateY(-2px)';"
                   onmouseout="this.style.transform='translateY(0)';">
                    📋 관상 결과 복사하기
                </button>
                
                <div id="copy-result-msg" style="
                    margin-top: 15px;
                    color: #28a745;
                    font-weight: bold;
                    font-size: 15px;
                    min-height: 25px;
                    opacity: 0;
                    transition: opacity 0.3s;
                "></div>
            </div>
            
            <script>
                function copyResult() {{
                    var resultText = "📜 관상가 아솔의 감정서 (by {successful_model} 장군신)\\n\\n{result_text_escaped}\\n\\n🧙‍♂️ 관상가 아솔 - https://gwangsangapp-ryes95aziswadr3h9bhcug.streamlit.app/";
                    
                    var messageDiv = document.getElementById('copy-result-msg');
                    var button = event.target;
                    
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        navigator.clipboard.writeText(resultText)
                            .then(function() {{
                                showCopySuccess(messageDiv, button);
                            }})
                            .catch(function() {{
                                fallbackCopy(resultText, messageDiv, button);
                            }});
                    }} else {{
                        fallbackCopy(resultText, messageDiv, button);
                    }}
                }}
                
                function fallbackCopy(text, messageDiv, button) {{
                    var textarea = document.createElement('textarea');
                    textarea.value = text;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    textarea.select();
                    
                    try {{
                        var successful = document.execCommand('copy');
                        if (successful) {{
                            showCopySuccess(messageDiv, button);
                        }} else {{
                            showCopyError(messageDiv);
                        }}
                    }} catch(err) {{
                        showCopyError(messageDiv);
                    }}
                    
                    document.body.removeChild(textarea);
                }}
                
                function showCopySuccess(messageDiv, button) {{
                    messageDiv.innerHTML = '✅ 관상 결과가 복사되었습니다!';
                    messageDiv.style.opacity = '1';
                    
                    var originalText = button.innerHTML;
                    button.innerHTML = '✅ 복사 완료!';
                    button.style.background = '#28a745';
                    
                    setTimeout(function() {{
                        messageDiv.style.opacity = '0';
                        button.innerHTML = originalText;
                        button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    }}, 3000);
                }}
                
                function showCopyError(messageDiv) {{
                    messageDiv.innerHTML = '⚠️ 복사 실패. 수동으로 선택해서 복사해주세요.';
                    messageDiv.style.color = '#dc3545';
                    messageDiv.style.opacity = '1';
                    
                    setTimeout(function() {{
                        messageDiv.style.opacity = '0';
                        messageDiv.style.color = '#28a745';
                    }}, 4000);
                }}
            </script>
            """, height=120)
            
            st.balloons()

        except Exception as e:
            st.error(f"⚠️ 예기치 못한 에러가 났소. (내용: {e})")
            progress_bar.empty()
            status_text.empty()

# --- 12. 하단 안내 및 푸터 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 <b>개인정보 보호:</b> 모든 사진은 분석 후 즉시 삭제됩니다.</p>
    <p>🎲 <b>엔터테인먼트 목적:</b> 본 서비스는 재미를 위한 것으로, 실제 운세와 무관합니다.</p>
    <p style="margin-top: 20px; color: #999; font-size: 12px;">
        🧙‍♂️ 관상가 아솔 © 2024 | Powered by Google Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
