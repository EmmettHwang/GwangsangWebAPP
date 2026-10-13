# -*- coding: utf-8 -*-
"""사진을 받기 전의 동의 — 문구 · 확인표(쿠키) · 기록.

왜 따로 두나 —
  v4.2.0 까지는 **사진을 찍거나 고르는 순간** 서버로 가서 얼굴을 읽었다.
  동의는 맨 끝 「메일로 받기」 앞에만 있었고, 그마저 "버튼을 누르면 동의한
  것으로 본다" 였다. 얼굴 사진은 처음부터 받으면서 그 사진을 어떻게 다루는지는
  한 번도 묻지 않은 셈이다(2026-10-13 점검).

규칙 —
  · 필수 둘: 만 14세 이상 · 얼굴 사진 처리. 둘 다 있어야 사진을 받는다.
  · 선택 하나: 「다시 온 사람 알아보기」(얼굴 특징값을 잠시 만들어 대조).
    끄고도 관상은 그대로 볼 수 있어야 하므로 필수에 묶지 않는다.
  · 서버가 확인한다. 화면에서 막는 것은 편의일 뿐이다 — 화면 코드가 바뀌거나
    누가 직접 요청을 보내도 이 규칙은 남아야 한다.
  · 확인표는 서명한 쿠키다. 서버 기억에 두면 다시 띄울 때마다 쓰던 분들이
    한꺼번에 막힌다. 표에는 **무작위 번호·문안 판·시각**만 담는다(사진·이름 없음).
  · 기록(data/consents.jsonl)은 덧붙이기만 한다. 사진은 담지 않는다.
    보유 기간이 지난 줄은 띄울 때 지운다.
"""
import base64
import datetime
import hashlib
import hmac
import io
import json
import os
import secrets
import threading

VERSION = "2026-10-13"            # 문안 판. 바꾸면 모두 다시 동의를 받는다.
COOKIE = "gw_consent"
MAX_AGE = 24 * 3600               # 하루가 지나면 다시 여쭙는다
LOG_RETAIN_DAYS = 365             # 동의 기록 보유 기간

DATA_DIR = os.path.dirname(os.getenv("LEADS_DB", "data/leads.db")) or "data"
LOG_PATH = os.path.join(DATA_DIR, "consents.jsonl")
SECRET_PATH = os.path.join(DATA_DIR, ".consent_secret")

REQUIRED = ("age14", "photo")
OPTIONAL = ("rec",)
XFER = "xfer"             # 메일 단계에서만 받는 [필수] 동의 — 첫 화면 확인표에는 넣지 않는다
_lock = threading.Lock()
_secret = None
_last_purge = 0.0

KST = datetime.timezone(datetime.timedelta(hours=9))


def _now():
    return datetime.datetime.now(KST)


# ── 문구 ─────────────────────────────────────────────────────────────
# 화면은 이것을 받아 그린다(/api/consent). 처리방침(static/privacy.html)과
# 어긋나지 않게, 고칠 때는 둘을 함께 본다.

PHOTO_ROWS = [
    ("처리하는 것", "찍거나 고르신 <b>얼굴 사진 한 장</b>. 카메라 영상은 이 기기(브라우저) 안에서만 보고, "
                  "찍힌 사진 한 장만 서버로 보냅니다."),
    ("목적", "얼굴 위치 찾기·자르기, 관상 감정서 짓기(재미로 보는 풀이이며 진단이 아닙니다)."),
    ("어디서 처리하나", "운영자가 직접 운영하는 <b>국내 서버</b>(웹 서버와 AI 서버)에서만 처리합니다. "
                      "외부 AI 회사(OpenAI·Google·Groq 등)로 보내지 않습니다."),
    ("저장하나", "<b>저장하지 않습니다.</b> 처리하는 동안 서버 메모리에만 있다가 응답과 함께 사라지며, "
               "디스크·데이터베이스·로그에 사진을 남기지 않습니다.<br>"
               "예외는 둘이며, 둘 다 나중에 <b>따로 고르실 때만</b>입니다 — "
               "① 「메일로 받기」: 감정서와 얼굴 사진을 메일에 넣어 보냅니다(보낸 사진은 서버에 남기지 않음). "
               "② 「기록으로 남기기」(선택 동의): 얼굴 사진·특징값을 마지막 방문일로부터 1년 보관하고, "
               "체크를 거두시면 곧바로 지웁니다."),
    ("보유 기간", "사진: 처리 직후 즉시 파기(위 예외 제외). 동의 기록(시각·문안 판·무작위 번호, 사진 없음): 1년."),
    ("국외 이전", "사진을 분석하러 국외로 보내지 않습니다. 다만 접속 구간을 중계하는 "
                "<b>Cloudflare, Inc.(미국)</b>의 네트워크를 암호화된 채로 지나가며(저장 목적 아님), "
                "「메일로 받기」를 고르신 경우에만 메일 발송을 맡은 <b>Twilio SendGrid(미국)</b>로 "
                "이름·메일 주소·감정서·얼굴 사진이 전송됩니다(그때 국외 이전 동의를 따로 받습니다). 자세한 내용은 개인정보처리방침 제5조."),
    ("거부할 권리", "동의하지 않으실 수 있습니다. 다만 사진이 있어야 관상을 볼 수 있으므로 "
                  "<b>동의하지 않으시면 이 서비스를 이용하실 수 없습니다.</b> 그 밖의 불이익은 없습니다."),
]

AGE_ROWS = [
    ("확인하는 것", "만 14세 이상인지 여쭙니다."),
    ("이유", "「개인정보 보호법」 제22조의2에 따라 만 14세 미만은 법정대리인의 동의가 있어야 "
           "개인정보를 처리할 수 있습니다. 이 서비스는 그 절차를 갖추지 않았으므로 "
           "만 14세 미만은 이용하실 수 없습니다."),
]

XFER_ROWS = [
    ("이전받는 자", "<b>Twilio Inc.</b>(SendGrid 메일 발송 서비스) · 개인정보 문의 privacy@twilio.com"),
    ("이전되는 국가", "<b>미국</b>"),
    ("이전 항목", "이름, 이메일 주소, 감정서 내용, <b>얼굴 사진</b>(메일 본문에 실림)"),
    ("이전 목적", "요청하신 감정서 메일을 받는 분께 전달하기"),
    ("시기·방법", "「자세히 보고 메일로 받기」를 누르실 때, 암호화된 네트워크로 전송"),
    ("보유·이용 기간", "발송 처리 후 Twilio SendGrid 의 정책에 따라 파기. "
                     "이 서버에는 얼굴 사진을 남기지 않습니다(「기록으로 남기기」를 고르신 경우만 예외)."),
    ("거부할 권리", "동의하지 않으실 수 있습니다. 그러면 <b>메일은 보내 드리지 못하지만</b>, "
                  "화면에서 감정서를 보시는 데에는 아무 지장이 없습니다."),
]

REC_ROWS = [
    ("처리하는 것", "얼굴 사진에서 계산한 <b>얼굴 특징값</b>(숫자 128개, 생체인식정보 — 민감정보)."),
    ("목적", "전에 「기록으로 남기기」를 하신 분인지 대조해 알아보고 인사드리기."),
    ("저장하나", "<b>저장하지 않습니다.</b> 이번 사진의 특징값은 대조에만 쓰고 바로 버립니다."),
    ("보유 기간", "대조 직후 즉시 파기. 동의 기록(시각·문안 판, 사진 없음)만 1년."),
    ("거부할 권리", "선택입니다. 동의하지 않으셔도 관상은 그대로 보실 수 있고, 다만 알아보지 못합니다."),
]


def terms():
    """화면이 그릴 동의 항목들."""
    return {
        "version": VERSION,
        "items": [
            {"key": "photo", "required": True, "read_required": True,
             "label": "[필수] 얼굴 사진 처리 동의",
             "title": "얼굴 사진 처리 동의 (필수)",
             "checkbox": "위 내용을 끝까지 읽었고, 얼굴 사진 처리에 동의합니다.",
             "rows": PHOTO_ROWS},
            {"key": "age14", "required": True, "read_required": False,
             "label": "[필수] 만 14세 이상입니다",
             "title": "만 14세 이상 확인 (필수)",
             "checkbox": "저는 만 14세 이상입니다.",
             "rows": AGE_ROWS},
            {"key": "xfer", "required": False, "read_required": True,
             "label": "[필수] 개인정보 국외 이전 동의 (메일 발송 — SendGrid, 미국)",
             "title": "개인정보 국외 이전 동의 (메일 발송 · 필수)",
             "checkbox": "위 내용을 끝까지 읽었고, 국외 이전에 동의합니다.",
             "rows": XFER_ROWS},
            {"key": "rec", "required": False, "read_required": True,
             "label": "[선택] 얼굴로 다시 온 사람 알아보기",
             "title": "얼굴 특징값 대조 동의 (선택 · 민감정보)",
             "checkbox": "위 내용을 끝까지 읽었고, 얼굴 특징값 대조에 동의합니다.",
             "rows": REC_ROWS},
        ],
    }


# ── 서명 ─────────────────────────────────────────────────────────────

def _key():
    """서명 열쇠. 환경변수가 없으면 data/ 에 한 번 만들어 두고 계속 쓴다."""
    global _secret
    if _secret:
        return _secret
    env = os.getenv("CONSENT_SECRET", "")
    if env:
        _secret = env.encode()
        return _secret
    with _lock:
        try:
            with io.open(SECRET_PATH, "rb") as f:
                _secret = f.read().strip()
        except FileNotFoundError:
            os.makedirs(DATA_DIR, exist_ok=True)
            _secret = secrets.token_hex(32).encode()
            fd = os.open(SECRET_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(_secret)
    return _secret


def _b64(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def make_token(cid, items, ts=None):
    body = json.dumps({"c": cid, "v": VERSION, "t": int(ts or _now().timestamp()),
                       "i": sorted(items)}, separators=(",", ":")).encode()
    sig = hmac.new(_key(), body, hashlib.sha256).digest()
    return _b64(body) + "." + _b64(sig)


def read_token(tok):
    """확인표를 읽는다. 맞지 않거나 지났거나 판이 다르면 None."""
    try:
        b, s = (tok or "").split(".", 1)
        body = _unb64(b)
        if not hmac.compare_digest(hmac.new(_key(), body, hashlib.sha256).digest(), _unb64(s)):
            return None
        d = json.loads(body)
    except Exception:
        return None
    if d.get("v") != VERSION:
        return None
    if _now().timestamp() - int(d.get("t", 0)) > MAX_AGE:
        return None
    if not all(k in d.get("i", []) for k in REQUIRED):
        return None
    return d


def state(req):
    """요청의 동의 상태. {"ok": bool, "rec": bool, "cid": str|None}"""
    d = read_token(req.cookies.get(COOKIE))
    if not d:
        return {"ok": False, "rec": False, "cid": None}
    return {"ok": True, "rec": "rec" in d.get("i", []), "cid": d.get("c")}


# ── 기록 ─────────────────────────────────────────────────────────────

def log(event, cid, items=(), read=()):
    """한 줄 덧붙인다. 사진·이름·연락처·IP 는 담지 않는다."""
    rec = {"ts": _now().isoformat(timespec="seconds"), "event": event,
           "version": VERSION, "cid": cid, "items": sorted(items),
           "read_full": sorted(read)}
    with _lock:
        os.makedirs(DATA_DIR, exist_ok=True)
        with io.open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    # 컨테이너가 몇 달씩 안 내려갈 수 있다. 띄울 때만 지우면 보유 기간이
    # 지켜지지 않으므로 하루에 한 번은 여기서도 지운다.
    global _last_purge
    if _now().timestamp() - _last_purge > 86400:
        _last_purge = _now().timestamp()
        try:
            purge()
        except Exception:
            pass
    return rec


def purge():
    """보유 기간이 지난 동의 기록을 지운다. 지운 줄 수."""
    if not os.path.exists(LOG_PATH):
        return 0
    cut = (_now() - datetime.timedelta(days=LOG_RETAIN_DAYS)).isoformat(timespec="seconds")
    with _lock:
        with io.open(LOG_PATH, encoding="utf-8") as f:
            lines = f.readlines()
        keep = []
        for ln in lines:
            try:
                if json.loads(ln).get("ts", "") >= cut:
                    keep.append(ln)
            except ValueError:
                continue
        gone = len(lines) - len(keep)
        if gone:
            tmp = LOG_PATH + ".tmp"
            with io.open(tmp, "w", encoding="utf-8") as f:
                f.writelines(keep)
            os.replace(tmp, LOG_PATH)
    return gone


def new_cid():
    return secrets.token_hex(8)
