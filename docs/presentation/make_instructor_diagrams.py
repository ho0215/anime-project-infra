#!/usr/bin/env python3
"""강사용 PPT 다이어그램 — AWS Architecture Icons + GitHub 공식 마크 사용."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
ICON = BASE / "images" / "icons"
OUT = BASE / "images" / "instructor"
OUT.mkdir(parents=True, exist_ok=True)

# Prefer Noto CJK if present, else WenQuanYi (system)
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


def fnt(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def load_icon(name: str, size: int = 64) -> Image.Image:
    path = ICON / f"{name}.png"
    img = Image.open(path).convert("RGBA")
    return img.resize((size, size), Image.Resampling.LANCZOS)


def paste_icon(base: Image.Image, name: str, cx: int, cy: int, size: int = 64):
    icon = load_icon(name, size)
    x = int(cx - size / 2)
    y = int(cy - size / 2)
    base.alpha_composite(icon, (x, y))


def rr(draw: ImageDraw.ImageDraw, xy, r, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def soft_card(img: Image.Image, xy, r=18, fill=WHITE, shadow=True):
    x0, y0, x1, y1 = xy
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0 + 3, y0 + 5, x1 + 3, y1 + 5), radius=r, fill=(15, 23, 42, 30))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    fill_a = fill + (255,) if len(fill) == 3 else fill
    d.rounded_rectangle(xy, radius=r, fill=fill_a)


def arrow_h(draw, x0, y, x1, color=SLATE, w=3):
    draw.line((x0, y, x1 - 10, y), fill=color, width=w)
    draw.polygon([(x1, y), (x1 - 12, y - 7), (x1 - 12, y + 7)], fill=color)


def arrow_v(draw, x, y0, y1, color=SLATE, w=3):
    draw.line((x, y0, x, y1 - 10), fill=color, width=w)
    draw.polygon([(x, y1), (x - 7, y1 - 12), (x + 7, y1 - 12)], fill=color)


def center_text(draw, text, cx, cy, font, fill=NAVY):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), text, font=font, fill=fill)


def service_tile(img, x, y, w, h, icon, title, sub, border=BLUE, bg=SOFT_BLUE, icon_size=52):
    soft_card(img, (x, y, x + w, y + h), r=16, fill=bg, shadow=True)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, outline=border, width=2)
    paste_icon(img, icon, x + w // 2, y + 28 + icon_size // 2 - 8, icon_size)
    center_text(d, title, x + w // 2, y + h - 42, fnt(18, True), NAVY)
    if sub:
        center_text(d, sub, x + w // 2, y + h - 20, fnt(13), MUTED)


# ---------------------------------------------------------------------------
# 01 On-prem 3-Tier
# ---------------------------------------------------------------------------
def make_01_onprem():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 28), "온프레미스 3-Tier 구조", font=fnt(36, True), fill=NAVY)
    d.text(
        (48, 78),
        "Users → Web(Nginx) → App(Django) → Data(NFS + MariaDB)  — 서버를 직접 운영",
        font=fnt(18),
        fill=SLATE,
    )

    # Users
    soft_card(img, (60, 280, 260, 560), fill=SOFT_BLUE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 280, 260, 560), radius=18, outline=BLUE, width=2)
    paste_icon(img, "users", 160, 360, 72)
    center_text(d, "Users", 160, 450, fnt(22, True), BLUE)
    center_text(d, "Browser", 160, 485, fnt(15), MUTED)

    tiers = [
        (320, GREEN, SOFT_GREEN, "nginx", "Web Tier", "Nginx 서버", "정적/미디어 · Reverse Proxy"),
        (680, ORANGE, SOFT_ORANGE, "django", "App Tier", "Django 서버", "Gunicorn/Daphne · 비즈니스로직"),
        (1040, PURPLE, SOFT_PURPLE, "rds", "Data Tier", "MariaDB + NFS", "DB · 파일 저장 서버"),
    ]
    for x, color, bg, icon, title, mid, sub in tiers:
        soft_card(img, (x, 220, x + 300, 620), fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 220, x + 300, 620), radius=20, outline=color, width=3)
        center_text(d, title, x + 150, 260, fnt(24, True), color)
        paste_icon(img, icon, x + 150, 360, 80)
        # servers icon under for "physical server" feel
        if icon != "rds":
            paste_icon(img, "servers" if (ICON / "servers.png").exists() else "ec2inst", x + 150, 455, 40)
        else:
            paste_icon(img, "efs", x + 100, 455, 40)
            paste_icon(img, "rds_maria" if (ICON / "rds_maria.png").exists() else "rds", x + 200, 455, 40)
        center_text(d, mid, x + 150, 520, fnt(17, True), NAVY)
        center_text(d, sub, x + 150, 555, fnt(13), MUTED)

    d = ImageDraw.Draw(img)
    for x0, x1 in [(260, 320), (620, 680), (980, 1040)]:
        arrow_h(d, x0 + 5, 420, x1 - 5, NAVY, 4)

    # pain callouts
    soft_card(img, (60, 680, 1540, 860), fill=SOFT_RED, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 680, 1540, 860), radius=16, outline=RED, width=2)
    d.text((90, 710), "운영 부담", font=fnt(20, True), fill=RED)
    pains = [
        "SSH로 서버별 수동 배포",
        "환경 불일치 (로컬 ≠ 서버)",
        "장애·확장 대응 느림",
        ".env / 키 파일 분산",
    ]
    for i, p in enumerate(pains):
        d.text((90 + i * 370, 770), f"• {p}", font=fnt(16), fill=NAVY)

    out = OUT / "01_onprem_3tier.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("Wrote", out)


# ---------------------------------------------------------------------------
# 05 Ops · HA · Monitoring · Security
# ---------------------------------------------------------------------------
def make_05_ops():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 28), "CI/CD · 고가용성 · 모니터링 · 보안", font=fnt(34, True), fill=NAVY)
    d.text((48, 78), "배포 경로 고정 · 트래픽 분산 · 관측 · 입구 보안을 AWS 서비스로", font=fnt(18), fill=SLATE)

    panels = [
        (
            40,
            BLUE,
            SOFT_BLUE,
            "CI/CD",
            [
                ("githubactions", "GitHub Actions"),
                ("s3", "S3 deploy.zip"),
                ("codedeploy", "CodeDeploy"),
                ("asg", "ASG 배포"),
            ],
            "ALB /health/ 로 성공 판정",
        ),
        (
            420,
            ORANGE,
            SOFT_ORANGE,
            "고가용성 (HA)",
            [
                ("alb", "ALB"),
                ("asg", "Auto Scaling"),
                ("ec2", "EC2 교체"),
                ("rds", "RDS Private"),
            ],
            "트래픽 분산 · 인스턴스 자동 교체",
        ),
        (
            800,
            TEAL,
            SOFT_TEAL,
            "모니터링",
            [
                ("cloudwatch", "CloudWatch"),
                ("alb", "TG Health"),
                ("ssm", "SSM 점검"),
                ("ec2inst", "서버 로그"),
            ],
            "알람 · 헬스체크 · 원격 점검",
        ),
        (
            1180,
            RED,
            SOFT_RED,
            "보안",
            [
                ("waf", "WAF"),
                ("acm", "HTTPS/ACM"),
                ("secrets", "Secrets"),
                ("nacl", "SG · NACL"),
            ],
            "입구 차단 · 암호화 · 키 주입",
        ),
    ]

    for x, color, bg, title, icons, footer in panels:
        soft_card(img, (x, 130, x + 360, 820), fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 130, x + 360, 820), radius=20, outline=color, width=3)
        center_text(d, title, x + 180, 175, fnt(22, True), color)
        for i, (icon, label) in enumerate(icons):
            iy = 230 + i * 120
            soft_card(img, (x + 30, iy, x + 330, iy + 100), fill=WHITE, shadow=False)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((x + 30, iy, x + 330, iy + 100), radius=14, outline=color, width=1)
            paste_icon(img, icon, x + 90, iy + 50, 52)
            d.text((x + 140, iy + 35), label, font=fnt(17, True), fill=NAVY)
        d = ImageDraw.Draw(img)
        center_text(d, footer, x + 180, 780, fnt(13), MUTED)

    out = OUT / "05_ops_security.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("Wrote", out)


# ---------------------------------------------------------------------------
# 06 HTTPS · WAF
# ---------------------------------------------------------------------------
def make_06_https_waf():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 28), "HTTPS · WAF — 한 줄로 보기", font=fnt(34, True), fill=NAVY)
    d.text(
        (48, 78),
        "사용자 → 도메인(Route 53) → WAF(문지기) → ACM/HTTPS(ALB) → EC2",
        font=fnt(18),
        fill=SLATE,
    )

    steps = [
        (50, BLUE, SOFT_BLUE, "users", "1. 사용자", "브라우저 접속", "https://aniverse.my"),
        (350, PURPLE, SOFT_PURPLE, "route53", "2. Route 53", "도메인 DNS", "어디로 갈지 안내"),
        (650, RED, SOFT_RED, "waf", "3. WAF", "앞단 문지기", "이상한 요청 차단"),
        (950, TEAL, SOFT_TEAL, "acm", "4. ACM + ALB", "HTTPS 자물쇠", "통신 암호화"),
        (1250, ORANGE, SOFT_ORANGE, "ec2", "5. EC2 / 앱", "실제 서비스", "Django 처리"),
    ]
    for x, color, bg, icon, t1, t2, t3 in steps:
        soft_card(img, (x, 180, x + 280, 480), fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 180, x + 280, 480), radius=18, outline=color, width=3)
        paste_icon(img, icon, x + 140, 270, 72)
        center_text(d, t1, x + 140, 360, fnt(20, True), color)
        center_text(d, t2, x + 140, 400, fnt(16, True), NAVY)
        center_text(d, t3, x + 140, 435, fnt(14), MUTED)

    d = ImageDraw.Draw(img)
    for x in (330, 630, 930, 1230):
        arrow_h(d, x, 330, x + 20, NAVY, 4)

    # ALB detail strip
    soft_card(img, (50, 540, 1550, 700), fill=SOFT_TEAL, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((50, 540, 1550, 700), radius=16, outline=TEAL, width=2)
    paste_icon(img, "alb", 120, 620, 56)
    paste_icon(img, "acm", 220, 620, 56)
    d.text((290, 580), "HTTPS에서 한 일", font=fnt(20, True), fill=TEAL)
    for i, line in enumerate(
        [
            "• ACM으로 aniverse.my 인증서 발급",
            "• ALB 443 Listener에 인증서 연결",
            "• HTTP → HTTPS 리다이렉트",
            "• 결과: 자물쇠 + 암호화 통신",
        ]
    ):
        d.text((290 + (i % 2) * 550, 625 + (i // 2) * 35), line, font=fnt(16), fill=NAVY)

    soft_card(img, (50, 730, 1550, 860), fill=SOFT_RED, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((50, 730, 1550, 860), radius=16, outline=RED, width=2)
    paste_icon(img, "waf", 120, 795, 56)
    d.text((220, 760), "WAF에서 한 일", font=fnt(20, True), fill=RED)
    d.text(
        (220, 805),
        "• SQL 삽입·이상한 입력 차단   ·   한 IP 과도 요청 차단   ·   통과한 요청만 EC2로 전달",
        font=fnt(16),
        fill=NAVY,
    )

    out = OUT / "06_https_waf.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("Wrote", out)


# ---------------------------------------------------------------------------
# 07 AWS · GitHub stack summary with real icons
# ---------------------------------------------------------------------------
def make_07_stack():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 24), "사용한 AWS · GitHub 한 장 정리", font=fnt(32, True), fill=NAVY)
    d.text((48, 68), "왼쪽 AWS(인프라) · 오른쪽 GitHub(자동화) — 공식 아이콘으로 역할만 빠르게 보기", font=fnt(16), fill=SLATE)

    # Left AWS panel header
    soft_card(img, (30, 110, 780, 870), fill=SOFT_BLUE, shadow=True)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((30, 110, 780, 870), radius=20, outline=BLUE, width=2)
    # AWS wordmark-ish
    center_text(d, "AWS", 150, 150, fnt(26, True), BLUE)
    d.text((220, 138), "실제로 띄운 클라우드 서비스", font=fnt(15), fill=MUTED)

    aws_groups = [
        (
            55,
            190,
            "네트워크 · 보안",
            BLUE,
            [("vpc", "VPC"), ("igw", "IGW"), ("nat", "NAT"), ("nacl", "NACL")],
        ),
        (
            415,
            190,
            "트래픽 · 서버",
            ORANGE,
            [("alb", "ALB"), ("asg", "ASG"), ("ec2", "EC2"), ("codedeploy", "CodeDeploy")],
        ),
        (
            55,
            520,
            "데이터 · 저장",
            TEAL,
            [("rds", "RDS"), ("efs", "EFS"), ("s3", "S3"), ("dynamodb", "DynamoDB")],
        ),
        (
            415,
            520,
            "보안 · 관측",
            RED,
            [("waf", "WAF"), ("acm", "ACM"), ("secrets", "Secrets"), ("cloudwatch", "CloudWatch")],
        ),
    ]
    for gx, gy, title, color, items in aws_groups:
        soft_card(img, (gx, gy, gx + 340, gy + 290), fill=WHITE, shadow=False)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((gx, gy, gx + 340, gy + 290), radius=14, outline=color, width=2)
        d.text((gx + 16, gy + 14), title, font=fnt(16, True), fill=color)
        for i, (icon, label) in enumerate(items):
            ix = gx + 30 + (i % 2) * 160
            iy = gy + 60 + (i // 2) * 105
            soft_card(img, (ix, iy, ix + 140, iy + 90), fill=(248, 250, 252), shadow=False)
            d = ImageDraw.Draw(img)
            paste_icon(img, icon, ix + 70, iy + 32, 40)
            center_text(d, label, ix + 70, iy + 72, fnt(13, True), NAVY)

    # Right GitHub panel
    soft_card(img, (810, 110, 1570, 870), fill=SOFT_ORANGE, shadow=True)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((810, 110, 1570, 870), radius=20, outline=ORANGE, width=2)
    paste_icon(img, "github", 870, 150, 40)
    d.text((900, 135), "GitHub", font=fnt(24, True), fill=NAVY)
    d.text((1020, 142), "코드 관리 · 자동 배포에 쓴 기능", font=fnt(15), fill=MUTED)

    gh_groups = [
        (
            835,
            190,
            "저장소",
            PURPLE,
            [("github", "anime-project"), ("terraform", "anime-project-infra")],
        ),
        (
            1205,
            190,
            "GitHub Actions",
            BLUE,
            [("githubactions", "Terraform CI/CD"), ("codedeploy", "App Deploy")],
        ),
        (
            835,
            520,
            "비밀값 · 인증",
            ORANGE,
            [("secrets", "GitHub Secrets"), ("iam", "OIDC → AWS")],
        ),
        (
            1205,
            520,
            "협업",
            GREEN,
            [("github", "Pull Request"), ("githubactions", "main 배포")],
        ),
    ]
    for gx, gy, title, color, items in gh_groups:
        soft_card(img, (gx, gy, gx + 340, gy + 290), fill=WHITE, shadow=False)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((gx, gy, gx + 340, gy + 290), radius=14, outline=color, width=2)
        d.text((gx + 16, gy + 14), title, font=fnt(16, True), fill=color)
        for i, (icon, label) in enumerate(items):
            ix = gx + 30 + (i % 2) * 160
            iy = gy + 70 + (i // 2) * 120
            soft_card(img, (ix, iy, ix + 140, iy + 100), fill=(248, 250, 252), shadow=False)
            d = ImageDraw.Draw(img)
            paste_icon(img, icon, ix + 70, iy + 36, 40)
            # wrap long labels
            center_text(d, label, ix + 70, iy + 78, fnt(12, True), NAVY)

    out = OUT / "07_aws_github_stack.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("Wrote", out)


# ---------------------------------------------------------------------------
# Extra: storage roles with AWS icons (for slide 10 visual support)
# ---------------------------------------------------------------------------
def make_08_storage_roles():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 28), "S3 · EFS · RDS — 저장 역할 정리", font=fnt(34, True), fill=NAVY)
    d.text((48, 78), "같은 ‘데이터’라도 성격에 따라 AWS 저장소를 나눔", font=fnt(18), fill=SLATE)

    cards = [
        (
            60,
            GREEN,
            SOFT_GREEN,
            "rds",
            "RDS (MariaDB)",
            "구조화된 DB 데이터",
            [
                "회원 · 로그인 계정",
                "커뮤니티 글 · 댓글",
                "거래 · 채팅 메타",
                "창작물 제목·본문",
                "관계·트랜잭션 필요 값",
            ],
        ),
        (
            560,
            TEAL,
            SOFT_TEAL,
            "efs",
            "EFS",
            "ASG가 공유하는 파일",
            [
                "EC2 media/ NFS 마운트",
                "인스턴스 교체돼도 유지",
                "여러 EC2가 같은 media",
                "온프렘 NFS 대체",
                "Nginx /media 서빙",
            ],
        ),
        (
            1060,
            ORANGE,
            SOFT_ORANGE,
            "s3",
            "S3",
            "객체 스토리지",
            [
                "업로드 이미지 원본",
                "community / goods / works",
                "공개 URL 제공",
                "배포 zip 패키지",
                "tfstate 버킷 (별도)",
            ],
        ),
    ]
    for x, color, bg, icon, title, sub, bullets in cards:
        # cards fill more vertical space (no bottom one-line banner)
        soft_card(img, (x, 140, x + 460, 820), fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 140, x + 460, 820), radius=20, outline=color, width=3)
        paste_icon(img, icon, x + 230, 250, 88)
        center_text(d, title, x + 230, 350, fnt(24, True), color)
        center_text(d, sub, x + 230, 395, fnt(16, True), SLATE)
        for i, b in enumerate(bullets):
            d.text((x + 50, 450 + i * 52), f"•  {b}", font=fnt(17), fill=NAVY)

    out = OUT / "08_storage_roles.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("Wrote", out)


# ---------------------------------------------------------------------------
# Team roles with AWS icons
# ---------------------------------------------------------------------------
def make_09_team_roles():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((48, 28), "AWS 이전 — 맡은 역할", font=fnt(34, True), fill=NAVY)
    d.text((48, 78), "앱 기능 담당과 별도로, 인프라 모듈을 나눠 담당", font=fnt(18), fill=SLATE)

    roles = [
        (
            40,
            PURPLE,
            SOFT_PURPLE,
            "박서이",
            "Network & Security",
            [("vpc", "VPC"), ("nat", "NAT"), ("nacl", "SG/NACL"), ("igw", "IGW")],
            "modules/network · security · nat",
        ),
        (
            430,
            ORANGE,
            SOFT_ORANGE,
            "강유민",
            "Compute & Traffic",
            [("alb", "ALB"), ("asg", "ASG"), ("ec2", "EC2"), ("efs", "EFS mount")],
            "modules/alb · compute",
        ),
        (
            820,
            GREEN,
            SOFT_GREEN,
            "김윤주",
            "Data & Storage",
            [("rds", "RDS"), ("efs", "EFS"), ("s3", "S3"), ("dynamodb", "State Lock")],
            "modules/database · storage",
        ),
        (
            1210,
            RED,
            SOFT_RED,
            "김현우",
            "DevOps & CI/CD",
            [("githubactions", "Actions"), ("codedeploy", "CodeDeploy"), ("waf", "WAF"), ("acm", "HTTPS")],
            "environments/dev · cicd",
        ),
    ]
    for x, color, bg, name, role, icons, mods in roles:
        soft_card(img, (x, 140, x + 370, 820), fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 140, x + 370, 820), radius=20, outline=color, width=3)
        center_text(d, name, x + 185, 195, fnt(24, True), color)
        center_text(d, role, x + 185, 240, fnt(16, True), NAVY)
        center_text(d, mods, x + 185, 280, fnt(13), MUTED)
        for i, (icon, label) in enumerate(icons):
            iy = 340 + i * 105
            soft_card(img, (x + 35, iy, x + 335, iy + 90), fill=WHITE, shadow=False)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((x + 35, iy, x + 335, iy + 90), radius=12, outline=color, width=1)
            paste_icon(img, icon, x + 95, iy + 45, 48)
            d.text((x + 140, iy + 32), label, font=fnt(17, True), fill=NAVY)

    out = OUT / "09_team_roles.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print("Wrote", out)


def main():
    # Ensure optional icons exist
    if not (ICON / "servers.png").exists() and (ICON / "ec2inst.png").exists():
        pass
    make_01_onprem()
    make_05_ops()
    make_06_https_waf()
    make_07_stack()
    make_08_storage_roles()
    make_09_team_roles()
    # AWS VPC architecture + layered terraform module map (NAT Instance)
    import subprocess
    import sys

    for script in ("make_aws_overview_diagram.py", "make_terraform_modules_diagram.py"):
        subprocess.run([sys.executable, str(BASE / script)], check=True)
    print("All instructor diagrams regenerated with AWS/GitHub icons.")


if __name__ == "__main__":
    main()
