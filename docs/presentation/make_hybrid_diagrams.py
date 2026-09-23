#!/usr/bin/env python3
"""하이브리드 PPT용 구성도 — AWS 아이콘 + 시스템 한글 폰트 (가시성 우선).

출력: images/hybrid/hybrid_*.png
PPT 헤더가 제목을 담당하므로 이미지 안 타이틀은 최소화하고 글씨·타일을 키움.
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

W, H = 1700, 780
BG = (248, 250, 252)
NAVY = (10, 17, 40)
SLATE = (71, 85, 105)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
CYAN = (0, 174, 239)
BLUE = (0, 174, 239)  # match template cyan
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


def caption(d, text):
    """PPT 헤더가 제목을 담당 — 이미지 안 캡션은 넣지 않음."""
    return


def tile(img, x, y, w, h, icon, title, sub, border=CYAN, bg=SOFT_BLUE, icon_size=56):
    soft_card(img, (x, y, x + w, y + h), r=16, fill=bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, outline=border, width=3)
    paste_icon(img, icon, x + w // 2, y + 44, icon_size)
    center_text(d, title, x + w // 2, y + h - 52, fnt(20, True), NAVY)
    if sub:
        center_text(d, sub, x + w // 2, y + h - 24, fnt(15), MUTED)


def normalize(name: str):
    """Export flat 1800x700 so PPT can pin images to the lower half."""
    path = OUT / name
    im = Image.open(path).convert("RGB")
    tw, th = 1800, 700
    scale = min(tw / im.width, th / im.height) * 0.88
    nw, nh = int(im.width * scale), int(im.height * scale)
    im2 = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), BG)
    canvas.paste(im2, ((tw - nw) // 2, th - nh))
    canvas.save(path, "PNG", optimize=True)


def save(img: Image.Image, name: str):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    normalize(name)
    print("Wrote", path)


def make_arch_v1():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "User → ALB → ASG/EC2 → RDS · EFS · S3")

    tile(img, 40, 40, 150, 170, "users", "Users", "Browser", CYAN, SOFT_BLUE, 52)
    tile(img, 220, 40, 150, 170, "route53", "Route53", "DNS", PURPLE, SOFT_PURPLE, 52)
    tile(img, 400, 40, 150, 170, "waf", "WAF", "Web ACL", RED, SOFT_RED, 52)

    soft_card(img, (40, 250, 1560, 700), r=20, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 250, 1560, 700), radius=20, outline=CYAN, width=3)
    d.text((60, 268), "VPC  (ap-northeast-2)", font=fnt(22, True), fill=CYAN)

    soft_card(img, (60, 320, 430, 670), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 320, 430, 670), radius=14, outline=GREEN, width=3)
    d.text((80, 335), "Public Subnet", font=fnt(18, True), fill=GREEN)
    tile(img, 90, 380, 150, 250, "alb", "ALB", "HTTPS / ACM", GREEN, WHITE, 52)
    tile(img, 260, 380, 150, 250, "nat", "NAT", "Outbound", ORANGE, WHITE, 52)

    soft_card(img, (450, 320, 1050, 670), r=14, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((450, 320, 1050, 670), radius=14, outline=CYAN, width=3)
    d.text((470, 335), "Private App Subnet", font=fnt(18, True), fill=CYAN)
    tile(img, 480, 380, 170, 250, "asg", "ASG / EC2", "Nginx + Django", CYAN, WHITE, 52)
    tile(img, 675, 380, 160, 250, "elasticache", "Redis", "Cache / Session", RED, WHITE, 52)
    tile(img, 855, 380, 170, 250, "efs", "EFS", "Shared files", TEAL, WHITE, 52)

    soft_card(img, (1070, 320, 1340, 670), r=14, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1070, 320, 1340, 670), radius=14, outline=PURPLE, width=3)
    d.text((1090, 335), "Private DB", font=fnt(18, True), fill=PURPLE)
    tile(img, 1100, 380, 210, 250, "rds_maria", "RDS MariaDB", "Primary DB", PURPLE, WHITE, 60)

    tile(img, 1370, 340, 170, 160, "s3", "S3", "Static / Media", ORANGE, SOFT_ORANGE, 52)
    tile(img, 1370, 520, 170, 140, "secrets", "Secrets", "Manager", GREEN, SOFT_GREEN, 44)

    d = ImageDraw.Draw(img)
    arrow_h(d, 190, 125, 220, NAVY)
    arrow_h(d, 370, 125, 400, NAVY)
    arrow_v(d, 475, 210, 250, NAVY)
    arrow_h(d, 430, 505, 450, NAVY)
    arrow_h(d, 1050, 505, 1070, NAVY)

    soft_card(img, (40, 730, 1560, 870), r=14, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 730, 1560, 870), radius=14, outline=CYAN, width=3)
    d.text((60, 755), "흐름 요약", font=fnt(20, True), fill=CYAN)
    d.text(
        (60, 805),
        "Users → Route53 → WAF → ALB → EC2(ASG) → Redis / EFS / RDS   |   Media → S3",
        font=fnt(18),
        fill=NAVY,
    )
    save(img, "hybrid_01_arch_v1_vpc.png")


def make_arch_v2():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "ALB Ingress → EKS Pods · DB StatefulSet · Argo GitOps · S3")

    tile(img, 40, 60, 140, 160, "users", "Users", "", CYAN, SOFT_BLUE, 48)
    tile(img, 210, 60, 140, 160, "route53", "Route53", "ACM", PURPLE, SOFT_PURPLE, 48)
    tile(img, 380, 60, 140, 160, "alb", "ALB", "Ingress", GREEN, SOFT_GREEN, 48)

    soft_card(img, (40, 260, 1100, 680), r=18, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 260, 1100, 680), radius=18, outline=CYAN, width=3)
    d.text((60, 280), "EKS Cluster  (aniverse)", font=fnt(22, True), fill=CYAN)

    tile(img, 70, 340, 230, 220, "django", "web Pod", "Django + Nginx", CYAN, SOFT_BLUE, 60)
    tile(img, 340, 340, 230, 220, "rds_maria", "db Pod", "MariaDB StatefulSet", PURPLE, SOFT_PURPLE, 60)
    tile(img, 610, 340, 220, 220, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL, 56)
    tile(img, 860, 340, 210, 220, "cloudwatch", "Observability", "Prom / Grafana / Loki", ORANGE, SOFT_ORANGE, 52)

    soft_card(img, (70, 590, 1070, 655), r=12, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 610), "web ↔ db (SQL)   |   db → PVC   |   photos → S3 (not in DB)", font=fnt(18), fill=NAVY)

    tile(img, 1160, 60, 190, 160, "githubactions", "Actions", "OIDC build", CYAN, SOFT_BLUE, 52)
    tile(img, 1380, 60, 180, 160, "s3", "ECR", "sha-* image", ORANGE, SOFT_ORANGE, 52)
    tile(img, 1160, 260, 400, 180, "terraform", "Argo CD", "GitOps sync", TEAL, SOFT_TEAL, 56)
    tile(img, 1160, 470, 190, 180, "s3", "S3 media", "images", ORANGE, SOFT_ORANGE, 52)
    tile(img, 1370, 470, 190, 180, "s3", "S3 backup", "db-backups/", GREEN, SOFT_GREEN, 52)

    d = ImageDraw.Draw(img)
    arrow_h(d, 180, 140, 210, NAVY)
    arrow_h(d, 350, 140, 380, NAVY)
    arrow_v(d, 450, 220, 260, NAVY)
    arrow_h(d, 300, 450, 340, NAVY)
    arrow_h(d, 570, 450, 610, NAVY)
    arrow_v(d, 1255, 220, 260, NAVY)

    soft_card(img, (40, 720, 1560, 870), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 720, 1560, 870), radius=14, outline=GREEN, width=3)
    d.text((60, 750), "흐름 요약", font=fnt(20, True), fill=GREEN)
    d.text(
        (60, 805),
        "Users → ALB → web Pod → MariaDB → PVC   |   Actions → ECR → Argo → EKS   |   Media/Backup → S3",
        font=fnt(17),
        fill=NAVY,
    )
    save(img, "hybrid_02_arch_v2_vpc.png")


def make_db_architecture():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "글=PVC · 시드=Git SQL · 백업=S3 · 사진=S3 media")

    soft_card(img, (40, 60, 1560, 280), r=16, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 60, 1560, 280), radius=16, outline=CYAN, width=3)
    d.text((60, 75), "1) 서비스 중 — 글/데이터", font=fnt(22, True), fill=CYAN)
    tile(img, 70, 115, 160, 140, "users", "Users", "", CYAN, WHITE, 48)
    tile(img, 280, 115, 160, 140, "alb", "ALB", "", GREEN, WHITE, 48)
    tile(img, 490, 115, 200, 140, "django", "web Pod", "Django", CYAN, WHITE, 52)
    tile(img, 740, 115, 220, 140, "rds_maria", "MariaDB Pod", "StatefulSet", PURPLE, WHITE, 52)
    tile(img, 1010, 115, 200, 140, "efs", "EBS PVC", "영구 저장", TEAL, WHITE, 52)
    d = ImageDraw.Draw(img)
    for x0, x1 in [(230, 280), (440, 490), (690, 740), (960, 1010)]:
        arrow_h(d, x0, 185, x1, NAVY)
    d.text((1240, 175), "eks-stop → PVC 유지", font=fnt(18, True), fill=GREEN)

    soft_card(img, (40, 305, 780, 520), r=16, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 305, 780, 520), radius=16, outline=GREEN, width=3)
    d.text((60, 320), "2) destroy 후 시드 복구", font=fnt(22, True), fill=GREEN)
    tile(img, 70, 365, 180, 130, "github", "GitHub", "aniverse_backup.sql", NAVY, WHITE, 48)
    tile(img, 300, 365, 200, 130, "codedeploy", "restore Job", "curl + import", ORANGE, WHITE, 48)
    tile(img, 550, 365, 180, 130, "rds_maria", "MariaDB", "seed", PURPLE, WHITE, 48)
    d = ImageDraw.Draw(img)
    arrow_h(d, 250, 430, 300, NAVY)
    arrow_h(d, 500, 430, 550, NAVY)

    soft_card(img, (820, 305, 1560, 520), r=16, fill=SOFT_ORANGE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((820, 305, 1560, 520), radius=16, outline=ORANGE, width=3)
    d.text((840, 320), "3) 주기 백업 (CronJob)", font=fnt(22, True), fill=ORANGE)
    tile(img, 860, 365, 180, 130, "rds_maria", "MariaDB", "mysqldump", PURPLE, WHITE, 48)
    tile(img, 1100, 365, 180, 130, "cloudwatch", "CronJob", "schedule", TEAL, WHITE, 48)
    tile(img, 1340, 365, 180, 130, "s3", "S3", "db-backups/", ORANGE, WHITE, 48)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1040, 430, 1100, NAVY)
    arrow_h(d, 1280, 430, 1340, NAVY)

    soft_card(img, (40, 545, 1560, 690), r=16, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 545, 1560, 690), radius=16, outline=PURPLE, width=3)
    d.text((60, 560), "4) 사진/미디어 — DB가 아님", font=fnt(22, True), fill=PURPLE)
    tile(img, 70, 600, 220, 70, "django", "web Pod", "", CYAN, WHITE, 36)
    d.text((320, 620), "upload  →", font=fnt(20), fill=NAVY)
    tile(img, 450, 600, 240, 70, "s3", "S3 media/", "goods_images 등", ORANGE, WHITE, 36)
    d.text((740, 620), "destroy 시 S3도 삭제 → Sync media 로 재업로드", font=fnt(18), fill=RED)

    soft_card(img, (40, 715, 1560, 870), r=14, fill=SOFT_RED, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 715, 1560, 870), radius=14, outline=RED, width=3)
    d.text((60, 745), "주의", font=fnt(20, True), fill=RED)
    d.text(
        (60, 800),
        "eks-stop: PVC 유지  |  terraform destroy: PVC + S3 삭제  |  Git SQL 이후 새 글은 덤프 갱신 없으면 미복구",
        font=fnt(17),
        fill=NAVY,
    )
    save(img, "db_architecture_overview.png")
    save(img, "hybrid_06_data.png")


def make_roles():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "역할 분담")
    panels = [
        (50, CYAN, SOFT_BLUE, "Network / Compute", "서이 등", ["EKS · VPC", "Ingress / ALB", "노드 · NAT"], "vpc"),
        (420, TEAL, SOFT_TEAL, "Container / DB / Observability", "윤주", ["Docker · Helm", "DB Pod · Backup", "Prom / Grafana / Loki"], "rds_maria"),
        (790, ORANGE, SOFT_ORANGE, "DevOps / GitOps", "현우", ["Actions · ECR", "Argo CD", "OIDC · 이관 복구"], "githubactions"),
        (1160, PURPLE, SOFT_PURPLE, "App / Product", "팀", ["Aniverse 서비스", "장터 · 창작", "커뮤니티"], "django"),
    ]
    for x, color, bg, title, who, lines, icon in panels:
        soft_card(img, (x, 40, x + 350, 860), r=20, fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 40, x + 350, 860), radius=20, outline=color, width=4)
        paste_icon(img, icon, x + 175, 180, 88)
        center_text(d, title, x + 175, 310, fnt(20, True), color)
        center_text(d, who, x + 175, 400, fnt(32, True), NAVY)
        for i, line in enumerate(lines):
            center_text(d, "· " + line, x + 175, 530 + i * 75, fnt(24), NAVY)
    save(img, "hybrid_00_roles.png")


def make_migration():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "로컬 검증 후 랩, 그다음 EKS")
    stages = [
        (70, CYAN, SOFT_BLUE, "django", "1. Local", "Docker Compose", "이미지 · 앱 동작"),
        (560, TEAL, SOFT_TEAL, "servers", "2. Lab K8s", "Helm / Kustomize", "워커 노드 검증"),
        (1050, ORANGE, SOFT_ORANGE, "vpc", "3. EKS", "Helm + Argo CD", "실환경 GitOps"),
    ]
    for x, color, bg, icon, title, mid, sub in stages:
        soft_card(img, (x, 120, x + 440, 760), r=22, fill=bg)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 120, x + 440, 760), radius=22, outline=color, width=4)
        center_text(d, title, x + 220, 200, fnt(32, True), color)
        paste_icon(img, icon, x + 220, 380, 96)
        center_text(d, mid, x + 220, 540, fnt(24, True), NAVY)
        center_text(d, sub, x + 220, 610, fnt(18), MUTED)
    d = ImageDraw.Draw(img)
    arrow_h(d, 510, 440, 560, NAVY, 5)
    arrow_h(d, 1000, 440, 1050, NAVY, 5)
    save(img, "hybrid_03_migration_path.png")


def make_workloads():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "EKS namespace aniverse — web 1/1 · db 1/1")
    soft_card(img, (60, 80, 1540, 820), r=22, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 80, 1540, 820), radius=22, outline=CYAN, width=4)
    d.text((90, 110), "namespace: aniverse", font=fnt(24, True), fill=CYAN)
    tile(img, 120, 220, 420, 480, "django", "aniverse-web", "Deployment · entrypoint migrate", CYAN, SOFT_BLUE, 88)
    tile(img, 610, 220, 420, 480, "rds_maria", "aniverse-db-0", "StatefulSet + PVC", PURPLE, SOFT_PURPLE, 88)
    tile(img, 1100, 220, 360, 480, "efs", "EBS PVC", "영구 볼륨", TEAL, SOFT_TEAL, 80)
    d = ImageDraw.Draw(img)
    arrow_h(d, 540, 460, 610, NAVY, 5)
    arrow_h(d, 1030, 460, 1100, NAVY, 5)
    save(img, "hybrid_04_workloads.png")


def make_gitops():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "GitOps 배포 파이프라인")
    steps = [
        (50, "github", "Git push", "anime-project"),
        (340, "githubactions", "Actions", "build + OIDC"),
        (630, "s3", "ECR", "sha-* tag"),
        (920, "terraform", "values bump", "image.tag"),
        (1210, "vpc", "Argo sync", "EKS deploy"),
    ]
    for x, icon, title, sub in steps:
        tile(img, x, 180, 260, 360, icon, title, sub, CYAN, SOFT_BLUE, 68)
    d = ImageDraw.Draw(img)
    for x0 in (310, 600, 890, 1180):
        arrow_h(d, x0, 360, x0 + 30, NAVY, 5)
    soft_card(img, (50, 620, 1550, 820), r=16, fill=SOFT_TEAL, shadow=False)
    d = ImageDraw.Draw(img)
    d.text((90, 700), "OIDC로 AWS 인증 · [skip ci] 로 태그 bump 재빌드 루프 방지", font=fnt(22), fill=NAVY)
    save(img, "hybrid_05_gitops.png")


def make_observability():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "Metrics · Logs · (Next) Alerts / Tracing")
    tile(img, 60, 140, 300, 360, "django", "EKS Pods", "web / db", CYAN, SOFT_BLUE, 72)
    tile(img, 430, 100, 300, 240, "cloudwatch", "Prometheus", "metrics", ORANGE, SOFT_ORANGE, 64)
    tile(img, 430, 380, 300, 240, "cloudwatch", "Loki + Alloy", "logs", TEAL, SOFT_TEAL, 64)
    tile(img, 800, 180, 340, 360, "cloudwatch", "Grafana", "dashboards", GREEN, SOFT_GREEN, 80)
    soft_card(img, (1200, 140, 1540, 620), r=18, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1200, 140, 1540, 620), radius=18, outline=PURPLE, width=3)
    center_text(d, "Next", 1370, 250, fnt(28, True), PURPLE)
    center_text(d, "AlertManager", 1370, 360, fnt(20), NAVY)
    center_text(d, "Tempo + OTel", 1370, 440, fnt(20), NAVY)
    d = ImageDraw.Draw(img)
    arrow_h(d, 360, 320, 430, NAVY)
    arrow_h(d, 360, 500, 430, NAVY)
    arrow_h(d, 730, 320, 800, NAVY)
    arrow_h(d, 730, 500, 800, NAVY)
    save(img, "hybrid_07_observability.png")


def make_account():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    caption(d, "키 유출 → Block → 신계정 이관")
    steps = [
        (40, RED, SOFT_RED, "secrets", "1. Key leak", ".env Access Key"),
        (350, ORANGE, SOFT_ORANGE, "ec2", "2. Abuse", "RunInstances"),
        (660, RED, SOFT_RED, "firewall", "3. Blocked", "StartInstances"),
        (970, TEAL, SOFT_TEAL, "iam", "4. New account", "8415…"),
        (1280, GREEN, SOFT_GREEN, "terraform", "5. Checklist", "ECR ACM OIDC"),
    ]
    for x, color, bg, icon, title, sub in steps:
        tile(img, x, 160, 280, 360, icon, title, sub, color, bg, 64)
    d = ImageDraw.Draw(img)
    for x0 in (320, 630, 940, 1250):
        arrow_h(d, x0, 340, x0 + 30, NAVY, 5)
    soft_card(img, (40, 600, 1560, 840), r=16, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.text(
        (70, 690),
        "표면: start 실패   |   근본: 장기 키 유출   |   이관 후 ARN 전수 교체 (ECR / ACM / OIDC / Secret)",
        font=fnt(20),
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
