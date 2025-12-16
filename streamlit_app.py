import streamlit as st
from PIL import Image
import google.generativeai as genai
import time
import base64

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="관상가 아솔",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. [핵심] 인앱 브라우저 차단 (최상단에 즉시 실행) ---
# height를 1로 설정하고 즉시 실행되도록 수정
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
    
    // 즉시 실행
    var ua = navigator.userAgent.toLowerCase();
    var href = window.top.location.href || window.location.href;
    
    // 인앱 브라우저 패턴 (더 정확한 감지)
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
        // 부모 window에 메시지 전송
        if (window.parent) {
            window.parent.postMessage({
                type: 'IN_APP_BROWSER_DETECTED',
                url: href,
                userAgent: ua
            }, '*');
        }
        
        // Android: Chrome으로 리다이렉트 시도
        if (ua.indexOf('android') > -1) {
            var intentUrl = 'intent://' + href.replace(/https?:\\/\\//, '') + 
                          '#Intent;scheme=https;package=com.android.chrome;end';
            
            // top window에서 리다이렉트
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

# --- 3. 추가 차단 레이어 (Streamlit 메인 영역) ---
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data.type === 'IN_APP_BROWSER_DETECTED') {
        // 인앱 브라우저 감지됨 - 전체 화면 차단
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
                var intentUrl = 'intent://' + '${currentUrl}'.replace(/https?:\\/\\//, '') + 
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
    
    import json
    manifest_json = json.dumps(manifest)
    
    pwa_html = f"""
    <link rel="manifest" href="data:application/json;base64,{base64.b64encode(manifest_json.encode()).decode()}">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
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
    </style>
    """, unsafe_allow_html=True)

# --- 6. API 키 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오.")
    st.stop()

# --- 7. 장군신 함수들 ---
def get_all_available_models():
    try:
        all_models = []
        for model_info in genai.list_models():
            if 'generateContent' in model_info.supported_generation_methods:
                all_models.append(model_info.name)
        return all_models
    except:
        return ['gemini-1.5-flash', 'gemini-1.5-pro', 'models/gemini-1.5-flash']

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

# --- 9. 메인 UI ---
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

# --- 10. 분석 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="선택된 얼굴", use_container_width=True)

    if st.button("🔮 아솔에게 관상 묻기"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("### 📡 당직 서는 장군신을 찾는 중이오...")
            progress_bar.progress(5)
            
            available_models = get_all_available_models()

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
            
            for model_name in available_models:
                display_name = model_name.replace('models/', '').replace('gemini-', '').upper()
                status_text.markdown(f"### ⚡ **{display_name}** 장군신 소환 중...")
                progress_bar.progress(85)
                
                response, error = try_model_with_image(model_name, prompt, image)
                
                if response is not None:
                    successful_model = display_name
                    break
                elif error == "quota_exceeded":
                    status_text.markdown(f"### 💤 {display_name} 장군신이 휴식 중...")
                    time.sleep(0.8)
            
            if response is None:
                st.error("⚠️ 모든 장군신이 휴식 중입니다. 잠시 후 다시 시도해주세요.")
                st.stop()
            
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

# --- 11. 하단 안내 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 <b>개인정보 보호:</b> 모든 사진은 분석 후 즉시 삭제됩니다.</p>
    <p>🧙‍♂️ 관상가 아솔 © 2024</p>
</div>
""", unsafe_allow_html=True)