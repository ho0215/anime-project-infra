#!/usr/bin/env python3
"""Terraform 모듈 계층 구성도 — 사용자 제공 원본 + NAT Instance 패치."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
SRC = BASE / "images" / "sources" / "terraform_modules_layers.png"
OUT = BASE / "images" / "instructor" / "03_terraform_modules.png"

OUT_W, OUT_H = 1600, 900
MUTED = (100, 116, 139)
PATCH_FILL = (252, 253, 254)
# nat 카드 subtitle "NAT Gateway" 영역 (1536×1024 원본 기준)
NAT_PATCH = (718, 351, 958, 379)

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def font(size: int = 16):
    path = next(p for p in _FONT_CANDIDATES if Path(p).exists())
    return ImageFont.truetype(path, size)


def patch_nat_gateway_to_instance(img: Image.Image) -> Image.Image:
    out = img.copy()
    d = ImageDraw.Draw(out)
    d.rectangle(NAT_PATCH, fill=PATCH_FILL)
    text = "NAT Instance"
    fn = font(16)
    bb = d.textbbox((0, 0), text, font=fn)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0, y0, x1, y1 = NAT_PATCH
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.text((cx - tw // 2, cy - th // 2), text, font=fn, fill=MUTED)
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
