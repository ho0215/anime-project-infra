#!/usr/bin/env python3
"""강사용 VIEW HTML — instructor 이미지를 상대 경로로 참조."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "VIEW_강사발표.html"


def main():
    html = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Aniverse 발표 (강사용)</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet"/>
<style>
body{margin:0;font-family:"Noto Sans KR","맑은 고딕",NanumGothic,system-ui,sans-serif;background:#f8fafc;color:#0f172a;line-height:1.5}
.wrap{max-width:1000px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.7rem;margin:0 0 6px} .sub{color:#64748b;margin-bottom:16px}
.tip{background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;padding:12px;margin-bottom:18px}
section{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;margin-bottom:14px}
h2{margin:0 0 10px;font-size:1.15rem;border-left:4px solid #2563eb;padding-left:10px}
img{max-width:100%;border:1px solid #e2e8f0;border-radius:10px;margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.card{border:1px solid #e2e8f0;border-radius:12px;padding:12px;background:#f8fafc}
.card dt{font-weight:700;color:#2563eb;margin-top:6px}
.card dd{margin:2px 0 0;padding:0;color:#334155}
.card .sub{font-size:.85rem;color:#64748b;margin:4px 0 8px}
ul{margin:6px 0 0;padding-left:18px}
</style></head><body><div class="wrap">
<h1>온프레미스 3-Tier → AWS</h1>
<p class="sub">PPT: ppt/Aniverse_발표_강사용.pptx · 발표 5~7분 · AWS Architecture Icons + GitHub 공식 마크</p>
<div class="tip"><b>보는 방법:</b> 이 HTML을 로컬에서 열거나 PowerPoint 파일을 여세요. 구성도에는 AWS·GitHub 공식 아이콘이 포함되어 있습니다.</div>

<section><h2>목차</h2>
<ol>
<li>AWS 이전하면서 맡은 역할</li>
<li>온프레미스 운영에서 어려웠던 점</li>
<li>기술 스택 (AWS · GitHub)</li>
<li>Terraform으로 구성한 인프라 (데이터·스토리지 포함)</li>
<li>GitHub Actions 자동화</li>
<li>CI/CD · 고가용성 · 모니터링 · 보안</li>
<li>HTTPS · WAF</li>
<li>트러블슈팅</li>
</ol>
</section>

<section><h2>1. 맡은 역할</h2>
<img src="images/instructor/09_team_roles.png" alt="team-roles"/>
</section>

<section><h2>2. 온프레미스 구조 &amp; 어려움</h2>
<img src="images/instructor/01_onprem_3tier.png" alt="onprem"/>
</section>

<section><h2>3. 기술 스택 (AWS · GitHub)</h2>
<p style="color:#64748b;margin:0 0 10px">Terraform 소개 전에 쓸 도구 지도를 먼저 보여줍니다.</p>
<img src="images/instructor/07_aws_github_stack.png" alt="tech-stack"/>
</section>

<section><h2>4. Terraform 구성</h2>
<img src="images/instructor/02_aws_overview.png" alt="aws"/>
<img src="images/instructor/03_terraform_modules.png" alt="modules"/>
</section>

<section><h2>4+. S3 · EFS · RDS 저장 역할</h2>
<img src="images/instructor/08_storage_roles.png" alt="storage"/>
</section>

<section><h2>5. GitHub Actions / CI/CD Pipeline</h2>
<img src="images/instructor/04_github_actions.png" alt="cicd"/>
</section>

<section><h2>6. CI/CD · HA · 모니터링 · 보안</h2>
<img src="images/instructor/05_ops_security.png" alt="ops"/>
</section>

<section><h2>7. HTTPS · WAF</h2>
<img src="images/instructor/06_https_waf.png" alt="https-waf"/>
</section>

<section><h2>8. 트러블슈팅</h2>
<p class="sub">상황 → 문제 → 선택 → 역할 → 결과</p>
<div class="grid">
<div class="card"><b>① NAT 모듈 분리</b>
<dl><dt>상황</dt><dd>network 모듈에 NAT까지 함께 설정</dd>
<dt>문제</dt><dd>security와 순환 의존 → Terraform 구성 불가</dd>
<dt>선택</dt><dd>network → security → nat 3모듈 분리</dd>
<dt>역할</dt><dd>network=망 · security=SG · nat=Instance</dd>
<dt>결과</dt><dd>순환 해소, 통합 테스트 완료</dd></dl></div>
<div class="card"><b>② IAM 키 노출 대응</b>
<dl><dt>상황</dt><dd>GitHub .env에 iac-admin 액세스 키 노출</dd>
<dt>문제</dt><dd>AWSCompromisedKeyQuarantineV3 자동 격리</dd>
<dt>선택</dt><dd>새 키 생성·교체, 노출 키 비활성화·삭제</dd>
<dt>역할</dt><dd>IaC용 IAM / 앱용 키 분리 운영</dd>
<dt>결과</dt><dd>CI/CD·Terraform 배포 복구</dd></dl></div>
<div class="card"><b>③ Remote State &amp; DynamoDB</b>
<p class="sub">앱 DB가 아니라, Terraform 자물쇠</p>
<dl><dt>상황</dt><dd>팀 4명이 같은 tfstate를 S3에 공유</dd>
<dt>문제</dt><dd>동시 apply → state 덮어쓰기·불일치</dd>
<dt>선택</dt><dd>bootstrap: S3(state) + DynamoDB(lock)</dd>
<dt>역할</dt><dd>RDS=앱 데이터 / DynamoDB=State Lock만</dd>
<dt>결과</dt><dd>충돌 없이 병렬 인프라 작업 가능</dd></dl></div>
</div>
</section>

</div></body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    print("Wrote", OUT, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
