# External Secrets Operator — 앱 시크릿 전환

## 배경

EKS 배포의 앱 시크릿(`DJANGO_SECRET_KEY`, `DB_PASSWORD`, `DB_ROOT_PASSWORD`)은 기존엔
GitHub Actions repo secret → `kubectl create secret`(최초 1회) → `scripts/argocd-eks-install.sh`가
그 살아있는 K8s Secret을 다시 읽어서 ArgoCD Application의 `helm.parameters`로 재주입하는,
부트스트랩에 의존하는 순환 구조였다. 이 체인의 한 단계라도 빠지면 `deploy/helm/aniverse/values.yaml`의
랩용 평문 기본값(`DB_PASSWORD: "aniversepass"` 등)으로 조용히 폴백할 여지가 구조적으로 있었다.

지금은 진짜 값을 AWS Secrets Manager(`aniverse/app-secrets`) 한 곳에만 두고, EKS 클러스터에 설치된
External Secrets Operator(ESO)가 IRSA로 그 값을 읽어와 기존과 동일한 이름/네임스페이스의
K8s Secret(`aniverse-app-secrets` / `aniverse`)을 자동 생성한다. 앱의 Deployment/StatefulSet은
이 Secret을 그대로 참조하므로 변경 없음.

## 구성 요소

- `anime-project-infra/modules/eks/main.tf` — `helm_release.external_secrets`(ESO 컨트롤러) +
  `aws_iam_role.external_secrets`(IRSA, `secretsmanager:GetSecretValue`/`DescribeSecret`을
  시크릿 ARN 하나로만 스코핑)
- `anime-project-infra/environments/dev/secrets.tf` — `aws_secretsmanager_secret.app_secrets`
  (메타데이터만, 값은 Terraform이 안 건드림)
- `anime-project/deploy/helm/aniverse/templates/external-secret.yaml` — `ClusterSecretStore` +
  `ExternalSecret` (EKS에서만 렌더링, `values-eks.yaml`의 `externalSecrets.enabled: true`)
- `anime-project/deploy/helm/aniverse/templates/secret.yaml` — `externalSecrets.enabled`일 때
  렌더링 안 함(ExternalSecret과 같은 이름의 Secret을 두고 충돌 방지). 랩/로컬은 그대로 동작.

## 전환 절차 (최초 1회, 무중단)

1. **인프라 apply** — ESO 컨트롤러 + IRSA + 빈 Secrets Manager 시크릿 생성:
   ```
   cd environments/dev
   AWS_PROFILE=aniverse-sso terraform apply
   ```

2. **현재 살아있는 값을 그대로 Secrets Manager에 주입** (로테이션 아님 — DB 접속 정보가 그대로라
   앱 재기동/`ALTER USER` 불필요):
   ```
   kubectl -n aniverse get secret aniverse-app-secrets -o json \
     | jq '.data | map_values(@base64d)' > /tmp/live-secrets.json
   AWS_PROFILE=aniverse-sso aws secretsmanager put-secret-value \
     --secret-id aniverse/app-secrets \
     --secret-string file:///tmp/live-secrets.json
   rm /tmp/live-secrets.json
   ```

3. **앱 배포** — `values-eks.yaml`의 `externalSecrets.enabled: true`가 반영된 차트를 Argo sync.
   `ExternalSecret`이 `creationPolicy: Owner`로 기존 `aniverse-app-secrets`를 이어받는다
   (값이 동일하므로 파드 재시작 불필요).

4. **검증**:
   ```
   kubectl get externalsecret -n aniverse          # SYNCED 확인
   kubectl get secret aniverse-app-secrets -n aniverse -o jsonpath='{.data.DB_PASSWORD}' | base64 -d
   # → 2번에서 읽은 값과 동일한지 확인
   ```
   앱 pod가 재시작 없이 정상 유지되는지, DB 접속이 계속 되는지 확인.

## 이번에 안 건드린 것 (후속 정리 대상)

`scripts/argocd-eks-install.sh`의 live-secret 재주입 로직, `.github/workflows/argocd-eks.yml`의
"Seed aniverse-app-secrets" 스텝, `application-eks-helm.yaml`의 Secret `ignoreDifferences` —
전부 "이미 있으면 skip" 방식이라 ESO와 당장 충돌은 없음. ESO 정상 동작 확인 후 별도 PR에서 제거.

## 후속 (별도 작업): 진짜 로테이션

지금은 기존 값 재사용이라 비밀번호 자체는 안 바뀜. 이후 실제로 로테이션하려면 같은 점검 창에서:
1. Secrets Manager 값 갱신 (`put-secret-value`)
2. MariaDB에서 `ALTER USER 'aniverse'@'%' IDENTIFIED BY '...'`
3. ESO `refreshInterval`(1h) 만료 대기 또는 `kubectl annotate externalsecret ... force-sync=$(date +%s) -n aniverse --overwrite`로 즉시 동기화
