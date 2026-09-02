# -*- coding: utf-8 -*-
"""얼굴을 찾아 반듯하게 잘라 준다. 메일용 타원과 보관용 크롭을 함께 만든다.

왜 따로 뒀나 — 메일(`mailer`)과 보관(`leads`)이 **같은 기준으로** 자르지 않으면
메일에 나간 얼굴과 DB 에 남은 얼굴이 달라진다. 한 군데서 정한다.

배경을 실제로 지우지는 않는다. `rembg` 같은 분리 모델은 400MB 가 넘고 요청마다
수 초가 드는데, **얼굴을 틀에 꽉 채우면** 배경이 거의 남지 않아 눈에 보이는
결과가 거의 같다. 서버 용량이 빠듯하므로 가벼운 쪽을 골랐다.
opencv 가 없거나 얼굴을 못 찾으면 가운데를 자른다 — 그래도 동작은 한다.
"""
import io

# 얼굴 폭의 몇 배를 남길지. 1.0 이면 얼굴만, 크면 여백이 는다.
WIDTH_RATIO = 1.55
# 눈이 틀 가운데쯤 오도록 중심을 얼굴 위쪽으로. 0.5 면 얼굴 정중앙.
CENTER_Y = 0.46


def find_face(im):
    """가장 큰 얼굴의 (x, y, w, h). 못 찾거나 opencv 가 없으면 None."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    try:
        gray = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
        gray = cv2.equalizeHist(gray)
        casc = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = casc.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
        if len(faces) == 0:
            return None
        return tuple(int(v) for v in max(faces, key=lambda f: int(f[2]) * int(f[3])))
    except Exception:
        return None


def _fit_box(iw, ih, cx, cy, bw, bh):
    """(cx,cy) 를 가운데 두는 bw×bh 상자를 사진 **안으로** 밀어 넣는다.

    이 밀어 넣기가 없으면 얼굴이 가장자리에 있을 때 상자가 사진 밖으로 나가고,
    PIL 은 그 부분을 검게 채운다. 실제로 얼굴이 동그라미 밖으로 삐져나와
    보이던 원인이 이것이다. 먼저 밀어 보고, 그래도 넘치면 상자를 줄인다.
    """
    if bw > iw:
        bh *= iw / float(bw)
        bw = float(iw)
    if bh > ih:
        bw *= ih / float(bh)
        bh = float(ih)
    left = min(max(cx - bw / 2.0, 0.0), iw - bw)
    top = min(max(cy - bh / 2.0, 0.0), ih - bh)
    return (int(round(left)), int(round(top)),
            int(round(left + bw)), int(round(top + bh)))


def _crop_box(im, w, h, face):
    """`face_crop` 이 쓸 자르기 상자. 상자를 따로 뺀 까닭은 `boxed_png` 가
    **같은 상자**를 알아야 얼굴 네모를 제자리에 그릴 수 있기 때문이다."""
    iw, ih = im.size

    if face is not None:
        fx, fy, fw, fh = face
        cx = fx + fw / 2.0
        cy = fy + fh * CENTER_Y
        bw = fw * WIDTH_RATIO
        bh = bw * (h / float(w))
        if bh < fh * 1.45:            # 턱이 잘리지 않게
            bh = fh * 1.45
            bw = bh * (w / float(h))
    else:
        scale = max(w / float(iw), h / float(ih))
        bw, bh = w / scale, h / scale
        cx, cy = iw / 2.0, ih * 0.42

    return _fit_box(iw, ih, cx, cy, bw, bh)


def face_crop(img, w, h):
    """얼굴을 가운데 둔 w×h 이미지. 얼굴을 못 찾으면 가운데를 자른다."""
    from PIL import Image

    im = img.convert("RGB")
    return im.crop(_crop_box(im, w, h, find_face(im))).resize((w, h), Image.LANCZOS)


def boxed_png(img, w=240, h=320, color=(200, 60, 60), width=3):
    """얼굴을 **어디로 보았는지** 네모로 표시한 PNG. 타원과 나란히 놓고 보여 준다.

    타원은 결과만 보여 줄 뿐 왜 그렇게 잘렸는지는 말해 주지 않는다. Haar 가
    찾아낸 자리를 그대로 그려 주면, 엉뚱한 데를 잡았을 때 사람이 바로 알아채고
    다시 찍는다. 얼굴을 못 찾았으면 네모 없이 크롭만 돌려준다 —
    못 찾았다는 말은 화면 쪽에서 한다.
    """
    from PIL import Image, ImageDraw

    im = img.convert("RGB")
    face = find_face(im)
    box = _crop_box(im, w, h, face)          # face_crop 과 같은 상자여야 자리가 맞는다
    out = im.crop(box).resize((w, h), Image.LANCZOS)

    if face is not None:
        fx, fy, fw, fh = face
        sx = w / float(box[2] - box[0])      # 자른 뒤 늘린 만큼 좌표도 늘린다
        sy = h / float(box[3] - box[1])
        x0, y0 = (fx - box[0]) * sx, (fy - box[1]) * sy
        ImageDraw.Draw(out).rectangle(
            [x0, y0, x0 + fw * sx, y0 + fh * sy], outline=color, width=width)

    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def oval_png(img, w=240, h=320, bg=(255, 255, 255)):
    """메일에 넣을 세로 타원 PNG.

    메일에서는 CSS ``border-radius`` 를 믿을 수 없으므로(Outlook 이 무시한다)
    **이미지 자체를** 타원으로 만든다. 투명 PNG 도 클라이언트마다 배경이 달라
    지저분해지므로 흰 바탕에 올려 불투명하게 굽고, 가장자리를 살짝 흐려
    오려 붙인 느낌을 낸다.
    """
    from PIL import Image, ImageDraw, ImageFilter

    im = face_crop(img, w, h)

    S = 4                                   # 4배로 그렸다 줄여 계단을 없앤다
    mask = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, w * S - 1, h * S - 1), fill=255)
    mask = mask.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.0))

    out = Image.new("RGB", (w, h), bg)
    out.paste(im, (0, 0), mask)

    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def face_jpeg(img, w=480, h=640, quality=88):
    """보관용 얼굴 크롭. 타원 마스크를 씌우지 않는다.

    마스크는 보여 주는 방식일 뿐이고, 나중에 다른 데 쓰려면 **가려지지 않은**
    크롭이 훨씬 쓸모 있다. 필요하면 그때 다시 타원을 씌우면 된다.
    """
    buf = io.BytesIO()
    face_crop(img, w, h).save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()
