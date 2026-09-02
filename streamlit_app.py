# ================================================================
# 관상가 아솔 - Streamlit App
# Version: v3.0.0 (2026-09-02)
# 수정 내용: 
#   - 기본 분석 결과 UI 추가
#   - AI 응답 디버그 출력
#   - 파싱 로직 완전 재작성
#   - f-string 문법 오류 수정
#   - 별점 줄바꿈 추가
#   - split() 문법 오류 긴급 수정
#   - 콘솔 디버그 출력 추가
#   - 중복 except 블록 제거 (문법 오류 수정)
#   - 화면에 버전 번호 표시 추가
#   - 들여쓰기 오류 긴급 수정
#   - 강력한 디버깅 로그 추가
#   - 초기 단계 디버깅 추가 (앱 시작, 버튼 클릭 감지)
#   - print flush=True 추가 (로그 즉시 출력)
#   - 여러 모델 자동 재시도 (최대 5개)\n#   - Hugging Face 무료 모델 fallback 추가\n#   - HF 모델 교체 (BLIP → Qwen2-VL-7B)\n#   - 에러 메시지 화면 제거 (로그만 출력)
#   - [v3.0.0] 주소를 asoul.ssirn.co.kr 로 · opencv 4.x 고정(5.0 에 Haar 없음)
#   - [v2.9.2] 얼굴을 찾아 타원에 꽉 맞게 자름 (전에는 얼굴이 원 밖으로 삐져나왔다)
#   - [v2.9.2] 얼굴 크롭을 DB 에도 보관 + 그에 맞게 고지 문구 수정
#   - [v2.9.1] 감정서 메일에 얼굴 사진(세로 타원)과 기본 분석 결과를 함께 넣음
#   - [v2.9.0] 메일로 받으려면 이름·이메일·전화번호를 동의받아 수집(SQLite)
#   - [v2.9.0] 버튼을 [메일로 받기] / [화면으로만 보기] 둘로 분리
#              (전에는 주소만 적혀 있으면 한 번에 발송돼서 갑작스러웠다)
#   - [v2.8.0] 나이를 직접 일러 줄 수 있게 (사진만으로는 60대를 40대로 보기도 한다)
#   - [v2.8.0] 맛보기 600자 -> [자세히 보기] 로 전체 1200자, 메일로도 발송
#   - [v2.8.0] 감정서를 버튼 블록 밖에서 그린다 (다시 그려도 사라지지 않게)
#   - [v2.7.0] 감정서를 쓰는 동안 글자수·경과시간과 쓰고 있는 대목을 실시간 표시
#              (GPU 는 도는데 화면이 멈춘 것처럼 보이던 문제)
#   - [v2.6.0] AI 백엔드를 사내 LLM 서버(OpenAI 호환)로 완전 교체
#   - [v2.6.0] Gemini / Hugging Face 경로 제거
#   - [v2.6.0] 윈도우 cp949 콘솔에서 이모지 print 로 앱이 죽던 버그 수정
# ================================================================

import sys
import io  # 이미지 변환용

# 윈도우 콘솔(cp949)에서는 print 의 이모지가 UnicodeEncodeError 를 내며
# 앱 전체를 죽인다. except 블록 안에서 터지면 진짜 원인까지 가려지므로
# 다른 무엇보다 먼저 표준출력을 UTF-8 로 고정한다.
if not getattr(sys, "_asol_utf8_done", False):
    for _name in ("stdout", "stderr"):
        _stream = getattr(sys, _name, None)
        try:
            if hasattr(_stream, "reconfigure"):
                _stream.reconfigure(encoding="utf-8", errors="replace")
            elif hasattr(_stream, "buffer"):
                setattr(sys, _name, io.TextIOWrapper(
                    _stream.buffer, encoding="utf-8", errors="replace", line_buffering=True))
        except Exception:
            pass  # 표준출력을 못 바꿔도 앱은 계속 떠야 한다
    sys._asol_utf8_done = True

import streamlit as st
from PIL import Image
import time
import base64
import json
import requests
import llm_client
import mailer
import leads
import faceutil  # 사내 LLM 서버(OpenAI 호환) 클라이언트

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

# --- 4. 인앱 브라우저 차단 화면 (현재 없음) ---
# 여기에는 카카오톡/인스타 인앱 브라우저를 감지해 차단 화면을 띄우는
# 자바스크립트가 st.markdown(unsafe_allow_html=True) 으로 들어 있었다.
# 그런데 **브라우저 규격상 innerHTML 로 넣은 <script> 는 실행되지 않는다.**
# 실제로 배포된 화면에서 typeof window.showBlockScreen 이 undefined 였다.
# 즉 위 3번의 iframe 이 IN_APP_BROWSER_DETECTED 를 보내도 받는 쪽이 없어
# 이 기능은 처음부터 동작한 적이 없다.
#
# 게다가 그 코드는 화면 맨 위에 } 한 글자를 흘려 놓고 있었다(마크다운이
# 스크립트 끝부분을 본문으로 잘라 냈다). 동작하지도 않으면서 흔적만 남기므로
# 지운다. 되살리려면 git 이력에서 v2.8.0 이전을 보면 된다.
#
# 다시 만들 거라면 차단 화면도 3번처럼 st.components.v1.html 안에서 그려야
# 한다. 다만 iframe 은 부모 문서를 건드릴 수 없으므로 설계를 다시 잡아야 한다.

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
    llm_client.configure(
        base_url=st.secrets["LLM_BASE_URL"],
        api_key=st.secrets["LLM_API_KEY"],
    )
    print("[OK] LLM 서버 설정 성공!", flush=True)
except Exception as e:
    print(f"[실패] LLM 서버 설정 실패: {e}", flush=True)
    st.error("🚨 LLM 설정을 확인하시오. `.streamlit/secrets.toml` 에 LLM_BASE_URL 과 LLM_API_KEY 가 필요합니다.")
    st.stop()

# --- 8. 장군신(AI 모델) 함수들 ---
def get_all_available_models():
    """사내 LLM 서버에서 쓸 수 있는 비전 모델 목록 (우선순위 순)"""
    return llm_client.list_vision_models()

def analyze_face_info(model_name, image):
    """얼굴에서 성별, 나이대, 직업 분석 (관상학 + 의상 분석)"""
    try:
        print(f"\n[DEBUG] analyze_face_info 호출됨 - 모델: {model_name}", flush=True)
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
        response, error = llm_client.generate_with_image(model_name, analysis_prompt, image)
        if response is None:
            return None, error
        print(f"[DEBUG] AI 응답 받음 - 길이: {len(response.text)} 문자", flush=True)
        print(f"[DEBUG] AI 응답 미리보기: {response.text[:200]}...", flush=True)
        return response.text, None
    except Exception as e:
        return None, str(e)

def try_model_with_image(model_name, prompt, image, on_progress=None):
    """특정 모델로 이미지 분석 시도. on_progress 로 진행 상황을 받아 볼 수 있다."""
    return llm_client.generate_with_image(model_name, prompt, image,
                                          on_progress=on_progress)

# --- 8-b. 감정서 프롬프트 ---
# 맛보기(600자)와 전체(1200자 이상)가 같은 양식을 쓰되 분량 지시만 다르다.
# 양식까지 따로 두면 두 감정서가 따로 놀아 이어 읽기 어색해진다.
SHORT_FORM = """당신의 이름은 '아솔'입니다. 조선 팔도에서 가장 용한 전설적인 관상가입니다.
이 사진의 인물을 보고 관상을 긍정적이고 재미있게 봐주세요.
말투는 위엄 있으면서도 친근한 사극 톤("~하오", "~이오", "~구려")을 사용하세요.{gender_age_info}

[중요] 이것은 **맛보기 감정서**요. 아래 다섯 항목만, **전체 600자 이상 800자 이하**로 쓰시오.
너무 짧으면 성의 없어 보이니 600자는 채우시오.
항목을 더 만들지 말고, 각 항목은 3문장 안팎으로 쓰시오.

🎭 **첫인상과 기운**
- 얼굴 전체의 균형과 타고난 복을 2~3문장으로.

💰 **재물운**
- 코와 광대로 보는 재물 축적 능력을 2~3문장으로.

💕 **애정운**
- 눈과 입으로 보는 인연과 가정운을 2문장으로.

🎯 **운세 점수**
- 재물운 ⭐ / 애정운 ⭐ / 건강운 ⭐ / 직업운 ⭐ (별 개수로만, 설명 없이)

📜 **아솔의 한마디**
- 용기와 희망을 주는 따뜻한 말 2문장.

**지침**
- **굵게** 강조와 이모티콘을 적당히 쓰시오(과하지 않게).
- 단점은 보완 가능한 점으로 부드럽게 표현하시오.
- 분량을 넘기지 마시오. 짧고 인상적인 것이 이 맛보기의 목적이오.
"""


SHORT_RULE = """전체 분량: **600자 내외**. 이것은 맛보기 감정서요. 절대 800자를 넘기지 마시오."""
FULL_RULE = """전체 분량: **최소 1200자 이상**. 각 항목을 앞서보다 훨씬 깊고 구체적으로."""

# 항목별 분량. 이것을 함께 바꾸지 않으면 "각 항목 4-5문장"이 600자 지시를 이겨 버린다.
# (실제로 그래서 맛보기가 1,585자로 나왔다)
SHORT_DETAIL = "각 항목은 **1~2문장**으로 짧게. 하위 세부 항목은 묶어서 한 문장으로."
FULL_DETAIL = "각 항목마다 **최소 4-5문장 이상** 매우 상세하게 작성"

# 맨 앞에서 한 번 더. 모델은 프롬프트 앞쪽을 더 무겁게 듣는다.
SHORT_HEAD = """[가장 중요] 이번 감정서는 **맛보기**요. 전체를 600자 안팎으로 짧게 쓰시오.
아래 양식의 큰 제목은 모두 남기되, 내용은 한두 문장으로 줄이시오.

"""
FULL_HEAD = ""


def _euro(word):
    """받침에 따라 '로' 인지 '으로' 인지 고른다.

    "30대 초반로" 처럼 어색해지는 것을 막는다. 한글 종성 인덱스가 0(받침 없음)
    이거나 8(ㄹ)이면 '로', 그밖에는 '으로'.
    """
    if not word:
        return "로"
    ch = word[-1]
    if not ("가" <= ch <= "힣"):
        return "로"
    return "로" if (ord(ch) - 0xAC00) % 28 in (0, 8) else "으로"


def build_prompt(gender_age_info, detailed=False):
    """감정서 프롬프트. detailed=True 면 전체판."""
    if not detailed:
        # 맛보기는 양식 자체가 짧다. 큰 양식에 "600자로 줄여라"라고만 하면
        # 항목이 열다섯 개라 물리적으로 불가능해 1,600자가 나왔다.
        return SHORT_FORM.format(gender_age_info=gender_age_info)
    return PROMPT_FORM.format(
        gender_age_info=gender_age_info,
        head_rule=FULL_HEAD,
        detail_rule=FULL_DETAIL,
        length_rule=FULL_RULE)


PROMPT_FORM = """당신의 이름은 '아솔'입니다. 조선 팔도에서 가장 용한 전설적인 관상가입니다.
{head_rule}이 사진의 인물을 보고 다음 내용을 바탕으로 관상을 긍정적이고 재미있게 봐주세요.
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
- 재물운: ⭐⭐⭐⭐⭐ (별 개수로 표시)
- 애정운: ⭐⭐⭐⭐⭐ (별 개수로 표시)
- 건강운: ⭐⭐⭐⭐⭐ (별 개수로 표시)
- 직업운: ⭐⭐⭐⭐⭐ (별 개수로 표시)
- 종합 평가: 한 줄 긍정적 요약

📜 **아솔의 한마디**
- 마지막으로 이 사람에게 용기와 희망을 주는 따뜻한 말 (4-5문장)
- 미래에 대한 긍정적 전망
- 응원의 메시지

**작성 지침:**
1. {detail_rule}
2. 구체적인 나이, 시기, 숫자를 언급하여 신빙성 높이기
3. **긍정 50% + 현실적 조언 50%** 비율 유지 
4. **별점은 적절하게 
5. 이모티콘 적절히 사용 (과하지 않게)
6. **굵게**, *이탤릭* 강조 문법 활용
7. {length_rule}
8. 재미있고 읽기 쉽게, 하지만 충분히 전문적으로
9. 사람들에게 희망과 용기를 주는 톤 유지
10. 단점보다는 보완 가능한 점으로 부드럽게 표현
"""

# --- 9. 세션 초기화 ---
if 'final_image' not in st.session_state:
    st.session_state.final_image = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_model' not in st.session_state:
    st.session_state.last_model = None
# 기본 정보(성별·나이·직업)와 전체 감정서. 결과를 버튼 블록 밖에서 그리기 위해 담아 둔다.
for _k in ('basic', 'full_result', 'mail_note', 'told_age', 'told_gender'):
    st.session_state.setdefault(_k, None)

# --- 10. 메인 UI ---
print("=" * 80, flush=True)
print("🚀 앱 시작됨!", flush=True)
print(f"⏰ 현재 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
print("=" * 80, flush=True)

st.markdown("<h1 class='main-header'>🧙‍♂️ 관상가 '아솔'</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 16px;'>조선 팔도를 떠돌며 수많은 관상을 봐온 전설의 관상가 <span style='color: #999; font-size: 12px;'>(v3.0.0)</span></p>", unsafe_allow_html=True)
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
        print("📸 카메라로 사진 촬영됨!", flush=True)
        st.session_state.final_image = camera_image
        
elif input_method == "📂 앨범 선택":
    uploaded_file = st.file_uploader("📂 사진을 선택하시오", type=['jpg', 'jpeg', 'png'], label_visibility="visible")
    if uploaded_file:
        print("📂 앨범에서 사진 선택됨!", flush=True)
        st.session_state.final_image = uploaded_file

# --- 11. 관상 분석 로직 ---
if st.session_state.final_image:
    st.write("---")
    st.image(st.session_state.final_image, caption="✅ 선택된 얼굴", use_container_width=True)

    # 사진만으로는 나이를 자주 틀린다 — 60대를 40대로 보기도 한다.
    # 알려 주면 그 값으로 감정하고, 비워 두면 아솔이 스스로 추정한다.
    st.write("")
    st.markdown("##### 🎂 나이를 일러 주시면 훨씬 잘 맞소")
    _c1, _c2 = st.columns([1, 1.3])
    with _c1:
        _dec = st.selectbox(
            "연대",
            ["🤖 아솔이 알아서 보겠소"] + [f"{d}대" for d in range(10, 90, 10)] + ["90대 이상"],
            key="ui_dec")
    _auto_age = _dec.startswith("🤖")
    with _c2:
        _part = st.radio("구간", ["초반", "중반", "후반"], index=1, horizontal=True,
                         key="ui_part", disabled=_auto_age,
                         help="40대 초반 · 중반 · 후반처럼 잡아 주시오.")
    _gsel = st.radio("성별", ["🤖 아솔이 알아서", "남성", "여성"], horizontal=True,
                     key="ui_gender")

    # 위젯 값을 그대로 두면 헷갈리니, 쓰기 좋은 형태로 옮겨 담는다.
    if _auto_age:
        st.session_state.told_age = None
    elif _dec == "90대 이상":
        st.session_state.told_age = "90대 이상"
    else:
        st.session_state.told_age = f"{_dec} {_part}"
    st.session_state.told_gender = (None if _gsel.startswith("🤖")
                                    else ("남자 사람" if _gsel == "남성" else "여자 사람"))
    st.write("")

    if st.button("🔮 아솔에게 관상 묻기", type="primary"):
        print("=" * 80, flush=True)
        print("🔮 버튼 클릭됨!", flush=True)
        print(f"⏰ 클릭 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print("=" * 80, flush=True)
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 1단계: 장군신 찾기
            status_text.markdown("<p class='status-text'>📡 당직 서는 장군신을 찾는 중이오...</p>", unsafe_allow_html=True)
            progress_bar.progress(3)
            
            available_models = get_all_available_models()
            print(f"[DEBUG] 사용 가능한 모델 개수: {len(available_models)}", flush=True)
            print(f"[DEBUG] 모델 목록: {available_models}", flush=True)
            
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
            
            # 여러 모델로 성별/나이/직업 분석 시도 (자동 fallback)
            print(f"[DEBUG] available_models 길이 체크: {len(available_models)}", flush=True)
            if len(available_models) > 0:
                # 최대 5개 모델 시도
                max_attempts = min(5, len(available_models))
                for attempt in range(max_attempts):
                    model_to_use = available_models[attempt]
                    print(f"[시도 {attempt+1}/{max_attempts}] 모델: {model_to_use}", flush=True)
                    
                    face_info, error = analyze_face_info(model_to_use, image)
                    print(f"[DEBUG] 반환값: face_info={'있음' if face_info else '없음'}, error={error[:100] if error else 'None'}", flush=True)
                    
                    if face_info:
                        print(f"✅ 성공! 모델 '{model_to_use}' 사용됨", flush=True)
                        break
                    else:
                        print(f"⚠️ 실패: {error[:80] if error else '알 수 없음'}", flush=True)
                        if attempt < max_attempts - 1:
                            print(f"🔄 다음 모델 시도 중...", flush=True)
                
                if not face_info:
                    # 비전 모델을 전부 시도했는데 실패. 화면에는 알리지 않고 로그만 남긴다.
                    print(f"[실패] 비전 모델 {max_attempts}개 모두 실패!", flush=True)
                
                try:
                    if face_info:
                        # ===== 디버그: AI 응답 전체 출력 =====
                        print("=" * 80, flush=True)
                        print("🔍 AI 원본 응답 (콘솔):", flush=True)
                        print(face_info)
                        print("=" * 80, flush=True)
                        st.info(f"🔍 AI 원본 응답:\n{face_info}")
                        
                        # 성별 추출 - 개선된 방식
                        gender = "사람"
                        if "성별" in face_info:
                            for line in face_info.split("\n"):
                                if "성별" in line:
                                    if "남성" in line or "남자" in line:
                                        gender = "남자 사람"
                                    elif "여성" in line or "여자" in line:
                                        gender = "여자 사람"
                                    break
                        
                        # 나이대 추출 - 개선된 방식
                        age_range = ""
                        if "나이" in face_info:
                            age_keywords = [
                                "80대 이상", "80대", "70대 후반", "70대 초반", "70대",
                                "60대 후반", "60대 초반", "60대",
                                "50대 후반", "50대 초반", "50대",
                                "40대 후반", "40대 초반", "40대",
                                "30대 후반", "30대 초반", "30대",
                                "20대 후반", "20대 초반", "20대",
                                "10대 후반", "10대 초반", "10대"
                            ]
                            for age_keyword in age_keywords:
                                if age_keyword in face_info:
                                    age_range = age_keyword
                                    break
                        
                        # 현재 직업 추출 - 개선된 방식
                        current_jobs = []
                        if "현재 직업" in face_info:
                            for line in face_info.split("\n"):
                                if "현재 직업" in line:
                                    # "현재 직업:" 이후 텍스트 추출
                                    job_text = line.split(":", 1)[-1].strip()
                                    # 쉼표로 분리
                                    jobs = [j.strip() for j in job_text.split(",") if j.strip()]
                                    current_jobs = jobs[:3]
                                    break
                        
                        # 어울리는 직업 추출 - 개선된 방식
                        suitable_jobs = []
                        if "어울리는 직업" in face_info:
                            for line in face_info.split("\n"):
                                if "어울리는 직업" in line:
                                    # "어울리는 직업:" 이후 텍스트 추출
                                    job_text = line.split(":", 1)[-1].strip()
                                    # 쉼표로 분리
                                    jobs = [j.strip() for j in job_text.split(",") if j.strip()]
                                    suitable_jobs = jobs[:3]
                                    break
                        
                        # 디버그 출력
                        print("=" * 80, flush=True)
                        print("✅ 파싱 결과 (콘솔):", flush=True)
                        print(f"성별: {gender}", flush=True)
                        print(f"나이: {age_range}")
                        print(f"현재직업: {current_jobs}")
                        print(f"어울리는직업: {suitable_jobs}")
                        print("=" * 80, flush=True)
                        st.success(f"✅ 파싱 결과:\n성별={gender}\n나이={age_range}\n현재직업={current_jobs}\n어울리는직업={suitable_jobs}")
                        
                except Exception as e:
                    print(f"[ERROR] 파싱 에러: {e}", flush=True)
                    import traceback
                    traceback.print_exc()
                    st.error(f"⚠️ 파싱 에러: {e}")
                    pass
            else:
                print(f"[DEBUG] available_models가 비어있습니다! 모델을 찾을 수 없습니다.", flush=True)
                st.error("⚠️ 사용 가능한 AI 모델이 없습니다. API 키를 확인해주세요.")
            
            # face_info 최종 상태 확인
            print(f"[DEBUG] 최종 face_info 상태: {'있음' if face_info else '없음'}", flush=True)
            print(f"[DEBUG] 최종 gender: {gender}", flush=True)
            print(f"[DEBUG] 최종 age_range: {age_range}", flush=True)
            print(f"[DEBUG] 최종 current_jobs: {current_jobs}", flush=True)
            print(f"[DEBUG] 최종 suitable_jobs: {suitable_jobs}", flush=True)

            # 알려 준 값이 있으면 그것으로 감정한다. 추정값은 따로 남겨
            # 화면에서 "아솔은 이렇게 보았소만" 하고 정직하게 같이 보여 준다.
            ai_age, ai_gender = age_range, gender
            if st.session_state.told_age:
                age_range = st.session_state.told_age
            if st.session_state.told_gender:
                gender = st.session_state.told_gender
            
            # 분석 결과 표시
            result_text = f"👤 **{gender}**"
            if age_range:
                result_text += f", **{age_range}**"
            
            if current_jobs:
                result_text += f"\n\n💼 현재 직업 추정: {', '.join(current_jobs)}"
            
            if suitable_jobs:
                result_text += f"\n✨ 어울리는 직업: {', '.join(suitable_jobs)}"
                
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
                    
                    # 현재 직엁과 어울리는 직업 비교
                    if current_jobs:
                        matching = any(cj in suitable_jobs or sj in current_jobs 
                                     for cj in current_jobs for sj in suitable_jobs)
                        if matching:
                            job_match_comment = f"""

**직업운 특별 멘트:**
현재 그대가 하고 있는 일({', '.join(current_jobs)})이 관상으로 본 어울리는 직업과 일치하는군요! 
오호! 그대는 운명에 맞게 살고 있습니다. 
이 길을 계속 가면 큰 성취를 이룰 것이오. 
그대의 얼굴에서 붉은 빛이 보이는군요!
"""
                        else:
                            job_match_comment = f"""

**직업운 특별 멘트:**
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
            
            prompt = build_prompt(gender_age_info, detailed=False)
            
            # 6단계: 관상 분석 실행
            response = None
            successful_model = None
            
            # 붓을 놀리는 동안 보여 줄 자리. 아무 표시가 없으면 멈춘 줄 안다.
            live_box = st.empty()

            for model_name in available_models:
                display_name = model_name.split(':')[0].upper()
                status_text.markdown(f"<p class='status-text'>⚡ <strong>{display_name}</strong> 장군신 소환 중...</p>", unsafe_allow_html=True)
                progress_bar.progress(85)
                
                def _live(text_so_far, chars, elapsed, _dn=display_name):
                    """조각이 올 때마다 — 글자수·경과시간과 지금 쓰는 대목을 보여 준다."""
                    # 1200자를 목표로 85% ~ 99% 사이를 채운다
                    progress_bar.progress(85 + min(14, int(14 * chars / 1200)))
                    status_text.markdown(
                        f"<p class='status-text'>🖌️ <strong>{_dn}</strong> 장군신이 "
                        f"감정서를 쓰는 중… <strong>{chars:,}자</strong> · {elapsed:.0f}초</p>",
                        unsafe_allow_html=True)
                    tail = text_so_far[-160:].replace("\n", " ")
                    live_box.markdown(
                        "<div style='color:#8a7a7a;font-size:13px;line-height:1.7;"
                        "padding:10px 14px;background:#faf7f7;border-left:3px solid #7D5A5A;"
                        "border-radius:6px;min-height:52px'>…"
                        f"{tail}<span style='opacity:.5'>▌</span></div>",
                        unsafe_allow_html=True)

                response, error = try_model_with_image(model_name, prompt, image,
                                                       on_progress=_live)
                live_box.empty()
                
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
            
            # 결과는 세션에 담고, 그리기는 버튼 블록 밖에서 한다.
            # 그래야 [자세히 보기]로 화면을 다시 그려도 감정서가 사라지지 않는다.
            st.session_state.basic = {
                "gender": gender, "age_range": age_range,
                "ai_gender": ai_gender, "ai_age": ai_age,
                "told_age": st.session_state.told_age,
                "current_jobs": current_jobs, "suitable_jobs": suitable_jobs,
                "gender_age_info": gender_age_info,
            }
            st.session_state.last_result = response.text
            st.session_state.last_model = successful_model
            st.session_state.full_result = None
            st.session_state.mail_note = None
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ 예기치 못한 에러가 났소. (내용: {e})")
            progress_bar.empty()
            status_text.empty()
            
            # ===== 📊 기본 분석 결과 표시 =====
            st.write("---")
            st.subheader("📊 기본 분석 결과")
            st.write("")  # 여백
            
            # result_text 생성 - 줄바꿈 개선
            result_parts = []
            result_parts.append(f"**성별**: {gender}")
            result_parts.append("")  # 빈 줄
            
            if age_range:
                result_parts.append(f"**추정 나이**: {age_range}")
                result_parts.append("")  # 빈 줄
            
            if current_jobs:
                job_list = ", ".join(current_jobs)
                result_parts.append(f"**현재 직업 추정** (옷차림 70% + 관상 30%):")
                result_parts.append(f"  {job_list}")
                result_parts.append("")  # 빈 줄
            
            if suitable_jobs:
                job_list = ", ".join(suitable_jobs)
                result_parts.append(f"**어울리는 직업** (100% 관상):")
                result_parts.append(f"  {job_list}")
            
            result_text = "\n".join(result_parts)
            st.info(result_text)
            
            st.write("")  # 여백
            st.markdown("💫 *추정이 맞으면 좋겠구려!*")
            st.write("---")
            # ===== 기본 분석 결과 표시 끝 =====


# --- 11-b. 감정서 표시 -------------------------------------------------------
# 버튼 블록 **밖**에 둔다. [자세히 보기]로 화면을 다시 그려도 감정서가 살아남는다.
if st.session_state.get("last_result"):
    _b = st.session_state.get("basic") or {}
    _is_full = bool(st.session_state.get("full_result"))
    _shown = st.session_state.get("full_result") or st.session_state.last_result

    # ===== 기본 분석 결과 =====
    st.write("---")
    st.subheader("📊 기본 분석 결과")
    _parts = [f"**성별**: {_b.get('gender', '사람')}", ""]
    if _b.get("age_range"):
        _told = _b.get("told_age")
        _parts.append(f"**나이**: {_b['age_range']}"
                      + ("  *(일러 주신 나이)*" if _told else "  *(아솔의 추정)*"))
        # 추정이 빗나갔으면 숨기지 않고 같이 보여 준다. 그래야 왜 물었는지 납득이 간다.
        if _told and _b.get("ai_age") and _b["ai_age"] != _told:
            _parts.append(f"  ↳ 아솔은 **{_b['ai_age']}**{_euro(_b['ai_age'])} "
                          "보았소만, 일러 주신 나이로 감정하였소.")
        _parts.append("")
    if _b.get("current_jobs"):
        _parts += ["**현재 직업 추정** (옷차림 70% + 관상 30%):",
                   "  " + ", ".join(_b["current_jobs"]), ""]
    if _b.get("suitable_jobs"):
        _parts += ["**어울리는 직업** (100% 관상):",
                   "  " + ", ".join(_b["suitable_jobs"])]
    st.info("\n".join(_parts))

    # ===== 감정서 =====
    st.write("---")
    st.subheader("📜 아솔의 관상 풀이" + ("" if _is_full else "  (맛보기)"))
    st.caption(f"*by {st.session_state.last_model} 장군신*")
    st.markdown(_shown)

    if st.session_state.get("mail_note"):
        _ok, _msg = st.session_state.mail_note
        (st.success if _ok else st.warning)(_msg)

    # ===== 자세히 보기 =====
    if not _is_full:
        st.write("---")
        st.markdown("### 🔍 자세히 보기")
        st.caption("여기까지는 맛보기였소. 전체 감정서는 두 배 넘게 길고, "
                   "메일 주소를 남기면 그리로도 보내 드리오.")
        with st.form("detail_form"):
            st.markdown(leads.NOTICE)
            _c1, _c2 = st.columns(2)
            with _c1:
                _name = st.text_input("이름", placeholder="홍길동")
                _mail = st.text_input("이메일", placeholder="you@example.com")
            with _c2:
                _phone = st.text_input("휴대전화", placeholder="010-1234-5678")
            _agree = st.checkbox("위 내용에 동의하오. 감정서를 메일로 보내 주시오.")
            _b1, _b2 = st.columns(2)
            with _b1:
                _send = st.form_submit_button("📬 메일로 받기", type="primary",
                                              use_container_width=True)
            with _b2:
                _only = st.form_submit_button("👀 화면으로만 보기",
                                              use_container_width=True)

        if _send or _only:
            # 메일로 받을 때만 검사한다. 화면으로만 볼 때는 아무것도 받지 않는다.
            _err = None
            if _send:
                if not _agree:
                    _err = ("동의하셔야 메일로 보내 드릴 수 있소. "
                            "동의 없이 보시려면 [화면으로만 보기]를 누르시오.")
                elif not leads.valid_name(_name):
                    _err = "이름을 두 글자 이상 적어 주시오."
                elif not mailer.valid(_mail):
                    _err = "메일 주소를 다시 확인해 주시오."
                elif not leads.valid_phone(_phone):
                    _err = "휴대전화번호를 다시 확인해 주시오. (예: 010-1234-5678)"
            if not st.session_state.final_image:
                _err = "사진이 사라졌소. 다시 올려 주시오."

            if _err:
                st.error(_err)
            else:
                _pb = st.progress(0)
                _sx = st.empty()
                _live = st.empty()
                _img = Image.open(st.session_state.final_image)
                _prompt = build_prompt(_b.get("gender_age_info", ""), detailed=True)
                _resp, _model = None, None

                for _m in get_all_available_models():
                    _dn = _m.split(":")[0].upper()
                    _sx.markdown(
                        f"<p class='status-text'>⚡ <strong>{_dn}</strong> 장군신이 "
                        "붓을 고쳐 잡는 중...</p>", unsafe_allow_html=True)

                    def _cb(text_so_far, chars, elapsed, _d=_dn):
                        # 전체판 목표는 1200자. 그 비율로 진행률을 채운다.
                        _pb.progress(min(99, int(99 * chars / 1200)))
                        _sx.markdown(
                            f"<p class='status-text'>🖌️ <strong>{_d}</strong> 장군신이 "
                            f"자세한 감정서를 쓰는 중... <strong>{chars:,}자</strong> "
                            f"· {elapsed:.0f}초</p>", unsafe_allow_html=True)
                        _tail = text_so_far[-160:].replace("\n", " ")
                        _live.markdown(
                            "<div style='color:#8a7a7a;font-size:13px;line-height:1.7;"
                            "padding:10px 14px;background:#faf7f7;"
                            "border-left:3px solid #7D5A5A;border-radius:6px;"
                            f"min-height:52px'>...{_tail}"
                            "<span style='opacity:.5'>▌</span></div>",
                            unsafe_allow_html=True)

                    _resp, _err = try_model_with_image(_m, _prompt, _img,
                                                       on_progress=_cb)
                    if _resp is not None:
                        _model = _dn
                        break

                _live.empty()
                _pb.empty()
                _sx.empty()

                if _resp is None:
                    st.error("모든 장군신이 휴식 중이오. 잠시 뒤 다시 청해 주시오.")
                else:
                    st.session_state.full_result = _resp.text
                    st.session_state.last_model = _model
                    st.session_state.mail_note = None
                    if _send:
                        # 화면에서 보여 준 기본 분석 결과를 메일에도 그대로 싣는다.
                        _age = _b.get("age_range", "")
                        if _age:
                            _age += ("  (일러 주신 나이)" if _b.get("told_age")
                                     else "  (아솔의 추정)")
                        _info = [
                            ("성별", _b.get("gender", "")),
                            ("나이", _age),
                            ("현재 직업 추정", ", ".join(_b.get("current_jobs") or [])),
                            ("어울리는 직업", ", ".join(_b.get("suitable_jobs") or [])),
                        ]
                        _ok, _note = mailer.send(
                            _mail, "📜 관상가 아솔의 감정서가 도착하였소",
                            _resp.text,
                            subtitle=f"{_b.get('gender', '')} · "
                                     f"{_b.get('age_range', '')}".strip(" ·"),
                            photo=_img, info=_info)
                        st.session_state.mail_note = (_ok, _note)
                        # 발송 결과까지 함께 남긴다 — 나중에 "안 왔다"는 문의가
                        # 오면 이 줄이 있어야 무슨 일이 있었는지 알 수 있다.
                        # 보관용 얼굴 크롭. 메일의 타원과 같은 기준으로 자르되
                        # 마스크는 씌우지 않는다 — 나중에 다른 데 쓰려면 가려지지
                        # 않은 쪽이 훨씬 쓸모 있다.
                        try:
                            _face = faceutil.face_jpeg(_img)
                        except Exception as _e:
                            print("[face] 크롭 실패:", _e, flush=True)
                            _face = None
                        _sv_ok, _sv_msg = leads.save(
                            _name, _mail, _phone, _agree,
                            {"gender": _b.get("gender"), "age": _b.get("age_range"),
                             "model": _model, "mail_ok": _ok, "mail_msg": _note},
                            photo_png=_face)
                        if not _sv_ok:
                            # 화면에는 안 띄운다(보는 사람이 할 수 있는 일이 없다).
                            # 대신 서버 로그에 남겨 우리가 알아채게 한다.
                            print("[leads] 저장 실패:", _sv_msg, flush=True)
                    st.rerun()

    # ===== 복사 버튼 =====
    successful_model = st.session_state.last_model or ""
    result_text_escaped = (_shown.replace("`", "")
                                 .replace(chr(34), chr(92) + chr(34))
                                 .replace("\n", chr(92) + "n"))
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
            var resultText = "📜 관상가 아솔의 감정서 (by {successful_model} 장군신)\\n\\n{result_text_escaped}\\n\\n🧙‍♂️ 관상가 아솔 - https://asoul.ssirn.co.kr/";
            
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


# --- 12. 하단 안내 및 푸터 ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
    <p>🔒 <b>개인정보:</b> 감정서를 <b>메일로 받으신 경우에만</b> 이름·연락처·얼굴 사진을
       1년간 보관하고, 지나면 자동으로 지웁니다. 그 외에는 아무것도 저장하지 않습니다.</p>
    <p>🎲 <b>엔터테인먼트 목적:</b> 본 서비스는 재미를 위한 것으로, 실제 운세와 무관합니다.</p>
    <p style="margin-top: 20px; color: #999; font-size: 12px;">
        🧙‍♂️ 관상가 아솔 © 2025 | Powered by 사내 LLM 서버
    </p>
</div>
""", unsafe_allow_html=True)
