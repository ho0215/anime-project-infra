#!/usr/bin/env python3
"""Terraform 모듈 계층 구성도 — 사용자 제공 원본."""
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent
SRC = BASE / "images" / "sources" / "terraform_modules_layers.png"
OUT = BASE / "images" / "instructor" / "03_terraform_modules.png"

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
