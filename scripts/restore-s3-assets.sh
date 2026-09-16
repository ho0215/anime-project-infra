#!/usr/bin/env bash
# Terraform destroy(force_destroy S3) 후 빈 버킷에
# anime-project 의 media/ + static/(css·img) 를 다시 올린다.
#
#   APP_DIR=../anime-project STATIC_BUCKET_NAME=aniverse-static-... \
#     ./scripts/restore-s3-assets.sh
#
# GitHub Actions(Terraform apply 직후 / Sync media 워크플로)에서도 사용.
set -euo pipefail

AWS_REGION="${AWS_REGION:-ap-northeast-2}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="${APP_DIR:-}"

if [ -z "${STATIC_BUCKET_NAME:-}" ]; then
  echo "STATIC_BUCKET_NAME required" >&2
  exit 1
fi

if [ -z "$APP_DIR" ]; then
  if [ -d "$ROOT/../anime-project" ]; then
    APP_DIR="$(cd "$ROOT/../anime-project" && pwd)"
  else
    echo "Set APP_DIR to anime-project checkout" >&2
    exit 1
  fi
fi

MEDIA_DIR="${APP_DIR}/media"
STATIC_DIR="${APP_DIR}/static"

echo "Bucket: s3://${STATIC_BUCKET_NAME}  region=${AWS_REGION}"
echo "App:    ${APP_DIR}"

# Public-read 정책 (destroy 후 새 버킷에도 Terraform 이 넣지만, 스크립트 단독 실행 대비)
if [ -x "${APP_DIR}/scripts/sync_media_to_s3.sh" ]; then
  # sync_media 가 정책+media sync 를 담당
  STATIC_BUCKET_NAME="${STATIC_BUCKET_NAME}" \
    AWS_REGION="${AWS_REGION}" \
    MEDIA_DIR="${MEDIA_DIR}" \
    bash "${APP_DIR}/scripts/sync_media_to_s3.sh"
else
  echo "sync_media_to_s3.sh missing" >&2
  exit 1
fi

# 라이브 HTML 은 /css/, /img/ 를 버킷 루트에서 읽음 (static/ 디렉터리 동기화)
if [ -d "$STATIC_DIR" ]; then
  echo "Syncing ${STATIC_DIR}/ → s3://${STATIC_BUCKET_NAME}/ (css, img, …)"
  aws s3 sync "${STATIC_DIR}/" "s3://${STATIC_BUCKET_NAME}/" \
    --region "${AWS_REGION}" \
    --exclude "src/*" \
    --exclude "*.map" \
    --cache-control "public,max-age=86400" \
    --only-show-errors
else
  echo "WARN: no ${STATIC_DIR}" >&2
fi

echo "restore-s3-assets complete."
