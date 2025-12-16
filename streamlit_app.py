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

# --- 2. [최우선] 모든 인앱 브라우저 무조건 차단 ---
st.components.v1.html("""
<script>
    (function() {
        var userAgent = navigator.userAgent.toLowerCase();
        var currentUrl = window.location.href;
        
        // 모든 인앱 브라우저 감지 (확장된 목록)
        var isInApp = userAgent.indexOf("kakao") > -1 ||          // 카카오톡
                      userAgent.indexOf("kakaotalk") > -1 ||       // 카카오톡
                      userAgent.indexOf("instagram") > -1 ||       // 인스타그램
                      userAgent.indexOf("line") > -1 ||            // 라인
                      userAgent.indexOf("fban") > -1 ||            // 페이스북
                      userAgent.indexOf("fbav") > -1 ||            // 페이스북 앱
                      userAgent.indexOf("fb_iab") > -1 ||          // 페이스북 인앱
                      userAgent.indexOf("naver") > -1 ||           // 네이버
                      userAgent.indexOf("snapchat") > -1 ||        // 스냅챗
                      userAgent.indexOf("twitter") > -1 ||         // 트위터
                      userAgent.indexOf("whatsapp") > -1 ||        // 왓츠앱
                      userAgent.indexOf("telegram") > -1 ||        // 텔레그램
                      userAgent.indexOf("wechat") > -1 ||          // 위챗
                      userAgent.indexOf("band") > -1 ||            // 밴드
                      userAgent.indexOf("daum") > -1 ||            // 다음
                      userAgent.indexOf("zumapp") > -1;            // 줌 인터넷
        
        // 인앱 브라우저 감지 시
        if (isInApp) {
            console.log('인앱 브라우저 감지됨 - Chrome으로 강제 이동');
            
            // Android: Chrome 앱으로 강제 리다이렉트
            if (/android/i.test(userAgent)) {
                // Intent 스킴으로 Chrome 앱 직접 호출
                var intentUrl = 'intent://' + currentUrl.replace(/https?:\\/\\//, '') + 
                                '#Intent;scheme=https;package=com.android.chrome;end';
                
                window.location.href = intentUrl;
                
                // 500ms 후에도 열리지 않으면 안내 화면
                setTimeout(function() {
                    showBlockScreen();
                }, 500);
                
            } else if (/iphone|ipad/i.test(userAgent)) {
                // iOS: 자동 리다이렉트 불가능, 즉시 안내 화면
                showBlockScreen();
                
            } else {
                // 기타 환경: 안내 화면
                showBlockScreen();
            }
        }
        
        function showBlockScreen() {
            // 전체 화면 덮어씌우기
            document.body.innerHTML = '';
            document.body.style.margin = '0';
            document.body.style.padding = '0';
            document.body.style.overflow = 'hidden';
            
            var blockDiv = document.createElement('div');
            blockDiv.innerHTML = `
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #FEE500 0%, #FFD700 100%);
                    z-index: 999999;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    box-sizing: border-box;
                ">
                    <div style="
                        background: white;
                        padding: 40px 30px;
                        border-radius: 20px;
                        max-width: 400px;
                        width: 100%;
                        text-align: center;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        box-sizing: border-box;
                    ">
                        <!-- 애니메이션 아이콘 -->
                        <div style="
                            font-size: 80px;
                            margin-bottom: 20px;
                            animation: bounce 1s infinite;
                        ">
                            🚫
                        </div>
                        
                        <!-- 메인 제목 -->
                        <h1 style="
                            color: #d32f2f;
                            font-size: 24px;
                            font-weight: bold;
                            margin: 0 0 15px 0;
                            line-height: 1.3;
                        ">
                            인앱 브라우저에서는<br>사용할 수 없습니다
                        </h1>
                        
                        <!-- 설명 -->
                        <p style="
                            color: #666;
                            font-size: 16px;
                            line-height: 1.6;
                            margin: 0 0 30px 0;
                        ">
                            카메라 기능을 사용하려면<br>
                            <b style="color: #333;">Chrome 브라우저</b>에서 열어야 합니다
                        </p>
                        
                        <!-- 안내 박스 -->
                        <div style="
                            background: #f8f9fa;
                            padding: 20px;
                            border-radius: 12px;
                            text-align: left;
                            margin-bottom: 25px;
                            border: 2px solid #e9ecef;
                        ">
                            <div style="
                                font-weight: bold;
                                color: #333;
                                margin-bottom: 12px;
                                font-size: 15px;
                            ">
                                📱 Chrome으로 여는 방법:
                            </div>
                            <ol style="
                                margin: 0;
                                padding-left: 20px;
                                color: #555;
                                font-size: 14px;
                                line-height: 1.8;
                            ">
                                <li>우측 상단 <b style="color: #000;">점 3개 (⋮)</b> 클릭</li>
                                <li><b style="color: #000;">"다른 브라우저로 열기"</b> 선택</li>
                                <li><b style="color: #000;">"Chrome"</b> 선택</li>
                            </ol>
                        </div>
                        
                        <!-- 주소 복사 버튼 -->
                        <button onclick="copyUrlAndNotify()" style="
                            width: 100%;
                            background: #7D5A5A;
                            color: white;
                            border: none;
                            padding: 16px;
                            border-radius: 12px;
                            font-size: 16px;
                            font-weight: bold;
                            cursor: pointer;
                            box-shadow: 0 4px 12px rgba(125, 90, 90, 0.3);
                            transition: all 0.2s;
                        " onmousedown="this.style.transform='scale(0.98)';"
                           onmouseup="this.style.transform='scale(1)';">
                            📋 주소 복사하고 Chrome에서 열기
                        </button>
                        
                        <!-- 복사 완료 메시지 -->
                        <div id="copy-message" style="
                            color: #28a745;
                            font-weight: bold;
                            margin-top: 15px;
                            height: 25px;
                            font-size: 15px;
                        "></div>
                        
                        <!-- 하단 추가 안내 -->
                        <p style="
                            color: #999;
                            font-size: 13px;
                            margin: 20px 0 0 0;
                            line-height: 1.5;
                        ">
                            💡 Chrome이 없다면<br>
                            <b>Safari</b>나 <b>Samsung Internet</b>도 가능합니다
                        </p>
                    </div>
                </div>
                
                <style>
                    @keyframes bounce {
                        0%, 100% { transform: translateY(0); }
                        50% { transform: translateY(-10px); }
                    }
                </style>
                
                <script>
                    function copyUrlAndNotify() {
                        var url = '${currentUrl}';
                        var messageDiv = document.getElementById('copy-message');
                        
                        if (navigator.clipboard && navigator.clipboard.writeText) {
                            navigator.clipboard.writeText(url)
                                .then(function() {
                                    messageDiv.innerHTML = '✅ 주소가 복사되었습니다!<br><small style="font-size: 12px;">이제 Chrome을 열어서 붙여넣기 하세요</small>';
                                    setTimeout(function() {
                                        messageDiv.textContent = '';
                                    }, 4000);
                                })
                                .catch(function() {
                                    fallbackCopy(url);
                                });
                        } else {
                            fallbackCopy(url);
                        }
                    }
                    
                    function fallbackCopy(text) {
                        var messageDiv = document.getElementById('copy-message');
                        var textarea = document.createElement('textarea');
                        textarea.value = text;
                        textarea.style.position = 'fixed';
                        textarea.style.opacity = '0';
                        document.body.appendChild(textarea);
                        
                        if (navigator.userAgent.match(/ipad|iphone/i)) {
                            var range = document.createRange();
                            range.selectNodeContents(textarea);
                            var selection = window.getSelection();
                            selection.removeAllRanges();
                            selection.addRange(range);
                            textarea.setSelectionRange(0, 999999);
                        } else {
                            textarea.select();
                        }
                        
                        try {
                            var successful = document.execCommand('copy');
                            if (successful) {
                                messageDiv.innerHTML = '✅ 주소가 복사되었습니다!<br><small style="font-size: 12px;">Chrome을 열어서 붙여넣기 하세요</small>';
                            } else {
                                messageDiv.innerHTML = '⚠️ 수동으로 주소를 복사해주세요';
                            }
                        } catch (err) {
                            messageDiv.innerHTML = '⚠️ 수동으로 주소를 복사해주세요';
                        }
                        
                        document.body.removeChild(textarea);
                        
                        setTimeout(function() {
                            messageDiv.textContent = '';
                        }, 4000);
                    }
                </script>
            `;
            
            document.body.appendChild(blockDiv);
        }
    })();
</script>
""", height=0)

# --- 3. PWA 지원 (정상 브라우저용) ---
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
        "icons": [
            {
                "src": "https://em-content.zobj.net/source/apple/391/mage_1f9d9.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    
    import json
    manifest_json = json.dumps(manifest)
    
    pwa_html = f"""
    <head>
        <link rel="manifest" href="data:application/json;base64,{base64.b64encode(manifest_json.encode()).decode()}">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#7D5A5A">
    </head>
    
    <script>
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            const installBtn = document.getElementById('pwa-install-btn');
            if (installBtn) installBtn.style.display = 'block';
        }});
        
        function installPWA() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        alert('✅ 설치 완료! 홈 화면에서 "아솔"을 찾아보세요.');
                    }}
                    deferredPrompt = null;
                    const installBtn = document.getElementById('pwa-install-btn');
                    if (installBtn) installBtn.style.display = 'none';
                }});
            }} else {{
                const ua = navigator.userAgent.toLowerCase();
                let msg = '';
                if (/iphone|ipad/.test(ua)) {{
                    msg = '📱 iOS: 하단 공유버튼 → "홈 화면에 추가"';
                }} else {{
                    msg = '📱 메뉴(⋮) → "홈 화면에 추가" 또는 "앱 설치"';
                }}
                alert(msg);
            }}
        }}
    </script>
    """
    
    st.components.v1.html(pwa_html, height=0)

add_pwa_support()

# --- 4. 스타일 ---
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
    #pwa-install-btn {
        display: none;
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. API 키 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오.")
    st.stop()

# --- 6. 장군신 함수들 ---
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

# --- 7. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

# --- 8. 메인 UI ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)

st.markdown("""
<button id="pwa-install-btn" onclick="installPWA()">
    💡 홈 화면에 추가하면 앱처럼 빠르게 접속할 수 있소!
</button>
""", unsafe_allow_html=True)

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

# --- 9. 분석 로직 ---
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

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 모든 사진은 분석 후 즉시 삭제됩니다</p>
    <p>🧙‍♂️ 관상가 아솔 © 2025</p>
</div>
""", unsafe_allow_html=True)