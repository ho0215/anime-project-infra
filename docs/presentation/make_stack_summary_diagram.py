#!/usr/bin/env python3
"""AWS · GitHub 사용 기능 한 장 요약 — 아이콘 카드형(가독성)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path(__file__).resolve().parent / "images" / "instructor" / "07_aws_github_stack.png"
FONT_R = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_B = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"

W, H = 1600, 900
BG = (247, 249, 252)
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


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def rr(draw, xy, r, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def soft_panel(img, xy, r, fill, shadow=True):
    x0, y0, x1, y1 = xy
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0 + 4, y0 + 6, x1 + 4, y1 + 6), radius=r, fill=(15, 23, 42, 28))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(xy, radius=r, fill=fill + ((255,) if len(fill) == 3 else ()), outline=None)


def icon_bg(draw, cx, cy, size, color):
    r = size // 2
    # soft circle
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color + (0,))  # placeholder
    # solid with light fill
    fill = tuple(min(255, c + 210) for c in color[:3])
    # mix toward white
    fill = tuple(int(c * 0.18 + 255 * 0.82) for c in color[:3])
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=color, width=3)


def draw_icon(draw, kind, cx, cy, color, size=44):
    icon_bg(draw, cx, cy, size, color)
    s = size * 0.28
    w = 3
    if kind == "net":
        draw.ellipse((cx - s, cy - s, cx + s, cy + s), outline=color, width=w)
        draw.line((cx - s * 1.4, cy, cx + s * 1.4, cy), fill=color, width=w)
        draw.line((cx, cy - s * 1.4, cx, cy + s * 1.4), fill=color, width=w)
    elif kind == "server":
        for i, dy in enumerate((-12, 0, 12)):
            draw.rounded_rectangle((cx - 14, cy + dy - 6, cx + 14, cy + dy + 6), 3, outline=color, width=w)
            draw.ellipse((cx - 10, cy + dy - 2, cx - 6, cy + dy + 2), fill=color)
    elif kind == "data":
        draw.ellipse((cx - 14, cy - 14, cx + 14, cy - 4), outline=color, width=w)
        draw.line((cx - 14, cy - 9, cx - 14, cy + 10), fill=color, width=w)
        draw.line((cx + 14, cy - 9, cx + 14, cy + 10), fill=color, width=w)
        draw.arc((cx - 14, cy + 4, cx + 14, cy + 14), 0, 180, fill=color, width=w)
        draw.arc((cx - 14, cy - 2, cx + 14, cy + 8), 0, 180, fill=color, width=w)
    elif kind == "shield":
        pts = [(cx, cy - 16), (cx + 14, cy - 8), (cx + 12, cy + 8), (cx, cy + 16), (cx - 12, cy + 8), (cx - 14, cy - 8)]
        draw.polygon(pts, outline=color)
        # thicken by redrawing
        draw.line(pts + [pts[0]], fill=color, width=w)
        draw.line((cx, cy - 4, cx, cy + 6), fill=color, width=w)
        draw.line((cx - 5, cy + 1, cx, cy + 6), fill=color, width=w)
        draw.line((cx + 5, cy + 1, cx, cy + 6), fill=color, width=w)
    elif kind == "repo":
        draw.rounded_rectangle((cx - 12, cy - 14, cx + 12, cy + 14), 4, outline=color, width=w)
        draw.line((cx - 6, cy - 6, cx + 6, cy - 6), fill=color, width=w)
        draw.line((cx - 6, cy, cx + 4, cy), fill=color, width=w)
        draw.line((cx - 6, cy + 6, cx + 2, cy + 6), fill=color, width=w)
    elif kind == "actions":
        draw.polygon([(cx - 10, cy - 14), (cx + 14, cy), (cx - 10, cy + 14)], outline=color)
        draw.line([(cx - 10, cy - 14), (cx + 14, cy), (cx - 10, cy + 14), (cx - 10, cy - 14)], fill=color, width=w)
    elif kind == "key":
        draw.ellipse((cx - 14, cy - 10, cx - 2, cy + 2), outline=color, width=w)
        draw.line((cx - 2, cy - 4, cx + 14, cy - 4), fill=color, width=w)
        draw.line((cx + 8, cy - 4, cx + 8, cy + 6), fill=color, width=w)
        draw.line((cx + 12, cy - 4, cx + 12, cy + 4), fill=color, width=w)
    elif kind == "pr":
        draw.ellipse((cx - 12, cy - 14, cx - 4, cy - 6), outline=color, width=w)
        draw.ellipse((cx - 12, cy + 6, cx - 4, cy + 14), outline=color, width=w)
        draw.line((cx - 8, cy - 6, cx - 8, cy + 6), fill=color, width=w)
        draw.line((cx - 8, cy, cx + 8, cy - 8), fill=color, width=w)
        draw.ellipse((cx + 4, cy - 14, cx + 12, cy - 6), outline=color, width=w)


def tile(draw, x, y, w, h, title, subtitle, color):
    fill = tuple(int(c * 0.08 + 255 * 0.92) for c in color)
    rr(draw, (x, y, x + w, y + h), 12, fill, color, 2)
    # left accent bar
    draw.rounded_rectangle((x, y, x + 8, y + h), 4, fill=color)
    draw.text((x + 18, y + 10), title, font=fnt(15, True), fill=NAVY)
    draw.text((x + 18, y + 34), subtitle, font=fnt(12), fill=MUTED)


def category_card(img, box, icon, title, hint, color, services):
    """One category: icon + title + service tiles."""
    x0, y0, x1, y1 = box
    soft_panel(img, box, 18, WHITE, True)
    d = ImageDraw.Draw(img)
    draw_icon(d, icon, x0 + 40, y0 + 40, color, 52)
    d.text((x0 + 76, y0 + 18), title, font=fnt(20, True), fill=NAVY)
    d.text((x0 + 76, y0 + 46), hint, font=fnt(13), fill=MUTED)

    # service grid
    inner_x = x0 + 22
    inner_y = y0 + 84
    avail_w = x1 - x0 - 44
    gap = 10
    n = len(services)
    cols = 1 if n <= 3 else 2
    tw = (avail_w - (cols - 1) * gap) // cols
    th = 58 if n <= 3 else 52
    for i, (name, desc) in enumerate(services):
        c = i % cols
        r = i // cols
        tx = inner_x + c * (tw + gap)
        ty = inner_y + r * (th + gap)
        tile(d, tx, ty, tw, th, name, desc, color)


def main():
    base = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(base)

    d.text((48, 22), "사용한 기능 한 장 정리", font=fnt(32, True), fill=NAVY)
    d.text(
        (48, 66),
        "왼쪽은 AWS(인프라)  ·  오른쪽은 GitHub(자동화)  ·  아이콘 카드로 역할만 빠르게 보기",
        font=fnt(16),
        fill=SLATE,
    )

    # column headers
    soft_panel(base, (40, 105, 790, 165), 14, (239, 246, 255), False)
    soft_panel(base, (810, 105, 1560, 165), 14, (255, 247, 237), False)
    d = ImageDraw.Draw(base)
    draw_icon(d, "net", 80, 135, BLUE, 44)
    d.text((115, 118), "AWS", font=fnt(24, True), fill=BLUE)
    d.text((200, 124), "실제로 띄운 클라우드 서비스", font=fnt(14), fill=SLATE)

    draw_icon(d, "actions", 850, 135, ORANGE, 44)
    d.text((885, 118), "GitHub", font=fnt(24, True), fill=ORANGE)
    d.text((990, 124), "코드 관리 · 자동 배포에 쓴 기능", font=fnt(14), fill=SLATE)

    aws = [
        (
            "net",
            "네트워크 · 보안",
            "망을 나누고 출입을 통제",
            BLUE,
            [
                ("VPC / Subnet", "서비스 네트워크"),
                ("IGW · NAT", "인터넷 출입"),
                ("Security Group", "인스턴스 방화벽"),
                ("NACL", "DB 서브넷 보호"),
            ],
        ),
        (
            "server",
            "트래픽 · 서버",
            "요청을 받아 앱을 실행",
            ORANGE,
            [
                ("ALB", "로드밸런서 입구"),
                ("ASG · EC2", "자동 확장 서버"),
                ("CodeDeploy", "앱 배포"),
                ("IAM · SSM", "권한 · 원격점검"),
            ],
        ),
        (
            "data",
            "데이터 · 저장",
            "글·파일·캐시를 보관",
            TEAL,
            [
                ("RDS MariaDB", "회원·게시글 DB"),
                ("EFS", "공유 media 폴더"),
                ("S3", "이미지·배포 파일"),
                ("Redis · DynamoDB", "캐시 · State Lock"),
            ],
        ),
        (
            "shield",
            "보안 · 관측",
            "암호화·차단·알람",
            RED,
            [
                ("ACM · Route53", "인증서 · 도메인"),
                ("WAF", "앞단 공격 차단"),
                ("Secrets Manager", "런타임 비밀값"),
                ("CloudWatch", "상태·알람"),
            ],
        ),
    ]

    github = [
        (
            "repo",
            "저장소",
            "앱 / 인프라 코드를 분리",
            PURPLE,
            [
                ("anime-project", "Django 앱"),
                ("anime-project-infra", "Terraform 인프라"),
            ],
        ),
        (
            "actions",
            "GitHub Actions",
            "push하면 검사·배포 자동 실행",
            BLUE,
            [
                ("Terraform CI", "인프라 검사"),
                ("Terraform CD", "인프라 반영"),
                ("App Deploy", "앱 패키징·배포"),
            ],
        ),
        (
            "key",
            "비밀값 · 인증",
            "키를 코드에 넣지 않음",
            ORANGE,
            [
                ("GitHub Secrets", "비밀번호·키 보관"),
                ("Variables", "설정값"),
                ("OIDC → AWS", "키 없이 AWS 접속"),
            ],
        ),
        (
            "pr",
            "협업",
            "리뷰 후 main에 반영",
            GREEN,
            [
                ("Pull Request", "변경 제안"),
                ("Code Review", "동료 검토"),
                ("main 배포", "병합 후 자동 배포"),
            ],
        ),
    ]

    # layout: 2 cols x 2 rows each side
    def place(groups, left):
        positions = [
            (left, 180),
            (left + 375, 180),
            (left, 520),
            (left + 375, 520),
        ]
        card_w, card_h = 360, 320
        for (icon, title, hint, color, services), (x, y) in zip(groups, positions):
            # for github groups with fewer services, still same card size
            category_card(base, (x, y, x + card_w, y + card_h), icon, title, hint, color, services)

    place(aws, 40)
    place(github, 810)

    # convert and save
    out = base.convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
