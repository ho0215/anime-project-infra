#!/usr/bin/env python3
"""AWS VPC 아키텍처 구성도 — 사용자 제공 원본 기반."""
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
SRC = BASE / "images" / "sources" / "aws_architecture_vpc.png"
OUT = BASE / "images" / "instructor" / "02_aws_overview.png"

# PPT 슬라이드에 맞춘 출력 크기 (put_img가 비율 유지)
OUT_W, OUT_H = 1600, 900


def main():
    if not SRC.exists():
        raise SystemExit(f"Missing source image: {SRC}")

    img = Image.open(SRC).convert("RGB")
    img = img.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
