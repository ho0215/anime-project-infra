#!/usr/bin/env python3
"""AWS · GitHub 사용 기능 한 장 요약 (강사용 PPT)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "images" / "instructor" / "07_aws_github_stack.png"
FONT_R = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_B = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"

W, H = 1600, 900
BG = (248, 250, 252)
NAVY = (15, 23, 42)
SLATE = (71, 85, 105)
BLUE = (37, 99, 235)
ORANGE = (234, 88, 12)
WHITE = (255, 255, 255)
SOFT_BLUE = (239, 246, 255)
SOFT_ORANGE = (255, 247, 237)
CHIP = (255, 255, 255)
LINE = (226, 232, 240)


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def round_rect(draw, xy, r, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def chip(draw, x, y, text, fill, outline, font):
    pad_x, pad_y = 14, 8
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    w, h = tw + pad_x * 2, th + pad_y * 2
    round_rect(draw, (x, y, x + w, y + h), 12, CHIP, outline, 2)
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=fill)
    return w, h


def flow_chips(draw, x0, y0, x1, items, color, font, gap=10):
    """Place chips wrapping within [x0, x1]. Returns final y after last row."""
    x, y = x0, y0
    row_h = 0
    for text in items:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0] + 28
        th = bbox[3] - bbox[1] + 16
        if x + tw > x1 and x > x0:
            x = x0
            y += row_h + gap
            row_h = 0
        chip(draw, x, y, text, color, color, font)
        x += tw + gap
        row_h = max(row_h, th)
    return y + row_h


def section(draw, box, title, subtitle, groups, accent, soft):
    x0, y0, x1, y1 = box
    round_rect(draw, box, 22, soft, accent, 3)
    draw.text((x0 + 28, y0 + 22), title, font=fnt(28, True), fill=accent)
    draw.text((x0 + 28, y0 + 62), subtitle, font=fnt(16), fill=SLATE)
    y = y0 + 105
    chip_font = fnt(15, True)
    group_font = fnt(15, True)
    for label, items in groups:
        draw.text((x0 + 28, y), label, font=group_font, fill=NAVY)
        y += 30
        y = flow_chips(draw, x0 + 28, y, x1 - 28, items, accent, chip_font, gap=8)
        y += 22


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((48, 28), "사용한 기능 한 장 정리", font=fnt(34, True), fill=NAVY)
    d.text(
        (48, 78),
        "AWS = 인프라·보안·운영   ·   GitHub = 코드·자동화·비밀값",
        font=fnt(20),
        fill=SLATE,
    )

    aws_groups = [
        ("네트워크·보안", ["VPC", "Subnet", "IGW", "NAT", "Security Group", "NACL", "VPC Endpoint"]),
        ("트래픽·서버", ["ALB", "ASG", "EC2", "IAM", "CodeDeploy", "SSM"]),
        ("데이터·저장", ["RDS MariaDB", "EFS", "S3", "ElastiCache Redis", "DynamoDB(State Lock)"]),
        ("보안·관측", ["ACM", "Route53", "WAF", "Secrets Manager", "CloudWatch"]),
    ]
    gh_groups = [
        ("저장소", ["anime-project (앱)", "anime-project-infra (인프라)"]),
        ("자동화 (Actions)", ["Terraform CI", "Terraform CD", "App Deploy"]),
        ("비밀값·설정", ["GitHub Secrets", "GitHub Variables", "OIDC → AWS"]),
        ("협업", ["Pull Request", "Code Review", "main 브랜치 배포"]),
    ]

    section(
        d,
        (40, 130, 790, 860),
        "AWS",
        "실제로 띄운 클라우드 서비스",
        aws_groups,
        BLUE,
        SOFT_BLUE,
    )
    section(
        d,
        (810, 130, 1560, 860),
        "GitHub",
        "코드 관리와 자동 배포에 쓴 기능",
        gh_groups,
        ORANGE,
        SOFT_ORANGE,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
