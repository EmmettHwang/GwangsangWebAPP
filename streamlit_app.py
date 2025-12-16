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

# --- 2. PWA 매니페스트 및 홈 화면 추가 기능 ---
def add_pwa_and_install_button():
    """PWA 지원 + 홈 화면 추가 버튼"""
    
    manifest = {
        "name": "관상가 아솔",
        "short_name": "아솔",
        "description": "조선 팔도 최고의 관상가 아솔",
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
            },
            {
                "src": "https://em-content.zobj.net/source/apple/391/mage_1f9d9.png",
                "sizes": "512x512",
                "type": "image/png"
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
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="관상가 아솔">
        <meta name="theme-color" content="#7D5A5A">
        <link rel="apple-touch-icon" href="https://em-content.zobj.net/source/apple/391/mage_1f9d9.png">
    </head>
    
    <script>
        // PWA 설치 프롬프트 저장
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            
            // 설치 버튼 표시
            const installBtn = document.getElementById('pwa-install-btn');
            if (installBtn) {{
                installBtn.style.display = 'block';
            }}
        }});
        
        // 설치 버튼 클릭 핸들러
        function installPWA() {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('PWA 설치 승인됨');
                        showInstallSuccess();
                    }} else {{
                        console.log('PWA 설치 거부됨');
                    }}
                    deferredPrompt = null;
                    
                    // 설치 버튼 숨기기
                    const installBtn = document.getElementById('pwa-install-btn');
                    if (installBtn) {{
                        installBtn.style.display = 'none';
                    }}
                }});
            }} else {{
                // PWA 설치 불가능한 경우 (이미 설치됨 또는 지원 안 함)
                showInstallGuide();
            }}
        }}
        
        function showInstallSuccess() {{
            alert('✅ 설치 완료! 홈 화면에서 "아솔" 아이콘을 찾아보세요.');
        }}
        
        function showInstallGuide() {{
            const userAgent = navigator.userAgent.toLowerCase();
            let message = '';
            
            if (/iphone|ipad/.test(userAgent)) {{
                message = '📱 iOS 설치 방법:\\n\\n1. 하단 공유 버튼 (□↑) 클릭\\n2. "홈 화면에 추가" 선택\\n3. "추가" 클릭';
            }} else if (/android/.test(userAgent)) {{
                message = '📱 Android 설치 방법:\\n\\n1. 우측 상단 ⋮ 메뉴 클릭\\n2. "홈 화면에 추가" 또는 "앱 설치" 선택';
            }} else {{
                message = '💡 모바일 브라우저(Chrome/Safari)에서 접속하면\\n홈 화면에 추가할 수 있습니다!';
            }}
            
            alert(message);
        }}
        
        // 이미 설치된 경우 버튼 숨기기
        window.addEventListener('appinstalled', () => {{
            const installBtn = document.getElementById('pwa-install-btn');
            if (installBtn) {{
                installBtn.style.display = 'none';
            }}
        }});
        
        // 스탠드얼론 모드에서 실행 중인지 확인
        if (window.matchMedia('(display-mode: standalone)').matches) {{
            const installBtn = document.getElementById('pwa-install-btn');
            if (installBtn) {{
                installBtn.style.display = 'none';
            }}
        }}
    </script>
    """
    
    st.components.v1.html(pwa_html, height=0)

# PWA 지원 추가
add_pwa_and_install_button()

# --- 3. 인앱 브라우저 차단 ---
st.components.v1.html("""
<script>
    var userAgent = navigator.userAgent.toLowerCase();
    var currentUrl = window.location.href;
    
    var isInApp = userAgent.indexOf("kakao") > -1 || 
                  userAgent.indexOf("instagram") > -1 || 
                  userAgent.indexOf("line") > -1 ||
                  userAgent.indexOf("fban") > -1 ||
                  userAgent.indexOf("fbav") > -1 ||
                  userAgent.indexOf("naver") > -1;
    
    if (isInApp) {
        if (/android/i.test(userAgent)) {
            var deeplink = 'intent://' + currentUrl.replace(/https?:\\/\\//, '') + '#Intent;scheme=https;package=com.android.chrome;end';
            window.location.href = deeplink;
            setTimeout(showWarning, 500);
        } else {
            showWarning();
        }
    }
    
    function showWarning() {
        document.body.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        z-index: 99999; display: flex; justify-content: center; align-items: center; 
                        padding: 20px; font-family: -apple-system, sans-serif;">
                
                <div style="background: white; padding: 40px 30px; border-radius: 20px; 
                            max-width: 400px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                    
                    <div style="font-size: 60px; margin-bottom: 20px;">📱</div>
                    
                    <h1 style="color: #d32f2f; margin-bottom: 15px; font-size: 22px;">
                        외부 브라우저에서 열어주세요
                    </h1>
                    
                    <p style="font-size: 15px; line-height: 1.6; color: #666; margin-bottom: 25px;">
                        카메라 기능을 사용하려면<br>
                        <b>Chrome</b> 또는 <b>Safari</b>로 열어야 합니다
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; 
                                text-align: left; margin-bottom: 20px;">
                        <div style="font-weight: bold; margin-bottom: 10px; color: #333;">
                            📋 여는 방법:
                        </div>
                        <ol style="margin: 0; padding-left: 20px; color: #666; font-size: 14px; line-height: 1.8;">
                            <li>우측 상단 <b>⋮</b> 또는 <b>공유</b> 버튼</li>
                            <li><b>"Chrome으로 열기"</b> 선택</li>
                            <li>카메라 권한 허용</li>
                        </ol>
                    </div>
                    
                    <button onclick="copyUrl()" style="width: 100%; background: #7D5A5A; color: white; 
                            border: none; padding: 15px; border-radius: 10px; font-size: 15px; 
                            font-weight: bold; cursor: pointer;">
                        주소 복사하기
                    </button>
                    
                    <div id="msg" style="color: #28a745; margin-top: 10px; height: 20px; font-size: 14px;"></div>
                </div>
            </div>
            
            <script>
                function copyUrl() {
                    var url = '${currentUrl}';
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(url).then(() => {
                            document.getElementById('msg').textContent = '✅ 복사 완료!';
                            setTimeout(() => document.getElementById('msg').textContent = '', 2000);
                        });
                    }
                }
            </script>
        `;
    }
</script>
""", height=0)

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
    
    /* 홈 화면 추가 버튼 스타일 */
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
        transition: transform 0.2s;
    }
    
    #pwa-install-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    #pwa-install-btn:active {
        transform: translateY(0);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. API 키 연결 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오.")
    st.stop()

# --- 6. 장군신 함수들 (이전과 동일) ---
def get_all_available_models():
    try:
        all_models = []
        for model_info in genai.list_models():
            if 'generateContent' in model_info.supported_generation_methods:
                all_models.append(model_info.name)
        return all_models
    except:
        return [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-1.5-pro-latest',
            'gemini-2.0-flash-exp',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro'
        ]

def try_model_with_image(model_name, prompt, image):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image])
        return response, None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return None, "quota_exceeded"
        elif "404" in error_msg or "not found" in error_msg.lower():
            return None, "model_not_found"
        else:
            return None, error_msg

# --- 7. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None

# --- 8. 화면 구성 ---
st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)

# 💡 홈 화면 추가 버튼 (핵심!)
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

# --- 9. 분석 로직 (이전과 동일) ---
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
            
            if not available_models:
                st.error("⚠️ 장군신 명단을 불러올 수 없소. 네트워크를 확인하시오.")
                st.stop()

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
            tried_models = []
            
            for model_name in available_models:
                display_name = model_name.replace('models/', '').replace('gemini-', '').upper()
                
                status_text.markdown(f"### ⚡ **{display_name}** 장군신 소환 중...")
                progress_bar.progress(85)
                
                response, error = try_model_with_image(model_name, prompt, image)
                tried_models.append(model_name)
                
                if response is not None:
                    successful_model = display_name
                    break
                else:
                    if error == "quota_exceeded":
                        status_text.markdown(f"##### 💤 {display_name} 장군신이 휴식 중이오... 다른 장군신 찾는 중...")
                        time.sleep(0.8)
                    elif error == "model_not_found":
                        continue
                    else:
                        continue
            
            if response is None:
                st.error("⚠️ 모든 장군신이 휴식 중이거나 소환할 수 없소.")
                st.info(f"💡 시도한 장군신: {len(tried_models)}명")
                st.warning("잠시 후 다시 시도하시거나, 다른 시간대에 찾아주시오.")
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

# --- 10. 하단 안내 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 <b>개인정보 보호:</b> 모든 사진은 분석 후 즉시 삭제됩니다.</p>
    <p>🧙‍♂️ 관상가 아솔 © 2024</p>
</div>
""", unsafe_allow_html=True)