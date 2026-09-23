#!/usr/bin/env python3
"""하이브리드 PPT용 구성도 — AWS 아이콘 + 시스템 한글 폰트 (깨짐 없음).

출력: images/hybrid/hybrid_*.png
스타일: 강사용 instructor 다이어그램과 동일 (카드·아이콘·화살표).
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
    if not path.exists():
        # fallback blank
        img = Image.new("RGBA", (size, size), (200, 200, 200, 255))
        return img
    img = Image.open(path).convert("RGBA")
    return img.resize((size, size), Image.Resampling.LANCZOS)


def paste_icon(base: Image.Image, name: str, cx: int, cy: int, size: int = 64):
    icon = load_icon(name, size)
    x = int(cx - size / 2)
    y = int(cy - size / 2)
    base.alpha_composite(icon, (x, y))


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


def arrow_h(draw, x0, y, x1, color=SLATE, w=3):
    if x1 < x0:
        x0, x1 = x1, x0
    draw.line((x0, y, x1 - 10, y), fill=color, width=w)
    draw.polygon([(x1, y), (x1 - 12, y - 7), (x1 - 12, y + 7)], fill=color)


def arrow_v(draw, x, y0, y1, color=SLATE, w=3):
    if y1 < y0:
        y0, y1 = y1, y0
    draw.line((x, y0, x, y1 - 10), fill=color, width=w)
    draw.polygon([(x, y1), (x - 7, y1 - 12), (x + 7, y1 - 12)], fill=color)


def center_text(draw, text, cx, cy, font, fill=NAVY):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2), text, font=font, fill=fill)


def title_block(d, title, sub):
    d.text((48, 24), title, font=fnt(32, True), fill=NAVY)
    d.text((48, 68), sub, font=fnt(16), fill=SLATE)


def tile(img, x, y, w, h, icon, title, sub, border=BLUE, bg=SOFT_BLUE, icon_size=48):
    soft_card(img, (x, y, x + w, y + h), r=14, fill=bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, outline=border, width=2)
    paste_icon(img, icon, x + w // 2, y + 36, icon_size)
    center_text(d, title, x + w // 2, y + h - 48, fnt(16, True), NAVY)
    if sub:
        center_text(d, sub, x + w // 2, y + h - 24, fnt(12), MUTED)


def save(img: Image.Image, name: str):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


# ---------------------------------------------------------------------------
# Architecture v1 — VPC style (one page)
# ---------------------------------------------------------------------------
def make_arch_v1():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Architecture v1", "User → ALB → ASG/EC2 → RDS · EFS · S3")

    # users
    tile(img, 40, 140, 140, 160, "users", "Users", "Browser", BLUE, SOFT_BLUE)
    tile(img, 210, 140, 140, 160, "route53", "Route53", "DNS", PURPLE, SOFT_PURPLE)
    tile(img, 380, 140, 140, 160, "waf", "WAF", "Web ACL", RED, SOFT_RED)

    # VPC box
    soft_card(img, (40, 340, 1560, 720), r=20, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 340, 1560, 720), radius=20, outline=BLUE, width=3)
    d.text((60, 355), "VPC  (ap-northeast-2)", font=fnt(18, True), fill=BLUE)

    # public
    soft_card(img, (60, 400, 420, 690), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 400, 420, 690), radius=14, outline=GREEN, width=2)
    d.text((80, 415), "Public Subnet", font=fnt(15, True), fill=GREEN)
    tile(img, 90, 460, 140, 180, "alb", "ALB", "HTTPS / ACM", GREEN, WHITE, 44)
    tile(img, 250, 460, 140, 180, "nat", "NAT", "Outbound", ORANGE, WHITE, 44)

    # app
    soft_card(img, (450, 400, 1050, 690), r=14, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((450, 400, 1050, 690), radius=14, outline=BLUE, width=2)
    d.text((470, 415), "Private App Subnet", font=fnt(15, True), fill=BLUE)
    tile(img, 480, 460, 160, 180, "asg", "ASG / EC2", "Nginx + Django", BLUE, WHITE, 44)
    tile(img, 670, 460, 150, 180, "elasticache", "Redis", "Cache / Session", RED, WHITE, 44)
    tile(img, 850, 460, 160, 180, "efs", "EFS", "Shared files", TEAL, WHITE, 44)

    # db
    soft_card(img, (1080, 400, 1340, 690), r=14, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1080, 400, 1340, 690), radius=14, outline=PURPLE, width=2)
    d.text((1100, 415), "Private DB", font=fnt(15, True), fill=PURPLE)
    tile(img, 1110, 460, 200, 180, "rds_maria", "RDS MariaDB", "Primary DB", PURPLE, WHITE, 52)

    # external
    tile(img, 1380, 420, 160, 150, "s3", "S3", "Static / Media", ORANGE, SOFT_ORANGE, 44)
    tile(img, 1380, 590, 160, 120, "secrets", "Secrets", "Manager", GREEN, SOFT_GREEN, 40)

    d = ImageDraw.Draw(img)
    arrow_h(d, 180, 220, 210, NAVY, 3)
    arrow_h(d, 350, 220, 380, NAVY, 3)
    arrow_v(d, 450, 300, 400, NAVY, 3)
    arrow_h(d, 420, 550, 450, NAVY, 3)
    arrow_h(d, 1050, 550, 1080, NAVY, 3)

    # footer
    soft_card(img, (40, 760, 1560, 870), r=12, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 760, 1560, 870), radius=12, outline=BLUE, width=2)
    d.text((60, 780), "흐름 요약", font=fnt(16, True), fill=BLUE)
    d.text(
        (60, 820),
        "Users → Route53 → WAF → ALB → EC2(ASG) → Redis / EFS / RDS   |   Media → S3",
        font=fnt(15),
        fill=NAVY,
    )
    save(img, "hybrid_01_arch_v1_vpc.png")


# ---------------------------------------------------------------------------
# Architecture v2 — EKS
# ---------------------------------------------------------------------------
def make_arch_v2():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Architecture v2 — EKS", "ALB Ingress → EKS Pods · DB StatefulSet · Argo GitOps · S3")

    tile(img, 40, 120, 130, 140, "users", "Users", "", BLUE, SOFT_BLUE, 40)
    tile(img, 190, 120, 130, 140, "route53", "Route53", "ACM", PURPLE, SOFT_PURPLE, 40)
    tile(img, 340, 120, 130, 140, "alb", "ALB", "Ingress", GREEN, SOFT_GREEN, 40)

    # EKS box
    soft_card(img, (40, 300, 1100, 700), r=18, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 300, 1100, 700), radius=18, outline=BLUE, width=3)
    d.text((60, 315), "EKS Cluster  (aniverse)", font=fnt(18, True), fill=BLUE)

    tile(img, 70, 370, 220, 200, "django", "web Pod", "Django + Nginx", BLUE, SOFT_BLUE, 52)
    tile(img, 330, 370, 220, 200, "rds_maria", "db Pod", "MariaDB StatefulSet", PURPLE, SOFT_PURPLE, 52)
    tile(img, 590, 370, 220, 200, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL, 48)
    tile(img, 850, 370, 220, 200, "cloudwatch", "Observability", "Prom / Grafana / Loki", ORANGE, SOFT_ORANGE, 48)

    soft_card(img, (70, 600, 1070, 680), r=10, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 625), "web ↔ db (SQL)   |   db → PVC   |   photos → S3 (not in DB)", font=fnt(15), fill=NAVY)

    # right side gitops + s3
    tile(img, 1160, 120, 180, 150, "githubactions", "Actions", "OIDC build", BLUE, SOFT_BLUE, 44)
    tile(img, 1380, 120, 180, 150, "s3", "ECR", "sha-* image", ORANGE, SOFT_ORANGE, 44)
    # reuse s3 icon for ecr - no ecr icon; use terraform or servers
    tile(img, 1160, 300, 400, 160, "terraform", "Argo CD", "GitOps sync", TEAL, SOFT_TEAL, 48)
    tile(img, 1160, 490, 190, 160, "s3", "S3 media", "images", ORANGE, SOFT_ORANGE, 44)
    tile(img, 1370, 490, 190, 160, "s3", "S3 backup", "db-backups/", GREEN, SOFT_GREEN, 44)

    d = ImageDraw.Draw(img)
    arrow_h(d, 170, 190, 190, NAVY, 3)
    arrow_h(d, 320, 190, 340, NAVY, 3)
    arrow_v(d, 405, 260, 300, NAVY, 3)
    arrow_h(d, 290, 470, 330, NAVY, 3)
    arrow_h(d, 550, 470, 590, NAVY, 3)
    arrow_v(d, 1250, 270, 300, NAVY, 3)

    soft_card(img, (40, 740, 1560, 870), r=12, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 740, 1560, 870), radius=12, outline=GREEN, width=2)
    d.text((60, 765), "흐름 요약", font=fnt(16, True), fill=GREEN)
    d.text(
        (60, 810),
        "Users → ALB → web Pod → MariaDB → PVC   |   Actions → ECR → Argo → EKS   |   Media/Backup → S3",
        font=fnt(15),
        fill=NAVY,
    )
    save(img, "hybrid_02_arch_v2_vpc.png")


# ---------------------------------------------------------------------------
# DB architecture (dedicated)
# ---------------------------------------------------------------------------
def make_db_architecture():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Aniverse DB Architecture", "글=PVC · 시드=Git SQL · 백업=S3 · 사진=S3 media")

    # path 1 live
    soft_card(img, (40, 110, 1560, 320), r=16, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 110, 1560, 320), radius=16, outline=BLUE, width=2)
    d.text((60, 125), "1) 서비스 중 — 글/데이터", font=fnt(18, True), fill=BLUE)
    tile(img, 70, 165, 160, 130, "users", "Users", "", BLUE, WHITE, 40)
    tile(img, 280, 165, 160, 130, "alb", "ALB", "", GREEN, WHITE, 40)
    tile(img, 490, 165, 200, 130, "django", "web Pod", "Django", BLUE, WHITE, 44)
    tile(img, 740, 165, 220, 130, "rds_maria", "MariaDB Pod", "StatefulSet", PURPLE, WHITE, 44)
    tile(img, 1010, 165, 200, 130, "efs", "EBS PVC", "영구 저장", TEAL, WHITE, 44)
    d = ImageDraw.Draw(img)
    for x0, x1 in [(230, 280), (440, 490), (690, 740), (960, 1010)]:
        arrow_h(d, x0, 230, x1, NAVY, 3)
    d.text((1240, 220), "eks-stop → PVC 유지", font=fnt(14, True), fill=GREEN)

    # path 2 restore
    soft_card(img, (40, 350, 780, 560), r=16, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 350, 780, 560), radius=16, outline=GREEN, width=2)
    d.text((60, 365), "2) destroy 후 시드 복구", font=fnt(18, True), fill=GREEN)
    tile(img, 70, 410, 180, 120, "github", "GitHub", "aniverse_backup.sql", NAVY, WHITE, 40)
    tile(img, 300, 410, 200, 120, "codedeploy", "restore Job", "curl + import", ORANGE, WHITE, 40)
    tile(img, 550, 410, 180, 120, "rds_maria", "MariaDB", "seed", PURPLE, WHITE, 40)
    d = ImageDraw.Draw(img)
    arrow_h(d, 250, 470, 300, NAVY, 3)
    arrow_h(d, 500, 470, 550, NAVY, 3)

    # path 3 backup
    soft_card(img, (820, 350, 1560, 560), r=16, fill=SOFT_ORANGE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((820, 350, 1560, 560), radius=16, outline=ORANGE, width=2)
    d.text((840, 365), "3) 주기 백업 (CronJob)", font=fnt(18, True), fill=ORANGE)
    tile(img, 860, 410, 180, 120, "rds_maria", "MariaDB", "mysqldump", PURPLE, WHITE, 40)
    tile(img, 1100, 410, 180, 120, "cloudwatch", "CronJob", "schedule", TEAL, WHITE, 40)
    tile(img, 1340, 410, 180, 120, "s3", "S3", "db-backups/", ORANGE, WHITE, 40)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1040, 470, 1100, NAVY, 3)
    arrow_h(d, 1280, 470, 1340, NAVY, 3)

    # path 4 media
    soft_card(img, (40, 590, 1560, 720), r=16, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 590, 1560, 720), radius=16, outline=PURPLE, width=2)
    d.text((60, 605), "4) 사진/미디어 — DB가 아님", font=fnt(18, True), fill=PURPLE)
    tile(img, 70, 640, 200, 60, "django", "web Pod", "", BLUE, WHITE, 28)
    # smaller tiles - use text
    d.text((320, 655), "upload  →", font=fnt(16), fill=NAVY)
    tile(img, 430, 640, 220, 60, "s3", "S3 media/", "goods_images 등", ORANGE, WHITE, 28)
    d.text((700, 655), "destroy 시 S3도 삭제 → Sync media 로 재업로드", font=fnt(15), fill=RED)

    soft_card(img, (40, 750, 1560, 870), r=12, fill=SOFT_RED, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 750, 1560, 870), radius=12, outline=RED, width=2)
    d.text((60, 775), "주의", font=fnt(16, True), fill=RED)
    d.text(
        (60, 815),
        "eks-stop: PVC 유지  |  terraform destroy: PVC + S3 삭제  |  Git SQL 이후 새 글은 덤프 갱신 없으면 미복구",
        font=fnt(15),
        fill=NAVY,
    )
    save(img, "db_architecture_overview.png")
    save(img, "hybrid_06_data.png")  # data slide uses same story


# ---------------------------------------------------------------------------
# Other slides
# ---------------------------------------------------------------------------
def make_roles():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Team Roles", "역할 분담")
    panels = [
        (60, BLUE, SOFT_BLUE, "Network / Compute", "서이 등", ["EKS · VPC", "Ingress / ALB", "노드 · NAT"], "vpc"),
        (420, TEAL, SOFT_TEAL, "Container / DB / Observability", "윤주", ["Docker · Helm", "DB Pod · Backup", "Prom / Grafana / Loki"], "rds_maria"),
        (780, ORANGE, SOFT_ORANGE, "DevOps / GitOps", "현우", ["Actions · ECR", "Argo CD", "OIDC · 이관 복구"], "githubactions"),
        (1140, PURPLE, SOFT_PURPLE, "App / Product", "팀", ["Aniverse 서비스", "장터 · 창작", "커뮤니티"], "django"),
    ]
    for x, color, bg, title, who, lines, icon in panels:
        soft_card(img, (x, 140, x + 340, 780), r=18, fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 140, x + 340, 780), radius=18, outline=color, width=3)
        paste_icon(img, icon, x + 170, 230, 64)
        center_text(d, title, x + 170, 320, fnt(17, True), color)
        center_text(d, who, x + 170, 360, fnt(20, True), NAVY)
        for i, line in enumerate(lines):
            center_text(d, "· " + line, x + 170, 440 + i * 50, fnt(16), NAVY)
    save(img, "hybrid_00_roles.png")


def make_migration():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Lab → EKS Migration Path", "로컬 검증 후 랩, 그다음 EKS")
    stages = [
        (80, BLUE, SOFT_BLUE, "django", "1. Local", "Docker Compose", "이미지 · 앱 동작"),
        (560, TEAL, SOFT_TEAL, "servers", "2. Lab K8s", "Helm / Kustomize", "워커 노드 검증"),
        (1040, ORANGE, SOFT_ORANGE, "vpc", "3. EKS", "Helm + Argo CD", "실환경 GitOps"),
    ]
    for x, color, bg, icon, title, mid, sub in stages:
        soft_card(img, (x, 200, x + 420, 620), r=20, fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 200, x + 420, 620), radius=20, outline=color, width=3)
        center_text(d, title, x + 210, 260, fnt(26, True), color)
        paste_icon(img, icon, x + 210, 380, 80)
        center_text(d, mid, x + 210, 500, fnt(20, True), NAVY)
        center_text(d, sub, x + 210, 550, fnt(15), MUTED)
    d = ImageDraw.Draw(img)
    arrow_h(d, 500, 410, 560, NAVY, 4)
    arrow_h(d, 980, 410, 1040, NAVY, 4)
    save(img, "hybrid_03_migration_path.png")


def make_workloads():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "App & DB Workloads", "EKS namespace aniverse — web 1/1 · db 1/1")
    soft_card(img, (80, 160, 1520, 720), r=20, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80, 160, 1520, 720), radius=20, outline=BLUE, width=3)
    d.text((110, 190), "namespace: aniverse", font=fnt(18, True), fill=BLUE)
    tile(img, 150, 280, 400, 320, "django", "aniverse-web", "Deployment · entrypoint migrate", BLUE, SOFT_BLUE, 72)
    tile(img, 650, 280, 400, 320, "rds_maria", "aniverse-db-0", "StatefulSet + PVC", PURPLE, SOFT_PURPLE, 72)
    tile(img, 1100, 280, 340, 320, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL, 64)
    d = ImageDraw.Draw(img)
    arrow_h(d, 550, 440, 650, NAVY, 4)
    arrow_h(d, 1050, 440, 1100, NAVY, 4)
    save(img, "hybrid_04_workloads.png")


def make_gitops():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Actions → ECR → Argo", "GitOps 배포 파이프라인")
    steps = [
        (60, "github", "Git push", "anime-project"),
        (340, "githubactions", "Actions", "build + OIDC"),
        (620, "s3", "ECR", "sha-* tag"),
        (900, "terraform", "values bump", "image.tag"),
        (1180, "vpc", "Argo sync", "EKS deploy"),
    ]
    for x, icon, title, sub in steps:
        tile(img, x, 280, 240, 280, icon, title, sub, BLUE, SOFT_BLUE, 56)
    d = ImageDraw.Draw(img)
    for x0 in (300, 580, 860, 1140):
        arrow_h(d, x0, 420, x0 + 40, NAVY, 4)
    soft_card(img, (60, 650, 1540, 820), r=12, fill=SOFT_TEAL, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 700), "OIDC로 AWS 인증 · [skip ci] 로 태그 bump 재빌드 루프 방지", font=fnt(18), fill=NAVY)
    save(img, "hybrid_05_gitops.png")


def make_observability():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Observability", "Metrics · Logs · (Next) Alerts / Tracing")
    tile(img, 80, 200, 280, 280, "django", "EKS Pods", "web / db", BLUE, SOFT_BLUE, 56)
    tile(img, 450, 160, 280, 200, "cloudwatch", "Prometheus", "metrics", ORANGE, SOFT_ORANGE, 52)
    tile(img, 450, 400, 280, 200, "cloudwatch", "Loki + Alloy", "logs", TEAL, SOFT_TEAL, 52)
    tile(img, 820, 250, 320, 280, "cloudwatch", "Grafana", "dashboards", GREEN, SOFT_GREEN, 64)
    soft_card(img, (1220, 200, 1540, 560), r=16, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1220, 200, 1540, 560), radius=16, outline=PURPLE, width=2)
    center_text(d, "Next", 1380, 280, fnt(22, True), PURPLE)
    center_text(d, "AlertManager", 1380, 360, fnt(16), NAVY)
    center_text(d, "Tempo + OTel", 1380, 420, fnt(16), NAVY)
    d = ImageDraw.Draw(img)
    arrow_h(d, 360, 340, 450, NAVY, 3)
    arrow_h(d, 360, 500, 450, NAVY, 3)
    arrow_h(d, 730, 340, 820, NAVY, 3)
    arrow_h(d, 730, 500, 820, NAVY, 3)
    save(img, "hybrid_07_observability.png")


def make_account():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    title_block(d, "Account Block → Migration", "키 유출 → Block → 신계정 이관")
    steps = [
        (60, RED, SOFT_RED, "secrets", "1. Key leak", ".env Access Key"),
        (360, ORANGE, SOFT_ORANGE, "ec2", "2. Abuse", "RunInstances"),
        (660, RED, SOFT_RED, "firewall", "3. Blocked", "StartInstances"),
        (960, TEAL, SOFT_TEAL, "iam", "4. New account", "8415…"),
        (1260, GREEN, SOFT_GREEN, "terraform", "5. Checklist", "ECR ACM OIDC"),
    ]
    for x, color, bg, icon, title, sub in steps:
        tile(img, x, 280, 260, 280, icon, title, sub, color, bg, 52)
    d = ImageDraw.Draw(img)
    for x0 in (320, 620, 920, 1220):
        arrow_h(d, x0, 420, x0 + 40, NAVY, 4)
    soft_card(img, (60, 640, 1540, 820), r=12, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 700), "표면: start 실패   |   근본: 장기 키 유출   |   이관 후 ARN 전수 교체 (ECR / ACM / OIDC / Secret)", font=fnt(16), fill=NAVY)
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
