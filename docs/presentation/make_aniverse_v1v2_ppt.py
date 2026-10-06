#!/usr/bin/env python3
"""Aniverse V1→V2 발표 PPT — 사용자 확정본(10장) 기준.

기준 문서: CONTENT_V1V2_working.md
소스 PPT: ppt/Aniverse_V1V2_발표_working.pptx (업로드 확정본 구조)

출력: ppt/Aniverse_V1V2_발표_vN.pptx 및 working.pptx 갱신
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

FONT = "맑은 고딕"
BASE = Path(__file__).resolve().parent
IMG = BASE / "images" / "hybrid"
OUT = BASE / "ppt"
OUT.mkdir(parents=True, exist_ok=True)

SW, SH = 13.333, 7.5
STEM = "Aniverse_V1V2_발표"
TOTAL = 19
WORKING = OUT / "Aniverse_V1V2_발표_working.pptx"

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


def font(run, size=18, bold=False, color=BLACK):
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


def set_text(tf, text, size=18, bold=False, color=BLACK, align=None):
    tf.clear()
    pad(tf)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    font(r, size, bold, color)
    if align is not None:
        p.alignment = align


def add_para(tf, text, size=16, bold=False, color=BLACK, space_before=8, align=None):
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


def circle_icon(slide, x, y, size, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, size, size)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def title_center(slide, text, y=0.22, size=36):
    box = slide.shapes.add_textbox(Inches(0.5), Inches(y), Inches(12.3), Inches(0.7))
    set_text(box.text_frame, text, size, True, BLACK, PP_ALIGN.CENTER)


def footer(slide, n):
    tx = slide.shapes.add_textbox(Inches(0.5), Inches(7.15), Inches(12.3), Inches(0.28))
    p = tx.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Aniverse  ·  Architecture V1 → V2"
    font(r, 13, False, GRAY)
    num = slide.shapes.add_textbox(Inches(11.3), Inches(7.15), Inches(1.5), Inches(0.28))
    p = num.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"{n} / {TOTAL}"
    font(r, 13, True, BLUE)
    p.alignment = PP_ALIGN.RIGHT


def put_img(slide, name, top=Inches(1.05), bottom=Inches(7.0), side=0.45):
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
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(0.1), h)
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    box = slide.shapes.add_textbox(x + Inches(0.22), y, w - Inches(0.3), h)
    tf = box.text_frame
    set_text(tf, title, 22, True, BLACK)
    add_para(tf, body, 18, False, GRAY, 10)


# ---------------------------------------------------------------------------
def slide_cover(prs):
    s = blank(prs)
    bg(s, RGBColor(239, 246, 255))
    t = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(8), Inches(2.5))
    tf = t.text_frame
    set_text(tf, "Aniverse", 54, True, BLUE)
    add_para(tf, "통합 서브컬처 커뮤니티 사이트", 24, False, NAVY, 14)
    add_para(tf, "Architecture V1 → V2  ·  EKS · GitOps 전환", 20, False, GRAY, 12)
    add_para(tf, "https://aniverse.my", 18, False, CYAN, 18)

    box = s.shapes.add_textbox(Inches(7.5), Inches(5.2), Inches(5.2), Inches(1.5))
    tf = box.text_frame
    set_text(tf, "Team", 18, True, BLUE, PP_ALIGN.RIGHT)
    add_para(tf, "김현우, 박서이, 김윤주, 강유민", 16, False, NAVY, 8, PP_ALIGN.RIGHT)


def slide_v1_def(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "Architecture V1")
    items = [
        (
            "구성",
            "ALB 뒤에 EC2 애플리케이션 서버를 두고, RDS·EFS·S3를 연결해 서비스를 운영했습니다.",
        ),
        (
            "배포",
            "Terraform으로 인프라를 만들고, GitHub Actions와 CodeDeploy를 통해 EC2에 배포했습니다.",
        ),
        (
            "전환 배경",
            "온프레미스에서 운영하던 서비스를 AWS로 옮기면서 EC2 기반 3-tier 구조를 선택했습니다.",
        ),
        (
            "운영 범위",
            "HTTPS, WAF, Redis, S3 미디어 저장까지 실제 서비스에 필요한 구성을 갖췄습니다.",
        ),
    ]
    positions = [(0.55, 1.25), (6.85, 1.25), (0.55, 4.15), (6.85, 4.15)]
    for (x, y), (title, body) in zip(positions, items):
        c = card(s, Inches(x), Inches(y), Inches(5.95), Inches(2.6), LIGHT)
        set_text(c.text_frame, title, 22, True, BLUE)
        add_para(c.text_frame, body, 18, False, NAVY, 12)
    footer(s, 2)


def slide_arch_v1(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "시스템 구성도  ·  Architecture V1", size=34)
    put_img(s, "hybrid_01_arch_v1_vpc.png")
    footer(s, 3)


def slide_v1_to_v2(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "V1의 한계  ·  V2에서 바꾼 점  ·  V2의 핵심", size=30)
    headers = [
        (0.4, RED, "V1의 한계"),
        (4.65, GREEN, "V2에서 바꾼 점"),
        (8.9, BLUE, "V2의 핵심"),
    ]
    for x, color, text in headers:
        h = card(s, Inches(x), Inches(1.05), Inches(4.05), Inches(0.65), color)
        set_text(h.text_frame, text, 20, True, WHITE, PP_ALIGN.CENTER)

    left = [
        ("상태를 한눈에 보기 어려움", "메트릭, 로그, 배포 상태가 흩어져 있어 문제를 찾는 데 시간이 걸렸습니다."),
        ("변경 반영이 느리고 복잡함", "앱과 인프라 변경이 EC2와 배포 에이전트에 묶여 있었습니다."),
        ("인스턴스 단위로만 확장", "작은 부하 변화에도 서버 단위로 늘려야 해 비용을 세밀하게 조절하기 어려웠습니다."),
    ]
    mid = [
        ("메트릭과 로그를 한곳에", "Prometheus, Alloy, Loki로 클러스터와 앱 상태를 함께 확인합니다."),
        ("커밋부터 배포까지 자동화", "이미지를 빌드하고 Git을 갱신하면 Argo CD가 변경 사항을 반영합니다."),
        ("노드와 파드를 따로 조절", "부하에 따라 파드를 늘리고, 사용하지 않을 때는 노드와 NAT를 중지합니다."),
    ]
    right = [
        ("통합 관측", "Prometheus·Loki·Tempo를 구성하고 AlertManager→Slack 알림까지 연결했습니다."),
        ("GitOps 배포", "Actions가 이미지를 올리고 태그를 바꾸면 Argo CD가 클러스터를 맞춥니다."),
        ("EKS + DB Pod", "앱과 DB를 Kubernetes에서 운영하고, 데이터는 PVC에 보관합니다."),
    ]
    for i, (t, b) in enumerate(left):
        accent_item(s, Inches(0.4), Inches(1.85) + i * Inches(1.65), Inches(4.05), Inches(1.5), RED, t, b)
    for i, (t, b) in enumerate(mid):
        accent_item(s, Inches(4.65), Inches(1.85) + i * Inches(1.65), Inches(4.05), Inches(1.5), GREEN, t, b)
    for i, (t, b) in enumerate(right):
        accent_item(s, Inches(8.9), Inches(1.85) + i * Inches(1.65), Inches(4.05), Inches(1.5), BLUE, t, b)
    footer(s, 4)


def slide_v2_def(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "Architecture V2")
    vision = card(s, Inches(0.55), Inches(1.15), Inches(12.2), Inches(1.45), LIGHT, BLUE)
    set_text(vision.text_frame, "비전", 20, True, BLUE)
    add_para(
        vision.text_frame,
        "EKS 위에서 같은 환경을 다시 만들 수 있도록 배포, 데이터 복구, 관측, 인증을 하나의 흐름으로 묶었습니다.",
        18,
        False,
        NAVY,
        8,
    )
    label = s.shapes.add_textbox(Inches(0.55), Inches(2.8), Inches(4), Inches(0.4))
    set_text(label.text_frame, "주요 기능", 20, True, BLACK)
    feats = [
        (BLUE, "ALB · HTTPS · WAF", "ACM으로 HTTPS를 적용하고, ALB 앞 WAF에서 공격 요청과 과도한 요청을 걸러냅니다."),
        (GREEN, "EKS web / db Pod", "Django·Daphne는 Deployment로, MariaDB는 StatefulSet과 PVC로 운영합니다."),
        (ORANGE, "Actions → ECR → Argo", "OIDC로 이미지를 올리고, Git의 이미지 태그를 기준으로 Argo CD가 배포합니다."),
        (PURPLE, "백업 · 관측", "DB는 S3에 백업하고, Prometheus·Loki·Tempo로 메트릭·로그·트레이스를 확인합니다."),
    ]
    for i, (color, title, body) in enumerate(feats):
        col, row = i % 2, i // 2
        x = Inches(0.55) + col * Inches(6.25)
        y = Inches(3.3) + row * Inches(1.7)
        card(s, x, y, Inches(6.0), Inches(1.5), SOFT)
        circle_icon(s, x + Inches(0.2), y + Inches(0.4), Inches(0.55), color)
        box = s.shapes.add_textbox(x + Inches(0.95), y + Inches(0.2), Inches(4.8), Inches(1.2))
        set_text(box.text_frame, title, 20, True, BLACK)
        add_para(box.text_frame, body, 17, False, GRAY, 8)
    footer(s, 5)


def slide_arch_v2(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "시스템 구성도  ·  Architecture V2", size=34)
    put_img(s, "hybrid_02_arch_v2_vpc.png")
    footer(s, 6)


def slide_v2_detail_1(prs):
    """V2 상세내용 ① — DB · 이미지 태그 · 시드 복구."""
    s = blank(prs)
    bg(s)
    title_center(s, "Architecture V2  ·  배포와 데이터")
    rows = [
        (
            "DB를 클러스터 안으로",
            "상시 RDS 비용을 줄이기 위해 MariaDB를 StatefulSet으로 운영하고, 데이터는 PVC에 저장했습니다.",
        ),
        (
            "배포 이미지도 Git으로 관리",
            "ECR에 sha-* 이미지를 올린 뒤 Helm의 태그를 갱신해, Git과 실제 배포 버전을 맞췄습니다.",
        ),
        (
            "인프라를 다시 만들어도 데이터 복구",
            "클러스터를 다시 만든 뒤 restore Job이 SQL을 불러와 서비스에 필요한 초기 데이터를 복원합니다.",
        ),
    ]
    for i, (a, b) in enumerate(rows):
        y = Inches(1.25) + i * Inches(1.75)
        c = card(s, Inches(0.55), y, Inches(12.2), Inches(1.55), LIGHT if i % 2 == 0 else SOFT)
        set_text(c.text_frame, a, 22, True, BLUE)
        add_para(c.text_frame, b, 18, False, NAVY, 10)
    footer(s, 7)


def slide_v2_detail_2(prs):
    """V2 상세내용 ② — Zero-Key · WAF · DNS 유지."""
    s = blank(prs)
    bg(s)
    title_center(s, "Architecture V2  ·  보안과 DNS")
    blocks = [
        (
            "장기 Access Key 미사용 (Zero-Key)",
            "OIDC(워크로드): 파드·CI에서 Access Key가 돌지 않도록 차단합니다. "
            "SSO(사람): 장기 키 없이 SSO 로그인으로 임시 자격증명만 받아 키 유출을 막습니다. "
            "결과: 장기 키를 최소화한 Zero-Key 구성으로 바꿨습니다. "
            "계정 접근이 제한되어 복구가 어려웠을 때 팀원 계정으로 이관하며 SSO·OIDC 기반으로 전환했습니다.",
        ),
        (
            "WAF로 ALB 앞단 보호",
            "관리형 웹 공격·악성 입력·SQLi 규칙과 IP별 5분 2,000회 요청 제한을 적용했습니다. 글쓰기 BODY 규칙은 오탐 방지를 위해 Count합니다.",
        ),
        (
            "클러스터를 지워도 도메인은 유지",
            "Route53 영역은 삭제 대상에서 제외해, 클러스터를 다시 만들어도 네임서버를 재등록하지 않습니다.",
        ),
    ]
    for i, (head, body) in enumerate(blocks):
        y = Inches(1.15) + i * Inches(1.85)
        c = card(s, Inches(0.55), y, Inches(12.2), Inches(1.7), LIGHT if i % 2 == 0 else SOFT)
        set_text(c.text_frame, head, 20, True, BLUE)
        add_para(c.text_frame, body, 15, False, NAVY, 6)
    footer(s, 8)


def slide_verify(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "기능 · 운영 검증 기준")
    note = s.shapes.add_textbox(Inches(0.55), Inches(0.95), Inches(12.2), Inches(0.35))
    set_text(
        note.text_frame,
        "확인 = 직접 검증 완료  ·  구성 = 스택 배포·연결까지 완료 (추가 시나리오 검증은 보완 과제)",
        14,
        False,
        GRAY,
        PP_ALIGN.CENTER,
    )
    items = [
        ("웹 · WAF", "HTTPS 응답 · Web ACL 연결", "curl · sampled requests", "구성"),
        ("DB 데이터", "복구 후 목록 데이터 표시", "테이블 수 · 시드 행", "확인"),
        ("GitOps", "Git 태그와 배포 이미지 일치", "Actions · Argo CD", "확인"),
        ("미디어", "재구축 후 이미지 정상 표시", "S3 media 경로", "확인"),
        ("관측", "메트릭·로그·트레이스 조회", "Prom · Loki · Tempo", "확인"),
        ("알림", "AlertManager 알림 수신", "Slack 채널", "확인"),
    ]
    for i, (t, check, method, result) in enumerate(items):
        col, row = i % 3, i // 3
        x = Inches(0.45) + col * Inches(4.25)
        y = Inches(1.4) + row * Inches(2.6)
        c = card(s, x, y, Inches(4.05), Inches(2.4), LIGHT)
        set_text(c.text_frame, t, 20, True, BLUE)
        add_para(c.text_frame, check, 16, False, NAVY, 8)
        add_para(c.text_frame, "방법: " + method, 15, False, GRAY, 6)
        add_para(c.text_frame, result, 17, True, GREEN if result == "확인" else ORANGE, 8)
    footer(s, 9)


def slide_stack(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "기술 스택  ·  Architecture V2", size=34)
    put_img(s, "hybrid_09_tech_stack.png")
    footer(s, 10)


def slide_data_flow(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "데이터 흐름  ·  Architecture V2", size=34)
    put_img(s, "hybrid_10_data_flow.png")
    footer(s, 11)


def slide_next(prs):
    s = blank(prs)
    bg(s)
    title_center(s, "앞으로 보완할 점")
    cols = [
        (
            ORANGE,
            "운영 고도화",
            "보안 · 복구 · 비용",
            [
                "OIDC 권한 범위 최소화",
                "정기 백업·복구 훈련 (S3 덤프 복구 경로 포함)",
                "반복 장애 자동 복구(AIOps)",
                "노드·NAT 중지·상시 RDS 제거로 비용 절감 유지",
            ],
        ),
        (
            GREEN,
            "완성도",
            "관측 성과 위에 남은 과제",
            [
                "시드 검증·운영 런북 자동화",
                "계정 이관 체크리스트 정리",
                "부하 병목(/works 지연)·Redis Timeout 해소",
                "Tempo로 찾은 병목을 성능 개선으로 연결",
            ],
        ),
    ]
    for i, (color, title, sub, lines) in enumerate(cols):
        x = Inches(0.9) + i * Inches(6.0)
        head = card(s, x, Inches(1.2), Inches(5.5), Inches(1.0), color)
        set_text(head.text_frame, title, 22, True, WHITE, PP_ALIGN.CENTER)
        add_para(head.text_frame, sub, 15, False, WHITE, 2, PP_ALIGN.CENTER)
        body = card(s, x, Inches(2.4), Inches(5.5), Inches(4.0), LIGHT)
        body.text_frame.clear()
        pad(body.text_frame)
        first = True
        for line in lines:
            if first:
                set_text(body.text_frame, "·  " + line, 17, False, NAVY)
                first = False
            else:
                add_para(body.text_frame, "·  " + line, 17, False, NAVY, 14)
    footer(s, 12)


def slide_load_trace(prs):
    """부하테스트 + Tempo 트레이싱 성과."""
    s = blank(prs)
    bg(s)
    title_center(s, "부하테스트 · 트레이싱으로 본 병목")
    cards = [
        (
            GREEN,
            "확인한 성과",
            [
                "HPA로 web 파드 2 → 4 확장 확인",
                "Tempo/OTel로 요청 구간 수집·조회",
                "AlertManager → Slack 알림 수신",
            ],
        ),
        (
            ORANGE,
            "발견한 병목",
            [
                "/works/ 응답 최대 약 2.91초",
                "Tempo 트레이스로 구간 병목 위치 확인",
                "WAF RateLimit에 걸려 차단된 구간도 확인",
            ],
        ),
        (
            RED,
            "남은 과제",
            [
                "Redis TimeoutError는 미해결",
                "병목 구간 쿼리·캐시 최적화",
                "부하 시나리오와 WAF 한도 정합",
            ],
        ),
    ]
    for i, (color, title, lines) in enumerate(cards):
        x = Inches(0.4) + i * Inches(4.3)
        head = card(s, x, Inches(1.2), Inches(4.1), Inches(0.7), color)
        set_text(head.text_frame, title, 20, True, WHITE, PP_ALIGN.CENTER)
        body = card(s, x, Inches(2.05), Inches(4.1), Inches(4.4), LIGHT)
        body.text_frame.clear()
        pad(body.text_frame)
        first = True
        for line in lines:
            if first:
                set_text(body.text_frame, "·  " + line, 16, False, NAVY)
                first = False
            else:
                add_para(body.text_frame, "·  " + line, 16, False, NAVY, 14)
    footer(s, 13)


def slide_trouble(prs, n, title, rows):
    """3건. rows: (제목, 한 줄 설명)."""
    s = blank(prs)
    bg(s)
    title_center(s, title, size=32)
    for i, (head, body) in enumerate(rows):
        y = Inches(1.15) + i * Inches(1.9)
        c = card(s, Inches(0.45), y, Inches(12.4), Inches(1.75), LIGHT if i % 2 == 0 else SOFT)
        set_text(c.text_frame, head, 20, True, BLUE)
        add_para(c.text_frame, body, 16, False, NAVY, 8)
    footer(s, n)


def slide_trouble_gitops(prs):
    slide_trouble(
        prs,
        14,
        "트러블슈팅  ·  GitOps · CI/CD",
        [
            (
                "중지 작업은 성공했지만 워커가 계속 실행됨",
                "desired만 0으로 바꾸자 Autoscaler가 노드를 다시 만들었습니다. ASG의 Launch를 중지하고 인스턴스 0대까지 확인한 뒤 NAT도 함께 껐습니다.",
            ),
            (
                "Argo CD에서 리소스가 계속 Missing으로 표시됨",
                "이전에 사용한 ServerSideApply 설정이 남아 상태 비교를 막고 있었습니다. 해당 옵션을 제거하고 일반 apply 방식으로 다시 동기화했습니다.",
            ),
            (
                "DB 복구 워크플로는 성공했지만 목록이 비어 있음",
                "테이블 수만 확인해 빈 스키마도 복구된 것으로 처리했습니다. 시드 행이 1개 이상일 때만 성공하도록 검증 기준을 바꿨습니다.",
            ),
        ],
    )


def slide_trouble_eks(prs):
    slide_trouble(
        prs,
        15,
        "트러블슈팅  ·  EKS",
        [
            (
                "HPA가 늘린 replicas가 1로 되돌아감 (9/15)",
                "deployment.yaml의 replicas: 1이 CI 재배포마다 HPA 값을 덮었습니다. replicas 필드를 제거하고 HPA만 관리하도록 바꿨습니다. 한 필드는 하나의 제어 주체만 두어야 합니다.",
            ),
            (
                "이관 중 Terraform 리소스 생성 순서 문제 (9/22)",
                "기존 환경에 가려진 의존성이 빈 계정에서 드러났습니다. NAT·프라이빗 라우팅을 먼저 만들도록 순서를 재배치했습니다. 이관 시에는 전체 생성 테스트가 필요합니다.",
            ),
            (
                "기존 DB 비밀번호가 약한 기본값일 가능성 (9/29)",
                "ESO 전환 시 약한 폴백 값을 그대로 옮길 위험이 있었습니다. 난수로 ALTER USER·Secrets Manager를 함께 갱신했습니다. 체계만 옮기지 말고 값의 안전성도 점검해야 합니다.",
            ),
        ],
    )


def slide_trouble_observe(prs):
    slide_trouble(
        prs,
        16,
        "트러블슈팅  ·  DB · 관측",
        [
            (
                "S3에 올라간 DB 백업 파일이 0바이트",
                "외부 컨테이너에서 DB에 연결하지 못하고 있었습니다. CronJob이 DB 파드 안에서 mariadb-dump를 실행하도록 바꿨습니다.",
            ),
            (
                "Alloy가 일부 노드에서 실행되지 않음",
                "노드당 파드 한도 17개를 넘긴 것이 원인이었습니다. max-pods를 높이고 노드를 다시 만들어 정상화했습니다.",
            ),
            (
                "AlertManager 알림이 Slack에 오지 않음",
                "웹훅 시크릿이 AlertManager 파드에 연결되지 않았습니다. 시크릿을 마운트하고 api_url_file로 읽도록 수정했습니다.",
            ),
        ],
    )


def slide_schedule(prs):
    s = blank(prs)
    bg(s)
    path = BASE / "images" / "v2_schedule_by_day.png"
    s.shapes.add_picture(str(path), Inches(0), Inches(0), width=Inches(SW), height=Inches(SH))


def slide_roles(prs):
    """팀 역할분담 — Q&A에서 분리한 전용 장."""
    s = blank(prs)
    bg(s)
    title_center(s, "팀 역할분담", size=34)
    put_img(s, "hybrid_00_roles.png", top=Inches(0.95), bottom=Inches(7.05))
    footer(s, 18)


def slide_qa(prs):
    s = blank(prs)
    bg(s, NAVY)
    box = s.shapes.add_textbox(Inches(0.8), Inches(2.4), Inches(11.7), Inches(1.2))
    set_text(box.text_frame, "Q & A", 54, True, WHITE, PP_ALIGN.CENTER)
    sub = s.shapes.add_textbox(Inches(0.8), Inches(3.8), Inches(11.7), Inches(0.6))
    set_text(
        sub.text_frame,
        "감사합니다  ·  Aniverse Architecture V1 → V2",
        22,
        False,
        RGBColor(191, 219, 254),
        PP_ALIGN.CENTER,
    )
    team = s.shapes.add_textbox(Inches(0.8), Inches(4.8), Inches(11.7), Inches(0.5))
    set_text(
        team.text_frame,
        "김현우  ·  박서이  ·  김윤주  ·  강유민",
        18,
        False,
        RGBColor(226, 232, 240),
        PP_ALIGN.CENTER,
    )
    num = s.shapes.add_textbox(Inches(11.3), Inches(7.15), Inches(1.5), Inches(0.28))
    set_text(num.text_frame, f"19 / {TOTAL}", 12, False, RGBColor(148, 163, 184), PP_ALIGN.RIGHT)


def main():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)

    slide_cover(prs)
    slide_v1_def(prs)
    slide_arch_v1(prs)
    slide_v1_to_v2(prs)
    slide_v2_def(prs)
    slide_arch_v2(prs)
    slide_v2_detail_1(prs)
    slide_v2_detail_2(prs)
    slide_verify(prs)
    slide_stack(prs)
    slide_data_flow(prs)
    slide_next(prs)
    slide_load_trace(prs)
    slide_trouble_gitops(prs)
    slide_trouble_eks(prs)
    slide_trouble_observe(prs)
    slide_schedule(prs)
    slide_roles(prs)
    slide_qa(prs)

    out = next_path()
    prs.save(out)
    shutil.copy2(out, WORKING)
    print(f"Wrote {out} and {WORKING} ({TOTAL} slides)")


if __name__ == "__main__":
    main()
