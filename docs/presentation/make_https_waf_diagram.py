#!/usr/bin/env python3
"""HTTPS · WAF 구성도 (강사용 PPT용) — 쉬운 설명 버전."""
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


def center_text_colored(draw, box, lines, color, gap=6):
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
        draw.text((x, y), line, font=fn, fill=color)
        y += h + gap


def arrow(draw, x0, y0, x1, y1, color=SLATE):
    draw.line((x0, y0, x1, y1), fill=color, width=4)
    if x1 > x0:
        draw.polygon([(x1, y1), (x1 - 12, y1 - 8), (x1 - 12, y1 + 8)], fill=color)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title = fnt(34, True)
    sub = fnt(20)
    box_t = fnt(22, True)
    box_s = fnt(17)
    small = fnt(15)

    d.text((48, 32), "HTTPS · WAF — 한 줄로 보기", font=title, fill=NAVY)
    d.text(
        (48, 82),
        "사용자 → 도메인(aniverse.my) → 공격 차단(WAF) → 암호화 입구(ALB) → 서버(EC2)",
        font=sub,
        fill=SLATE,
    )

    boxes = [
        (50, 160, 290, 310, SOFT_BLUE, BLUE, "1. 도메인", "aniverse.my", "어디로 갈지 안내"),
        (350, 160, 600, 310, SOFT_RED, RED, "2. WAF", "문지기", "이상한 요청 차단"),
        (660, 160, 980, 310, SOFT_TEAL, TEAL, "3. HTTPS (ALB)", "자물쇠 입구", "통신 암호화"),
        (1040, 160, 1550, 310, SOFT_ORANGE, ORANGE, "4. 서버", "EC2 / 앱", "실제 서비스 처리"),
    ]
    for x0, y0, x1, y1, fill, outline, t1, t2, t3 in boxes:
        round_rect(d, (x0, y0, x1, y1), 18, fill, outline, 3)
        center_text_colored(
            d,
            (x0, y0, x1, y1),
            [(t1, box_t), (t2, box_s), (t3, small)],
            outline,
            gap=6,
        )

    for x in (300, 620, 1000):
        arrow(d, x, 235, x + 40, 235, SLATE)

    left = (50, 360, 780, 850)
    right = (820, 360, 1550, 850)
    round_rect(d, left, 18, WHITE, BLUE, 2)
    round_rect(d, right, 18, WHITE, RED, 2)

    d.text((80, 390), "HTTPS = 암호화", font=box_t, fill=BLUE)
    https_lines = [
        "• ACM: aniverse.my용 인증서(자물쇠) 발급",
        "• ALB: https(443)로 접속 받기",
        "• http로 오면 https로 자동 이동",
        "• 결과: 주소창 자물쇠 + 내용 보호",
        "• Terraform으로 설정 고정",
    ]
    y = 460
    for line in https_lines:
        d.text((80, y), line, font=box_s, fill=NAVY)
        y += 58

    d.text((850, 390), "WAF = 공격 차단", font=box_t, fill=RED)
    waf_lines = [
        "• ALB 앞에서 요청을 먼저 검사",
        "• SQL 삽입·이상한 입력 걸러냄",
        "• 한 IP가 너무 자주 치면 차단",
        "• 통과한 요청만 서버로 전달",
        "• Terraform으로 ALB에 연결",
    ]
    y = 460
    for line in waf_lines:
        d.text((850, y), line, font=box_s, fill=NAVY)
        y += 58

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
