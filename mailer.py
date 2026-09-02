# -*- coding: utf-8 -*-
"""감정서를 메일로 보낸다.

발송은 **반드시 SMTP 릴레이**를 거친다. 이 서버의 공인 IP 는 역방향 이름(PTR)이
없어서 직접 보내면 받는 쪽이 스팸으로 거르거나 아예 거부한다(네이버는 25번 자체가
막혀 있다). 릴레이를 쓰면 보내는 주체가 그쪽 서버가 되므로 정상 도착한다.

설정(환경변수 · app.env):
    SMTP_HOST   릴레이 주소            예) smtp.gmail.com
    SMTP_PORT   기본 587
    SMTP_USER   릴레이 계정
    SMTP_PASS   릴레이 비밀번호(구글은 앱 비밀번호)
    SMTP_FROM   보내는 주소            예) 아솔 <asol@ssirn.co.kr>
    SMTP_MODE   starttls(기본) | ssl | plain

설정이 없으면 **보내지 않고 그렇다고 말한다.** 조용히 성공한 척하지 않는다.
"""
import os
import re
import html
import io
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate, make_msgid, parseaddr

# 완벽한 검사는 불가능하다. 오타를 걸러 주는 정도면 충분하다.
EMAIL_RE = re.compile(r"^[^@\s,;]+@[^@\s,;]+\.[A-Za-z]{2,}$")


def valid(addr: str) -> bool:
    """주소가 형태상 말이 되는지."""
    return bool(addr) and bool(EMAIL_RE.match(addr.strip()))


def _cfg():
    return {
        "host": os.getenv("SMTP_HOST", "").strip(),
        "port": int(os.getenv("SMTP_PORT", "587") or 587),
        "user": os.getenv("SMTP_USER", "").strip(),
        "pw":   os.getenv("SMTP_PASS", ""),
        "from": os.getenv("SMTP_FROM", "").strip(),
        "mode": (os.getenv("SMTP_MODE", "starttls") or "starttls").lower(),
    }


def configured() -> bool:
    """보낼 준비가 됐는지. 호스트와 보내는 주소는 반드시 있어야 한다."""
    c = _cfg()
    return bool(c["host"] and c["from"])


def status() -> str:
    """설정 상태를 사람이 읽을 문장으로. 비밀번호는 절대 담지 않는다."""
    c = _cfg()
    if not c["host"]:
        return "SMTP_HOST 가 없습니다 — 메일 발송이 꺼져 있습니다."
    if not c["from"]:
        return "SMTP_FROM 이 없습니다 — 보내는 주소를 정해야 합니다."
    return f"{c['host']}:{c['port']} ({c['mode']}) 로 보냅니다."


def oval_png(img, w=240, h=320, bg=(255, 255, 255)):
    """얼굴 사진을 세로로 긴 타원으로 잘라 PNG 바이트로 돌려준다.

    메일에서는 CSS ``border-radius`` 를 믿을 수 없다(Outlook 이 무시한다).
    그래서 **이미지 자체를 타원으로** 만들어 둔다. 투명 PNG 도 배경색이
    제각각인 클라이언트에서 지저분해지므로, 흰 바탕에 올려 불투명하게 굽는다.

    가장자리는 4배로 그린 마스크를 줄여 부드럽게 만든다(안티에일리어싱).
    """
    from PIL import Image, ImageDraw

    im = img.convert("RGB")
    # 얼굴은 가운데 위쪽에 있으므로, 세로로 자를 때 위를 조금 더 남긴다.
    tw, th = w, h
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    im = im.resize((max(1, int(sw * scale)), max(1, int(sh * scale))),
                   Image.LANCZOS)
    sw, sh = im.size
    left = (sw - tw) // 2
    top = int((sh - th) * 0.38)          # 정가운데(0.5)보다 위
    im = im.crop((left, top, left + tw, top + th))

    S = 4
    mask = Image.new("L", (tw * S, th * S), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, tw * S - 1, th * S - 1), fill=255)
    mask = mask.resize((tw, th), Image.LANCZOS)

    out = Image.new("RGB", (tw, th), bg)
    out.paste(im, (0, 0), mask)

    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _info_html(info):
    """기본 분석 결과를 메일용 표로. info 는 (이름, 값) 목록이다."""
    if not info:
        return ""
    rows = "".join(
        "<tr>"
        "<td style='padding:5px 14px 5px 0;color:#8a7a7a;font-size:13px;"
        "white-space:nowrap;vertical-align:top'>%s</td>"
        "<td style='padding:5px 0;font-size:14px;color:#3a2f2f'>%s</td>"
        "</tr>" % (html.escape(str(k)), html.escape(str(v)))
        for k, v in info if v)
    if not rows:
        return ""
    return ("<table style='border-collapse:collapse;margin:0 auto 4px'>"
            + rows + "</table>")


def _to_html(md: str) -> str:
    """감정서 마크다운을 메일용 HTML 로. 완전한 변환기가 아니라
    이 앱이 실제로 쓰는 문법(**굵게** · 목록 · 줄바꿈)만 다룬다."""
    out = []
    for raw in md.split("\n"):
        line = html.escape(raw.rstrip())
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", line)
        s = line.strip()
        if not s:
            out.append("<div style='height:10px'></div>")
        elif s.startswith("- "):
            out.append(f"<div style='margin:4px 0 4px 14px'>• {s[2:]}</div>")
        else:
            out.append(f"<div style='margin:6px 0'>{s}</div>")
    return "\n".join(out)


def render(body_md: str, title: str, subtitle: str = "",
           photo_cid: str = "", info=None) -> str:
    """메일 본문 HTML. 메일 클라이언트는 외부 CSS 를 무시하므로 전부 인라인으로 쓴다.

    photo_cid 를 주면 그 자리에 얼굴 사진을 넣는다. 이미지는 CID 로 붙인
    첨부라야 한다 — Gmail 은 ``src="data:..."`` 를 지운다.
    """
    photo_block = ("<div style='text-align:center;margin:0 0 14px'>"
                   "<img src='cid:%s' width='240' height='320' alt='' "
                   "style='display:inline-block;border:0;outline:none;"
                   "text-decoration:none'></div>" % photo_cid) if photo_cid else ""
    info_block = ("<div style='text-align:center;margin:0 0 20px;padding:14px 10px;"
                  "background:#faf7f7;border-radius:10px'>" + _info_html(info) + "</div>"
                  ) if _info_html(info) else ""
    return f"""<div style="margin:0;padding:24px 12px;background:#f6f2ee">
  <div style="max-width:640px;margin:0 auto;background:#fff;border-radius:14px;
              overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.06);
              font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;
              color:#3a2f2f;font-size:15px;line-height:1.85">
    <div style="background:linear-gradient(135deg,#7D5A5A,#a07878);color:#fff;
                padding:26px 28px">
      <div style="font-size:21px;font-weight:700">🧙‍♂️ {html.escape(title)}</div>
      {f'<div style="opacity:.85;font-size:13px;margin-top:6px">{html.escape(subtitle)}</div>' if subtitle else ''}
    </div>
    <div style="padding:26px 28px">
      {photo_block}
      {info_block}
      {_to_html(body_md)}
    </div>
    <div style="padding:16px 28px 24px;border-top:1px solid #eee;
                color:#999;font-size:12px;line-height:1.7">
      재미를 위한 것이오. 실제 운세와는 무관하니 마음 편히 보시구려.<br>
      사진은 분석 뒤 바로 지웠고, 메일 주소는 이 감정서를 보내는 데에만 썼소.
    </div>
  </div>
</div>"""


def send(to: str, subject: str, body_md: str,
         title: str = "관상가 아솔의 감정서", subtitle: str = "",
         photo=None, info=None):
    """감정서를 보낸다. 돌려주는 값은 (성공여부, 사람이 읽을 설명).

    실패를 삼키지 않는다 — 왜 못 보냈는지 그대로 돌려준다."""
    if not valid(to):
        return False, "메일 주소 형식이 올바르지 않습니다."
    if not configured():
        return False, status()

    c = _cfg()
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = c["from"]
    msg["To"] = to.strip()
    msg["Date"] = formatdate(localtime=True)
    # Message-ID 의 도메인은 보내는 주소를 따라간다(없으면 기본값).
    dom = (parseaddr(c["from"])[1].split("@")[-1] or "ssirn.co.kr")
    msg["Message-ID"] = make_msgid(domain=dom)
    # 사진은 미리 구워 둔다. 실패해도 감정서는 나가야 하므로 없는 셈 친다.
    png, cid = None, ""
    if photo is not None:
        try:
            png = oval_png(photo)
            cid = "face"
        except Exception:
            png, cid = None, ""

    plain = re.sub(r"\*\*|__", "", body_md)
    if info:
        plain = ("\n".join("%s: %s" % (k, v) for k, v in info if v)
                 + "\n\n" + plain)
    msg.set_content(plain)                                   # 평문 대안
    msg.add_alternative(render(body_md, title, subtitle, cid, info), subtype="html")

    if png:
        # HTML 부분 안에 붙여야 multipart/related 가 되어 본문에 표시된다.
        msg.get_payload()[1].add_related(png, "image", "png", cid="<%s>" % cid)

    try:
        if c["mode"] == "ssl":
            srv = smtplib.SMTP_SSL(c["host"], c["port"] or 465,
                                   timeout=25, context=ssl.create_default_context())
        else:
            srv = smtplib.SMTP(c["host"], c["port"] or 587, timeout=25)
        with srv:
            srv.ehlo()
            if c["mode"] == "starttls":
                srv.starttls(context=ssl.create_default_context())
                srv.ehlo()
            if c["user"]:
                srv.login(c["user"], c["pw"])
            srv.send_message(msg)
        return True, f"{to} 로 보냈습니다."
    except smtplib.SMTPAuthenticationError:
        return False, "릴레이 로그인에 실패했습니다 — SMTP_USER/SMTP_PASS 를 확인하세요."
    except smtplib.SMTPRecipientsRefused:
        return False, "받는 주소가 거부되었습니다 — 주소를 확인하세요."
    except (smtplib.SMTPException, OSError) as e:
        return False, f"보내지 못했습니다: {type(e).__name__} {e}"


# ── 남긴 주소 기록 ─────────────────────────────────────────────────────────
# 발송이 실패해도 주소는 남겨 둔다. 나중에 다시 보내거나 원인을 볼 수 있어야 한다.
RECORD_PATH = os.getenv("EMAIL_LOG", "data/emails.jsonl")


def record(addr: str, meta=None):
    """주소 하나를 한 줄로 남긴다. 실패해도 앱을 멈추지 않는다."""
    import json
    import datetime
    try:
        p = os.path.dirname(RECORD_PATH)
        if p:
            os.makedirs(p, exist_ok=True)
        row = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
               "email": addr.strip()}
        row.update(meta or {})
        with open(RECORD_PATH, "a", encoding="utf-8") as f:
            print(json.dumps(row, ensure_ascii=False), file=f)
    except OSError:
        pass          # 기록 실패로 감정서 발송까지 막지는 않는다
