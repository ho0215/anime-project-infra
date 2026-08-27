#!/usr/bin/env python3
"""HTTPS · WAF 구성도 (강사용 PPT용)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "images" / "instructor" / "06_https_waf.png"
FONT_R = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
FONT_B = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"

W, H = 1600, 900
BG = (248, 250, 252)
NAVY = (15, 23, 42)
SLATE = (71, 85, 105)
BLUE = (37, 99, 235)
RED = (220, 38, 38)
TEAL = (13, 148, 136)
ORANGE = (234, 88, 12)
WHITE = (255, 255, 255)
SOFT_BLUE = (239, 246, 255)
SOFT_RED = (254, 242, 242)
SOFT_TEAL = (240, 253, 250)
SOFT_ORANGE = (255, 247, 237)


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def round_rect(draw, xy, r, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def center_text(draw, box, lines, font, fill, gap=4):
    x0, y0, x1, y1 = box
    heights = []
    widths = []
    for line, fn in lines:
        bbox = draw.textbbox((0, 0), line, font=fn)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = y0 + (y1 - y0 - total_h) // 2
    for (line, fn), h, w in zip(lines, heights, widths):
        x = x0 + (x1 - x0 - w) // 2
        draw.text((x, y), line, font=fn, fill=fill)
        y += h + gap


def arrow(draw, x0, y0, x1, y1, color=SLATE):
    draw.line((x0, y0, x1, y1), fill=color, width=4)
    # simple chevron
    if x1 > x0:
        draw.polygon([(x1, y1), (x1 - 12, y1 - 8), (x1 - 12, y1 + 8)], fill=color)
    else:
        draw.polygon([(x1, y1), (x1 + 12, y1 - 8), (x1 + 12, y1 + 8)], fill=color)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = fnt(36, True)
    sub = fnt(20)
    box_t = fnt(22, True)
    box_s = fnt(16)
    small = fnt(15)

    d.text((48, 36), "HTTPS · WAF 보호 경로", font=title, fill=NAVY)
    d.text(
        (48, 88),
        "Route53 → WAF → ALB(ACM HTTPS) → ASG/EC2   ·   aniverse.my",
        font=sub,
        fill=SLATE,
    )

    # flow boxes
    boxes = [
        (60, 180, 280, 320, SOFT_BLUE, BLUE, "Route 53", "aniverse.my", "DNS Alias → ALB"),
        (360, 180, 580, 320, SOFT_RED, RED, "WAF", "Regional Web ACL", "SQLi · Rate · Common"),
        (660, 180, 980, 320, SOFT_TEAL, TEAL, "ALB HTTPS", "ACM 인증서", "80 → 443 redirect"),
        (1060, 180, 1540, 320, SOFT_ORANGE, ORANGE, "ASG / EC2", "Nginx + Daphne", "Target Group forward"),
    ]
    for x0, y0, x1, y1, fill, outline, t1, t2, t3 in boxes:
        round_rect(d, (x0, y0, x1, y1), 18, fill, outline, 3)
        center_text(
            d,
            (x0, y0, x1, y1),
            [(t1, box_t), (t2, box_s), (t3, small)],
            None,
            outline,
            gap=6,
        )

    for x in (300, 600, 1000):
        arrow(d, x, 250, x + 50, 250, SLATE)

    # detail panels
    left = (60, 380, 780, 840)
    right = (820, 380, 1540, 840)
    round_rect(d, left, 18, WHITE, BLUE, 2)
    round_rect(d, right, 18, WHITE, RED, 2)

    d.text((90, 410), "HTTPS (ACM + ALB)", font=box_t, fill=BLUE)
    https_lines = [
        "• modules/acm : aniverse.my DNS 검증 인증서",
        "• modules/alb : 443 HTTPS Listener + TLS1.3 policy",
        "• HTTP 80 → HTTPS 443 301 리다이렉트",
        "• Route53 A/Alias 로 apex · www → ALB",
        "• 앱 Secrets: USE_HTTPS=True, CSRF https 허용",
        "• 결과: 브라우저 자물쇠 + 암호화 전송",
    ]
    y = 470
    for line in https_lines:
        d.text((90, y), line, font=box_s, fill=NAVY)
        y += 48

    d.text((850, 410), "WAF (ALB 연결)", font=box_t, fill=RED)
    waf_lines = [
        "• modules/waf : aniverse-alb-waf (REGIONAL)",
        "• AWSManagedRulesCommonRuleSet",
        "• KnownBadInputs + SQLi RuleSet",
        "• RateLimitPerIP (IP당 요청 제한 → Block)",
        "• aws_wafv2_web_acl_association → ALB",
        "• CloudWatch metrics · sampled requests",
    ]
    y = 470
    for line in waf_lines:
        d.text((850, y), line, font=box_s, fill=NAVY)
        y += 48

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
