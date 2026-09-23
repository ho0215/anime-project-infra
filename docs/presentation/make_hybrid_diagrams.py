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
    """아이콘·제목·부제 — 타일 세로 중앙(약간 아래) 배치."""
    soft_card(img, (x, y, x + w, y + h), r=16, fill=bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, outline=border, width=3)

    has_sub = bool(sub)
    title_f = fnt(18 if h < 160 else 20, True)
    sub_f = fnt(14 if h < 160 else 16)
    gap = 12 if h < 180 else 16
    title_h = 24
    sub_h = 20 if has_sub else 0
    stack = icon_size + gap + title_h + (gap + sub_h if has_sub else 0)
    # slightly below geometric center so icons don't sit too high
    top = y + max(14, int((h - stack) * 0.48))

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

    tile(img, 1360, 380, 180, 140, "s3", "S3", "Static / Media", ORANGE, SOFT_ORANGE, 48)
    tile(img, 1360, 540, 180, 130, "secrets", "Secrets", "Manager", GREEN, SOFT_GREEN, 48)

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

    tile(img, 50, 60, 150, 150, "users", "Users", "", CYAN, SOFT_BLUE, 48)
    tile(img, 230, 60, 150, 150, "route53", "Route53", "ACM", PURPLE, SOFT_PURPLE, 48)
    tile(img, 410, 60, 150, 150, "alb", "ALB", "Ingress", GREEN, SOFT_GREEN, 48)

    soft_card(img, (40, 240, 1100, 700), r=18, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 240, 1100, 700), radius=18, outline=CYAN, width=3)
    d.text((60, 255), "EKS Cluster  (aniverse)", font=fnt(20, True), fill=CYAN)

    tile(img, 70, 310, 230, 280, "django", "web Pod", "Django + Nginx", CYAN, SOFT_BLUE, 64)
    tile(img, 330, 310, 230, 280, "rds_maria", "db Pod", "MariaDB StatefulSet", PURPLE, SOFT_PURPLE, 64)
    tile(img, 590, 310, 220, 280, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL, 60)
    tile(img, 840, 310, 220, 280, "cloudwatch", "Observability", "Prom / Grafana / Loki", ORANGE, SOFT_ORANGE, 56)

    soft_card(img, (70, 620, 1070, 675), r=12, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 635), "web ↔ db (SQL)   |   db → PVC   |   photos → S3 (not in DB)", font=fnt(16), fill=NAVY)

    tile(img, 1150, 60, 200, 150, "githubactions", "Actions", "OIDC build", CYAN, SOFT_BLUE, 52)
    tile(img, 1380, 60, 180, 150, "s3", "ECR", "sha-* image", ORANGE, SOFT_ORANGE, 52)
    tile(img, 1150, 250, 410, 180, "terraform", "Argo CD", "GitOps sync", TEAL, SOFT_TEAL, 56)
    tile(img, 1150, 460, 195, 200, "s3", "S3 media", "images", ORANGE, SOFT_ORANGE, 52)
    tile(img, 1365, 460, 195, 200, "s3", "S3 backup", "db-backups/", GREEN, SOFT_GREEN, 52)

    d = ImageDraw.Draw(img)
    arrow_h(d, 200, 135, 230, NAVY)
    arrow_h(d, 380, 135, 410, NAVY)
    arrow_v(d, 485, 210, 240, NAVY)
    arrow_h(d, 300, 450, 330, NAVY)
    arrow_h(d, 560, 450, 590, NAVY)
    arrow_v(d, 1250, 210, 250, NAVY)

    soft_card(img, (40, 730, 1560, 870), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 730, 1560, 870), radius=14, outline=GREEN, width=3)
    d.text((60, 755), "흐름 요약", font=fnt(18, True), fill=GREEN)
    d.text(
        (60, 805),
        "Users → ALB → web Pod → MariaDB → PVC   |   Actions → ECR → Argo → EKS   |   Media/Backup → S3",
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
        (50, CYAN, SOFT_BLUE, "Network / Compute", "서이 등", ["EKS · VPC", "Ingress / ALB", "노드 · NAT"], "vpc"),
        (420, TEAL, SOFT_TEAL, "Container / DB / Observability", "윤주", ["Docker · Helm", "DB Pod · Backup", "Prom / Grafana / Loki"], "rds_maria"),
        (790, ORANGE, SOFT_ORANGE, "DevOps / GitOps", "현우", ["Actions · ECR", "Argo CD", "OIDC · 이관 복구"], "githubactions"),
        (1160, PURPLE, SOFT_PURPLE, "App / Product", "팀", ["Aniverse 서비스", "장터 · 창작", "커뮤니티"], "django"),
    ]
    for x, color, bg, title, who, lines, icon in panels:
        y0, y1 = 60, 840
        soft_card(img, (x, y0, x + 350, y1), r=20, fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, y0, x + 350, y1), radius=20, outline=color, width=4)
        icon_size = 88
        block_h = icon_size + 55 + 45 + 55 + 3 * 78
        # lower half of panel
        top = y0 + int((y1 - y0 - block_h) * 0.72)
        paste_icon(img, icon, x + 175, top + icon_size // 2, icon_size)
        center_text(d, title, x + 175, top + icon_size + 42, fnt(19, True), color)
        center_text(d, who, x + 175, top + icon_size + 100, fnt(32, True), NAVY)
        for i, line in enumerate(lines):
            center_text(d, "· " + line, x + 175, top + icon_size + 185 + i * 78, fnt(24), NAVY)
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
        (920, "terraform", "values bump", "image.tag"),
        (1210, "vpc", "Argo sync", "EKS deploy"),
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
    tile(img, 60, 160, 300, 420, "django", "EKS Pods", "web / db", CYAN, SOFT_BLUE, 72)
    tile(img, 430, 120, 300, 240, "cloudwatch", "Prometheus", "metrics", ORANGE, SOFT_ORANGE, 64)
    tile(img, 430, 400, 300, 240, "cloudwatch", "Loki + Alloy", "logs", TEAL, SOFT_TEAL, 64)
    tile(img, 800, 180, 340, 400, "cloudwatch", "Grafana", "dashboards", GREEN, SOFT_GREEN, 80)
    soft_card(img, (1200, 160, 1540, 620), r=18, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1200, 160, 1540, 620), radius=18, outline=PURPLE, width=3)
    # center Next block
    center_text(d, "Next", 1370, 300, fnt(28, True), PURPLE)
    center_text(d, "AlertManager", 1370, 400, fnt(20), NAVY)
    center_text(d, "Tempo + OTel", 1370, 470, fnt(20), NAVY)
    d = ImageDraw.Draw(img)
    arrow_h(d, 360, 320, 430, NAVY)
    arrow_h(d, 360, 520, 430, NAVY)
    arrow_h(d, 730, 320, 800, NAVY)
    arrow_h(d, 730, 520, 800, NAVY)
    save(img, "hybrid_07_observability.png")


def make_account():
    img = Image.new("RGBA", (W, H), BG + (255,))
    steps = [
        (40, RED, SOFT_RED, "secrets", "1. Key leak", ".env Access Key"),
        (350, ORANGE, SOFT_ORANGE, "ec2", "2. Abuse", "RunInstances"),
        (660, RED, SOFT_RED, "firewall", "3. Blocked", "StartInstances"),
        (970, TEAL, SOFT_TEAL, "iam", "4. New account", "8415…"),
        (1280, GREEN, SOFT_GREEN, "terraform", "5. Checklist", "ECR ACM OIDC"),
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
        "표면: start 실패   |   근본: 장기 키 유출   |   이관 후 ARN 전수 교체 (ECR / ACM / OIDC / Secret)",
        font=fnt(18),
        fill=NAVY,
    )
    save(img, "hybrid_08_account.png")


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
    print("All hybrid diagrams written to", OUT)


if __name__ == "__main__":
    main()
