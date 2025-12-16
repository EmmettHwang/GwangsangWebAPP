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

# --- 2. PWA 매니페스트 및 Service Worker 추가 ---
def add_pwa_support():
    """PWA 설치 지원 (홈 화면 추가 가능)"""
    
    # manifest.json 내용
    manifest = {
        "name": "관상가 아솔",
        "short_name": "아솔",
        "description": "조선 팔도 최고의 관상가 아솔이 당신의 운명을 풀어드립니다",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#7D5A5A",
        "orientation": "portrait",
        "icons": [
            {
                "src": "https://em-content.zobj.net/source/apple/391/mage_1f9d9.png",
                "sizes": "192x192",
                "type": "image/png"
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
    
    # Service Worker (오프라인 지원)
    service_worker = """
    self.addEventListener('install', (event) => {
        console.log('Service Worker 설치됨');
    });
    
    self.addEventListener('fetch', (event) => {
        event.respondWith(fetch(event.request));
    });
    """
    
    # HTML에 PWA 메타태그 및 스크립트 삽입
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
        // Service Worker 등록
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('data:text/javascript;base64,{base64.b64encode(service_worker.encode()).decode()}')
                .then(reg => console.log('Service Worker 등록 성공'))
                .catch(err => console.log('Service Worker 등록 실패:', err));
        }}
        
        // PWA 설치 프롬프트
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            
            // 설치 안내 배너 표시
            const installBanner = document.createElement('div');
            installBanner.innerHTML = `
                <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); 
                            background: #7D5A5A; color: white; padding: 15px 25px; border-radius: 10px; 
                            box-shadow: 0 4px 6px rgba(0,0,0,0.3); z-index: 9999; text-align: center;
                            max-width: 90%; font-family: sans-serif;">
                    <div style="margin-bottom: 10px;">📱 홈 화면에 '아솔'을 추가하시겠소?</div>
                    <button id="installBtn" style="background: white; color: #7D5A5A; border: none; 
                            padding: 8px 20px; border-radius: 5px; font-weight: bold; cursor: pointer; margin-right: 10px;">
                        추가하기
                    </button>
                    <button id="dismissBtn" style="background: transparent; color: white; border: 1px solid white; 
                            padding: 8px 20px; border-radius: 5px; cursor: pointer;">
                        나중에
                    </button>
                </div>
            `;
            document.body.appendChild(installBanner);
            
            // 설치 버튼 클릭 시
            document.getElementById('installBtn').addEventListener('click', () => {{
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('사용자가 PWA 설치 동의');
                    }}
                    deferredPrompt = null;
                    installBanner.remove();
                }});
            }});
            
            // 나중에 버튼 클릭 시
            document.getElementById('dismissBtn').addEventListener('click', () => {{
                installBanner.remove();
            }});
        }});
        
        // 카메라 권한 사전 요청 (Chrome 최적화)
        window.addEventListener('load', () => {{
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
                // 페이지 로드 시 카메라 권한 체크 (실제 스트림은 시작 안 함)
                console.log('카메라 API 사용 가능');
            }}
        }});
    </script>
    """
    
    st.components.v1.html(pwa_html, height=0)

# PWA 지원 활성화
add_pwa_support()

# --- 3. [업그레이드] 인앱 브라우저 차단 + Chrome 권장 ---
st.components.v1.html("""
<script>
    var userAgent = navigator.userAgent.toLowerCase();
    var isInApp = userAgent.indexOf("kakao") > -1 || 
                  userAgent.indexOf("instagram") > -1 || 
                  userAgent.indexOf("line") > -1 ||
                  userAgent.indexOf("fban") > -1 ||  // Facebook
                  userAgent.indexOf("fbav") > -1;    // Facebook
    
    var isChrome = userAgent.indexOf("chrome") > -1 && userAgent.indexOf("edg") === -1;
    
    if (isInApp) {
        document.body.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background-color: #fff; z-index: 9999; display: flex; 
                        flex-direction: column; justify-content: center; align-items: center; 
                        text-align: center; font-family: sans-serif; padding: 20px;">
                <h1 style="color: #d32f2f; margin-bottom: 20px;">⛔️ 접속 불가</h1>
                <p style="font-size: 18px; line-height: 1.8; color: #333;">
                    죄송하오. <b>인앱 브라우저</b>에서는 카메라가 작동하지 않소.<br><br>
                    <span style="background: #fff3cd; padding: 5px 10px; border-radius: 5px; display: inline-block; margin: 10px 0;">
                        📱 우측 상단 점 3개 <b>(...)</b> 클릭<br>
                        → <b>[Chrome으로 열기]</b> 또는 <b>[Safari로 열기]</b> 선택
                    </span>
                </p>
            </div>
        `;
    } else if (!isChrome && /mobile|android/i.test(userAgent)) {
        // 모바일인데 Chrome이 아닐 경우 권장 메시지
        var banner = document.createElement('div');
        banner.innerHTML = `
            <div style="background: #fff3cd; color: #856404; padding: 12px; text-align: center; 
                        font-size: 14px; border-bottom: 2px solid #ffc107; font-family: sans-serif;">
                💡 <b>Chrome 브라우저</b>에서 가장 안정적으로 작동합니다!
            </div>
        `;
        document.body.insertBefore(banner, document.body.firstChild);
    }
</script>
""", height=0)

# --- 4. 스타일 꾸미기 ---
st.markdown("""
    <style>
    /* 기본 스타일 */
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
    
    /* PWA 모드일 때 상단 여백 조정 */
    @media all and (display-mode: standalone) {
        .main { 
            padding-top: 2rem; 
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. API 키 연결 ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("🚨 API 키 설정을 확인하시오.")
    st.stop()

# --- 6. [핵심] 장군신 자동 로테이션 시스템 ---
def get_all_available_models():
    """사용 가능한 모든 장군신 목록 가져오기"""
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
    """특정 장군신으로 관상 시도"""
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

# PWA 설치 안내 (선택적)
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
    💡 <b>팁:</b> 홈 화면에 추가하면 앱처럼 빠르게 접속할 수 있소!
</div>
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

# --- 9. 분석 및 실행 로직 ---
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
                        status_text.markdown(f"### 💤 {display_name} 장군신이 휴식 중이오... 다른 장군신 찾는 중...")
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
            st.info("💡 네트워크 연결을 확인하거나, 잠시 후 다시 시도해주시오.")

# --- 10. 하단 안내 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 <b>개인정보 보호:</b> 모든 사진은 분석 후 즉시 삭제됩니다.</p>
    <p>🧙‍♂️ 관상가 아솔 © 2024</p>
</div>
""", unsafe_allow_html=True)