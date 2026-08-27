#!/usr/bin/env python3
"""
강사 만족용 5~7분 발표 PPT
주제: 온프레미스 3-tier → AWS
기준: 청중이 '왜 중요한지' 바로 이해
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt, Emu

OUT = Path(__file__).resolve().parent / "ppt"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = RGBColor(15, 23, 42)
WHITE = RGBColor(255, 255, 255)
SLATE = RGBColor(71, 85, 105)
BLUE = RGBColor(37, 99, 235)
LIGHT = RGBColor(248, 250, 252)
PURPLE = RGBColor(124, 58, 237)
ORANGE = RGBColor(234, 88, 12)
GREEN = RGBColor(22, 163, 74)
RED = RGBColor(220, 38, 38)
TEAL = RGBColor(13, 148, 136)
AMBER = RGBColor(217, 119, 6)
SOFT = RGBColor(239, 246, 255)


def font(run, size=16, bold=False, color=NAVY):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Malgun Gothic"


def set_text(shape_or_tf, text, size=16, bold=False, color=NAVY, align=None):
    tf = shape_or_tf if hasattr(shape_or_tf, "paragraphs") else shape_or_tf.text_frame
    tf.clear()
    tf.word_wrap = True
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
        sh.line.width = Pt(1.75)
    else:
        sh.line.fill.background()
    return sh


def header(slide, title, why):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.95))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    box = slide.shapes.add_textbox(Inches(0.45), Inches(0.12), Inches(12.4), Inches(0.75))
    tf = box.text_frame
    set_text(tf, title, 22, True, WHITE)
    add_para(tf, f"왜 중요한가: {why}", 12, False, RGBColor(147, 197, 253), 2)


def footer(slide, n, total=11):
    tx = slide.shapes.add_textbox(Inches(0.45), Inches(7.05), Inches(12.4), Inches(0.3))
    p = tx.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"Aniverse · 온프레미스 3-tier → AWS   |   {n}/{total}   |   발표 5~7분"
    font(r, 10, False, SLATE)
    p.alignment = PP_ALIGN.RIGHT


def cover(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    t = s.shapes.add_textbox(Inches(0.7), Inches(1.8), Inches(12), Inches(3.5))
    tf = t.text_frame
    set_text(tf, "Aniverse", 40, True, WHITE)
    add_para(tf, "온프레미스 3-tier 서비스를 AWS로 이전한 이야기", 22, False, RGBColor(191, 219, 254), 14)
    add_para(tf, "인프라 코드화 · 자동 배포 · 보안 · 운영 안정성", 16, False, RGBColor(147, 197, 253), 18)
    add_para(tf, "발표 5~7분  |  https://aniverse.my", 14, False, RGBColor(125, 211, 252), 24)
    return s


def agenda(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "목차", "오늘 발표가 ‘무엇을 해결했는지’ 흐름으로 따라갈 수 있게")
    items = [
        ("01", "AWS 이전, 맡은 역할 한눈에", "누가 무엇을 책임졌는지"),
        ("02", "온프레미스에서 어려웠던 점", "왜 옮겨야 했는지"),
        ("03", "Terraform으로 구성한 인프라", "재현 가능한 설계"),
        ("04", "GitHub Actions 사용", "사람 손 없이 배포"),
        ("05", "CI/CD · HA · 모니터링 · 보안", "서비스가 버티는 이유"),
    ]
    for i, (num, title, why) in enumerate(items):
        y = Inches(1.25) + i * Inches(1.05)
        card = rect(s, Inches(0.6), y, Inches(12.1), Inches(0.9), LIGHT, BLUE)
        tf = card.text_frame
        set_text(tf, f"{num}  {title}", 18, True, NAVY)
        add_para(tf, why, 13, False, SLATE, 4)
    footer(s, 2)
    return s


def roles(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "1. AWS 이전 — 맡은 역할 한눈에", "역할이 나뉘면 장애·배포 책임이 명확해진다")
    roles = [
        ("박서이", "Network & Security", "VPC · SG · NAT", "외부/내부 망을 갈라\n사고 범위를 줄임", PURPLE),
        ("강유민", "Compute & Traffic", "ALB · ASG · EC2", "트래픽을 안정적으로\n앱 서버에 전달", ORANGE),
        ("김윤주", "Data & Storage", "RDS · EFS · S3", "데이터·파일을\n안전하게 보관", GREEN),
        ("김현우", "DevOps & CI/CD", "Terraform 조립\nActions · CodeDeploy", "변경이 자동으로\n안전하게 반영", RED),
    ]
    for i, (name, role, mods, why, color) in enumerate(roles):
        x = Inches(0.35) + i * Inches(3.2)
        card = rect(s, x, Inches(1.3), Inches(3.05), Inches(5.1), LIGHT, color)
        tf = card.text_frame
        set_text(tf, name, 18, True, color, PP_ALIGN.CENTER)
        add_para(tf, role, 13, True, NAVY, 8)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        add_para(tf, mods, 12, False, SLATE, 10)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        add_para(tf, "────────", 11, False, RGBColor(203, 213, 225), 10)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        add_para(tf, why, 13, False, NAVY, 6)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
    footer(s, 3)
    return s


def onprem_pain(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "2. 온프레미스에서 어려웠던 점", "같은 문제가 반복되면 서비스·학습 모두 멈춘다")
    pains = [
        ("수동 배포", "서버 4대에 직접 접속해\n설정·재시작", "실수 한 번에\n전체 서비스 영향"),
        ("환경 불일치", "내 PC OK / 서버 NG\n설정이 사람 기억에 의존", "원인 찾기에\n시간 대부분 소비"),
        ("확장·복구 어려움", "트래픽·장애 시\n서버를 손으로 늘림", "밤샘 대응,\n재현 불가"),
        ("보안·비밀키 관리", ".env / 키 파일\n서버에 흩어짐", "유출·권한 사고\n리스크"),
    ]
    for i, (t, how, why) in enumerate(pains):
        x = Inches(0.4) + (i % 2) * Inches(6.4)
        y = Inches(1.3) + (i // 2) * Inches(2.6)
        card = rect(s, x, y, Inches(6.1), Inches(2.35), LIGHT, RED)
        tf = card.text_frame
        set_text(tf, t, 18, True, RED)
        add_para(tf, how, 14, False, NAVY, 8)
        add_para(tf, f"→ 청중 관점: {why}", 13, True, SLATE, 10)
    footer(s, 4)
    return s


def terraform(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "3. Terraform으로 구성한 인프라", "코드로 남기면 ‘누가 서버를 어떻게 만들었는지’ 설명 가능")
    # left flow
    left = rect(s, Inches(0.4), Inches(1.25), Inches(6.2), Inches(5.3), SOFT, BLUE)
    tf = left.text_frame
    set_text(tf, "구성 한눈에 (3-tier → AWS)", 16, True, BLUE)
    lines = [
        "① Network: VPC · Public/Private · NAT · SG",
        "② Traffic: ALB (+ HTTPS/ACM) · Target Group",
        "③ Compute: ASG · EC2 (Nginx + Daphne)",
        "④ Data: RDS MariaDB · EFS · S3",
        "⑤ Ops: Secrets · WAF · Redis · CodeDeploy",
        "",
        "모듈을 나눠 만들고 → environments/dev 에서 조립",
    ]
    for line in lines:
        add_para(tf, line, 14, False, NAVY, 6)
    # right why
    right = rect(s, Inches(6.9), Inches(1.25), Inches(5.9), Inches(5.3), LIGHT, TEAL)
    tf = right.text_frame
    set_text(tf, "청중에게 중요한 점", 16, True, TEAL)
    for line in [
        "• 문서가 아니라 ‘실행 가능한 설계도’",
        "• 팀원 모듈을 합쳐도 충돌을 줄임",
        "• 다시 만들어도 같은 구조가 나옴",
        "• 리뷰(PR)로 인프라 변경을 검증",
        "",
        "결과",
        "서버를 ‘기억’이 아니라",
        "코드로 운영하게 됨",
    ]:
        add_para(tf, line, 14, False, NAVY, 7)
    footer(s, 5)
    return s


def github_actions(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "4. GitHub Actions로 한 일", "버튼/접속 없이, push가 배포의 시작이 된다")
    # pipeline boxes
    steps = [
        ("push", "main 반영"),
        ("Checks", "포맷·검증"),
        ("Artifact", "zip / plan"),
        ("Deploy", "Apply/\nCodeDeploy"),
        ("Live", "aniverse.my"),
    ]
    for i, (a, b) in enumerate(steps):
        x = Inches(0.45) + i * Inches(2.5)
        card = rect(s, x, Inches(1.4), Inches(2.25), Inches(1.7), LIGHT, BLUE)
        tf = card.text_frame
        set_text(tf, a, 16, True, BLUE, PP_ALIGN.CENTER)
        add_para(tf, b, 13, False, NAVY, 8)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        if i < 4:
            ar = s.shapes.add_textbox(x + Inches(2.15), Inches(1.95), Inches(0.4), Inches(0.4))
            set_text(ar.text_frame, "→", 20, True, SLATE, PP_ALIGN.CENTER)

    box = rect(s, Inches(0.45), Inches(3.5), Inches(12.4), Inches(2.9), SOFT, TEAL)
    tf = box.text_frame
    set_text(tf, "두 갈래 자동화", 16, True, TEAL)
    add_para(tf, "① anime-project-infra  →  Terraform apply  (인프라)", 15, False, NAVY, 10)
    add_para(tf, "② anime-project        →  S3 zip → CodeDeploy  (앱)", 15, False, NAVY, 8)
    add_para(tf, "왜 중요한가: ‘배포 방법’이 사람마다 다르지 않고, 기록이 Actions 로그에 남는다", 14, True, SLATE, 14)
    footer(s, 6)
    return s


def cicd_ha(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "5-1. CI/CD · 고가용성", "배포가 잦아도, 서비스는 멈추지 않아야 한다")
    left = rect(s, Inches(0.4), Inches(1.3), Inches(6.1), Inches(5.2), LIGHT, BLUE)
    tf = left.text_frame
    set_text(tf, "CI/CD", 18, True, BLUE)
    for line in [
        "• Infra: plan → apply 자동화",
        "• App: CodeDeploy → ASG",
        "• /health/ 로 배포 성공 판정",
        "• 실패 시 로그로 원인 추적",
        "",
        "청중 포인트",
        "‘누가 배포했는가’보다",
        "‘항상 같은 방식으로 배포’",
    ]:
        add_para(tf, line, 14, False, NAVY, 6)

    right = rect(s, Inches(6.8), Inches(1.3), Inches(6.1), Inches(5.2), LIGHT, ORANGE)
    tf = right.text_frame
    set_text(tf, "고가용성 (HA)", 18, True, ORANGE)
    for line in [
        "• ALB: 한 대로 트래픽 분산",
        "• ASG: 인스턴스 교체·확장",
        "• Multi-subnet 배치",
        "• EFS: 여러 EC2가 파일 공유",
        "",
        "청중 포인트",
        "서버 1대가 죽어도",
        "사이트가 ‘전부 다운’되지 않음",
    ]:
        add_para(tf, line, 14, False, NAVY, 6)
    footer(s, 7)
    return s


def monitor_security(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "5-2. 모니터링 · 보안", "문제가 ‘늦게’ 보이면 이미 사용자 피해다")
    left = rect(s, Inches(0.4), Inches(1.3), Inches(6.1), Inches(5.2), LIGHT, TEAL)
    tf = left.text_frame
    set_text(tf, "모니터링", 18, True, TEAL)
    for line in [
        "• CloudWatch 알람",
        "• ALB / Target 상태 확인",
        "• SSM으로 서버 접속·점검",
        "• 배포·장애 로그 추적",
        "",
        "청중 포인트",
        "장애를 ‘느낌’이 아니라",
        "지표로 먼저 알게 됨",
    ]:
        add_para(tf, line, 14, False, NAVY, 6)

    right = rect(s, Inches(6.8), Inches(1.3), Inches(6.1), Inches(5.2), LIGHT, RED)
    tf = right.text_frame
    set_text(tf, "보안", 18, True, RED)
    for line in [
        "• Security Group 최소 개방",
        "• Secrets Manager (.env 주입)",
        "• HTTPS (ACM) + WAF",
        "• Private Subnet 앱/DB",
        "",
        "청중 포인트",
        "키·DB·관리포트가",
        "인터넷에 그대로 노출되지 않음",
    ]:
        add_para(tf, line, 14, False, NAVY, 6)
    footer(s, 8)
    return s


def result(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "결과 — 무엇이 달라졌나", "이전 전/후를 한 장으로 비교하면 설득력이 생긴다")
    add_table = True
    # simple comparison cards
    before = rect(s, Inches(0.4), Inches(1.35), Inches(6.0), Inches(4.9), RGBColor(254, 242, 242), RED)
    tf = before.text_frame
    set_text(tf, "Before (온프레미스)", 18, True, RED)
    for line in [
        "• 서버 4대 수동 운영",
        "• 배포 = SSH + 기억",
        "• 장애 = 사람 의존",
        "• 설정 공유 어려움",
        "• HTTPS/WAF 약함",
    ]:
        add_para(tf, line, 15, False, NAVY, 10)

    after = rect(s, Inches(6.8), Inches(1.35), Inches(6.0), Inches(4.9), RGBColor(220, 252, 231), GREEN)
    tf = after.text_frame
    set_text(tf, "After (AWS)", 18, True, GREEN)
    for line in [
        "• 관리형 서비스 + ASG",
        "• push → 자동 배포",
        "• 헬스체크·알람으로 감지",
        "• Terraform으로 재현",
        "• HTTPS · WAF · Secrets",
    ]:
        add_para(tf, line, 15, False, NAVY, 10)
    footer(s, 9)
    return s


def closing(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    t = s.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(4.5))
    tf = t.text_frame
    set_text(tf, "한 줄 결론", 20, True, RGBColor(147, 197, 253))
    add_para(tf, "서버를 ‘손으로 지키는 일’에서", 24, True, WHITE, 16)
    add_para(tf, "코드와 파이프라인으로 운영하는 일로 바꿨습니다.", 24, True, WHITE, 8)
    add_para(tf, "", 12, False, WHITE, 18)
    add_para(tf, "서이·유민·윤주·현우가 역할을 나눠", 16, False, RGBColor(191, 219, 254), 6)
    add_para(tf, "망 / 트래픽 / 데이터 / 자동화를 책임졌고", 16, False, RGBColor(191, 219, 254), 4)
    add_para(tf, "지금은 https://aniverse.my 로 서비스 중입니다.", 16, True, RGBColor(125, 211, 252), 4)
    return s


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    cover(prs)
    agenda(prs)
    roles(prs)
    onprem_pain(prs)
    terraform(prs)
    github_actions(prs)
    cicd_ha(prs)
    monitor_security(prs)
    result(prs)
    closing(prs)
    out = OUT / "Aniverse_발표_강사용.pptx"
    prs.save(out)
    print("Wrote", out)
    return out


if __name__ == "__main__":
    build()
