# -*- coding: utf-8 -*-
"""아솔은 진단하지 않는다 — 그 약속을 코드가 지키는지 확인한다.

계획서의 「병을 말하지 않는다」를 시험한다. 프롬프트는 지시일 뿐이라 모델이
한 번만 어겨도 그대로 사람에게 간다. 그래서 코드가 마지막에 걸러야 하고,
그 거르개가 실제로 동작하는지는 여기서 본다.

    python tests/test_medical.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reading  # noqa: E402

ok = fail = 0


def chk(cond, label):
    global ok, fail
    if cond:
        ok += 1
        print("  OK   %s" % label)
    else:
        fail += 1
        print("  FAIL %s" % label)


def sec(t):
    print("── %s ──" % t)


# ── 1. 걸러야 할 것 ──────────────────────────────────────────────────────
sec("1. 의료 표현이 든 문장은 빠지는가")
for word in reading.NO_MEDICAL_WORDS:
    src = "이마가 훤하니 복이 많소.\n%s 이야기를 하니 딱하오." % word
    clean, dropped = reading.scrub_medical(src)
    chk(word not in clean and len(dropped) == 1, "'%s' 가 든 문장이 빠진다" % word)

sec("2. 성한 문장은 남는가")
src = "이마가 훤하니 복이 많소. 눈매가 서글서글하여 사람이 따르오."
clean, dropped = reading.scrub_medical(src)
chk(clean.strip() == src and not dropped, "의료 표현이 없으면 한 글자도 안 건드린다")

sec("3. 한 문장만 골라 빼는가")
src = "이마가 훤하오. 이는 치료가 필요하오. 눈매가 곱소."
clean, dropped = reading.scrub_medical(src)
chk("이마가 훤하오." in clean, "앞 문장은 남는다")
chk("눈매가 곱소." in clean, "뒷 문장은 남는다")
chk("치료" not in clean, "가운데 문장만 빠진다")
chk(len(dropped) == 1, "뺀 것이 하나로 보고된다")

sec("4. 애먼 것이 걸리지 않는가 (오탐)")
for w in ("병풍처럼 든든하오", "병자년에 태어난 기운이오", "명예를 얻겠소",
          "학문에 뜻이 있소", "환하게 웃는 상이오"):
    clean, dropped = reading.scrub_medical(w + ".")
    chk(not dropped, "'%s' 는 걸리지 않는다" % w)

sec("5. 문단과 제목을 지키는가")
src = "## 아솔의 감정서\n\n이마가 훤하오.\n\n질병을 조심하시오.\n\n눈매가 곱소."
clean, dropped = reading.scrub_medical(src)
chk(clean.startswith("## 아솔의 감정서"), "제목 줄은 그대로다")
chk("이마가 훤하오." in clean and "눈매가 곱소." in clean, "다른 문단은 남는다")
chk("질병" not in clean, "걸린 문단은 빠진다")
chk("\n\n" in clean, "문단 사이가 무너지지 않는다")

sec("6. 빈 입력·이상한 입력에 안 죽는가")
for bad in ("", None, "\n\n", "...", "치료"):
    try:
        reading.scrub_medical(bad)
        chk(True, "%r 에 안 죽는다" % (bad,))
    except Exception as e:
        chk(False, "%r 에서 터짐: %s" % (bad, e))

sec("7. 진행 미리보기는 낱말만 가리는가")
masked = reading.mask_medical("이는 치료가 필요한 질병이오")
chk("치료" not in masked and "질병" not in masked, "낱말이 가려진다")
chk("이는" in masked and "필요한" in masked, "나머지 글자는 남는다 (진행 표시라 흐름이 보여야 한다)")
chk(reading.mask_medical("") == "", "빈 글에 안 죽는다")

sec("8. 프롬프트 양쪽에 금지가 들어 있는가")
chk("진단하지 마시오" in reading.SHORT_FORM, "★ 맛보기 양식 — 전에는 없어서 첫 방문자가 무방비였다")
chk("진단하지 마시오" in reading.PROMPT_FORM, "★ 전체 양식")

print()
print("통과 %d · 실패 %d" % (ok, fail))
sys.exit(1 if fail else 0)
