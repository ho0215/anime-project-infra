#!/usr/bin/env python3
"""V2 일자별 일정 이미지 생성."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
OUT = BASE / "images" / "v2_schedule_by_day.png"
FONT_DIR = Path("/tmp/fonts")

W, H = 2400, 1350
BG = "#F8FAFC"
NAVY = "#0A1128"
TEXT = "#0F172A"
MUTED = "#64748B"
LINE = "#E2E8F0"
WHITE = "#FFFFFF"


def font(size, bold=False):
    name = "NotoSansKR-Bold.otf" if bold else "NotoSansKR-Regular.otf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def centered(draw, box, text, ft, fill, spacing=8):
    left, top, right, bottom = box
    lines = text.split("\n")
    heights = []
    widths = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=ft)
        widths.append(b[2] - b[0])
        heights.append(b[3] - b[1])
    total = sum(heights) + spacing * (len(lines) - 1)
    y = top + (bottom - top - total) / 2
    for line, width, height in zip(lines, widths, heights):
        draw.text(((left + right - width) / 2, y), line, font=ft, fill=fill)
        y += height + spacing


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((55, 36), "V2 일정", font=font(44, True), fill=TEXT)
    draw.text((270, 50), "준비 → 구축 → 이관 → 복구 → 정리 → 보안", font=font(22, True), fill="#00AEEF")
    draw.rectangle((55, 105, 275, 113), fill="#00AEEF")

    dates = [
        ("9/11", "금"),
        ("9/14", "월"),
        ("9/15", "화"),
        ("9/16", "수"),
        ("9/18", "금"),
        ("9/21", "월"),
        ("9/22", "화"),
        ("9/23", "수"),
        ("9/28", "월"),
        ("9/29", "화"),
        ("10/1", "목"),
    ]
    phases = [
        (0, 1, "준비", "#00AEEF"),
        (2, 3, "구축", "#2563EB"),
        (4, 4, "이관", "#DC2626"),
        (5, 7, "복구", "#16A34A"),
        (8, 9, "정리", "#7C3AED"),
        (10, 10, "보안", "#EA580C"),
    ]

    x0, x1, gap = 280, 2360, 10
    col_w = (x1 - x0 - gap * (len(dates) - 1)) / len(dates)

    def col_x(index):
        return x0 + index * (col_w + gap)

    for start, end, label, color in phases:
        left = col_x(start)
        right = col_x(end) + col_w
        rounded(draw, (left, 130, right, 168), 10, color)
        centered(draw, (left, 130, right, 168), label, font(18, True), WHITE)

    for i, (day, weekday) in enumerate(dates):
        left = col_x(i)
        rounded(draw, (left, 178, left + col_w, 265), 12, NAVY)
        centered(draw, (left, 186, left + col_w, 230), day, font(28, True), WHITE)
        centered(draw, (left, 228, left + col_w, 258), weekday, font(16), "#CBD5E1")

    rows = [
        (
            "GitOps\nCI/CD",
            "#008CC4",
            "#E8F7FF",
            "#0284C7",
            [
                "방향 확정\nDocker·미니K8s",
                "ECR·OIDC\nstart / stop",
                "S3 static\nArgo → Helm",
                "Argo·HTTPS\nDB 시드 Job",
                "계정 Block\ndestroy 정리",
                "—",
                "ALB 복구\nArgo Missing",
                "시드 검증\n태그 sync",
                "—",
                "끄기·켜기\n대기 수정",
                "WAF\nTerraform",
            ],
        ),
        (
            "EKS\n네트워크",
            "#0D9488",
            "#ECFDFA",
            "#0D9488",
            [
                "—",
                "쿼터·Ingress\nPVC",
                "EKS 클러스터\nHPA·CNI·CSI",
                "—",
                "백업 IRSA",
                "—",
                "신계정 apply",
                "—",
                "External\nSecrets",
                "RBAC 설정\nESO v1\n파드 수 상향",
                "WAFv2\nALB 연결",
            ],
        ),
        (
            "DB\n관측",
            "#EA580C",
            "#FFF7ED",
            "#EA580C",
            [
                "—",
                "Helm 차트\n로컬 쿠버",
                "PVC 검증",
                "파드 한도\nQuota",
                "백업·Loki\n설정",
                "—",
                "—",
                "DB 덤프\nmariadb-dump",
                "OTel·Tempo\nAlertManager",
                "파드\n안티어피니티",
                "부하\n테스트",
            ],
        ),
    ]
    row_tops = [285, 620, 955]
    row_h = 300

    for (label, label_color, cell_color, accent, values), top in zip(rows, row_tops):
        rounded(draw, (45, top, 260, top + row_h), 14, label_color)
        centered(draw, (45, top, 260, top + row_h), label, font(32, True), WHITE, 12)

        for i, value in enumerate(values):
            left = col_x(i)
            rounded(draw, (left, top, left + col_w, top + row_h), 14, WHITE, LINE, 2)
            if value != "—":
                rounded(draw, (left + 10, top + 12, left + col_w - 10, top + row_h - 12), 10, cell_color)
                draw.rectangle((left + 10, top + 12, left + 18, top + row_h - 12), fill=accent)
                centered(
                    draw,
                    (left + 22, top + 25, left + col_w - 8, top + row_h - 25),
                    value,
                    font(18, True),
                    "#0F4650" if label_color != "#EA580C" else "#9A3412",
                    8,
                )
            else:
                centered(draw, (left, top, left + col_w, top + row_h), value, font(28), "#CBD5E1")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
