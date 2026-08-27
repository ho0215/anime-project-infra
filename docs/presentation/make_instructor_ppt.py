#!/usr/bin/env python3
"""강사용 5~7분 발표 PPT — 구성도 이미지 포함, 청중라벨 없음."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# 한국어 Windows 기본 글꼴. latin + ea(동아시아) 둘 다 지정해야 한글이 깨지지 않음.
FONT_NAME = "맑은 고딕"

BASE = Path(__file__).resolve().parent
IMG = BASE / "images" / "instructor"
OUT = BASE / "ppt"
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
SOFT = RGBColor(239, 246, 255)


def font(run, size=16, bold=False, color=NAVY):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = FONT_NAME
    # python-pptx는 font.name이 latin만 설정함 → 한글은 a:ea typeface 필요
    rPr = run._r.get_or_add_rPr()
    for tag in ("latin", "ea", "cs"):
        el = rPr.find(qn(f"a:{tag}"))
        if el is None:
            el = rPr.makeelement(qn(f"a:{tag}"), {})
            rPr.append(el)
        el.set("typeface", FONT_NAME)


def set_text(tf, text, size=16, bold=False, color=NAVY, align=None):
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
        sh.line.width = Pt(1.5)
    else:
        sh.line.fill.background()
    return sh


def header(slide, title, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.85))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    box = slide.shapes.add_textbox(Inches(0.45), Inches(0.12), Inches(12.4), Inches(0.65))
    tf = box.text_frame
    set_text(tf, title, 22, True, WHITE)
    if subtitle:
        add_para(tf, subtitle, 12, False, RGBColor(147, 197, 253), 2)


TOTAL = 17


def footer(slide, n, total=TOTAL):
    tx = slide.shapes.add_textbox(Inches(0.45), Inches(7.05), Inches(12.4), Inches(0.3))
    p = tx.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = f"Aniverse · 온프레미스 3-tier → AWS   |   {n}/{total}"
    font(r, 10, False, SLATE)
    p.alignment = PP_ALIGN.RIGHT


def put_img(slide, name, x, y, w=None, h=None):
    path = IMG / name
    if path.exists():
        slide.shapes.add_picture(str(path), x, y, width=w, height=h)
        return True
    return False


def cover(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    t = s.shapes.add_textbox(Inches(0.7), Inches(1.7), Inches(12), Inches(3.8))
    tf = t.text_frame
    set_text(tf, "Aniverse", 40, True, WHITE)
    add_para(tf, "온프레미스 3-Tier 서비스 → AWS 이전", 24, False, RGBColor(191, 219, 254), 14)
    add_para(tf, "Terraform · Actions · CI/CD · HA · HTTPS · WAF", 16, False, RGBColor(147, 197, 253), 16)
    add_para(tf, "https://aniverse.my", 15, False, RGBColor(125, 211, 252), 20)


def agenda(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "목차")
    items = [
        "01  AWS 이전하면서 맡은 역할",
        "02  온프레미스 운영에서 어려웠던 점",
        "03  Terraform으로 구성한 인프라",
        "04  GitHub Actions 자동화",
        "05  CI/CD · 고가용성 · 모니터링 · 보안",
        "06  HTTPS · WAF",
    ]
    for i, title in enumerate(items):
        y = Inches(1.15) + i * Inches(0.88)
        card = rect(s, Inches(0.7), y, Inches(11.9), Inches(0.75), LIGHT, BLUE)
        set_text(card.text_frame, title, 18, True, NAVY)
    footer(s, 2)


def roles(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "1. AWS 이전 — 맡은 역할", "앱 기능 담당과 별도로, 인프라 모듈을 나눠 담당")
    roles = [
        ("박서이", "Network & Security", "modules/network\nsecurity · nat", "VPC / Subnet / IGW\nNAT Instance\nSecurity Group", PURPLE),
        ("강유민", "Compute & Traffic", "modules/alb\nmodules/compute", "ALB / Target Group\nLaunch Template / ASG\nuser_data (Nginx·EFS)", ORANGE),
        ("김윤주", "Data & Storage", "modules/database\nmodules/storage", "RDS MariaDB\nEFS · S3\nRemote State", GREEN),
        ("김현우", "DevOps & CI/CD", "environments/dev\ncicd · Actions", "모듈 조립·Apply\nCodeDeploy / SSM\nHTTPS · WAF · Secrets", RED),
    ]
    for i, (name, role, mods, work, color) in enumerate(roles):
        x = Inches(0.3) + i * Inches(3.2)
        card = rect(s, x, Inches(1.2), Inches(3.05), Inches(5.3), LIGHT, color)
        tf = card.text_frame
        set_text(tf, name, 18, True, color, PP_ALIGN.CENTER)
        add_para(tf, role, 13, True, NAVY, 8)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        add_para(tf, mods, 12, False, SLATE, 12)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        add_para(tf, "────────", 11, False, RGBColor(203, 213, 225), 8)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        add_para(tf, work, 13, False, NAVY, 6)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
    footer(s, 3)


def pain_detail(prs):
    """02 어려움 — 더 자세히, 이미지(온프렘 구조) 함께."""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "2. 온프레미스에서 어려웠던 점 (1)", "3-Tier: Nginx · Django · NFS/MariaDB 를 서버별로 직접 운영")
    put_img(s, "01_onprem_3tier.png", Inches(0.4), Inches(1.1), w=Inches(12.5))
    footer(s, 4)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "2. 온프레미스에서 어려웠던 점 (2)", "수동 운영이 만든 반복 문제")
    pains = [
        (
            "① 배포가 전부 수작업",
            [
                "서버 4대에 SSH로 접속해 pull · restart",
                "순서가 조금만 달라져도 결과가 달라짐",
                "누가 언제 무엇을 배포했는지 기록이 남기 어려움",
            ],
        ),
        (
            "② 환경 불일치",
            [
                "로컬에서는 되는데 서버에서만 실패하는 경우 빈번",
                "패키지·환경변수·권한 설정이 사람 기억에 의존",
                "원인 파악에 시간을 대부분 소모",
            ],
        ),
        (
            "③ 장애·확장 대응이 느림",
            [
                "트래픽 증가 시 서버를 직접 추가·설정",
                "한 대 장애가 곧 서비스 전체 영향으로 이어짐",
                "복구 절차가 문서화되어 있어도 재현이 어려움",
            ],
        ),
        (
            "④ 보안·비밀값 관리",
            [
                ".env, API Key가 서버 파일에 흩어져 존재",
                "HTTPS·방화벽 규칙을 서버마다 따로 맞춤",
                "권한/키 교체 시 누락 위험이 큼",
            ],
        ),
    ]
    for i, (title, bullets) in enumerate(pains):
        x = Inches(0.35) + (i % 2) * Inches(6.45)
        y = Inches(1.15) + (i // 2) * Inches(2.75)
        card = rect(s, x, y, Inches(6.2), Inches(2.55), LIGHT, RED)
        tf = card.text_frame
        set_text(tf, title, 16, True, RED)
        for b in bullets:
            add_para(tf, "• " + b, 13, False, NAVY, 6)
    footer(s, 5)


def terraform_slides(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "3. Terraform 인프라 구성 (1)", "온프레미스 3-Tier를 AWS 서비스로 대응")
    put_img(s, "02_aws_overview.png", Inches(0.35), Inches(1.05), w=Inches(12.6))
    footer(s, 6)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "3. Terraform 인프라 구성 (2)", "모듈을 나눠 만들고 environments/dev 에서 조립")
    put_img(s, "03_terraform_modules.png", Inches(0.25), Inches(1.0), w=Inches(12.8))
    footer(s, 7)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "3. Terraform 인프라 구성 (3)", "주요 리소스와 연결 관계")
    left = rect(s, Inches(0.4), Inches(1.2), Inches(6.2), Inches(5.3), SOFT, BLUE)
    tf = left.text_frame
    set_text(tf, "계층별 구성", 17, True, BLUE)
    for line in [
        "Network: VPC · Public/Private Subnet · IGW · NAT",
        "Security: ALB/App/NAT/DB/EFS/Redis/endpoints 용 Security Group",
        "Traffic: ALB · Target Group · HTTPS Listener",
        "Compute: Launch Template · ASG · IAM Role",
        "Data: RDS MariaDB · EFS · S3",
        "Ops: Secrets Manager · WAF · Redis · CodeDeploy",
    ]:
        add_para(tf, "• " + line, 13, False, NAVY, 8)

    right = rect(s, Inches(6.9), Inches(1.2), Inches(5.9), Inches(5.3), LIGHT, TEAL)
    tf = right.text_frame
    set_text(tf, "조립 방식", 17, True, TEAL)
    for line in [
        "1) S3 + DynamoDB로 Remote State 환경 선구축",
        "2) 팀원이 모듈 PR로 기능 단위 작성",
        "3) outputs.tf 로 vpc_id, sg_id 등 연결",
        "4) environments/dev/main.tf 에서 module 호출",
        "5) terraform plan / apply 로 한 번에 반영",
        "",
        "결과",
        "• 인프라가 코드로 리뷰·재현 가능",
        "• 서버 ‘기억 의존’ 감소",
        "• 팀 전체가 충돌 없이 동시 작업 가능 (State Lock)",
    ]:
        add_para(tf, line, 12, False, NAVY, 5)
    footer(s, 8)

    # 데이터베이스·스토리지 구성 요소
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "3. 데이터베이스·스토리지 구성", "김윤주 Data & Storage — RDS · EFS · S3 · Remote State")
    cards = [
        (
            "RDS (MariaDB)",
            GREEN,
            [
                "modules/database",
                "앱 DB를 관리형으로 이전",
                "Private subnet 배치",
                "스냅샷 · Secrets 연동",
            ],
        ),
        (
            "EFS",
            TEAL,
            [
                "modules/storage",
                "온프렘 NFS 대체",
                "ASG EC2 간 공유 마운트",
                "미디어·업로드 파일 공유",
            ],
        ),
        (
            "S3 + DynamoDB",
            BLUE,
            [
                "Remote State 선구축",
                "S3: tfstate 저장",
                "DynamoDB: State Lock",
                "팀 동시 apply 충돌 방지",
            ],
        ),
        (
            "S3 CORS + Lifecycle",
            ORANGE,
            [
                "정적/미디어 버킷 정책",
                "CORS: 브라우저 GET 허용",
                "Lifecycle: 오래된 객체 정리",
                "비용·운영 부담 감소",
            ],
        ),
    ]
    for i, (title, color, bullets) in enumerate(cards):
        x = Inches(0.3) + (i % 4) * Inches(3.2)
        y = Inches(1.2)
        card = rect(s, x, y, Inches(3.05), Inches(5.3), LIGHT, color)
        tf = card.text_frame
        set_text(tf, title, 16, True, color, PP_ALIGN.CENTER)
        for b in bullets:
            add_para(tf, "• " + b, 13, False, NAVY, 10)
            tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
    footer(s, 9)

    # S3 / EFS / RDS — 각각 무엇을 저장하는가
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "3. S3 · EFS · RDS — 저장 역할 정리", "같은 ‘데이터’라도 성격에 따라 저장소를 나눔")
    store_cards = [
        (
            "RDS (MariaDB)",
            GREEN,
            "구조화된 DB 데이터",
            [
                "회원 · 로그인 계정",
                "커뮤니티 글 · 댓글 · 좋아요",
                "거래 상품 정보 · 채팅 메타",
                "창작물 제목·본문·상태",
                "관계·검색·트랜잭션이 필요한 값",
            ],
        ),
        (
            "EFS",
            TEAL,
            "ASG가 공유하는 파일 공간",
            [
                "EC2 media/ 경로에 NFS 마운트",
                "인스턴스 교체돼도 파일 유지",
                "여러 대 EC2가 같은 media 공유",
                "온프렘 NFS 역할을 AWS에서 대체",
                "Nginx /media 로컬·fallback 서빙",
            ],
        ),
        (
            "S3",
            ORANGE,
            "객체 스토리지 (파일·배포)",
            [
                "업로드 이미지 원본",
                "community/ · goods_images/",
                "works_images/",
                "공개 URL로 브라우저 제공",
                "배포 zip · (별도) tfstate 버킷",
            ],
        ),
    ]
    for i, (title, color, subtitle, bullets) in enumerate(store_cards):
        x = Inches(0.35) + i * Inches(4.25)
        card = rect(s, x, Inches(1.15), Inches(4.05), Inches(5.15), LIGHT, color)
        tf = card.text_frame
        set_text(tf, title, 18, True, color, PP_ALIGN.CENTER)
        add_para(tf, subtitle, 13, True, SLATE, 8)
        tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
        for b in bullets:
            add_para(tf, "• " + b, 13, False, NAVY, 8)
            tf.paragraphs[-1].alignment = PP_ALIGN.CENTER
    one = s.shapes.add_textbox(Inches(0.4), Inches(6.4), Inches(12.5), Inches(0.45))
    set_text(
        one.text_frame,
        "한 줄:  RDS = ‘무슨 글인지’  ·  S3 = ‘사진 파일’  ·  EFS = ‘여러 EC2가 같이 쓰는 폴더’",
        14,
        True,
        TEAL,
        PP_ALIGN.CENTER,
    )
    footer(s, 10)


def actions_slides(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "4. GitHub Actions (1)", "인프라 저장소 / 앱 저장소를 나눠 자동화")
    put_img(s, "04_github_actions.png", Inches(0.3), Inches(1.05), w=Inches(12.7))
    footer(s, 11)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "4. GitHub Actions (2)", "실제로 돌아가는 파이프라인")
    left = rect(s, Inches(0.4), Inches(1.2), Inches(6.2), Inches(5.3), SOFT, BLUE)
    tf = left.text_frame
    set_text(tf, "anime-project-infra", 16, True, BLUE)
    for line in [
        "trigger: main push / workflow_dispatch",
        "steps: checkout → setup TF → fmt",
        "        validate → plan → apply",
        "결과: VPC/ALB/ASG/RDS/S3/WAF 갱신",
        "Secrets: AWS 자격증명, TF_VAR_*",
    ]:
        add_para(tf, "• " + line, 13, False, NAVY, 8)

    right = rect(s, Inches(6.9), Inches(1.2), Inches(5.9), Inches(5.3), RGBColor(255, 247, 237), ORANGE)
    tf = right.text_frame
    set_text(tf, "anime-project", 16, True, ORANGE)
    for line in [
        "trigger: main push / workflow_dispatch",
        "steps: media → S3 sync",
        "        앱 zip 패키징 → deploy S3",
        "        CodeDeploy → ASG 배포",
        "hooks: install → migrate → Daphne 기동",
    ]:
        add_para(tf, "• " + line, 13, False, NAVY, 8)
    footer(s, 12)


def ops_slides(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "5. CI/CD · HA · 모니터링 · 보안", "배포·가용성·관측·보안을 한 장으로")
    put_img(s, "05_ops_security.png", Inches(0.45), Inches(1.15), w=Inches(12.4))
    footer(s, 13)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "5. 적용 내용 상세", "서비스가 실제로 어떻게 버티는지")
    items = [
        ("CI/CD", BLUE, ["Actions + CodeDeploy로 배포 경로 고정", "ALB /health/ 로 배포 성공 판정", "실패 시 Actions·배포 로그로 추적"]),
        ("고가용성", ORANGE, ["ALB로 트래픽 분산", "ASG로 인스턴스 교체·확장", "App/DB 서브넷 분리 배치"]),
        ("모니터링", TEAL, ["CloudWatch 알람", "Target Group health 확인", "SSM으로 서버 점검"]),
        ("보안", RED, ["SG 최소 포트 개방", "DB subnet NACL 설정", "Secrets Manager로 키 주입", "ACM HTTPS + WAF(SQLi/Rate)"]),
    ]
    for i, (title, color, bullets) in enumerate(items):
        x = Inches(0.3) + (i % 2) * Inches(6.45)
        y = Inches(1.15) + (i // 2) * Inches(2.75)
        card = rect(s, x, y, Inches(6.2), Inches(2.55), LIGHT, color)
        tf = card.text_frame
        set_text(tf, title, 17, True, color)
        for b in bullets:
            add_para(tf, "• " + b, 13, False, NAVY, 7)
    footer(s, 14)


def https_waf_slides(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "6. HTTPS · WAF (1)", "도메인부터 ALB까지 암호화·필터링 경로")
    put_img(s, "06_https_waf.png", Inches(0.35), Inches(1.0), w=Inches(12.6))
    footer(s, 15)

    s = prs.slides.add_slide(prs.slide_layouts[6])
    header(s, "6. HTTPS · WAF (2)", "Terraform으로 고정한 보안 엣지")
    left = rect(s, Inches(0.35), Inches(1.15), Inches(6.2), Inches(5.5), SOFT, TEAL)
    tf = left.text_frame
    set_text(tf, "HTTPS — ACM + ALB", 18, True, TEAL)
    for line in [
        "modules/acm",
        "• aniverse.my DNS 검증 인증서",
        "• www SAN 포함 · Route53 검증 레코드",
        "",
        "modules/alb",
        "• 443 HTTPS Listener (TLS 1.3)",
        "• 80 → 443 HTTP 301 redirect",
        "• Target Group → ASG/EC2",
        "",
        "앱 연동",
        "• Secrets: USE_HTTPS=True",
        "• CSRF / ALLOWED_HOSTS https 허용",
    ]:
        add_para(tf, line, 13, False, NAVY, 5)

    right = rect(s, Inches(6.8), Inches(1.15), Inches(6.15), Inches(5.5), RGBColor(254, 242, 242), RED)
    tf = right.text_frame
    set_text(tf, "WAF — ALB Web ACL", 18, True, RED)
    for line in [
        "modules/waf → aniverse-alb-waf",
        "• scope: REGIONAL (ALB 전용)",
        "",
        "관리형 규칙",
        "• CommonRuleSet (일반 웹 공격)",
        "• KnownBadInputs",
        "• SQLi RuleSet",
        "",
        "커스텀",
        "• RateLimitPerIP → Block",
        "",
        "연결",
        "• web_acl_association → ALB ARN",
        "• CloudWatch metrics / sampled req",
    ]:
        add_para(tf, line, 13, False, NAVY, 4)
    footer(s, 16)


def closing(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()
    t = s.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(4))
    tf = t.text_frame
    set_text(tf, "정리", 20, True, RGBColor(147, 197, 253))
    add_para(tf, "3-Tier 수동 서버 → AWS 모듈형 인프라 + 자동 배포", 22, True, WHITE, 14)
    add_para(tf, "서이(망) · 유민(트래픽) · 윤주(데이터) · 현우(자동화·HTTPS·WAF)", 16, False, RGBColor(191, 219, 254), 16)
    add_para(tf, "https://aniverse.my", 16, False, RGBColor(125, 211, 252), 14)


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    cover(prs)
    agenda(prs)
    roles(prs)
    pain_detail(prs)
    terraform_slides(prs)
    actions_slides(prs)
    ops_slides(prs)
    https_waf_slides(prs)
    closing(prs)
    out = OUT / "Aniverse_발표_강사용.pptx"
    prs.save(out)
    print("Wrote", out)


if __name__ == "__main__":
    build()
