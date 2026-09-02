# -*- coding: utf-8 -*-
"""감정서를 메일로 받겠다고 남긴 사람의 정보를 담는다.

개인정보라 다루는 규칙을 코드에 박아 둔다 — 화면에 적어 둔 약속과
실제 동작이 어긋나면 그게 제일 나쁘다.

  · 수집 항목 : 이름, 이메일, 휴대전화번호
  · 수집 목적 : 감정서 발송
  · 보유 기간 : RETAIN_DAYS 일. **열 때마다 지난 것을 실제로 지운다.**
  · 동의 없이는 저장하지 않는다(save 가 거부한다).

파일은 컨테이너 볼륨(`data/`)에 있어 이미지를 다시 구워도 남고,
`.gitignore` 로 저장소에는 들어가지 않는다.
"""
import os
import re
import sqlite3
import datetime

DB_PATH = os.getenv("LEADS_DB", "data/leads.db")
RETAIN_DAYS = int(os.getenv("LEADS_RETAIN_DAYS", "365"))

# 국내 휴대전화. 하이픈이 있든 없든 받고, 숫자만 남겨 비교한다.
PHONE_RE = re.compile(r"^0\d{1,2}\d{7,8}$")


def normalize_phone(raw):
    """숫자만 남긴다. 사람마다 010-1234-5678 / 01012345678 / 010 1234 5678 로 쓴다."""
    return re.sub(r"\D", "", raw or "")


def valid_phone(raw):
    return bool(PHONE_RE.match(normalize_phone(raw)))


def valid_name(raw):
    n = (raw or "").strip()
    return 2 <= len(n) <= 30


def _conn():
    d = os.path.dirname(DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init():
    """표를 만들고, 보유 기간이 지난 것을 지운다. 지운 건수를 돌려준다."""
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                ts       TEXT    NOT NULL,
                name     TEXT    NOT NULL,
                email    TEXT    NOT NULL,
                phone    TEXT    NOT NULL,
                gender   TEXT,
                age      TEXT,
                model    TEXT,
                mail_ok  INTEGER,
                mail_msg TEXT
            )""")
        c.execute("CREATE INDEX IF NOT EXISTS leads_ts ON leads(ts)")
        cut = (datetime.datetime.now()
               - datetime.timedelta(days=RETAIN_DAYS)).isoformat(timespec="seconds")
        cur = c.execute("DELETE FROM leads WHERE ts < ?", (cut,))
        return cur.rowcount


def save(name, email, phone, consent, meta=None):
    """한 사람을 저장한다. 돌려주는 값은 (성공여부, 설명).

    **동의가 없으면 저장하지 않는다.** 화면에서 막더라도 여기서 한 번 더 막는다 —
    화면 코드가 바뀌어도 이 규칙은 남아야 한다.
    """
    if not consent:
        return False, "동의 없이는 저장하지 않습니다."
    if not valid_name(name):
        return False, "이름을 확인해 주세요."
    if not valid_phone(phone):
        return False, "휴대전화번호를 확인해 주세요."

    m = meta or {}
    try:
        init()
        with _conn() as c:
            c.execute(
                "INSERT INTO leads (ts,name,email,phone,gender,age,model,mail_ok,mail_msg)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (datetime.datetime.now().isoformat(timespec="seconds"),
                 name.strip(), email.strip(), normalize_phone(phone),
                 m.get("gender"), m.get("age"), m.get("model"),
                 1 if m.get("mail_ok") else 0, m.get("mail_msg")))
        return True, "저장했습니다."
    except sqlite3.Error as e:
        # 저장 실패로 감정서까지 막지는 않는다. 다만 성공한 척도 하지 않는다.
        return False, "저장하지 못했습니다: %s" % e


def count():
    """지금 담겨 있는 사람 수."""
    try:
        with _conn() as c:
            return c.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    except sqlite3.Error:
        return 0


NOTICE = """**개인정보 수집·이용 동의**

- **수집 항목** — 이름, 이메일 주소, 휴대전화번호
- **수집 목적** — 관상 감정서 발송 및 관련 문의 응대
- **보유 기간** — 수집일로부터 **%d일**, 지나면 자동으로 지워집니다
- 동의를 **거부하실 수 있습니다.** 거부해도 아래 **[화면으로만 보기]** 로
  전체 감정서를 그대로 보실 수 있습니다.
""" % RETAIN_DAYS
