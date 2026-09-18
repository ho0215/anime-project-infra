# 계정 Block 해제 대기 중 체크리스트

EC2 `StartInstances` 가 Blocked 인 동안에도 할 수 있는 일.

## 보안 (지금 당장)

- [ ] IAM → `iac-admin`(및 기타 유저) **Access Key 전부 삭제**
- [ ] 루트 **Access Key 없음** 확인 (있으면 삭제)
- [ ] 루트·IAM **MFA** 켜짐 확인
- [ ] GitHub Secrets 에 `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` 있으면 **삭제** (OIDC만 사용)
- [ ] 로컬·메신저·노션·옛 `.env` 에 키 남아 있으면 파기
- [ ] Billing / Cost Explorer 로 9/17 전후 이상 과금·리전 확인
- [ ] **모든 리전** EC2 에서 모르는 인스턴스 Terminated/삭제

## Support

- [ ] 케이스에 회신: 키 삭제·무단 리소스 정리 완료, Start 제한 해제 요청
- [ ] 전담팀 회신·활성화 메일 대기 (수시간~1일+ 가능)

## 해제된 뒤

1. 콘솔에서 NAT Start 되는지만 확인
2. Actions → **EKS start/stop** → `start`
3. `https://aniverse.my/health/`

## 발표용 한 줄

> Access Key(`iac-admin`)가 유출되어 무단 `RunInstances`가 발생했고, AWS가 계정을 잠가 EKS start가 막혔다. OIDC 전환·키 제거로 재발을 막는다.
