#!/usr/bin/env python3
"""아키텍처 다이어그램 후보 4종 — 공식 AWS 아이콘 합성본."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
ICON = BASE / "images" / "icons"
OUT = BASE / "images" / "instructor" / "architecture-options"
OUT.mkdir(parents=True, exist_ok=True)

_FONT_CANDIDATES = [
    ("/tmp/fonts/NotoSansKR-Regular.otf", "/tmp/fonts/NotoSansKR-Bold.otf"),
    (
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ),
]
FONT_R, FONT_B = next(
    ((r, b) for r, b in _FONT_CANDIDATES if Path(r).exists()),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
)

W, H = 1600, 900
BG = (248, 250, 252)
NAVY = (15, 23, 42)
SLATE = (71, 85, 105)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
BLUE = (37, 99, 235)
ORANGE = (234, 88, 12)
TEAL = (13, 148, 136)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
PURPLE = (124, 58, 237)
SOFT_BLUE = (239, 246, 255)
SOFT_ORANGE = (255, 247, 237)
SOFT_PURPLE = (245, 243, 255)
SOFT_GREEN = (240, 253, 244)
SOFT_TEAL = (240, 253, 250)
SOFT_RED = (254, 242, 242)
SOFT_YELLOW = (254, 252, 232)


def fnt(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def load_icon(name: str, size: int = 64) -> Image.Image:
    return Image.open(ICON / f"{name}.png").convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)


def paste_icon(base: Image.Image, name: str, cx: int, cy: int, size: int = 64):
    icon = load_icon(name, size)
    base.alpha_composite(icon, (int(cx - size / 2), int(cy - size / 2)))


def soft_card(img: Image.Image, xy, r=16, fill=WHITE, shadow=True):
    x0, y0, x1, y1 = xy
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0 + 3, y0 + 5, x1 + 3, y1 + 5), radius=r, fill=(15, 23, 42, 28))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(xy, radius=r, fill=fill + (255,) if len(fill) == 3 else fill)


def center_text(draw, text, cx, cy, font, fill=NAVY):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), text, font=font, fill=fill)


def arrow_h(draw, x0, y, x1, color=SLATE, w=3):
    draw.line((x0, y, x1 - 10, y), fill=color, width=w)
    draw.polygon([(x1, y), (x1 - 12, y - 7), (x1 - 12, y + 7)], fill=color)


def arrow_v(draw, x, y0, y1, color=SLATE, w=3):
    draw.line((x, y0, x, y1 - 10), fill=color, width=w)
    draw.polygon([(x, y1), (x - 7, y1 - 12), (x + 7, y1 - 12)], fill=color)


def tile(img, x, y, w, h, icon, title, sub, border, bg, icon_size=48):
    soft_card(img, (x, y, x + w, y + h), r=14, fill=bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, outline=border, width=2)
    paste_icon(img, icon, x + w // 2, y + 28 + icon_size // 2 - 6, icon_size)
    center_text(d, title, x + w // 2, y + h - 38, fnt(15, True), NAVY)
    if sub:
        center_text(d, sub, x + w // 2, y + h - 16, fnt(12), MUTED)


# ---------------------------------------------------------------------------
# Option 1: Horizontal request flow
# ---------------------------------------------------------------------------
def option1_flow():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 24), "Aniverse AWS Architecture", font=fnt(34, True), fill=NAVY)
    d.text((48, 72), "옵션 A · 요청 흐름형  —  사용자 → Route53 → WAF → ALB(HTTPS) → EC2 → 데이터", font=fnt(16), fill=SLATE)

    # main flow
    steps = [
        (40, "users", "Users", "브라우저", BLUE, SOFT_BLUE),
        (280, "route53", "Route 53", "DNS", PURPLE, SOFT_PURPLE),
        (520, "waf", "WAF", "문지기", RED, SOFT_RED),
        (760, "alb", "ALB", "HTTPS 종료·ACM", TEAL, SOFT_TEAL),
        (1000, "asg", "ASG+EC2", "Private · Nginx/Django", ORANGE, SOFT_ORANGE),
    ]
    for x, icon, t1, t2, color, bg in steps:
        tile(img, x, 160, 210, 200, icon, t1, t2, color, bg, 56)
    d = ImageDraw.Draw(img)
    for x in (250, 490, 730, 970):
        arrow_h(d, x, 260, x + 30, NAVY, 4)

    # data row
    soft_card(img, (1000, 420, 1540, 700), fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1000, 420, 1540, 700), radius=16, outline=PURPLE, width=2)
    center_text(d, "Data Tier (Private)", 1270, 450, fnt(16, True), PURPLE)
    tile(img, 1030, 480, 150, 180, "rds", "RDS", "MariaDB", GREEN, SOFT_GREEN, 44)
    tile(img, 1200, 480, 150, 180, "efs", "EFS", "media 공유", TEAL, SOFT_TEAL, 44)
    tile(img, 1370, 480, 150, 180, "s3", "S3", "Static/Media", ORANGE, SOFT_ORANGE, 44)

    arrow_v(d, 1105, 360, 420, ORANGE, 3)

    # side notes
    tile(img, 40, 420, 280, 160, "nat", "NAT", "Private 아웃바운드", PURPLE, SOFT_PURPLE, 44)
    tile(img, 350, 420, 280, 160, "ssm", "SSM", "Session Manager", TEAL, SOFT_TEAL, 44)
    tile(img, 660, 420, 280, 160, "acm", "ACM", "인증서 → ALB", TEAL, SOFT_TEAL, 44)

    soft_card(img, (40, 760, 1560, 860), fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 760, 1560, 860), radius=14, outline=BLUE, width=2)
    center_text(
        d,
        "사용자는 https://aniverse.my 로 접속  ·  AWS 퍼블릭 입구는 ALB  ·  TLS는 ALB에서 종료 후 EC2로 HTTP 전달",
        800,
        810,
        fnt(16, True),
        NAVY,
    )

    path = OUT / "01_flow.png"
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


# ---------------------------------------------------------------------------
# Option 2: VPC nested
# ---------------------------------------------------------------------------
def option2_vpc():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 20), "Aniverse AWS Architecture", font=fnt(32, True), fill=NAVY)
    d.text((48, 64), "옵션 B · VPC 계층형  —  Public / Private App / Private DB 서브넷", font=fnt(16), fill=SLATE)

    # external
    tile(img, 40, 120, 160, 150, "users", "Users", "Internet", BLUE, SOFT_BLUE, 44)
    tile(img, 230, 120, 160, 150, "route53", "Route 53", "aniverse.my", PURPLE, SOFT_PURPLE, 44)
    tile(img, 420, 120, 160, 150, "waf", "WAF", "ALB 앞단", RED, SOFT_RED, 44)
    d = ImageDraw.Draw(img)
    arrow_h(d, 200, 195, 230, NAVY, 3)
    arrow_h(d, 390, 195, 420, NAVY, 3)
    arrow_h(d, 580, 195, 620, NAVY, 3)

    # VPC box
    soft_card(img, (40, 300, 1560, 860), fill=(255, 255, 255), shadow=True)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 300, 1560, 860), radius=18, outline=PURPLE, width=3)
    d.text((60, 315), "VPC 10.0.0.0/16  ·  ap-northeast-2", font=fnt(16, True), fill=PURPLE)

    # Public
    soft_card(img, (60, 360, 520, 820), fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 360, 520, 820), radius=14, outline=GREEN, width=2)
    center_text(d, "Public Subnet", 290, 390, fnt(17, True), GREEN)
    tile(img, 100, 430, 180, 170, "alb", "ALB", "HTTPS·ACM", TEAL, WHITE, 48)
    tile(img, 300, 430, 180, 170, "ec2", "NAT Instance", "아웃바운드·EC2 NAT", ORANGE, WHITE, 48)
    tile(img, 100, 630, 380, 150, "igw", "IGW", "인터넷 게이트웨이", BLUE, WHITE, 44)

    # Private App
    soft_card(img, (550, 360, 1050, 820), fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((550, 360, 1050, 820), radius=14, outline=BLUE, width=2)
    center_text(d, "Private App Subnet", 800, 390, fnt(17, True), BLUE)
    tile(img, 590, 430, 200, 170, "asg", "ASG+EC2", "Nginx/Django", ORANGE, WHITE, 48)
    tile(img, 820, 430, 200, 170, "efs", "EFS", "media 마운트", TEAL, WHITE, 48)
    tile(img, 590, 630, 200, 150, "ssm", "SSM EP", "Endpoints", TEAL, WHITE, 40)
    tile(img, 820, 630, 200, 150, "elasticache", "Redis", "Channels", PURPLE, WHITE, 40)

    # Private DB
    soft_card(img, (1070, 360, 1540, 820), fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1070, 360, 1540, 820), radius=14, outline=PURPLE, width=2)
    center_text(d, "Private DB Subnet", 1305, 390, fnt(17, True), PURPLE)
    tile(img, 1160, 480, 280, 220, "rds", "RDS MariaDB", "Private · 3306", GREEN, WHITE, 64)
    # S3 outside note
    tile(img, 1160, 720, 280, 80, "s3", "S3 (VPC 밖)", "Static/Media", ORANGE, WHITE, 36)

    d = ImageDraw.Draw(img)
    arrow_h(d, 520, 515, 550, NAVY, 3)
    arrow_h(d, 1050, 560, 1070, NAVY, 3)

    path = OUT / "02_vpc.png"
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


# ---------------------------------------------------------------------------
# Option 3: 3-tier columns
# ---------------------------------------------------------------------------
def option3_tiers():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 24), "Aniverse AWS Architecture", font=fnt(34, True), fill=NAVY)
    d.text((48, 72), "옵션 C · 3-Tier 대응형  —  Web / App / Data 를 AWS 서비스로 매핑", font=fnt(16), fill=SLATE)

    cols = [
        (
            50,
            GREEN,
            SOFT_GREEN,
            "Web Tier (Public)",
            "온프렘: Nginx",
            [
                ("users", "Users"),
                ("route53", "Route 53"),
                ("waf", "WAF"),
                ("alb", "ALB + ACM"),
            ],
        ),
        (
            560,
            ORANGE,
            SOFT_ORANGE,
            "App Tier (Private)",
            "온프렘: Django",
            [
                ("asg", "ASG + EC2"),
                ("nginx", "Nginx"),
                ("django", "Daphne/Django"),
                ("ssm", "SSM"),
            ],
        ),
        (
            1070,
            PURPLE,
            SOFT_PURPLE,
            "Data Tier (Private)",
            "온프렘: NFS + MariaDB",
            [
                ("rds", "RDS MariaDB"),
                ("efs", "EFS"),
                ("s3", "S3"),
                ("elasticache", "Redis"),
            ],
        ),
    ]
    for x, color, bg, title, sub, items in cols:
        soft_card(img, (x, 130, x + 480, 820), fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 130, x + 480, 820), radius=20, outline=color, width=3)
        center_text(d, title, x + 240, 175, fnt(20, True), color)
        center_text(d, sub, x + 240, 215, fnt(14), MUTED)
        for i, (icon, label) in enumerate(items):
            iy = 260 + i * 130
            soft_card(img, (x + 40, iy, x + 440, iy + 110), fill=WHITE, shadow=False)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((x + 40, iy, x + 440, iy + 110), radius=12, outline=color, width=1)
            paste_icon(img, icon, x + 110, iy + 55, 52)
            d.text((x + 160, iy + 38), label, font=fnt(18, True), fill=NAVY)

    d = ImageDraw.Draw(img)
    for x in (530, 1040):
        arrow_h(d, x, 475, x + 30, NAVY, 4)

    path = OUT / "03_3tier.png"
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


# ---------------------------------------------------------------------------
# Option 4: HTTPS emphasis compact
# ---------------------------------------------------------------------------
def option4_https():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 22), "Aniverse AWS Architecture", font=fnt(34, True), fill=NAVY)
    d.text((48, 70), "옵션 D · HTTPS 입구 강조  —  프로토콜(HTTPS) vs AWS 입구(ALB)를 한 장에", font=fnt(16), fill=SLATE)

    # top banner
    soft_card(img, (40, 120, 1560, 220), fill=SOFT_TEAL, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 120, 1560, 220), radius=14, outline=TEAL, width=2)
    center_text(
        d,
        "사용자: https://aniverse.my   →   DNS(Route 53)   →   WAF   →   ALB에서 TLS 종료   →   EC2는 HTTP:80",
        800,
        170,
        fnt(17, True),
        TEAL,
    )

    # flow tiles
    steps = [
        (50, "users", "Users", BLUE, SOFT_BLUE),
        (290, "route53", "Route 53", PURPLE, SOFT_PURPLE),
        (530, "waf", "WAF", RED, SOFT_RED),
        (770, "alb", "ALB+ACM", TEAL, SOFT_TEAL),
        (1010, "asg", "ASG EC2", ORANGE, SOFT_ORANGE),
    ]
    for x, icon, title, color, bg in steps:
        tile(img, x, 260, 210, 180, icon, title, "", color, bg, 52)
    d = ImageDraw.Draw(img)
    for x in (260, 500, 740, 980):
        arrow_h(d, x, 350, x + 30, NAVY, 4)

    # labels under ALB
    d.text((790, 455), "HTTPS 종료", font=fnt(13, True), fill=TEAL)
    d.text((1030, 455), "Private", font=fnt(13, True), fill=ORANGE)

    # bottom data + side
    tile(img, 50, 520, 240, 200, "rds", "RDS", "MariaDB Private", GREEN, SOFT_GREEN, 48)
    tile(img, 320, 520, 240, 200, "efs", "EFS", "공유 media", TEAL, SOFT_TEAL, 48)
    tile(img, 590, 520, 240, 200, "s3", "S3", "Static/Media", ORANGE, SOFT_ORANGE, 48)
    tile(img, 860, 520, 240, 200, "nat", "NAT", "아웃바운드", PURPLE, SOFT_PURPLE, 48)
    tile(img, 1130, 520, 240, 200, "ssm", "SSM", "원격 점검", TEAL, SOFT_TEAL, 48)

    soft_card(img, (40, 760, 1560, 860), fill=SOFT_YELLOW, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 760, 1560, 860), radius=14, outline=ORANGE, width=2)
    center_text(
        d,
        "핵심: HTTPS는 ‘프로토콜’이고, ALB는 그 요청을 받는 ‘AWS 퍼블릭 입구’이다 (TLS 종료 지점 = ALB)",
        800,
        810,
        fnt(16, True),
        NAVY,
    )

    # connect ASG to data
    d = ImageDraw.Draw(img)
    arrow_v(d, 1115, 440, 520, ORANGE, 3)

    path = OUT / "04_https.png"
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


def main():
    option1_flow()
    option2_vpc()
    option3_tiers()
    option4_https()
    print("Done →", OUT)


if __name__ == "__main__":
    main()
