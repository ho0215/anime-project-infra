#!/usr/bin/env python3
"""Terraform 모듈 계층 구성도 (강사용 PPT 슬라이드 7)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path(__file__).resolve().parent / "images" / "instructor" / "03_terraform_modules.png"
FONT_R = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_B = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"

W, H = 1600, 900
BG = (247, 249, 252)
NAVY = (15, 23, 42)
SLATE = (71, 85, 105)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
BLUE = (37, 99, 235)
TEAL = (13, 148, 136)
ORANGE = (234, 88, 12)
PURPLE = (124, 58, 237)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
PINK = (219, 39, 119)


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def soft_panel(img, xy, r, fill, shadow=True, outline=None, width=0):
    x0, y0, x1, y1 = xy
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0 + 3, y0 + 5, x1 + 3, y1 + 5), radius=r, fill=(15, 23, 42, 24))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def text_center(draw, box, text, font, fill):
    x0, y0, x1, y1 = box
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((x0 + (x1 - x0 - tw) // 2, y0 + (y1 - y0 - th) // 2), text, font=font, fill=fill)


def text_center_multiline(draw, box, lines, fonts, fills, gap=4):
    x0, y0, x1, y1 = box
    heights = []
    widths = []
    for line, fn in zip(lines, fonts):
        bb = draw.textbbox((0, 0), line, font=fn)
        widths.append(bb[2] - bb[0])
        heights.append(bb[3] - bb[1])
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = y0 + (y1 - y0 - total_h) // 2
    for line, fn, fill, h, w in zip(lines, fonts, fills, heights, widths):
        draw.text((x0 + (x1 - x0 - w) // 2, y), line, font=fn, fill=fill)
        y += h + gap


def draw_arrow_down(draw, cx, y0, y1, color=SLATE):
    draw.line((cx, y0, cx, y1 - 10), fill=color, width=4)
    draw.polygon([(cx, y1), (cx - 9, y1 - 14), (cx + 9, y1 - 14)], fill=color)


def icon_circle(draw, cx, cy, r, color):
    fill = tuple(int(c * 0.15 + 255 * 0.85) for c in color)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=color, width=3)


def draw_module_icon(draw, kind, cx, cy, color):
    icon_circle(draw, cx, cy, 24, color)
    w = 3
    if kind == "network":
        draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), outline=color, width=w)
        draw.line((cx - 14, cy, cx + 14, cy), fill=color, width=w)
        draw.line((cx, cy - 14, cx, cy + 14), fill=color, width=w)
    elif kind == "shield":
        pts = [(cx, cy - 14), (cx + 12, cy - 7), (cx + 10, cy + 7), (cx, cy + 14), (cx - 10, cy + 7), (cx - 12, cy - 7)]
        draw.line(pts + [pts[0]], fill=color, width=w)
    elif kind == "nat":
        draw.rounded_rectangle((cx - 12, cy - 10, cx + 12, cy + 10), 3, outline=color, width=w)
        draw.line((cx - 6, cy - 4, cx - 6, cy + 4), fill=color, width=w)
        draw.line((cx + 6, cy - 4, cx + 6, cy + 4), fill=color, width=w)
        draw.line((cx - 6, cy, cx + 6, cy), fill=color, width=w)
    elif kind == "endpoint":
        draw.arc((cx - 12, cy - 8, cx + 12, cy + 8), 200, 340, fill=color, width=w)
        draw.line((cx - 8, cy + 2, cx + 8, cy + 2), fill=color, width=w)
    elif kind == "database":
        draw.ellipse((cx - 12, cy - 12, cx + 12, cy - 2), outline=color, width=w)
        draw.line((cx - 12, cy - 7, cx - 12, cy + 8), fill=color, width=w)
        draw.line((cx + 12, cy - 7, cx + 12, cy + 8), fill=color, width=w)
        draw.arc((cx - 12, cy + 2, cx + 12, cy + 12), 0, 180, fill=color, width=w)
    elif kind == "bucket":
        draw.polygon([(cx - 12, cy - 6), (cx + 12, cy - 6), (cx + 10, cy + 10), (cx - 10, cy + 10)], outline=color)
        draw.line([(cx - 12, cy - 6), (cx + 12, cy - 6), (cx + 10, cy + 10), (cx - 10, cy + 10), (cx - 12, cy - 6)], fill=color, width=w)
    elif kind == "redis":
        for i, dy in enumerate((-8, 0, 8)):
            draw.rounded_rectangle((cx - 12, cy + dy - 3, cx + 12, cy + dy + 3), 2, outline=color, width=2)
    elif kind == "cert":
        draw.rounded_rectangle((cx - 10, cy - 12, cx + 10, cy + 12), 2, outline=color, width=w)
        draw.ellipse((cx - 4, cy + 4, cx + 4, cy + 12), outline=color, width=2)
    elif kind == "alb":
        draw.line((cx, cy - 12, cx, cy + 4), fill=color, width=w)
        draw.line((cx - 12, cy + 4, cx + 12, cy + 4), fill=color, width=w)
        for dx in (-10, 0, 10):
            draw.line((cx + dx, cy + 4, cx + dx, cy + 12), fill=color, width=w)
    elif kind == "waf":
        draw.polygon([(cx, cy - 12), (cx + 12, cy + 10), (cx - 12, cy + 10)], outline=color)
        draw.line([(cx, cy - 12), (cx + 12, cy + 10), (cx - 12, cy + 10), (cx, cy - 12)], fill=color, width=w)
    elif kind == "lock":
        draw.rounded_rectangle((cx - 10, cy - 2, cx + 10, cy + 12), 3, outline=color, width=w)
        draw.arc((cx - 8, cy - 12, cx + 8, cy + 2), 180, 0, fill=color, width=w)
    elif kind == "chip":
        draw.rounded_rectangle((cx - 12, cy - 10, cx + 12, cy + 10), 3, outline=color, width=w)
        for dx, dy in ((-12, 0), (12, 0), (0, -10), (0, 10)):
            draw.line((cx + dx, cy + dy, cx + dx + (4 if dx < 0 else -4 if dx > 0 else 0), cy + dy + (4 if dy < 0 else -4 if dy > 0 else 0)), fill=color, width=2)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 14), (cx + 8, cy + 6), (cx, cy + 2), (cx - 8, cy + 6)], outline=color)
        draw.line([(cx, cy - 14), (cx + 8, cy + 6), (cx, cy + 2), (cx - 8, cy + 6), (cx, cy - 14)], fill=color, width=w)
    elif kind == "chart":
        for i, h in enumerate((8, 14, 10)):
            draw.rectangle((cx - 10 + i * 8, cy + 8 - h, cx - 4 + i * 8, cy + 8), fill=color)
    elif kind == "code":
        draw.text((cx - 12, cy - 10), "</>", font=fnt(16, True), fill=color)


def module_card(img, box, name, desc, icon, color):
    x0, y0, x1, y1 = box
    soft_panel(img, box, 12, WHITE, True, (226, 232, 240), 1)
    d = ImageDraw.Draw(img)
    cx = (x0 + x1) // 2
    draw_module_icon(d, icon, cx, y0 + 36, color)
    text_center(d, (x0, y0 + 58, x1, y0 + 84), name, fnt(15, True), NAVY)
    lines = desc.split("\n")
    text_center_multiline(
        d,
        (x0 + 6, y0 + 84, x1 - 6, y1 - 6),
        lines,
        [fnt(11)] * len(lines),
        [MUTED] * len(lines),
        gap=2,
    )


def layer_row(img, y, h, num, title_en, title_ko, color, modules):
    x_left = 36
    x_right = 1180
    soft_panel(img, (x_left, y, x_right, y + h), 16, tuple(int(c * 0.06 + 255 * 0.94) for c in color), True, color, 2)
    d = ImageDraw.Draw(img)
    d.ellipse((x_left + 16, y + 16, x_left + 52, y + 52), fill=color)
    text_center(d, (x_left + 16, y + 16, x_left + 52, y + 52), str(num), fnt(18, True), WHITE)
    d.text((x_left + 62, y + 18), title_en, font=fnt(18, True), fill=color)
    d.text((x_left + 62, y + 44), title_ko, font=fnt(13), fill=SLATE)

    inner_x0 = x_left + 170
    inner_x1 = x_right - 20
    inner_y0 = y + 12
    inner_y1 = y + h - 12
    n = len(modules)
    gap = 12
    card_w = (inner_x1 - inner_x0 - gap * (n - 1)) // n
    card_h = inner_y1 - inner_y0
    for i, (name, desc, icon, mod_color) in enumerate(modules):
        cx0 = inner_x0 + i * (card_w + gap)
        module_card(img, (cx0, inner_y0, cx0 + card_w, inner_y0 + card_h), name, desc, icon, mod_color)


def side_panel(img):
    box = (1200, 150, 1560, 760)
    soft_panel(img, box, 18, WHITE, True, BLUE, 2)
    d = ImageDraw.Draw(img)
    # dashed border effect
    x0, y0, x1, y1 = box
    for i in range(x0, x1, 14):
        d.line((i, y0, min(i + 8, x1), y0), fill=BLUE, width=2)
        d.line((i, y1, min(i + 8, x1), y1), fill=BLUE, width=2)
    for i in range(y0, y1, 14):
        d.line((x0, i, x0, min(i + 8, y1)), fill=BLUE, width=2)
        d.line((x1, i, x1, min(i + 8, y1)), fill=BLUE, width=2)

    icon_circle(d, (x0 + x1) // 2, y0 + 90, 34, BLUE)
    d.text(((x0 + x1) // 2 - 18, y0 + 72), "</>", font=fnt(22, True), fill=BLUE)
    text_center(d, (x0 + 20, y0 + 150, x1 - 20, y0 + 190), "modules/*", fnt(22, True), NAVY)
    draw_arrow_down(d, (x0 + x1) // 2, y0 + 200, y0 + 280, BLUE)
    text_center_multiline(
        d,
        (x0 + 16, y0 + 300, x1 - 16, y0 + 380),
        ["environments/", "dev/main.tf"],
        [fnt(18, True), fnt(18, True)],
        [TEAL, TEAL],
        gap=6,
    )
    text_center_multiline(
        d,
        (x0 + 16, y0 + 420, x1 - 16, y0 + 520),
        ["각 모듈을", "환경 main.tf 에서", "조립 · apply"],
        [fnt(14)] * 3,
        [MUTED] * 3,
        gap=4,
    )


def main():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Terraform Module Map — Layers", font=fnt(30, True), fill=NAVY)
    d.text((40, 66), "모듈 구성도 · 계층", font=fnt(16), fill=SLATE)

    layer1 = [
        ("network", "VPC, Subnets,\nRoute Tables", "network", BLUE),
        ("security", "Security Groups,\nNACL, IAM", "shield", BLUE),
        ("nat", "NAT Instance", "nat", BLUE),
        ("endpoints", "VPC Endpoints\n(S3, DDB, ECR 등)", "endpoint", BLUE),
    ]
    layer2 = [
        ("database", "RDS\n(MySQL/PostgreSQL)", "database", TEAL),
        ("storage", "S3 Buckets", "bucket", TEAL),
        ("redis", "ElastiCache\n(Redis)", "redis", RED),
        ("acm", "ACM\nCertificate", "cert", PINK),
        ("alb", "Application\nLoad Balancer", "alb", BLUE),
        ("waf", "AWS WAF\n(Web ACL)", "waf", ORANGE),
        ("secrets", "Secrets Manager /\nParameter Store", "lock", GREEN),
        ("compute", "Auto Scaling,\nLaunch Template", "chip", ORANGE),
    ]
    layer3 = [
        ("cicd", "CodePipeline,\nCodeBuild, CodeDeploy", "rocket", ORANGE),
        ("monitoring", "CloudWatch,\nAlarms, Dashboards", "chart", ORANGE),
        ("environments/dev", "조립 (Composition)\nmain.tf", "code", ORANGE),
    ]

    y1, h1 = 110, 150
    y2, h2 = 300, 150
    y3, h3 = 490, 150

    layer_row(img, y1, h1, 1, "Foundation", "기반 계층", BLUE, layer1)
    layer_row(img, y2, h2, 2, "Platform", "플랫폼 계층", TEAL, layer2)
    layer_row(img, y3, h3, 3, "Delivery & Ops", "전달 & 운영 계층", ORANGE, layer3)

    d = ImageDraw.Draw(img)
    draw_arrow_down(d, 610, y1 + h1 + 4, y2 - 6)
    draw_arrow_down(d, 610, y2 + h2 + 4, y3 - 6)

    side_panel(img)

    d = ImageDraw.Draw(img)
    d.text((40, 860), "Layer 1 → Layer 2 → Layer 3  ·  하위 계층을 먼저 만들고 상위에서 조립", font=fnt(13), fill=MUTED)

    out = img.convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
