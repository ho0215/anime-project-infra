#!/usr/bin/env bash
# Wait until at least one ASG instance is SSM Online (used by CI / local ops).
set -euo pipefail

AWS_REGION="${AWS_REGION:-ap-northeast-2}"
ASG_NAME="${ASG_NAME:-aniverse-asg}"
TIMEOUT_SEC="${TIMEOUT_SEC:-600}"
SLEEP_SEC=15
START=$(date +%s)

echo "Waiting for SSM Online instance in ASG=$ASG_NAME (timeout ${TIMEOUT_SEC}s)"

while true; do
  mapfile -t ASG_IDS < <(aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names "$ASG_NAME" \
    --region "$AWS_REGION" \
    --query 'AutoScalingGroups[0].Instances[].InstanceId' \
    --output text 2>/dev/null | tr '\t' '\n' | grep -E '^i-' || true)

  for id in "${ASG_IDS[@]:-}"; do
    [ -z "$id" ] && continue
    ping=$(aws ssm describe-instance-information \
      --region "$AWS_REGION" \
      --filters "Key=InstanceIds,Values=$id" \
      --query 'InstanceInformationList[0].PingStatus' \
      --output text 2>/dev/null || echo "None")
    echo "$(date -u +%H:%M:%S) $id $ping"
    if [ "$ping" = "Online" ]; then
      echo "READY=$id"
      exit 0
    fi
  done

  NOW=$(date +%s)
  if [ $((NOW - START)) -ge "$TIMEOUT_SEC" ]; then
    echo "Timed out waiting for SSM Online instance" >&2
    exit 1
  fi
  sleep "$SLEEP_SEC"
done
