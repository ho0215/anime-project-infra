#!/usr/bin/env python3
"""Terraform 모듈 계층 구성도 — 사용자 제공 원본 + NAT Instance 패치."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
SRC = BASE / "images" / "sources" / "terraform_modules_layers.png"
OUT = BASE / "images" / "instructor" / "03_terraform_modules.png"

OUT_W, OUT_H = 1600, 900
MUTED = (100, 116, 139)

# nat 모듈 카드 영역 (1536×1024 원본)
NAT_CARD_X = (720, 955)
NAT_TITLE_Y = (318, 345)  # "nat" 제목 — 패치에서 제외
NAT_TEXT_X_OFFSET = 14  # 카드 중앙 대비 오른쪽 보정

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def font(size: int = 13):
    path = next(p for p in _FONT_CANDIDATES if Path(p).exists())
    return ImageFont.truetype(path, size)


def _is_subtitle_pixel(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    return r < 150 and g < 155 and b < 185 and (r + g + b) < 400


def find_nat_gateway_bbox(img: Image.Image) -> tuple[int, int, int, int]:
    x0, x1 = NAT_CARD_X
    rows: list[tuple[int, int, int]] = []
    for y in range(350, 385):
        xs = [x for x in range(x0, x1) if _is_subtitle_pixel(img.getpixel((x, y)))]
        if len(xs) >= 8:
            rows.append((y, min(xs), max(xs)))
    if not rows:
        raise RuntimeError("Could not locate NAT Gateway subtitle in source image")

    miny = min(r[0] for r in rows)
    maxy = max(r[0] for r in rows)
    minx = min(r[1] for r in rows)
    maxx = max(r[2] for r in rows)

    # "nat" 제목 줄이 섞이지 않도록 y 하한 보정
    miny = max(miny, NAT_TITLE_Y[1] + 8)
    pad_x, pad_y = 4, 3
    return (minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y)


def patch_nat_gateway_to_instance(img: Image.Image) -> Image.Image:
    out = img.copy()
    d = ImageDraw.Draw(out)
    patch = find_nat_gateway_bbox(out)
    x0, y0, x1, y1 = patch

    fill_y = max(0, y0 - 2)
    fill = out.getpixel(((x0 + x1) // 2, fill_y))

    d.rectangle(patch, fill=fill)

    text = "NAT Instance"
    fn = font(13)
    bb = d.textbbox((0, 0), text, font=fn)
    cx = (NAT_CARD_X[0] + NAT_CARD_X[1]) / 2 + NAT_TEXT_X_OFFSET
    cy = (y0 + y1) / 2
    tx = cx - (bb[0] + bb[2]) / 2
    ty = cy - (bb[1] + bb[3]) / 2
    d.text((tx, ty), text, font=fn, fill=MUTED)
    return out


def main():
    if not SRC.exists():
        raise SystemExit(f"Missing source image: {SRC}")

    img = Image.open(SRC).convert("RGB")
    img = patch_nat_gateway_to_instance(img)
    img = img.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
