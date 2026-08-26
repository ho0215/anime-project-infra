from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE = Path(__file__).resolve().parent
IMG = BASE / 'images'
OUT = BASE / 'ppt'
OUT.mkdir(parents=True, exist_ok=True)

BLUE = RGBColor(37, 99, 235)
NAVY = RGBColor(15, 23, 42)
SLATE = RGBColor(71, 85, 105)
LIGHT = RGBColor(248, 250, 252)
TEAL = RGBColor(13, 148, 136)
GREEN = RGBColor(22, 163, 74)
AMBER = RGBColor(245, 158, 11)
RED = RGBColor(220, 38, 38)
PURPLE = RGBColor(124, 58, 237)
WHITE = RGBColor(255, 255, 255)


def add_title(slide, title, subtitle=None):
    tx = slide.shapes.add_textbox(Inches(0.55), Inches(0.25), Inches(12.0), Inches(0.8))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = NAVY
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(10)
        p2.font.color.rgb = SLATE


def add_footer(slide, text='Aniverse 발표자료'):
    tx = slide.shapes.add_textbox(Inches(0.5), Inches(7.0), Inches(12.2), Inches(0.25))
    p = tx.text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(9)
    p.font.color.rgb = SLATE
    p.alignment = PP_ALIGN.RIGHT


def add_bullets(slide, x, y, w, h, title, bullets, color=BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = LIGHT
    shape.line.color.rgb = color
    shape.line.width = Pt(1.5)
    tx = shape.text_frame
    tx.clear()
    tx.word_wrap = True
    p = tx.paragraphs[0]
    p.text = title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = color
    for item in bullets:
        bp = tx.add_paragraph()
        bp.text = item
        bp.level = 0
        bp.font.size = Pt(12)
        bp.font.color.rgb = NAVY
        bp.space_after = Pt(4)


def add_table(slide, x, y, w, h, data, col_widths=None, header_fill=RGBColor(219, 234, 254)):
    rows = len(data)
    cols = len(data[0])
    table = slide.shapes.add_table(rows, cols, x, y, w, h).table
    if col_widths:
        for i, cw in enumerate(col_widths):
            table.columns[i].width = cw
    row_h = int(h / rows)
    for r in range(rows):
        table.rows[r].height = row_h
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = str(data[r][c])
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11 if r else 12)
                p.font.bold = (r == 0)
                p.font.color.rgb = NAVY
                p.alignment = PP_ALIGN.CENTER if r == 0 else PP_ALIGN.LEFT
            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_fill
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE if r % 2 else LIGHT
    return table


def add_image(slide, path, x, y, w=None, h=None):
    slide.shapes.add_picture(str(path), x, y, width=w, height=h)


def new_prs(title_sub=''):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def build_infra_ppt():
    prs = new_prs()
    # 1 cover
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.background.fill
    bg.solid(); bg.fore_color.rgb = WHITE
    add_title(s, 'Aniverse 인프라 발표자료', 'Terraform · AWS · GitHub Actions · CodeDeploy')
    add_bullets(s, Inches(0.7), Inches(1.2), Inches(5.2), Inches(2.4), '발표 핵심', [
        'Terraform 모듈형 인프라 구축',
        'GitHub Actions 기반 CI/CD 자동화',
        'ALB 분리 리팩터링 (0 add / 0 change / 0 destroy)',
        'SSM, RDS 스냅샷 복원, 모니터링, 앱 배포 연동'
    ], BLUE)
    add_image(s, IMG/'aniverse-architecture-overview.png', Inches(6.2), Inches(1.05), w=Inches(6.4))
    add_footer(s)

    # 2 architecture
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '1. 전체 아키텍처', 'Public ALB / Private App, DB / S3 / EFS / SSM')
    add_image(s, IMG/'aniverse-architecture-overview.png', Inches(0.6), Inches(0.95), w=Inches(12.1))
    add_footer(s)

    # 3 modules
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '2. Terraform 모듈 구성', 'network → security → nat → endpoints → database → storage → alb → compute → cicd → monitoring')
    add_image(s, IMG/'aniverse-terraform-modules.png', Inches(0.55), Inches(1.0), w=Inches(7.0))
    add_table(s, Inches(7.8), Inches(1.15), Inches(4.9), Inches(4.7), [
        ['모듈', '설명'],
        ['network/security', 'VPC, 서브넷, 보안그룹'],
        ['nat/endpoints', '외부 통신, SSM Endpoint'],
        ['database/storage', 'RDS, EFS, S3'],
        ['alb', 'ALB / TG / Listener'],
        ['compute', 'Launch Template / ASG / IAM'],
        ['cicd/monitoring', 'CodeDeploy, CloudWatch'],
    ])
    add_bullets(s, Inches(7.8), Inches(5.95), Inches(4.9), Inches(0.8), '핵심 포인트', ['ALB를 compute에서 분리하고 moved로 state만 이전'], TEAL)
    add_footer(s)

    # 4 cicd
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '3. CI/CD 파이프라인', '인프라와 앱 저장소를 분리해 자동화')
    add_image(s, IMG/'aniverse-cicd-pipeline.png', Inches(0.6), Inches(0.95), w=Inches(7.0))
    add_table(s, Inches(7.8), Inches(1.05), Inches(4.9), Inches(3.0), [
        ['구분', '자동화 내용'],
        ['Infra CI', 'fmt / validate / plan'],
        ['Infra CD', 'apply / destroy + SSM 대기'],
        ['App CD', 'deploy.zip → CodeDeploy'],
        ['공통', 'GitHub Secrets 기반 배포'],
    ])
    add_table(s, Inches(7.8), Inches(4.35), Inches(4.9), Inches(1.95), [
        ['필수 Secret', '설명'],
        ['AWS_ACCESS_KEY_ID', 'AWS 인증'],
        ['TF_VAR_DB_PASSWORD', 'RDS 비밀번호'],
        ['S3_BUCKET_NAME', '앱 deploy 버킷'],
    ], header_fill=RGBColor(220,252,231))
    add_footer(s)

    # 5 alb split
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '4. ALB 분리 리팩터링', 'feature/compute-module 구조를 안전하게 반영')
    add_bullets(s, Inches(0.7), Inches(1.1), Inches(5.7), Inches(4.2), '무엇을 바꿨는가', [
        '기존: compute 모듈 안에 ALB / TG / Listener 포함',
        '변경: modules/alb 신설, compute는 target_group_arn만 사용',
        '호환성 유지: Ubuntu / CodeDeploy / /health/ 설정 그대로 유지',
        'Terraform moved 블록으로 실 리소스 재생성 방지'
    ], BLUE)
    add_bullets(s, Inches(0.7), Inches(5.45), Inches(5.7), Inches(1.0), '검증 결과', [
        'Plan: 0 add / 0 change / 0 destroy',
        'ALB DNS 동일, /health/ 및 / 응답 200 확인'
    ], GREEN)
    add_table(s, Inches(6.8), Inches(1.2), Inches(5.6), Inches(3.0), [
        ['Before', 'After'],
        ['module.compute.aws_lb.*', 'module.alb.aws_lb.*'],
        ['module.compute.aws_lb_target_group.*', 'module.alb.aws_lb_target_group.*'],
        ['module.compute.aws_lb_listener.*', 'module.alb.aws_lb_listener.*'],
    ], header_fill=RGBColor(204,251,241))
    add_image(s, IMG/'aniverse-terraform-modules.png', Inches(7.0), Inches(4.45), w=Inches(5.1))
    add_footer(s)

    # 6 ops troubles
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '5. 트러블슈팅 및 운영 안정화', '주요 장애 원인과 해결 내용')
    add_image(s, IMG/'aniverse-problems-solved.png', Inches(0.55), Inches(0.95), w=Inches(7.1))
    add_table(s, Inches(7.85), Inches(1.05), Inches(4.8), Inches(4.9), [
        ['문제', '해결'],
        ['terraform-cd 미인식', '확장자 .yml 수정'],
        ['TF 1.5.7 한계', '1.10.5로 상향'],
        ['이미지 403', 'S3 public read + sync'],
        ['챗봇 실패', 'CSRF + GEMINI 주입'],
        ['WebSocket 불가', 'Gunicorn → Daphne'],
        ['RDS IDE 오탐', 'locals literal로 정리'],
    ], header_fill=RGBColor(254,242,242))
    add_footer(s)

    # 7 results roadmap
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '6. 결과 및 향후 계획', '현재 운영 상태와 다음 단계')
    add_bullets(s, Inches(0.7), Inches(1.1), Inches(5.8), Inches(2.1), '현재 결과', [
        'main 브랜치 반영 완료',
        '인프라/앱 자동 배포 파이프라인 구축',
        'SSM 기반 운영, DB 복원, 미디어 동기화 가능'
    ], GREEN)
    add_bullets(s, Inches(0.7), Inches(3.55), Inches(5.8), Inches(2.0), '향후 고도화', [
        '커스텀 도메인 + ACM HTTPS',
        '멀티 계정 테스트 환경 템플릿화',
        '모니터링/알람 확대, 비용 최적화'
    ], PURPLE)
    add_table(s, Inches(6.8), Inches(1.2), Inches(5.4), Inches(2.2), [
        ['검증 항목', '상태'],
        ['Terraform CI/CD', '완료'],
        ['ALB 분리', '완료'],
        ['챗봇/이미지/WS', '완료'],
        ['도메인/HTTPS', '추가 예정'],
    ], header_fill=RGBColor(237,233,254))
    add_image(s, IMG/'aniverse-architecture-overview.png', Inches(6.9), Inches(3.75), w=Inches(5.2))
    add_footer(s, 'Aniverse 인프라 발표자료 · 발표 마무리')

    prs.save(OUT/'aniverse-infra-presentation.pptx')


def build_app_ppt():
    prs = new_prs()
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, 'Aniverse 사이트/앱 발표자료', 'Django · Daphne · CodeDeploy')
    add_bullets(s, Inches(0.7), Inches(1.2), Inches(5.3), Inches(2.6), '앱 핵심 구현', [
        'Django 웹사이트 + Daphne(ASGI)',
        '거래 채팅 WebSocket 지원',
        'Gemini 기반 AI 챗봇',
        'CodeDeploy 자동 배포'
    ], BLUE)
    add_image(s, IMG/'aniverse-cicd-pipeline.png', Inches(6.2), Inches(1.05), w=Inches(6.2))
    add_footer(s, 'Aniverse 사이트/앱 발표자료')

    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '1. 사용자 기능 및 런타임', '웹 접속, 챗봇, 이미지, 거래 채팅')
    add_table(s, Inches(0.8), Inches(1.1), Inches(5.8), Inches(3.0), [
        ['항목', '내용'],
        ['웹 서버', 'nginx → Daphne → Django'],
        ['AI 챗봇', 'Gemini 3.6 Flash'],
        ['채팅', 'WebSocket /ws/'],
        ['이미지', 'S3 media/static'],
        ['배포', 'GitHub Actions + CodeDeploy'],
    ])
    add_bullets(s, Inches(7.0), Inches(1.25), Inches(5.2), Inches(2.7), '안정화 포인트', [
        'CSRF 쿠키/Trusted Origins 수정',
        'Gemini API Key를 SSM으로 주입',
        'Broken image 시 No Image fallback 제공'
    ], TEAL)
    add_image(s, IMG/'aniverse-problems-solved.png', Inches(6.9), Inches(4.2), w=Inches(5.3))
    add_footer(s, 'Aniverse 사이트/앱 발표자료')

    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title(s, '2. 배포 흐름과 개선 사항', '앱 저장소 중심 요약')
    add_image(s, IMG/'aniverse-cicd-pipeline.png', Inches(0.7), Inches(1.0), w=Inches(6.7))
    add_table(s, Inches(7.6), Inches(1.0), Inches(5.0), Inches(4.1), [
        ['문제', '개선'],
        ['챗봇 통신 실패', 'CSRF + API Key 주입'],
        ['거래 채팅 미동작', 'Daphne/ASGI 전환'],
        ['이미지 403', 'S3 정책 + sync'],
        ['DB 복원 번거로움', 'restore_db 자동화'],
    ])
    add_bullets(s, Inches(7.6), Inches(5.35), Inches(5.0), Inches(1.0), '한 줄 결론', ['앱은 push만으로 배포되고, 장애 포인트를 대부분 자동화로 흡수'], GREEN)
    add_footer(s, 'Aniverse 사이트/앱 발표자료 · 끝')

    prs.save(OUT/'aniverse-app-presentation.pptx')


if __name__ == '__main__':
    build_infra_ppt()
    build_app_ppt()
    print('generated:', OUT/'aniverse-infra-presentation.pptx')
    print('generated:', OUT/'aniverse-app-presentation.pptx')
