#!/usr/bin/env python3
"""Aniverse 발표 PPT — NunSub(1_Final) 구조 참고.

P시스템 → Architecture V1 (EC2/ASG/RDS)
F시스템 → Architecture V2 (EKS/GitOps)

스타일: 흰 배경 · 연회색 카드 · 컬러 액센트 바 · 큰 제목
출력: ppt/Aniverse_V1V2_발표_vN.pptx
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu

FONT = "맑은 고딕"
BASE = Path(__file__).resolve().parent
IMG = BASE / "images" / "hybrid"
OUT = BASE / "ppt"
OUT.mkdir(parents=True, exist_ok=True)

SW, SH = 13.333, 7.5
STEM = "Aniverse_V1V2_발표"
TOTAL = 12

NAVY = RGBColor(15, 23, 42)
BLACK = RGBColor(17, 24, 39)
WHITE = RGBColor(255, 255, 255)
GRAY = RGBColor(107, 114, 128)
LIGHT = RGBColor(243, 244, 246)
SOFT = RGBColor(249, 250, 251)
BLUE = RGBColor(37, 99, 235)
CYAN = RGBColor(14, 165, 233)
RED = RGBColor(239, 68, 68)
GREEN = RGBColor(34, 197, 94)
ORANGE = RGBColor(249, 115, 22)
PURPLE = RGBColor(139, 92, 246)
TEAL = RGBColor(20, 184, 166)


def next_path() -> Path:
    best = 0
    for p in OUT.glob(f"{STEM}_v*.pptx"):
        m = re.search(r"_v(\d+)\.pptx$", p.name)
        if m:
            best = max(best, int(m.group(1)))
    return OUT / f"{STEM}_v{best + 1}.pptx"


def font(run, size=16, bold=False, color=BLACK):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = FONT
    rPr = run._r.get_or_add_rPr()
    for tag in ("latin", "ea", "cs"):
        el = rPr.find(qn(f"a:{tag}"))
        if el is None:
            el = rPr.makeelement(qn(f"a:{tag}"), {})
            rPr.append(el)
        el.set("typeface", FONT)


def pad(tf, l=0.16, t=0.12, r=0.16, b=0.12):
    tf.word_wrap = True
    tf.margin_left = Inches(l)
    tf.margin_right = Inches(r)
    tf.margin_top = Inches(t)
    tf.margin_bottom = Inches(b)


def set_text(tf, text, size=16, bold=False, color=BLACK, align=None):
    tf.clear()
    pad(tf)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    font(r, size, bold, color)
    if align is not None:
        p.alignment = align


def add_para(tf, text, size=14, bold=False, color=BLACK, space_before=8, align=None):
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = text
    font(r, size, bold, color)
    p.space_before = Pt(space_before)
    if align is not None:
        p.alignment = align
    return p


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=WHITE):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(SH))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()


def card(slide, x, y, w, h, fill=SOFT, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    pad(sh.text_frame)
    return sh


def circle_icon(slide, x, y, size, fill, glyph="●"):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, size, size)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    set_text(sh.text_frame, glyph, 14, True, WHITE, PP_ALIGN.CENTER)
    sh.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    try:
        sh.text_frame.paragraphs[0].space_before = Pt(4)
    except Exception:
        pass
    return sh


def title_center(slide, text, y=0.35, size=28):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(12.3), Inches(0.6))
    set_text(box.text_frame, text, size, True, BLACK, PP_ALIGN.CENTER)


def footer(slide, n):
    tx = slide.shapes.add_textbox(Inches(0.5), Inches(7.15), Inches(12.3), Inches(0.28))
    p = tx.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"Aniverse  ·  Architecture V1 → V2"
    font(r, 11, False, GRAY)
    num = slide.shapes.add_textbox(Inches(11.3), Inches(7.15), Inches(1.5), Inches(0.28))
    p = num.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"{n} / {TOTAL}"
    font(r, 11, True, BLUE)
    p.alignment = PP_ALIGN.RIGHT


def put_img(slide, name, top=Inches(1.15), bottom=Inches(7.0), side=0.45):
    path = IMG / name
    if not path.exists():
        return False
    iw, ih = Image.open(path).size
    aspect = ih / float(iw)
    max_w = SW - side * 2
    max_h = bottom.inches - top.inches
    w_in = max_w
    h_in = w_in * aspect
    if h_in > max_h:
        h_in = max_h
        w_in = h_in / aspect
    x_in = (SW - w_in) / 2.0
    y_in = top.inches + (max_h - h_in) / 2.0
    slide.shapes.add_picture(
        str(path), Inches(x_in), Inches(y_in), width=Inches(w_in), height=Inches(h_in)
    )
    return True


def accent_item(slide, x, y, w, h, color, title, body):
    """NunSub 3열 스타일: 왼쪽 컬러 바 + 제목 + 본문."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.1), h)
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    box = slide.shapes.add_textbox(x + Inches(0.22), y, w - Inches(0.3), h)
    tf = box.text_frame
    set_text(tf, title, 15, True, BLACK)
    add_para(tf, body, 12, False, GRAY, 6)


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------
def slide_cover(prs):
    s = blank(prs)
    bg(s, RGBColor(239, 246, 255))  # soft blue-white like NunSub
    # brand
    t = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(7), Inches(2.2))
    tf = t.text_frame
    set_text(tf, "Aniverse", 48, True, BLUE)
    add_para(tf, "통합 서브컬처 커뮤니티 사이트", 20, False, NAVY, 14)
    add_para(tf, "Architecture V1 → V2  ·  EKS · GitOps 전환", 16, False, GRAY, 12)
    add_para(tf, "https://aniverse.my", 14, False, CYAN, 18)

    # team credits (bottom-right like NunSub)
    roles = [
        ("Network / Compute", "서이 등"),
        ("Container · DB · 관측", "윤주"),
        ("DevOps · GitOps", "현우"),
        ("App / Product", "팀"),
    ]
    box = s.shapes.add_textbox(Inches(8.2), Inches(4.8), Inches(4.5), Inches(2.2))
    tf = box.text_frame
    set_text(tf, "Team", 14, True, BLUE, PP_ALIGN.RIGHT)
    for role, who in roles:
        add_para(tf, f"{role}   {who}", 13, False, NAVY, 6, PP_ALIGN.RIGHT)


def slide_v1_def(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "Architecture V1 정의")
    items = [
        (
            "V1 정의",
            "User → ALB → ASG/EC2(Nginx+Django) → RDS · EFS · S3 로 "
            "Aniverse 서비스를 운영하던 초기 클라우드 구성입니다.",
        ),
        (
            "구현 방식",
            "Terraform으로 VPC·ALB·ASG를 구성하고, CodeDeploy / Actions로 "
            "EC2에 배포하는 방식을 사용했습니다.",
        ),
        (
            "개발 배경",
            "통합 서브컬처 사이트(장터·창작·커뮤니티)를 AWS에서 안정적으로 "
            "서비스하기 위해, 익숙한 EC2 기반 3-tier로 먼저 구축했습니다.",
        ),
        (
            "구현 범위",
            "HTTPS(ACM)·WAF·Redis·미디어 S3까지 포함한 운영 가능한 "
            "프로덕션 형태까지 구현이 완료된 상태였습니다.",
        ),
    ]
    positions = [
        (0.55, 1.25),
        (6.85, 1.25),
        (0.55, 4.15),
        (6.85, 4.15),
    ]
    for (x, y), (title, body) in zip(positions, items):
        c = card(s, Inches(x), Inches(y), Inches(5.95), Inches(2.6), LIGHT)
        set_text(c.text_frame, title, 18, True, BLUE)
        add_para(c.text_frame, body, 14, False, NAVY, 12)
    footer(s, 2)


def slide_v1_to_v2(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "V1의 한계  ·  V2 목표  ·  V2 차별점", size=26)

    # column headers
    headers = [
        (0.45, RED, "V1의 한계"),
        (4.7, GREEN, "V2의 기능 · 개발 목표"),
        (8.95, BLUE, "V2 차별점"),
    ]
    for x, color, text in headers:
        h = card(s, Inches(x), Inches(1.15), Inches(3.95), Inches(0.55), color)
        set_text(h.text_frame, text, 16, True, WHITE, PP_ALIGN.CENTER)

    left = [
        (
            "모니터링이 한눈에 안 보임",
            "메트릭·로그·배포 상태가 흩어져 있어, 장애/부하를 한 화면에서 파악하기 어려웠습니다.",
        ),
        (
            "수정 → 서비스 반영이 어려움",
            "인프라·앱을 바꿔도 EC2/에이전트 경로에 묶여, 변경이 서비스에 빠르게·일관되게 반영되기 어려웠습니다.",
        ),
        (
            "ASG만으로 늘렸다 줄이기",
            "스케일이 ASG(인스턴스) 단위에 의존해, 필요할 때만 줄이기 어렵고 상시 용량으로 비용 낭비가 생길 수 있었습니다.",
        ),
    ]
    mid = [
        (
            "관측을 한곳에",
            "Prom/Grafana · Loki로 메트릭·로그를 모아, 클러스터·앱 상태를 한눈에 보는 것을 목표로 합니다.",
        ),
        (
            "변경이 곧 배포",
            "이미지 빌드 + GitOps(Argo)로 인프라/앱 수정이 Synced 상태로 서비스에 반영되게 합니다.",
        ),
        (
            "필요한 만큼만 스케일",
            "노드·파드 단위로 스케일을 나누고, start/stop으로 미사용 구간 비용을 줄이는 구성을 목표로 합니다.",
        ),
    ]
    right = [
        (
            "관측 스택",
            "Prometheus · Grafana · Loki를 V2 기본 구성에 두고, 이후 Alert/Tempo로 확장합니다.",
        ),
        (
            "Actions → ECR → Argo",
            "sha-* 태그 bump 후 Argo sync로, 코드/차트 변경이 클러스터에 선언적으로 반영됩니다.",
        ),
        (
            "EKS + DB Pod",
            "ASG만의 인스턴스 스케일 대신 EKS 노드/파드 스케일과 PVC 기반 DB로 낭비를 줄입니다.",
        ),
    ]
    for i, (t, b) in enumerate(left):
        accent_item(s, Inches(0.45), Inches(1.95) + i * Inches(1.55), Inches(3.95), Inches(1.4), RED, t, b)
    for i, (t, b) in enumerate(mid):
        accent_item(s, Inches(4.7), Inches(1.95) + i * Inches(1.55), Inches(3.95), Inches(1.4), GREEN, t, b)
    for i, (t, b) in enumerate(right):
        accent_item(s, Inches(8.95), Inches(1.95) + i * Inches(1.55), Inches(3.95), Inches(1.4), BLUE, t, b)
    footer(s, 3)


def slide_v2_def(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "Architecture V2 (최종) 정의")

    vision = card(s, Inches(0.55), Inches(1.15), Inches(12.2), Inches(1.45), LIGHT, BLUE)
    set_text(vision.text_frame, "비전", 16, True, BLUE)
    add_para(
        vision.text_frame,
        "Aniverse를 EKS 위에서 GitOps로 재현 가능하게 운영하고, "
        "데이터·관측·보안까지 한 사이클로 다루는 최종 아키텍처를 목표로 합니다.",
        14,
        False,
        NAVY,
        8,
    )

    label = s.shapes.add_textbox(Inches(0.55), Inches(2.8), Inches(4), Inches(0.4))
    set_text(label.text_frame, "주요 기능", 16, True, BLACK)

    feats = [
        (BLUE, "ALB Ingress · HTTPS", "ACM ISSUED 후 Ingress ALB + Route53으로 외부 진입을 구성합니다."),
        (GREEN, "EKS web / db Pod", "Django+Nginx Deployment와 MariaDB StatefulSet+PVC로 앱·DB를 운영합니다."),
        (ORANGE, "Actions → ECR → Argo", "OIDC 빌드, sha-* 이미지, values bump 후 Argo sync로 배포합니다."),
        (PURPLE, "백업 · 관측", "restore Job / CronJob→S3, Prom·Grafana·Loki로 운영 가시성을 확보합니다."),
    ]
    for i, (color, title, body) in enumerate(feats):
        col, row = i % 2, i // 2
        x = Inches(0.55) + col * Inches(6.25)
        y = Inches(3.3) + row * Inches(1.7)
        c = card(s, x, y, Inches(6.0), Inches(1.5), SOFT)
        circle_icon(s, x + Inches(0.2), y + Inches(0.4), Inches(0.55), color)
        box = s.shapes.add_textbox(x + Inches(0.95), y + Inches(0.2), Inches(4.8), Inches(1.2))
        set_text(box.text_frame, title, 16, True, BLACK)
        add_para(box.text_frame, body, 13, False, GRAY, 6)
    footer(s, 4)


def slide_value(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "프로젝트 · 전환이 주는 가치")
    values = [
        ("서비스", "장터·창작·커뮤니티를 한곳에서 쓰는 통합 서브컬처 경험"),
        ("재현성", "이미지 + GitOps로 동일 환경을 다시 올릴 수 있음"),
        ("비용", "EKS start/stop · DB Pod로 학습/실험 비용 통제"),
        ("운영", "관측·백업·이관 체크리스트까지 운영 사이클 완성"),
    ]
    colors = [BLUE, TEAL, ORANGE, PURPLE]
    for i, ((t, b), color) in enumerate(zip(values, colors)):
        y = Inches(1.4) + i * Inches(1.3)
        c = card(s, Inches(1.2), y, Inches(10.9), Inches(1.15), LIGHT, color)
        set_text(c.text_frame, t, 20, True, color)
        add_para(c.text_frame, b, 15, False, NAVY, 6)
    footer(s, 5)


def slide_scenario(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "전환 시나리오  ·  Local → Lab → EKS")

    left = card(s, Inches(0.5), Inches(1.2), Inches(5.8), Inches(5.5), LIGHT)
    set_text(left.text_frame, "대상 · 맥락", 18, True, BLUE)
    for line in [
        "웹 서비스 + 클라우드 인프라를 한 사이클로 실습",
        "1차로 EC2 기반 V1을 완성한 뒤 EKS로 전환",
        "윤주: Docker · Helm · DB · 관측",
        "현우: Actions · Argo · OIDC · 이관",
        "네트워크/컴퓨트: VPC · Ingress · 노드",
    ]:
        add_para(left.text_frame, "·  " + line, 14, False, NAVY, 12)

    steps = [
        ("1", "문제 인식", "배포 재현·비용·관측이 V1에서 병목"),
        ("2", "Local", "Docker Compose로 이미지·앱 검증"),
        ("3", "Lab K8s", "Helm으로 워커 노드에서 동작 확인"),
        ("4", "EKS V2", "Argo GitOps · PVC · S3 백업까지 연결"),
        ("5", "검증", "health 200 + 시드/목록 UI 확인"),
    ]
    for i, (num, title, body) in enumerate(steps):
        y = Inches(1.2) + i * Inches(1.05)
        c = card(s, Inches(6.6), y, Inches(6.2), Inches(0.95), SOFT, BLUE)
        set_text(c.text_frame, f"{num}.  {title}", 15, True, BLUE)
        add_para(c.text_frame, body, 13, False, NAVY, 4)
    footer(s, 6)


def slide_requirements(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "전환 요구사항  ·  왜 V2(EKS)인가")
    rows = [
        ("배포 재현", "동일 이미지·매니페스트로 환경을 다시 올릴 것", "Actions → ECR → Argo"),
        ("스케일 분리", "노드 스케일과 파드 HPA를 분리 설계", "EKS + HPA 여지"),
        ("DB 비용", "RDS 상시 대신 학습용 영구 볼륨", "StatefulSet + PVC"),
        ("보안", "장기 키 금지 · 이관 시 ARN 전수 교체", "GitHub OIDC · IRSA"),
        ("관측", "메트릭·로그를 기본 구성에 포함", "Prom / Grafana / Loki"),
        ("검증", "CI 초록만으로 끝내지 않음", "health + 시드/목록 UI"),
    ]
    # header
    h = card(s, Inches(0.5), Inches(1.15), Inches(12.3), Inches(0.55), NAVY)
    set_text(h.text_frame, "구분          요청 / 문제                          반영", 14, True, WHITE)
    for i, (a, b, c) in enumerate(rows):
        y = Inches(1.8) + i * Inches(0.8)
        fill = LIGHT if i % 2 == 0 else SOFT
        row = card(s, Inches(0.5), y, Inches(12.3), Inches(0.72), fill)
        set_text(row.text_frame, f"{a}", 14, True, BLUE)
        add_para(row.text_frame, f"{b}   →   {c}", 13, False, NAVY, 4)
    footer(s, 7)


def slide_verify(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "기능 · 운영 검증 기준")
    items = [
        ("웹 health", "Ingress/ALB 통해 HTTPS 200", "curl / 브라우저", "충족"),
        ("DB 시드", "restore Job 후 목록 UI에 데이터", "minTables + seed_rows", "충족"),
        ("GitOps", "image.tag bump → Argo Synced", "Actions 로그 + Argo UI", "충족"),
        ("미디어", "destroy 후 Sync media 재업로드", "S3 media/ 확인", "충족"),
        ("관측", "Prom/Grafana 대시보드 조회", "클러스터 메트릭", "구성"),
        ("알림/트레이싱", "AlertManager · Tempo", "다음 단계", "예정"),
    ]
    for i, (t, check, method, result) in enumerate(items):
        col, row = i % 3, i // 3
        x = Inches(0.45) + col * Inches(4.25)
        y = Inches(1.25) + row * Inches(2.7)
        c = card(s, x, y, Inches(4.05), Inches(2.45), LIGHT)
        set_text(c.text_frame, t, 16, True, BLUE)
        add_para(c.text_frame, "검증: " + check, 13, False, NAVY, 10)
        add_para(c.text_frame, "방법: " + method, 12, False, GRAY, 6)
        add_para(c.text_frame, "결과: " + result, 13, True, GREEN if result == "충족" else ORANGE, 10)
    footer(s, 8)


def slide_stack(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "기술 스택  ·  데이터 흐름")

    stack = card(s, Inches(0.5), Inches(1.15), Inches(5.9), Inches(5.5), LIGHT)
    set_text(stack.text_frame, "Tech Stack", 18, True, BLUE)
    for line in [
        "App: Django + Nginx",
        "Container: Docker · Helm",
        "Orchestration: EKS (V2)",
        "DB: MariaDB StatefulSet + EBS PVC",
        "Storage: S3 (media / static / db-backups)",
        "CI/CD: GitHub Actions · ECR · Argo CD",
        "Auth to AWS: GitHub OIDC",
        "Observability: Prometheus · Grafana · Loki",
        "IaC: Terraform (anime-project-infra)",
    ]:
        add_para(stack.text_frame, "·  " + line, 14, False, NAVY, 10)

    flow = card(s, Inches(6.7), Inches(1.15), Inches(6.1), Inches(5.5), SOFT, TEAL)
    set_text(flow.text_frame, "Data Flow (V2)", 18, True, TEAL)
    for line in [
        "Users → Route53/ACM → ALB Ingress",
        "→ web Pod (Django) → MariaDB Pod",
        "→ EBS PVC (글/데이터 영구 저장)",
        "",
        "사진/미디어 → S3 media/ (DB 아님)",
        "",
        "destroy 후: Git SQL 시드 import",
        "운영 중: CronJob → S3 db-backups/",
        "",
        "eks-stop: PVC 유지",
        "terraform destroy: PVC + S3 삭제",
    ]:
        add_para(flow.text_frame, line, 14, False, NAVY, 8)
    footer(s, 9)


def slide_arch_v1(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "시스템 구성도  ·  Architecture V1", size=26)
    put_img(s, "hybrid_01_arch_v1_vpc.png", top=Inches(1.05), bottom=Inches(7.0))
    footer(s, 10)


def slide_arch_v2(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "시스템 구성도  ·  Architecture V2", size=26)
    put_img(s, "hybrid_02_arch_v2_vpc.png", top=Inches(1.05), bottom=Inches(7.0))
    footer(s, 11)


def slide_next(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "향후 계획  ·  3UP")

    cols = [
        (
            ORANGE,
            "Unique Up",
            "차별성",
            [
                "관측 고도화 (Alert · Tempo/OTel)",
                "시드/목록 검증을 CI 게이트로",
                "운영 런북·이관 체크리스트 표준화",
            ],
        ),
        (
            GREEN,
            "Complete Up",
            "완성도",
            [
                "Loki/Alloy EKS 반영 완료",
                "OIDC 권한 축소 · Budgets",
                "백업 덤프 주기·복구 드릴",
            ],
        ),
        (
            BLUE,
            "Performance Up",
            "시연·운영",
            [
                "start/stop 데모 시나리오",
                "아키텍처 V1/V2 대비 한 장 더 다듬기",
                "장애 재현(Missing/SSA) 데모 정리",
            ],
        ),
    ]
    for i, (color, title, sub, lines) in enumerate(cols):
        x = Inches(0.5) + i * Inches(4.25)
        head = card(s, x, Inches(1.2), Inches(4.05), Inches(1.0), color)
        set_text(head.text_frame, title, 18, True, WHITE, PP_ALIGN.CENTER)
        add_para(head.text_frame, sub, 12, False, WHITE, 2, PP_ALIGN.CENTER)
        body = card(s, x, Inches(2.4), Inches(4.05), Inches(3.6), LIGHT)
        set_text(body.text_frame, "", 12)
        body.text_frame.clear()
        pad(body.text_frame)
        first = True
        for line in lines:
            if first:
                set_text(body.text_frame, "·  " + line, 14, False, NAVY)
                first = False
            else:
                add_para(body.text_frame, "·  " + line, 14, False, NAVY, 14)

    tip = card(s, Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.75), SOFT, BLUE)
    set_text(
        tip.text_frame,
        "원칙: 아키텍처 확정 → 동작 확인 → 관측·보안 고도화   |   Actions 초록 ≠ 시드/목록 검증",
        14,
        True,
        NAVY,
        PP_ALIGN.CENTER,
    )
    footer(s, 12)


def main():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)

    slide_cover(prs)
    slide_v1_def(prs)
    slide_v1_to_v2(prs)
    slide_v2_def(prs)
    slide_value(prs)
    slide_scenario(prs)
    slide_requirements(prs)
    slide_verify(prs)
    slide_stack(prs)
    slide_arch_v1(prs)
    slide_arch_v2(prs)
    slide_next(prs)

    out = next_path()
    prs.save(out)
    print(f"Wrote {out} ({TOTAL} slides)")


if __name__ == "__main__":
    main()
