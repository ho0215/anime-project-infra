#!/usr/bin/env python3
"""하이브리드 발표 PPT — 프로젝트 소개 + EKS 전환 + 윤주(관측/DB) 반영.

구조도는 images/hybrid/*.png (AI 생성) 사용.
출력: ppt/Aniverse_하이브리드_EKS_vN.pptx (생성할 때마다 버전 +1)
"""
from pathlib import Path
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from PIL import Image

FONT_NAME = "맑은 고딕"
BASE = Path(__file__).resolve().parent
IMG = BASE / "images" / "hybrid"
OUT = BASE / "ppt"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = RGBColor(15, 23, 42)
WHITE = RGBColor(255, 255, 255)
SLATE = RGBColor(71, 85, 105)
BLUE = RGBColor(37, 99, 235)
LIGHT = RGBColor(248, 250, 252)
TEAL = RGBColor(13, 148, 136)
GREEN = RGBColor(22, 163, 74)
ORANGE = RGBColor(234, 88, 12)
SOFT = RGBColor(239, 246, 255)

TOTAL = 18
STEM = "Aniverse_하이브리드_EKS"


def next_version_path() -> Path:
    """ppt/Aniverse_하이브리드_EKS_vN.pptx — 기존 최대 N+1, 없으면 v1."""
    best = 0
    for p in OUT.glob(f"{STEM}_v*.pptx"):
        m = re.search(r"_v(\d+)\.pptx$", p.name)
        if m:
            best = max(best, int(m.group(1)))
    return OUT / f"{STEM}_v{best + 1}.pptx"


def font(run, size=16, bold=False, color=NAVY):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = FONT_NAME
    rPr = run._r.get_or_add_rPr()
    for tag in ("latin", "ea", "cs"):
        el = rPr.find(qn(f"a:{tag}"))
        if el is None:
            el = rPr.makeelement(qn(f"a:{tag}"), {})
            rPr.append(el)
        el.set("typeface", FONT_NAME)


def pad_tf(tf, left=0.1, top=0.06, right=0.1, bottom=0.06):
    tf.word_wrap = True
    tf.margin_left = Inches(left)
    tf.margin_right = Inches(right)
    tf.margin_top = Inches(top)
    tf.margin_bottom = Inches(bottom)


def set_text(tf, text, size=16, bold=False, color=NAVY, align=None):
    tf.clear()
    pad_tf(tf)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    font(r, size, bold, color)
    if align is not None:
        p.alignment = align


def add_para(tf, text, size=14, bold=False, color=NAVY, space_before=6):
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = text
    font(r, size, bold, color)
    p.space_before = Pt(space_before)
    return p


def rect(slide, x, y, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    pad_tf(sh.text_frame)
    return sh


def header(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.82))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    box = slide.shapes.add_textbox(Inches(0.4), Inches(0.1), Inches(12.5), Inches(0.65))
    tf = box.text_frame
    set_text(tf, title, 20, True, WHITE)
    if subtitle:
        add_para(tf, subtitle, 11, False, RGBColor(147, 197, 253), 1)


def footer(slide, n):
    tx = slide.shapes.add_textbox(Inches(0.4), Inches(7.05), Inches(12.5), Inches(0.28))
    p = tx.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"Aniverse · 프로젝트 + EKS 전환   |   {n}/{TOTAL}"
    font(r, 10, False, SLATE)
    p.alignment = PP_ALIGN.RIGHT


def put_img(slide, name, x, y, w=None, max_bottom=Inches(6.95)):
    path = IMG / name
    if not path.exists():
        return False
    iw, ih = Image.open(path).size
    aspect = ih / float(iw)
    x_in, y_in = x.inches, y.inches
    max_h = max_bottom.inches - y_in
    if w is not None:
        w_in = w.inches
        h_in = w_in * aspect
    else:
        w_in = 12.5
        h_in = w_in * aspect
    if h_in > max_h:
        h_in = max_h
        w_in = h_in / aspect
        box_w = w.inches if w is not None else 12.5
        if w_in < box_w:
            x_in += (box_w - w_in) / 2.0
    slide.shapes.add_picture(str(path), Inches(x_in), Inches(y_in), width=Inches(w_in), height=Inches(h_in))
    return True


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def cover(prs):
    s = blank(prs)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    t = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(12), Inches(4))
    tf = t.text_frame
    set_text(tf, "Aniverse", 42, True, WHITE)
    add_para(tf, "프로젝트 소개 + EKS · GitOps 전환", 24, False, RGBColor(191, 219, 254), 14)
    add_para(tf, "EC2 / CodeDeploy → EKS / Argo CD · DB Pod · 관측", 15, False, RGBColor(147, 197, 253), 14)
    add_para(tf, "https://aniverse.my", 14, False, RGBColor(125, 211, 252), 18)
    add_para(tf, "발표 5~7분 · 하이브리드 구성", 12, False, RGBColor(148, 163, 184), 20)


def agenda(prs):
    s = blank(prs)
    header(s, "목차", "프로젝트 소개 → EKS 전환 → 데이터·관측 → 트러블 → 교훈")
    items = [
        "01  서비스 · 팀 역할",
        "02  As-Is 전체구조 · To-Be · 왜 EKS",
        "03  랩 → EKS 경로 · 워크로드",
        "04  GitOps · 데이터 백업/복구",
        "05  관측 (Prom / Grafana / Loki)",
        "06  전환 이슈 · 계정 Block / 이관",
        "07  Before/After · 다음",
    ]
    for i, title in enumerate(items):
        y = Inches(1.05) + i * Inches(0.78)
        card = rect(s, Inches(0.7), y, Inches(11.9), Inches(0.68), LIGHT, BLUE)
        set_text(card.text_frame, title, 16, True, NAVY)
    footer(s, 2)


def service(prs):
    s = blank(prs)
    header(s, "1. Aniverse — 무엇을 만들었나", "서브컬처 커뮤니티 · 거래 · 창작")
    cards = [
        ("서비스", ["장터(굿즈) · 창작 마당", "커뮤니티 · 회원", "https://aniverse.my"]),
        ("인프라 목표", ["재현 가능한 배포", "비용 통제 (start/stop)", "문서·트러블슈팅"]),
        ("이번 발표 포인트", ["프로젝트 전체 구조", "EKS·GitOps 전환", "DB Pod · 관측 · 이관"]),
    ]
    colors = [BLUE, TEAL, ORANGE]
    for i, (title, lines) in enumerate(cards):
        x = Inches(0.5) + i * Inches(4.15)
        card = rect(s, x, Inches(1.2), Inches(3.95), Inches(5.2), LIGHT, colors[i])
        set_text(card.text_frame, title, 18, True, colors[i])
        for line in lines:
            add_para(card.text_frame, "· " + line, 14, False, NAVY, 12)
    footer(s, 3)


def roles(prs):
    s = blank(prs)
    header(s, "1. 팀 역할", "윤주=컨테이너·DB·관측 / 현우=Actions·Argo / 네트워크·컴퓨트")
    if not put_img(s, "hybrid_00_roles.png", Inches(0.35), Inches(0.95), w=Inches(12.6)):
        tip = rect(s, Inches(0.5), Inches(1.2), Inches(12.3), Inches(5), LIGHT, BLUE)
        set_text(tip.text_frame, "역할 이미지 없음 — images/hybrid/hybrid_00_roles.png", 14, False, SLATE)
    footer(s, 4)


def asis_overview(prs):
    s = blank(prs)
    header(
        s,
        "2. As-Is (1) — 전체 구조",
        "User → ALB → ASG/EC2(Nginx+Django) → RDS · EFS · S3",
    )
    put_img(s, "hybrid_01_asis_overview.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 5)


def asis_flow(prs):
    s = blank(prs)
    header(
        s,
        "2. As-Is (2) — 요청 · 배포가 흐르는 방식",
        "상단: 트래픽 경로 · 하단: Actions → CodeDeploy → EC2",
    )
    put_img(s, "hybrid_01_asis_flow.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 6)


def tobe(prs):
    s = blank(prs)
    header(s, "2. To-Be (v2 EKS)", "Ingress/ALB · Pod · DB StatefulSet · ECR · Argo GitOps")
    put_img(s, "hybrid_02_tobe.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 7)


def why_eks(prs):
    s = blank(prs)
    header(s, "2. 왜 EKS · DB Pod 인가", "멘토링·비용·동작 확인 우선")
    rows = [
        ("배포·재현", "이미지 + GitOps로 동일 환경 재현"),
        ("스케일", "노드 스케일 + 파드 HPA를 분리해 설계"),
        ("DB Pod", "RDS 상시 비용 대신 StatefulSet+PVC (학습/2차)"),
        ("원칙", "아키텍처 확정 → 동작 확인 → 관측·보안 고도화"),
    ]
    for i, (t, b) in enumerate(rows):
        y = Inches(1.15) + i * Inches(1.3)
        card = rect(s, Inches(0.6), y, Inches(12.1), Inches(1.15), SOFT, TEAL)
        set_text(card.text_frame, t, 16, True, TEAL)
        add_para(card.text_frame, b, 14, False, NAVY, 8)
    footer(s, 8)


def migration(prs):
    s = blank(prs)
    header(s, "3. 랩 → EKS 전환 경로", "Compose → Lab K8s(Helm) → EKS + Argo")
    put_img(s, "hybrid_03_migration_path.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 9)


def workloads(prs):
    s = blank(prs)
    header(s, "3. 앱 · DB 워크로드", "윤주: Docker · Helm · StatefulSet — EKS에서 web/db 1/1")
    put_img(s, "hybrid_04_workloads.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 10)


def gitops(prs):
    s = blank(prs)
    header(s, "4. GitOps · CI/CD", "Actions → ECR(sha-*) → values bump → Argo sync · OIDC")
    put_img(s, "hybrid_05_gitops.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 11)


def data(prs):
    s = blank(prs)
    header(s, "4. 데이터 — 백업 · 복구", "윤주: restore Job · CronJob → S3 db-backups/ · media는 S3 sync")
    put_img(s, "hybrid_06_data.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 12)


def observability(prs):
    s = blank(prs)
    header(s, "5. 관측", "완료: Prom+Grafana · Loki/Alloy 구성 — 예정: AlertManager · Tempo/OTel")
    put_img(s, "hybrid_07_observability.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 13)


def ops(prs):
    s = blank(prs)
    header(s, "5. 운영 포인트", "HTTPS · DNS · 비용 start/stop")
    items = [
        ("HTTPS", "ACM ISSUED 후 Ingress ALB · Route53"),
        ("비용", "EKS start/stop — 미사용 시 노드·NAT 절감"),
        ("보안", "장기 Access Key 금지 · GitHub OIDC · Pod S3 IRSA"),
        ("검증", "health 200 + 시드/목록 UI (Actions 초록만으로 끝내지 않음)"),
    ]
    for i, (t, b) in enumerate(items):
        col, row = i % 2, i // 2
        x = Inches(0.5) + col * Inches(6.3)
        y = Inches(1.2) + row * Inches(2.6)
        card = rect(s, x, y, Inches(6.05), Inches(2.35), LIGHT, BLUE)
        set_text(card.text_frame, t, 18, True, BLUE)
        add_para(card.text_frame, b, 14, False, NAVY, 14)
    footer(s, 14)


def issue_tech(prs):
    s = blank(prs)
    header(s, "6. 전환 이슈 — 기술", "같은 Missing이라도 원인이 둘")
    left = rect(s, Inches(0.45), Inches(1.15), Inches(6.1), Inches(5.4), LIGHT, ORANGE)
    set_text(left.text_frame, "A. Job sync-wave", 18, True, ORANGE)
    for line in [
        "Ingress가 ALB ADDRESS 전 Progressing",
        "다음 wave Job이 영구 Missing",
        "조치: Job에 높은 wave 금지",
        "DB ready는 Job 내부 ping",
    ]:
        add_para(left.text_frame, "· " + line, 13, False, NAVY, 10)
    right = rect(s, Inches(6.75), Inches(1.15), Inches(6.1), Inches(5.4), LIGHT, TEAL)
    set_text(right.text_frame, "B. ServerSideApply", 18, True, TEAL)
    for line in [
        "terminatingReplicas ComparisonError",
        "live SSA 잔존 시 재발",
        "조치: SSA 제거 · client-side apply",
        "install 후 syncOptions strip",
    ]:
        add_para(right.text_frame, "· " + line, 13, False, NAVY, 10)
    footer(s, 15)


def issue_account(prs):
    s = blank(prs)
    header(s, "6. 계정 Block → 이관", "표면은 start 실패 · 근본은 키 유출")
    put_img(s, "hybrid_08_account.png", Inches(0.35), Inches(0.95), w=Inches(12.6))
    footer(s, 16)


def before_after(prs):
    s = blank(prs)
    header(s, "7. Before / After", "v1 EC2 운영 → v2 EKS GitOps")
    left = rect(s, Inches(0.45), Inches(1.2), Inches(6.1), Inches(5.3), LIGHT, SLATE)
    set_text(left.text_frame, "Before (v1)", 18, True, SLATE)
    for line in [
        "EC2 + CodeDeploy",
        "RDS MariaDB",
        "수동·에이전트 배포",
        "환경 재현 어려움",
    ]:
        add_para(left.text_frame, "· " + line, 14, False, NAVY, 12)
    right = rect(s, Inches(6.75), Inches(1.2), Inches(6.1), Inches(5.3), SOFT, GREEN)
    set_text(right.text_frame, "After (v2)", 18, True, GREEN)
    for line in [
        "EKS + Argo CD",
        "DB Pod + PVC · SQL/CronJob 백업",
        "Actions → ECR → GitOps",
        "Prom/Grafana · Loki 관측",
    ]:
        add_para(right.text_frame, "· " + line, 14, False, NAVY, 12)
    footer(s, 17)


def closing(prs):
    s = blank(prs)
    header(s, "7. 배운 점 · 다음", "하이브리드 발표 마무리")
    lessons = [
        ("배운 점", [
            "아키텍처 확정 후 동작 확인이 1순위",
            "장기 키 금지 → OIDC · 이관 시 ARN 전수 교체",
            "Actions 초록 ≠ 시드/목록 검증",
        ]),
        ("다음", [
            "Loki/Alloy EKS 반영 · AlertManager",
            "Tempo + Django OpenTelemetry",
            "OIDC 권한 축소 · Budgets",
        ]),
    ]
    for i, (title, lines) in enumerate(lessons):
        x = Inches(0.5) + i * Inches(6.3)
        card = rect(s, x, Inches(1.2), Inches(6.05), Inches(5.3), LIGHT, BLUE if i == 0 else TEAL)
        set_text(card.text_frame, title, 18, True, BLUE if i == 0 else TEAL)
        for line in lines:
            add_para(card.text_frame, "· " + line, 14, False, NAVY, 14)
    footer(s, 18)


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    cover(prs)
    agenda(prs)
    service(prs)
    roles(prs)
    asis_overview(prs)
    asis_flow(prs)
    tobe(prs)
    why_eks(prs)
    migration(prs)
    workloads(prs)
    gitops(prs)
    data(prs)
    observability(prs)
    ops(prs)
    issue_tech(prs)
    issue_account(prs)
    before_after(prs)
    closing(prs)

    out = next_version_path()
    prs.save(out)
    print(f"Wrote {out} ({TOTAL} slides)")


if __name__ == "__main__":
    main()