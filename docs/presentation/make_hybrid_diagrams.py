#!/usr/bin/env python3
"""하이브리드 PPT용 구성도 — AWS 아이콘 + 시스템 한글 폰트.

출력: images/hybrid/hybrid_*.png
타일/카드 안 아이콘·글씨를 세로 중앙에 배치 (위로 몰리지 않게).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
ICON = BASE / "images" / "icons"
OUT = BASE / "images" / "hybrid"
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
NAVY = (10, 17, 40)
SLATE = (71, 85, 105)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
CYAN = (0, 174, 239)
ORANGE = (234, 88, 12)
TEAL = (13, 148, 136)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
PURPLE = (124, 58, 237)
SOFT_BLUE = (236, 248, 255)
SOFT_ORANGE = (255, 247, 237)
SOFT_PURPLE = (245, 243, 255)
SOFT_GREEN = (240, 253, 244)
SOFT_TEAL = (240, 253, 250)
SOFT_RED = (254, 242, 242)


def fnt(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def load_icon(name: str, size: int = 64) -> Image.Image:
    path = ICON / f"{name}.png"
    if not path.exists():
        return Image.new("RGBA", (size, size), (200, 200, 200, 255))
    img = Image.open(path).convert("RGBA")
    return img.resize((size, size), Image.Resampling.LANCZOS)


def paste_icon(base: Image.Image, name: str, cx: int, cy: int, size: int = 64):
    icon = load_icon(name, size)
    base.alpha_composite(icon, (int(cx - size / 2), int(cy - size / 2)))


def soft_card(img: Image.Image, xy, r=16, fill=WHITE, shadow=True):
    x0, y0, x1, y1 = xy
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0 + 3, y0 + 5, x1 + 3, y1 + 5), radius=r, fill=(15, 23, 42, 28))
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    fill_a = fill + (255,) if len(fill) == 3 else fill
    d.rounded_rectangle(xy, radius=r, fill=fill_a)


def arrow_h(draw, x0, y, x1, color=SLATE, w=4):
    if x1 < x0:
        x0, x1 = x1, x0
    draw.line((x0, y, x1 - 12, y), fill=color, width=w)
    draw.polygon([(x1, y), (x1 - 14, y - 8), (x1 - 14, y + 8)], fill=color)


def arrow_v(draw, x, y0, y1, color=SLATE, w=4):
    if y1 < y0:
        y0, y1 = y1, y0
    draw.line((x, y0, x, y1 - 12), fill=color, width=w)
    draw.polygon([(x, y1), (x - 8, y1 - 14), (x + 8, y1 - 14)], fill=color)


def center_text(draw, text, cx, cy, font, fill=NAVY):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), text, font=font, fill=fill)


def tile(img, x, y, w, h, icon, title, sub, border=CYAN, bg=SOFT_BLUE, icon_size=56):
    """아이콘·제목·부제 — 부제가 타일 바닥에 붙거나 잘리지 않게 배치."""
    soft_card(img, (x, y, x + w, y + h), r=16, fill=bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, outline=border, width=3)

    has_sub = bool(sub)
    title_f = fnt(16 if h < 140 else (18 if h < 160 else 20), True)
    sub_f = fnt(13 if h < 140 else (14 if h < 160 else 16))
    gap = 8 if h < 140 else (10 if h < 150 else (12 if h < 180 else 16))
    title_h = 20 if h < 140 else (22 if h < 150 else 24)
    sub_h = 16 if has_sub and h < 140 else (18 if has_sub and h < 150 else (20 if has_sub else 0))
    bottom_pad = 18 if h < 160 else 16
    top_pad = 8 if h < 140 else 10

    while True:
        stack = icon_size + gap + title_h + (gap + sub_h if has_sub else 0)
        if stack + top_pad + bottom_pad <= h or icon_size <= 28:
            break
        icon_size -= 2

    free = h - stack
    max_top = max(0, free - bottom_pad)
    ideal_top = free // 2
    top = y + max(min(top_pad, max_top), min(ideal_top, max_top))

    paste_icon(img, icon, x + w // 2, top + icon_size // 2, icon_size)
    ty = top + icon_size + gap + title_h // 2
    center_text(d, title, x + w // 2, ty, title_f, NAVY)
    if has_sub:
        center_text(d, sub, x + w // 2, ty + title_h // 2 + gap + sub_h // 2, sub_f, MUTED)


def save(img: Image.Image, name: str):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


def make_arch_v1():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    # top flow — mid-upper, not flush top
    tile(img, 60, 70, 160, 150, "users", "Users", "Browser", CYAN, SOFT_BLUE, 48)
    tile(img, 260, 70, 160, 150, "route53", "Route53", "DNS", PURPLE, SOFT_PURPLE, 48)
    tile(img, 460, 70, 160, 150, "waf", "WAF", "Web ACL", RED, SOFT_RED, 48)

    # VPC fills middle band tightly
    soft_card(img, (40, 250, 1560, 720), r=20, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 250, 1560, 720), radius=20, outline=CYAN, width=3)
    d.text((60, 265), "VPC  (ap-northeast-2)", font=fnt(20, True), fill=CYAN)

    # subnet boxes — shorter tiles, vertically centered (not stuck to top)
    soft_card(img, (60, 310, 420, 690), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 310, 420, 690), radius=14, outline=GREEN, width=3)
    d.text((80, 322), "Public Subnet", font=fnt(16, True), fill=GREEN)
    tile(img, 85, 430, 150, 230, "alb", "ALB", "HTTPS / ACM", GREEN, WHITE, 56)
    tile(img, 255, 430, 150, 230, "nat", "NAT", "Outbound", ORANGE, WHITE, 56)

    soft_card(img, (440, 310, 1040, 690), r=14, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((440, 310, 1040, 690), radius=14, outline=CYAN, width=3)
    d.text((460, 322), "Private App Subnet", font=fnt(16, True), fill=CYAN)
    tile(img, 465, 430, 170, 230, "asg", "ASG / EC2", "Nginx + Django", CYAN, WHITE, 56)
    tile(img, 655, 430, 160, 230, "elasticache", "Redis", "Cache / Session", RED, WHITE, 56)
    tile(img, 835, 430, 180, 230, "efs", "EFS", "Shared files", TEAL, WHITE, 56)

    soft_card(img, (1060, 310, 1330, 690), r=14, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1060, 310, 1330, 690), radius=14, outline=PURPLE, width=3)
    d.text((1080, 322), "Private DB", font=fnt(16, True), fill=PURPLE)
    tile(img, 1090, 430, 210, 230, "rds_maria", "RDS MariaDB", "Primary DB", PURPLE, WHITE, 64)

    tile(img, 1360, 370, 180, 145, "s3", "S3", "Static / Media", ORANGE, SOFT_ORANGE, 48)
    tile(img, 1360, 530, 180, 155, "secrets", "Secrets", "Manager", GREEN, SOFT_GREEN, 44)

    d = ImageDraw.Draw(img)
    arrow_h(d, 220, 145, 260, NAVY)
    arrow_h(d, 420, 145, 460, NAVY)
    arrow_v(d, 540, 220, 250, NAVY)
    arrow_h(d, 420, 545, 440, NAVY)
    arrow_h(d, 1040, 545, 1060, NAVY)

    soft_card(img, (40, 740, 1560, 870), r=14, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 740, 1560, 870), radius=14, outline=CYAN, width=3)
    d.text((60, 765), "흐름 요약", font=fnt(18, True), fill=CYAN)
    d.text(
        (60, 810),
        "Users → Route53 → WAF → ALB → EC2(ASG) → Redis / EFS / RDS   |   Media → S3",
        font=fnt(17),
        fill=NAVY,
    )
    save(img, "hybrid_01_arch_v1_vpc.png")


def make_arch_v2():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    # 요청 흐름: 외부 진입 뒤 EKS의 web/db/PVC로 이어지는 한 줄 구성
    soft_card(img, (750, 35, 1310, 265), r=18, fill=WHITE, shadow=False)
    d.rounded_rectangle((750, 35, 1310, 265), radius=18, outline=CYAN, width=3)
    d.text((770, 45), "EKS Cluster  (aniverse)", font=fnt(17, True), fill=CYAN)

    request_tiles = [
        (30, "users", "Users", "서비스 이용", CYAN, SOFT_BLUE),
        (215, "route53", "Route53", "DNS", PURPLE, SOFT_PURPLE),
        (400, "waf", "WAFv2", "Web ACL", RED, SOFT_RED),
        (585, "alb", "ALB", "Ingress", GREEN, SOFT_GREEN),
        (770, "django", "web Pod", "Django · Daphne", CYAN, SOFT_BLUE),
        (955, "rds_maria", "MariaDB", "StatefulSet", PURPLE, SOFT_PURPLE),
        (1140, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL),
    ]
    for x, icon, title, sub, border, fill in request_tiles:
        tile(img, x, 80, 150, 160, icon, title, sub, border, fill, 48)

    d = ImageDraw.Draw(img)
    for x0, x1 in [(180, 215), (365, 400), (550, 585), (735, 770), (920, 955), (1105, 1140)]:
        arrow_h(d, x0, 160, x1, NAVY)

    # GitOps: 웹훅 대신 Actions가 hard refresh와 sync를 직접 실행
    gitops_tiles = [
        (120, "githubactions", "GitHub Actions", "OIDC · build", CYAN, SOFT_BLUE),
        (370, "s3", "ECR", "sha-* image", ORANGE, SOFT_ORANGE),
        (620, "argo", "Argo CD", "hard refresh · sync", TEAL, SOFT_TEAL),
        (870, "servers", "EKS", "Synced · rollout", PURPLE, SOFT_PURPLE),
    ]
    for x, icon, title, sub, border, fill in gitops_tiles:
        tile(img, x, 365, 190, 210, icon, title, sub, border, fill, 62)

    d = ImageDraw.Draw(img)
    for x0, x1 in [(310, 370), (560, 620), (810, 870)]:
        arrow_h(d, x0, 470, x1, TEAL)

    # Argo CD 공식 문어 로고가 분명히 보이도록 별도 설명을 추가
    soft_card(img, (620, 590, 810, 640), r=10, fill=SOFT_TEAL, shadow=False)
    center_text(d, "별도 GitHub Webhook 없음", 715, 615, fnt(14, True), TEAL)

    # 운영 구성은 발표 화면에서 읽기 쉽도록 2×2 카드로 정리
    soft_card(img, (1125, 330, 1560, 675), r=18, fill=WHITE, shadow=False)
    d.rounded_rectangle((1125, 330, 1560, 675), radius=18, outline=ORANGE, width=3)
    d.text((1145, 345), "운영 서비스", font=fnt(18, True), fill=ORANGE)
    tile(img, 1145, 375, 185, 135, "elasticache", "Redis", "Channels", PURPLE, SOFT_PURPLE, 36)
    tile(img, 1350, 375, 185, 135, "secrets", "ESO", "Secrets Mgr", GREEN, SOFT_GREEN, 36)
    tile(img, 1145, 520, 185, 135, "s3", "S3", "media · backup", ORANGE, SOFT_ORANGE, 36)
    tile(img, 1350, 520, 185, 135, "grafana", "Observability", "Grafana · Tempo", RED, SOFT_RED, 36)

    soft_card(img, (40, 700, 1560, 870), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 700, 1560, 870), radius=14, outline=GREEN, width=3)
    d.text((60, 725), "흐름 요약", font=fnt(18, True), fill=GREEN)
    d.text(
        (60, 775),
        "요청: Users → Route53 → WAF → ALB → web Pod → MariaDB → PVC",
        font=fnt(16),
        fill=NAVY,
    )
    d.text(
        (60, 815),
        "배포: Actions → ECR → Argo CD → EKS   |   운영: Redis · ESO · S3 · Grafana/Loki/Tempo",
        font=fnt(16),
        fill=NAVY,
    )
    save(img, "hybrid_02_arch_v2_vpc.png")


def make_db_architecture():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    soft_card(img, (40, 40, 1560, 270), r=16, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 40, 1560, 270), radius=16, outline=CYAN, width=3)
    d.text((60, 52), "1) 서비스 중 — 글/데이터", font=fnt(20, True), fill=CYAN)
    tile(img, 70, 95, 160, 150, "users", "Users", "", CYAN, WHITE, 48)
    tile(img, 280, 95, 160, 150, "alb", "ALB", "", GREEN, WHITE, 48)
    tile(img, 490, 95, 200, 150, "django", "web Pod", "Django", CYAN, WHITE, 52)
    tile(img, 740, 95, 220, 150, "rds_maria", "MariaDB Pod", "StatefulSet", PURPLE, WHITE, 52)
    tile(img, 1010, 95, 200, 150, "efs", "EBS PVC", "영구 저장", TEAL, WHITE, 52)
    d = ImageDraw.Draw(img)
    for x0, x1 in [(230, 280), (440, 490), (690, 740), (960, 1010)]:
        arrow_h(d, x0, 170, x1, NAVY)
    d.text((1240, 160), "eks-stop → PVC 유지", font=fnt(17, True), fill=GREEN)

    soft_card(img, (40, 290, 780, 520), r=16, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 290, 780, 520), radius=16, outline=GREEN, width=3)
    d.text((60, 302), "2) destroy 후 시드 복구", font=fnt(20, True), fill=GREEN)
    tile(img, 70, 350, 180, 145, "github", "GitHub", "aniverse_backup.sql", NAVY, WHITE, 48)
    tile(img, 300, 350, 200, 145, "codedeploy", "restore Job", "curl + import", ORANGE, WHITE, 48)
    tile(img, 550, 350, 180, 145, "rds_maria", "MariaDB", "seed", PURPLE, WHITE, 48)
    d = ImageDraw.Draw(img)
    arrow_h(d, 250, 420, 300, NAVY)
    arrow_h(d, 500, 420, 550, NAVY)

    soft_card(img, (820, 290, 1560, 520), r=16, fill=SOFT_ORANGE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((820, 290, 1560, 520), radius=16, outline=ORANGE, width=3)
    d.text((840, 302), "3) 주기 백업 (CronJob)", font=fnt(20, True), fill=ORANGE)
    tile(img, 860, 350, 180, 145, "rds_maria", "MariaDB", "mysqldump", PURPLE, WHITE, 48)
    tile(img, 1100, 350, 180, 145, "cloudwatch", "CronJob", "schedule", TEAL, WHITE, 48)
    tile(img, 1340, 350, 180, 145, "s3", "S3", "db-backups/", ORANGE, WHITE, 48)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1040, 420, 1100, NAVY)
    arrow_h(d, 1280, 420, 1340, NAVY)

    soft_card(img, (40, 540, 1560, 700), r=16, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 540, 1560, 700), radius=16, outline=PURPLE, width=3)
    d.text((60, 555), "4) 사진/미디어 — DB가 아님", font=fnt(20, True), fill=PURPLE)
    tile(img, 70, 595, 220, 85, "django", "web Pod", "", CYAN, WHITE, 36)
    d.text((320, 625), "upload  →", font=fnt(18), fill=NAVY)
    tile(img, 450, 595, 240, 85, "s3", "S3 media/", "goods_images 등", ORANGE, WHITE, 36)
    d.text((740, 625), "destroy 시 S3도 삭제 → Sync media 로 재업로드", font=fnt(17), fill=RED)

    soft_card(img, (40, 720, 1560, 870), r=14, fill=SOFT_RED, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 720, 1560, 870), radius=14, outline=RED, width=3)
    d.text((60, 750), "주의", font=fnt(18, True), fill=RED)
    d.text(
        (60, 800),
        "eks-stop: PVC 유지  |  terraform destroy: PVC + S3 삭제  |  Git SQL 이후 새 글은 덤프 갱신 없으면 미복구",
        font=fnt(16),
        fill=NAVY,
    )
    save(img, "db_architecture_overview.png")
    save(img, "hybrid_06_data.png")


def make_roles():
    img = Image.new("RGBA", (W, H), BG + (255,))
    panels = [
        (
            50,
            ORANGE,
            SOFT_ORANGE,
            "DevOps / GitOps",
            "김현우",
            ["Actions · ECR", "Argo CD", "OIDC · 이관 복구"],
            "githubactions",
        ),
        (
            420,
            CYAN,
            SOFT_BLUE,
            "EKS · 네트워크 · 보안",
            "박서이",
            ["EKS · VPC", "Ingress · WAF · RBAC", "노드 · NAT"],
            "vpc",
        ),
        (
            790,
            TEAL,
            SOFT_TEAL,
            "컨테이너 · DB · 관측",
            "김윤주",
            ["Docker · Helm", "DB Pod · Backup", "Tempo · Alert"],
            "rds_maria",
        ),
        (
            1160,
            PURPLE,
            SOFT_PURPLE,
            "컴퓨트 · 트래픽",
            "강유민",
            ["노드 운영", "ALB 연동", "트래픽 경로"],
            "alb",
        ),
    ]
    for x, color, fill, title, who, lines, icon in panels:
        y0, y1 = 40, 860
        soft_card(img, (x, y0, x + 350, y1), r=22, fill=fill)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, y0, x + 350, y1), radius=22, outline=color, width=4)
        # 아이콘을 카드 상단에 크게 (첨부 이미지와 동일 배치)
        icon_size = 110
        icon_cy = y0 + 130
        paste_icon(img, icon, x + 175, icon_cy, icon_size)
        center_text(d, title, x + 175, icon_cy + 95, fnt(18, True), color)
        center_text(d, who, x + 175, icon_cy + 165, fnt(34, True), NAVY)
        for i, line in enumerate(lines):
            center_text(d, "· " + line, x + 175, icon_cy + 260 + i * 70, fnt(22), NAVY)
    save(img, "hybrid_00_roles.png")


def make_migration():
    img = Image.new("RGBA", (W, H), BG + (255,))
    stages = [
        (70, CYAN, SOFT_BLUE, "django", "1. Local", "Docker Compose", "이미지 · 앱 동작"),
        (560, TEAL, SOFT_TEAL, "servers", "2. Lab K8s", "Helm / Kustomize", "워커 노드 검증"),
        (1050, ORANGE, SOFT_ORANGE, "vpc", "3. EKS", "Helm + Argo CD", "실환경 GitOps"),
    ]
    for x, color, bg, icon, title, mid, sub in stages:
        y0, y1 = 80, 820
        soft_card(img, (x, y0, x + 440, y1), r=22, fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, y0, x + 440, y1), radius=22, outline=color, width=4)
        icon_size = 100
        block_h = 50 + icon_size + 90
        top = y1 - block_h - 100
        center_text(d, title, x + 220, top + 20, fnt(30, True), color)
        paste_icon(img, icon, x + 220, top + 70 + icon_size // 2, icon_size)
        center_text(d, mid, x + 220, top + 70 + icon_size + 45, fnt(22, True), NAVY)
        center_text(d, sub, x + 220, top + 70 + icon_size + 85, fnt(17), MUTED)
    d = ImageDraw.Draw(img)
    arrow_h(d, 510, 450, 560, NAVY, 5)
    arrow_h(d, 1000, 450, 1050, NAVY, 5)
    save(img, "hybrid_03_migration_path.png")


def make_workloads():
    img = Image.new("RGBA", (W, H), BG + (255,))
    soft_card(img, (50, 60, 1550, 840), r=22, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((50, 60, 1550, 840), radius=22, outline=CYAN, width=4)
    d.text((80, 85), "namespace: aniverse", font=fnt(22, True), fill=CYAN)
    # mid-height tiles so icon+text aren't lost in tall empty cards
    tile(img, 100, 220, 420, 480, "django", "aniverse-web", "Deployment · entrypoint migrate", CYAN, SOFT_BLUE, 96)
    tile(img, 580, 220, 420, 480, "rds_maria", "aniverse-db-0", "StatefulSet + PVC", PURPLE, SOFT_PURPLE, 96)
    tile(img, 1060, 220, 420, 480, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL, 88)
    d = ImageDraw.Draw(img)
    arrow_h(d, 520, 460, 580, NAVY, 5)
    arrow_h(d, 1000, 460, 1060, NAVY, 5)
    save(img, "hybrid_04_workloads.png")


def make_gitops():
    img = Image.new("RGBA", (W, H), BG + (255,))
    steps = [
        (50, "github", "Git push", "anime-project"),
        (340, "githubactions", "Actions", "build + OIDC"),
        (630, "s3", "ECR", "sha-* tag"),
        (920, "githubactions", "values bump", "image.tag"),
        (1210, "argo", "Argo sync", "EKS deploy"),
    ]
    for x, icon, title, sub in steps:
        tile(img, x, 160, 260, 420, icon, title, sub, CYAN, SOFT_BLUE, 72)
    d = ImageDraw.Draw(img)
    for x0 in (310, 600, 890, 1180):
        arrow_h(d, x0, 370, x0 + 30, NAVY, 5)
    soft_card(img, (50, 640, 1550, 840), r=16, fill=SOFT_TEAL, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 720), "OIDC로 AWS 인증 · [skip ci] 로 태그 bump 재빌드 루프 방지", font=fnt(22), fill=NAVY)
    save(img, "hybrid_05_gitops.png")


def make_observability():
    img = Image.new("RGBA", (W, H), BG + (255,))
    tile(img, 40, 180, 260, 400, "django", "EKS Pods", "web / db", CYAN, SOFT_BLUE, 64)
    tile(img, 350, 100, 260, 220, "cloudwatch", "Prometheus", "metrics", ORANGE, SOFT_ORANGE, 56)
    tile(img, 350, 360, 260, 220, "cloudwatch", "Loki + Alloy", "logs", TEAL, SOFT_TEAL, 56)
    tile(img, 660, 180, 280, 400, "grafana", "Grafana", "dashboards", GREEN, SOFT_GREEN, 72)
    tile(img, 990, 100, 260, 220, "tempo", "Tempo · OTel", "traces", PURPLE, SOFT_PURPLE, 56)
    tile(img, 990, 360, 260, 220, "alertmanager", "AlertManager", "Slack", RED, SOFT_RED, 56)
    soft_card(img, (1280, 180, 1560, 580), r=18, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1280, 180, 1560, 580), radius=18, outline=CYAN, width=3)
    center_text(d, "확인 결과", 1420, 280, fnt(26, True), CYAN)
    center_text(d, "메트릭·로그", 1420, 360, fnt(18), NAVY)
    center_text(d, "실제 trace 조회", 1420, 420, fnt(18), NAVY)
    center_text(d, "Slack 알림 수신", 1420, 480, fnt(18), NAVY)
    d = ImageDraw.Draw(img)
    arrow_h(d, 300, 320, 350, NAVY)
    arrow_h(d, 300, 520, 350, NAVY)
    arrow_h(d, 610, 320, 660, NAVY)
    arrow_h(d, 610, 520, 660, NAVY)
    arrow_h(d, 940, 210, 990, NAVY)
    arrow_h(d, 940, 470, 990, NAVY)
    save(img, "hybrid_07_observability.png")


def make_account():
    img = Image.new("RGBA", (W, H), BG + (255,))
    steps = [
        (40, RED, SOFT_RED, "firewall", "1. Access limited", "원인 미확정"),
        (350, ORANGE, SOFT_ORANGE, "ec2", "2. Start failed", "Actions / Console"),
        (660, RED, SOFT_RED, "iam", "3. Migration", "복구 일정 확보"),
        (970, TEAL, SOFT_TEAL, "iam", "4. New account", "8415…"),
        (1280, GREEN, SOFT_GREEN, "terraform", "5. Zero-Key", "OIDC / SSO"),
    ]
    for x, color, bg, icon, title, sub in steps:
        tile(img, x, 140, 280, 420, icon, title, sub, color, bg, 68)
    d = ImageDraw.Draw(img)
    for x0 in (320, 630, 940, 1250):
        arrow_h(d, x0, 350, x0 + 30, NAVY, 5)
    soft_card(img, (40, 620, 1560, 850), r=16, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.text(
        (70, 710),
        "확인: Actions·콘솔 start 실패   |   원인: 미확정   |   대응: 신계정 이관 + OIDC·SSO + ARN 전수 교체",
        font=fnt(18),
        fill=NAVY,
    )
    save(img, "hybrid_08_account.png")


def make_tech_stack_v2():
    """V2 기술 스택 한 장 — 카테고리 카드 + 아이콘 (가독성용)."""
    img = Image.new("RGBA", (W, H), BG + (255,))

    groups = [
        (
            40,
            40,
            "앱 · 런타임",
            CYAN,
            SOFT_BLUE,
            [("django", "Django"), ("servers", "Daphne"), ("servers", "Docker · Helm")],
        ),
        (
            545,
            40,
            "오케스트레이션",
            PURPLE,
            SOFT_PURPLE,
            [("servers", "EKS"), ("rds_maria", "MariaDB STS"), ("efs", "EBS PVC")],
        ),
        (
            1050,
            40,
            "스토리지",
            ORANGE,
            SOFT_ORANGE,
            [("s3", "S3 media"), ("s3", "S3 static"), ("s3", "S3 db-backups")],
        ),
        (
            40,
            470,
            "CI/CD · GitOps",
            TEAL,
            SOFT_TEAL,
            [
                ("githubactions", "Actions"),
                ("s3", "ECR"),
                ("argo", "Argo CD"),
            ],
        ),
        (
            545,
            470,
            "보안 · 인증 · IaC",
            GREEN,
            SOFT_GREEN,
            [("waf", "WAFv2"), ("iam", "OIDC · SSO"), ("terraform", "TF · IRSA · ESO")],
        ),
        (
            1050,
            470,
            "관측",
            RED,
            SOFT_RED,
            [
                ("grafana", "Prom · Grafana"),
                ("tempo", "Tempo · OTel"),
                ("alertmanager", "Alert · Slack"),
            ],
        ),
    ]
    for gx, gy, title, color, fill, items in groups:
        soft_card(img, (gx, gy, gx + 490, gy + 400), r=18, fill=fill, shadow=True)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((gx, gy, gx + 490, gy + 400), radius=18, outline=color, width=3)
        d.text((gx + 22, gy + 18), title, font=fnt(22, True), fill=color)
        for i, (icon, label) in enumerate(items):
            ix = gx + 28 + i * 155
            iy = gy + 70
            soft_card(img, (ix, iy, ix + 140, iy + 300), r=14, fill=WHITE, shadow=False)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((ix, iy, ix + 140, iy + 300), radius=14, outline=color, width=2)
            paste_icon(img, icon, ix + 70, iy + 100, 72)
            # 긴 라벨은 최대 3줄 (TF · IRSA · ESO 등)
            if " · " in label or "·" in label:
                parts = [p.strip() for p in label.replace(" · ", "\n").replace("·", "\n").split("\n") if p.strip()]
                if len(parts) == 1:
                    parts = label.split(" ", 1)
                parts = parts[:3]
                line_h = 24 if len(parts) >= 3 else 28
                y0 = iy + (188 if len(parts) >= 3 else 200)
                for j, part in enumerate(parts):
                    center_text(d, part, ix + 70, y0 + j * line_h, fnt(14 if len(parts) >= 3 else 15, True), NAVY)
            else:
                center_text(d, label, ix + 70, iy + 230, fnt(16, True), NAVY)

    save(img, "hybrid_09_tech_stack.png")


def make_data_flow_v2():
    """데이터 흐름 전용 장 — 서비스/시드/백업/미디어 (주의 칸 없음)."""
    img = Image.new("RGBA", (W, H), BG + (255,))

    # 1) service path — full width top
    soft_card(img, (40, 30, 1560, 290), r=16, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 30, 1560, 290), radius=16, outline=CYAN, width=3)
    d.text((60, 42), "1) 서비스 중 — 글 / 데이터", font=fnt(22, True), fill=CYAN)
    tile(img, 60, 95, 150, 170, "users", "Users", "", CYAN, WHITE, 48)
    tile(img, 250, 95, 150, 170, "waf", "WAFv2", "Web ACL", RED, WHITE, 48)
    tile(img, 440, 95, 150, 170, "alb", "ALB", "Ingress", GREEN, WHITE, 48)
    tile(img, 630, 95, 190, 170, "django", "web Pod", "Django", CYAN, WHITE, 52)
    tile(img, 860, 95, 210, 170, "rds_maria", "MariaDB Pod", "StatefulSet", PURPLE, WHITE, 52)
    tile(img, 1110, 95, 190, 170, "efs", "EBS PVC", "영구 저장", TEAL, WHITE, 52)
    d = ImageDraw.Draw(img)
    for x0, x1 in [(210, 250), (400, 440), (590, 630), (820, 860), (1070, 1110)]:
        arrow_h(d, x0, 180, x1, NAVY)
    d.text((1330, 145), "eks-stop", font=fnt(18, True), fill=GREEN)
    d.text((1330, 175), "→ PVC 유지", font=fnt(18, True), fill=GREEN)

    # 2) seed  ·  3) backup — mid row
    soft_card(img, (40, 320, 780, 590), r=16, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 320, 780, 590), radius=16, outline=GREEN, width=3)
    d.text((60, 335), "2) destroy 후 시드 복구", font=fnt(22, True), fill=GREEN)
    tile(img, 70, 385, 185, 175, "github", "GitHub", "backup.sql", NAVY, WHITE, 56)
    tile(img, 300, 385, 205, 175, "codedeploy", "restore Job", "curl + import", ORANGE, WHITE, 56)
    tile(img, 550, 385, 185, 175, "rds_maria", "MariaDB", "seed", PURPLE, WHITE, 56)
    d = ImageDraw.Draw(img)
    arrow_h(d, 255, 470, 300, NAVY)
    arrow_h(d, 505, 470, 550, NAVY)

    soft_card(img, (820, 320, 1560, 590), r=16, fill=SOFT_ORANGE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((820, 320, 1560, 590), radius=16, outline=ORANGE, width=3)
    d.text((840, 335), "3) 주기 백업 (CronJob)", font=fnt(22, True), fill=ORANGE)
    tile(img, 860, 385, 185, 175, "rds_maria", "MariaDB", "mariadb-dump", PURPLE, WHITE, 56)
    tile(img, 1090, 385, 185, 175, "cloudwatch", "CronJob", "schedule", TEAL, WHITE, 56)
    tile(img, 1320, 385, 195, 175, "s3", "S3", "db-backups/", ORANGE, WHITE, 56)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1045, 470, 1090, NAVY)
    arrow_h(d, 1275, 470, 1320, NAVY)

    # 4) media — bottom full width
    soft_card(img, (40, 620, 1560, 870), r=16, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 620, 1560, 870), radius=16, outline=PURPLE, width=3)
    d.text((60, 638), "4) 사진 / 미디어 — DB가 아님", font=fnt(22, True), fill=PURPLE)
    tile(img, 70, 690, 260, 145, "django", "web Pod", "upload", CYAN, WHITE, 52)
    d.text((370, 750), "→", font=fnt(28, True), fill=NAVY)
    tile(img, 420, 690, 300, 145, "s3", "S3 media/", "goods_images 등", ORANGE, WHITE, 52)
    d.text(
        (760, 745),
        "destroy 시 S3도 삭제 → Sync media 로 재업로드",
        font=fnt(20),
        fill=RED,
    )
    save(img, "hybrid_10_data_flow.png")


def main():
    make_roles()
    make_arch_v1()
    make_arch_v2()
    make_db_architecture()
    make_migration()
    make_workloads()
    make_gitops()
    make_observability()
    make_account()
    make_tech_stack_v2()
    make_data_flow_v2()
    print("All hybrid diagrams written to", OUT)


if __name__ == "__main__":
    main()
