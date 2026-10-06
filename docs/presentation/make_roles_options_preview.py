#!/usr/bin/env python3
"""역할분담 옵션 A~F 미리보기 PNG 생성."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "images" / "roles_options"
OUT.mkdir(parents=True, exist_ok=True)
ART = Path("/opt/cursor/artifacts/roles_options")
ART.mkdir(parents=True, exist_ok=True)

_FONT_CANDIDATES = [
    ("/tmp/fonts/NotoSansKR-Regular.otf", "/tmp/fonts/NotoSansKR-Bold.otf"),
    ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
]
FONT_R, FONT_B = next(
    ((r, b) for r, b in _FONT_CANDIDATES if Path(r).exists()),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
)

W, H = 1600, 900
BG = (248, 250, 252)
NAVY = (15, 23, 42)
WHITE = (255, 255, 255)
GRAY = (107, 114, 128)
LIGHT = (243, 244, 246)
SOFT = (249, 250, 251)
CYAN = (14, 165, 233)
ORANGE = (249, 115, 22)
PURPLE = (139, 92, 246)
TEAL = (20, 184, 166)

ROLES = [
    (ORANGE, "김현우", "DevOps / GitOps", ["Actions · ECR", "Argo CD", "OIDC · 이관 복구"]),
    (CYAN, "박서이", "EKS · 네트워크 · 보안", ["EKS · VPC", "Ingress · WAF · RBAC", "노드 · NAT"]),
    (TEAL, "김윤주", "컨테이너 · DB · 관측", ["Docker · Helm", "DB Pod · Backup", "Tempo · Alert"]),
    (PURPLE, "강유민", "창작마당 · Compute", ["창작마당", "노드 운영", "ALB · 트래픽"]),
]


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def rr(d, box, r, fill, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def center(d, text, cx, cy, font, fill=NAVY):
    b = d.textbbox((0, 0), text, font=font)
    d.text((cx - (b[2] - b[0]) / 2, cy - (b[3] - b[1]) / 2), text, font=font, fill=fill)


def header(img, code, title):
    d = ImageDraw.Draw(img)
    center(d, f"옵션 {code}  ·  {title}", W // 2, 48, fnt(34, True), NAVY)
    center(d, "PPT에서 텍스트 수정 가능", W // 2, 90, fnt(16), GRAY)


def save(img, name):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    img.convert("RGB").save(ART / name, "PNG", optimize=True)
    print("Wrote", path)


def option_a():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(img, "A", "컬러 헤더 4열")
    for i, (color, name, area, lines) in enumerate(ROLES):
        x = 40 + i * 390
        rr(d, (x, 130, x + 360, 280), 16, color)
        center(d, name, x + 180, 185, fnt(28, True), WHITE)
        center(d, area, x + 180, 235, fnt(15), WHITE)
        rr(d, (x, 295, x + 360, 820), 16, LIGHT)
        for j, line in enumerate(lines):
            center(d, "·  " + line, x + 180, 400 + j * 90, fnt(20), NAVY)
    save(img, "roles_option_A.png")


def option_b():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(img, "B", "가로 행 + 액센트 바")
    for i, (color, name, area, lines) in enumerate(ROLES):
        y = 140 + i * 170
        d.rectangle((55, y, 70, y + 140), fill=color)
        rr(d, (80, y, 1545, y + 140), 14, LIGHT)
        d.text((110, y + 28), f"{name}    ·    {area}", font=fnt(26, True), fill=NAVY)
        d.text((110, y + 85), "  ·  ".join(lines), font=fnt(18), fill=GRAY)
    save(img, "roles_option_B.png")


def option_c():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(img, "C", "2×2 그리드 + 아이콘")
    icon_dir = BASE / "images" / "icons"
    icons = ["githubactions", "vpc", "rds_maria", "alb"]
    positions = [(50, 130), (820, 130), (50, 490), (820, 490)]
    for (x, y), (color, name, area, lines), icon in zip(positions, ROLES, icons):
        rr(d, (x, y, x + 730, y + 320), 18, SOFT, color, 3)
        icon_path = icon_dir / f"{icon}.png"
        if icon_path.exists():
            ic = Image.open(icon_path).convert("RGBA").resize((88, 88), Image.Resampling.LANCZOS)
            img.paste(ic, (x + 36, y + 100), ic)
        d.text((x + 150, y + 40), name, font=fnt(32, True), fill=color)
        d.text((x + 150, y + 100), area, font=fnt(20, True), fill=NAVY)
        for j, line in enumerate(lines):
            d.text((x + 150, y + 165 + j * 40), "·  " + line, font=fnt(20), fill=GRAY)
    save(img, "roles_option_C.png")


def option_d():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(img, "D", "번호 뱃지 · 미니멀")
    for i, (color, name, area, lines) in enumerate(ROLES):
        y = 150 + i * 160
        d.ellipse((70, y + 30, 150, y + 110), fill=color)
        center(d, str(i + 1), 110, y + 70, fnt(28, True), WHITE)
        d.text((190, y + 25), name, font=fnt(28, True), fill=NAVY)
        d.text((190, y + 75), area, font=fnt(18), fill=color)
        d.text((620, y + 50), "  ·  ".join(lines), font=fnt(20), fill=NAVY)
    save(img, "roles_option_D.png")


def option_e():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(img, "E", "영역 칩 + 세로 카드")
    for i, (color, name, area, lines) in enumerate(ROLES):
        x = 45 + i * 390
        rr(d, (x, 140, x + 360, 830), 18, WHITE, color, 3)
        center(d, name, x + 180, 230, fnt(30, True), NAVY)
        rr(d, (x + 40, 290, x + 320, 345), 20, color)
        center(d, area, x + 180, 317, fnt(14, True), WHITE)
        for j, line in enumerate(lines):
            center(d, "·  " + line, x + 180, 450 + j * 80, fnt(20), NAVY)
    save(img, "roles_option_E.png")


def option_f():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(img, "F", "표 형식")
    rr(d, (50, 140, 1550, 210), 12, NAVY)
    d.text((80, 158), "이름", font=fnt(18, True), fill=WHITE)
    d.text((320, 158), "영역", font=fnt(18, True), fill=WHITE)
    d.text((720, 158), "담당", font=fnt(18, True), fill=WHITE)
    for i, (color, name, area, lines) in enumerate(ROLES):
        y = 230 + i * 140
        fill = LIGHT if i % 2 == 0 else SOFT
        rr(d, (50, y, 1550, y + 125), 12, fill)
        d.text((80, y + 45), name, font=fnt(24, True), fill=color)
        d.text((320, y + 50), area, font=fnt(18), fill=NAVY)
        d.text((720, y + 50), "  ·  ".join(lines), font=fnt(18), fill=GRAY)
    save(img, "roles_option_F.png")


def main():
    option_a()
    option_b()
    option_c()
    option_d()
    option_e()
    option_f()
    print("Previews →", OUT, "and", ART)


if __name__ == "__main__":
    main()
