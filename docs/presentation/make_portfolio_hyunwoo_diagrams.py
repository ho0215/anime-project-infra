#!/usr/bin/env python3
"""김현우(DevOps/GitOps) 포트폴리오용 구성도 PNG.

출력: images/portfolio_hyunwoo/*.png
기존 hybrid 스타일(아이콘 타일)을 재사용한다.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent
ICON = BASE / "images" / "icons"
OUT = BASE / "images" / "portfolio_hyunwoo"
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
    soft_card(img, (x, y, x + w, y + h), r=16, fill=bg)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, outline=border, width=3)

    has_sub = bool(sub)
    title_f = fnt(17 if h < 160 else 20, True)
    sub_f = fnt(13 if h < 160 else 15)
    gap = 10 if h < 180 else 14
    title_h = 22
    sub_h = 18 if has_sub else 0
    stack = icon_size + gap + title_h + (gap + sub_h if has_sub else 0)
    top = y + max(12, int((h - stack) * 0.45))

    paste_icon(img, icon, x + w // 2, top + icon_size // 2, icon_size)
    ty = top + icon_size + gap + title_h // 2
    center_text(d, title, x + w // 2, ty, title_f, NAVY)
    if has_sub:
        center_text(d, sub, x + w // 2, ty + title_h // 2 + gap + sub_h // 2, sub_f, MUTED)


def title_bar(img, text, sub=""):
    d = ImageDraw.Draw(img)
    d.text((48, 28), text, font=fnt(30, True), fill=NAVY)
    if sub:
        d.text((48, 70), sub, font=fnt(18), fill=MUTED)


def footer(img, text):
    soft_card(img, (40, 780, 1560, 870), r=14, fill=SOFT_BLUE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 780, 1560, 870), radius=14, outline=CYAN, width=3)
    d.text((60, 812), text, font=fnt(18), fill=NAVY)


def save(img: Image.Image, name: str):
    path = OUT / name
    img.convert("RGB").save(path, "PNG", optimize=True)
    print("Wrote", path)


def make_01_deploy_overview():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "1. 배포·운영 아키텍처 개요", "담당: CI/CD · GitOps · IaC 연동 (V1 → V2)")

    soft_card(img, (40, 110, 780, 740), r=18, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 110, 780, 740), radius=18, outline=ORANGE, width=3)
    d.text((60, 130), "V1 · EC2 / CodeDeploy", font=fnt(22, True), fill=ORANGE)
    flow = [
        (70, 200, "github", "GitHub", "push"),
        (220, 200, "githubactions", "Actions", "CI"),
        (370, 200, "codedeploy", "CodeDeploy", "zip deploy"),
        (520, 200, "asg", "ASG/EC2", "Nginx+Django"),
    ]
    for x, y, ic, t, s in flow:
        tile(img, x, y, 130, 200, ic, t, s, ORANGE, SOFT_ORANGE, 48)
    d = ImageDraw.Draw(img)
    for x in (200, 350, 500):
        arrow_h(d, x, 300, x + 20, ORANGE)
    d.text((70, 440), "인프라: Terraform apply", font=fnt(16, True), fill=SLATE)
    tile(img, 70, 480, 160, 180, "terraform", "Terraform", "IaC", TEAL, SOFT_TEAL, 48)
    tile(img, 260, 480, 160, 180, "alb", "ALB", "target", CYAN, SOFT_BLUE, 48)
    tile(img, 450, 480, 160, 180, "ssm", "SSM", "ops access", GREEN, SOFT_GREEN, 48)

    soft_card(img, (820, 110, 1560, 740), r=18, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((820, 110, 1560, 740), radius=18, outline=CYAN, width=3)
    d.text((840, 130), "V2 · EKS / GitOps", font=fnt(22, True), fill=CYAN)
    flow2 = [
        (850, 200, "github", "GitHub", "push"),
        (1000, 200, "githubactions", "Actions", "OIDC build"),
        (1150, 200, "s3", "ECR", "sha-* image"),
        (1300, 200, "servers", "Argo CD", "sync"),
    ]
    for x, y, ic, t, s in flow2:
        tile(img, x, y, 130, 200, ic, t, s, CYAN, SOFT_BLUE, 48)
    d = ImageDraw.Draw(img)
    for x in (980, 1130, 1280):
        arrow_h(d, x, 300, x + 20, CYAN)
    d.text((850, 440), "런타임: EKS Pod · Git = source of truth", font=fnt(16, True), fill=SLATE)
    tile(img, 850, 480, 160, 180, "servers", "EKS", "web/db Pod", PURPLE, SOFT_PURPLE, 48)
    tile(img, 1040, 480, 160, 180, "iam", "OIDC/IRSA", "Zero-Key", GREEN, SOFT_GREEN, 48)
    tile(img, 1230, 480, 160, 180, "terraform", "Terraform", "cluster IaC", TEAL, SOFT_TEAL, 48)

    save(img, "01_deploy_overview_v1v2.png")


def make_02_ssm_keyless():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "2. SSM 키리스 접속 · VPC Endpoint", "SSH/22 의존 축소 · NAT 장애와 관리 접속 분리")

    soft_card(img, (40, 120, 1560, 720), r=20, fill=WHITE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 120, 1560, 720), radius=20, outline=CYAN, width=3)
    d.text((60, 140), "VPC · Private App Subnet", font=fnt(20, True), fill=CYAN)

    tile(img, 80, 220, 200, 220, "iam", "IAM Role", "ssm permissions", GREEN, SOFT_GREEN, 56)
    tile(img, 340, 220, 220, 220, "ec2", "EC2 (Private)", "no SSH key", CYAN, SOFT_BLUE, 56)
    tile(img, 620, 220, 240, 220, "ssm", "Session Manager", "keyless shell", TEAL, SOFT_TEAL, 56)
    tile(img, 920, 200, 200, 140, "vpc", "Interface EP", "ssm", PURPLE, SOFT_PURPLE, 48)
    tile(img, 1140, 200, 200, 140, "vpc", "Interface EP", "ssmmessages", PURPLE, SOFT_PURPLE, 48)
    tile(img, 1360, 200, 160, 140, "vpc", "Interface EP", "ec2messages", PURPLE, SOFT_PURPLE, 48)

    d = ImageDraw.Draw(img)
    arrow_h(d, 280, 330, 340, NAVY)
    arrow_h(d, 560, 330, 620, NAVY)
    arrow_h(d, 860, 330, 920, NAVY)

    soft_card(img, (80, 480, 700, 680), r=14, fill=SOFT_RED, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80, 480, 700, 680), radius=14, outline=RED, width=3)
    d.text((100, 500), "Before (위험)", font=fnt(18, True), fill=RED)
    d.text((100, 545), "· SSH 키 파일 관리 / 유출 위험", font=fnt(17), fill=NAVY)
    d.text((100, 585), "· SG 22번 포트 개방 → 공격면 확대", font=fnt(17), fill=NAVY)
    d.text((100, 625), "· SSM이 NAT만 쓰면 NAT 장애 시 접속 불가", font=fnt(17), fill=NAVY)

    soft_card(img, (740, 480, 1480, 680), r=14, fill=SOFT_GREEN, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((740, 480, 1480, 680), radius=14, outline=GREEN, width=3)
    d.text((760, 500), "After (설계)", font=fnt(18, True), fill=GREEN)
    d.text((760, 545), "· IAM + Session Manager 키리스 접속", font=fnt(17), fill=NAVY)
    d.text((760, 585), "· Endpoint로 관리 트래픽을 VPC 내부 HTTPS", font=fnt(17), fill=NAVY)
    d.text((760, 625), "· Bastion SSH는 비상 옵션으로만 최소화", font=fnt(17), fill=NAVY)

    footer(img, "운영 편의와 보안(노출면 축소)을 함께 맞춘 관리 접속 경로")
    save(img, "02_ssm_keyless_endpoint.png")


def make_03_codedeploy_boot():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "3. CodeDeploy 기동 순서 재설계", "표면: HEALTH_CONSTRAINTS / ApplicationStop → 원인: Agent 미설치")

    # bad order
    soft_card(img, (40, 120, 1560, 400), r=16, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 120, 1560, 400), radius=16, outline=RED, width=3)
    d.text((60, 140), "문제 순서 (Before)", font=fnt(20, True), fill=RED)
    steps_bad = [
        (80, 200, "alb", "ALB health", "OK 먼저"),
        (300, 200, "nginx", "Nginx", "user_data"),
        (520, 200, "secrets", "Secrets", "user_data"),
        (740, 200, "efs", "EFS", "user_data"),
        (960, 200, "codedeploy", "Agent", "너무 늦음"),
        (1180, 200, "codedeploy", "Deploy", "실패"),
    ]
    for x, y, ic, t, s in steps_bad:
        tile(img, x, y, 180, 160, ic, t, s, RED, SOFT_RED, 44)
    d = ImageDraw.Draw(img)
    for x in (260, 480, 700, 920, 1140):
        arrow_h(d, x, 280, x + 40, RED)

    soft_card(img, (40, 430, 1560, 740), r=16, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 430, 1560, 740), radius=16, outline=GREEN, width=3)
    d.text((60, 450), "수정 순서 (After)", font=fnt(20, True), fill=GREEN)
    steps_ok = [
        (80, 510, "codedeploy", "Agent 먼저", "user_data 최우선"),
        (300, 510, "nginx", "Nginx", "이후 설정"),
        (520, 510, "secrets", "Secrets", "이후 설정"),
        (740, 510, "efs", "EFS", "이후 설정"),
        (960, 510, "ssm", "SSM 설치", "기존 인스턴스"),
        (1180, 510, "asg", "Refresh", "LT 동기화"),
    ]
    for x, y, ic, t, s in steps_ok:
        tile(img, x, y, 180, 180, ic, t, s, GREEN, SOFT_GREEN, 44)
    d = ImageDraw.Draw(img)
    for x in (260, 480, 700, 920, 1140):
        arrow_h(d, x, 600, x + 40, GREEN)

    footer(img, "ALB healthy ≠ 배포 준비 완료 · Agent·LT·Instance Refresh까지 맞춰 재발 방지")
    save(img, "03_codedeploy_boot_order.png")


def make_04_gitops():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "4. GitOps 파이프라인", "Actions → ECR → Git values → Argo CD → EKS")

    nodes = [
        (60, 200, "github", "Git push", "anime-project"),
        (330, 200, "githubactions", "Actions", "build + OIDC"),
        (600, 200, "s3", "ECR", "sha-* tag"),
        (870, 200, "terraform", "values bump", "image.tag"),
        (1140, 200, "servers", "Argo sync", "EKS deploy"),
        (1380, 200, "django", "web Pod", "running"),
    ]
    for x, y, ic, t, s in nodes:
        tile(img, x, y, 200, 260, ic, t, s, CYAN, SOFT_BLUE, 56)
    d = ImageDraw.Draw(img)
    for x in (260, 530, 800, 1070, 1340):
        arrow_h(d, x, 330, x + 70, NAVY)

    soft_card(img, (60, 520, 1540, 740), r=14, fill=SOFT_PURPLE, shadow=False)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 520, 1540, 740), radius=14, outline=PURPLE, width=3)
    d.text((90, 550), "운영 포인트", font=fnt(20, True), fill=PURPLE)
    d.text((90, 600), "· Git이 source of truth — 클러스터 상태는 Argo Sync로 맞춘다", font=fnt(18), fill=NAVY)
    d.text((90, 645), "· OIDC로 AWS 인증 · values bump에 [skip ci]로 재빌드 루프 방지", font=fnt(18), fill=NAVY)
    d.text((90, 690), "· OutOfSync/Missing ≠ 즉시 장애 — sync-wave·적용 방식까지 확인", font=fnt(18), fill=NAVY)

    footer(img, "담당: GitOps 구성 · 이미지 태그 갱신 · Argo 동기화 운영")
    save(img, "04_gitops_pipeline.png")


def make_05_oidc():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "5. Zero-Key 인증 (OIDC · IRSA)", "장기 액세스 키 없이 CI·워크로드 권한 부여")

    soft_card(img, (40, 130, 760, 700), r=18, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 130, 760, 700), radius=18, outline=GREEN, width=3)
    d.text((60, 155), "CI 경로", font=fnt(22, True), fill=GREEN)
    tile(img, 100, 220, 200, 200, "githubactions", "Actions", "workflow", CYAN, SOFT_BLUE, 56)
    tile(img, 400, 220, 200, 200, "iam", "IAM Role", "OIDC trust", GREEN, SOFT_GREEN, 56)
    tile(img, 100, 460, 200, 180, "terraform", "Terraform", "plan/apply", TEAL, SOFT_TEAL, 52)
    tile(img, 400, 460, 200, 180, "s3", "ECR push", "short-lived", ORANGE, SOFT_ORANGE, 52)
    d = ImageDraw.Draw(img)
    arrow_h(d, 300, 320, 400, NAVY)
    arrow_v(d, 500, 420, 460, NAVY)
    arrow_v(d, 200, 420, 460, NAVY)

    soft_card(img, (840, 130, 1560, 700), r=18, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((840, 130, 1560, 700), radius=18, outline=PURPLE, width=3)
    d.text((860, 155), "워크로드 경로", font=fnt(22, True), fill=PURPLE)
    tile(img, 920, 220, 200, 200, "django", "web Pod", "IRSA", CYAN, SOFT_BLUE, 56)
    tile(img, 1220, 220, 200, 200, "iam", "IRSA Role", "S3 etc.", PURPLE, SOFT_PURPLE, 56)
    tile(img, 1070, 460, 220, 180, "s3", "S3 media", "Get/Put", ORANGE, SOFT_ORANGE, 52)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1120, 320, 1220, NAVY)
    arrow_v(d, 1320, 420, 500, NAVY)
    arrow_h(d, 1180, 550, 1290, NAVY)

    footer(img, "사람·CI·Pod 모두 장기 키를 두지 않고, 필요한 순간에만 권한을 받도록 설계")
    save(img, "05_oidc_zerokey.png")


def make_06_restore_sync():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "6. 복구·미디어 Sync 경로", "SQL 복구 ≠ 미디어 복구 · Actions 초록 ≠ 복구 완료")

    soft_card(img, (40, 120, 760, 620), r=16, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 120, 760, 620), radius=16, outline=GREEN, width=3)
    d.text((60, 145), "DB 시드 복구", font=fnt(22, True), fill=GREEN)
    tile(img, 80, 210, 180, 180, "github", "Git SQL", "seed dump", CYAN, SOFT_BLUE, 52)
    tile(img, 310, 210, 180, 180, "servers", "restore Job", "curl + import", TEAL, SOFT_TEAL, 52)
    tile(img, 540, 210, 180, 180, "rds_maria", "MariaDB", "seed rows", PURPLE, SOFT_PURPLE, 52)
    d = ImageDraw.Draw(img)
    arrow_h(d, 260, 300, 310, NAVY)
    arrow_h(d, 490, 300, 540, NAVY)
    d.text((80, 430), "검증", font=fnt(18, True), fill=SLATE)
    d.text((80, 475), "· 테이블 수만 보면 Skip될 수 있음", font=fnt(17), fill=NAVY)
    d.text((80, 520), "· 시드 행 ≥ 1 일 때만 복구 성공으로 판정", font=fnt(17), fill=NAVY)
    d.text((80, 565), "· 목록 화면까지 확인", font=fnt(17), fill=NAVY)

    soft_card(img, (840, 120, 1560, 620), r=16, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((840, 120, 1560, 620), radius=16, outline=ORANGE, width=3)
    d.text((860, 145), "미디어 Sync (별도)", font=fnt(22, True), fill=ORANGE)
    tile(img, 880, 210, 180, 180, "django", "local media/", "repo assets", CYAN, SOFT_BLUE, 52)
    tile(img, 1110, 210, 180, 180, "githubactions", "Sync job", "s3 sync", TEAL, SOFT_TEAL, 52)
    tile(img, 1340, 210, 180, 180, "s3", "S3 media", "images", ORANGE, SOFT_ORANGE, 52)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1060, 300, 1110, NAVY)
    arrow_h(d, 1290, 300, 1340, NAVY)
    d.text((880, 430), "검증", font=fnt(18, True), fill=SLATE)
    d.text((880, 475), "· SQL OK여도 이미지는 깨질 수 있음", font=fnt(17), fill=NAVY)
    d.text((880, 520), "· Secrets의 AWS_STORAGE_BUCKET_NAME 확인", font=fnt(17), fill=NAVY)
    d.text((880, 565), "· 객체 존재·페이지 이미지 표시 확인", font=fnt(17), fill=NAVY)

    footer(img, "다음 과제: wipe 후 복구 드릴(RPO/RTO)을 운영 루틴으로 고정")
    save(img, "06_restore_media_sync.png")


def make_07_start_stop():
    img = Image.new("RGBA", (W, H), BG + (255,))
    title_bar(img, "7. EKS start/stop 비용 운영", "워크플로 성공만 보지 않고 실제 리소스 상태까지 확인")

    soft_card(img, (40, 130, 760, 700), r=18, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((40, 130, 760, 700), radius=18, outline=RED, width=3)
    d.text((60, 155), "STOP", font=fnt(24, True), fill=RED)
    tile(img, 80, 220, 180, 180, "githubactions", "Actions", "stop workflow", CYAN, SOFT_BLUE, 52)
    tile(img, 300, 220, 180, 180, "asg", "ASG = 0", "nodes down", ORANGE, SOFT_ORANGE, 52)
    tile(img, 520, 220, 180, 180, "nat", "NAT stop", "cost cut", RED, SOFT_RED, 52)
    d = ImageDraw.Draw(img)
    arrow_h(d, 260, 310, 300, NAVY)
    arrow_h(d, 480, 310, 520, NAVY)
    d.text((80, 450), "확인 기준", font=fnt(18, True), fill=SLATE)
    d.text((80, 500), "· desired=0 만으로 끝내지 않음", font=fnt(17), fill=NAVY)
    d.text((80, 545), "· EC2 인스턴스 0대까지 확인", font=fnt(17), fill=NAVY)
    d.text((80, 590), "· NAT stopped 함께 확인", font=fnt(17), fill=NAVY)
    d.text((80, 635), "· Actions 초록 ≠ 비용 절감 완료", font=fnt(17), fill=NAVY)

    soft_card(img, (840, 130, 1560, 700), r=18, fill=WHITE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((840, 130, 1560, 700), radius=18, outline=GREEN, width=3)
    d.text((860, 155), "START", font=fnt(24, True), fill=GREEN)
    tile(img, 880, 220, 160, 170, "nat", "NAT first", "egress", ORANGE, SOFT_ORANGE, 48)
    tile(img, 1080, 220, 160, 170, "servers", "Nodes", "EKS ready", PURPLE, SOFT_PURPLE, 48)
    tile(img, 1280, 220, 160, 170, "servers", "Argo sync", "apps up", CYAN, SOFT_BLUE, 48)
    tile(img, 980, 430, 160, 170, "rds_maria", "DB seed", "restore", GREEN, SOFT_GREEN, 48)
    tile(img, 1180, 430, 160, 170, "s3", "Media sync", "images", ORANGE, SOFT_ORANGE, 48)
    d = ImageDraw.Draw(img)
    arrow_h(d, 1040, 305, 1080, NAVY)
    arrow_h(d, 1240, 305, 1280, NAVY)
    arrow_v(d, 1360, 390, 480, NAVY)
    arrow_h(d, 1140, 515, 1180, NAVY)

    footer(img, "미사용 시간 노드·NAT 비용을 줄이되, 기동 순서(NAT→노드→Sync→데이터)를 지킨다")
    save(img, "07_eks_start_stop.png")


def main():
    make_01_deploy_overview()
    make_02_ssm_keyless()
    make_03_codedeploy_boot()
    make_04_gitops()
    make_05_oidc()
    make_06_restore_sync()
    make_07_start_stop()
    print("Done →", OUT)


if __name__ == "__main__":
    main()
