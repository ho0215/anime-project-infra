#!/usr/bin/env bash
# Connect to an Aniverse ASG EC2 instance via AWS SSM Session Manager.
# Usage:
#   ./scripts/ssm-connect.sh              # pick first Online instance in ASG
#   ./scripts/ssm-connect.sh i-0abc123    # specific instance
#   ASG_NAME=aniverse-asg ./scripts/ssm-connect.sh
set -euo pipefail

AWS_REGION="${AWS_REGION:-ap-northeast-2}"
ASG_NAME="${ASG_NAME:-aniverse-asg}"
INSTANCE_ID="${1:-}"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing dependency: $1" >&2
    echo "Install AWS CLI v2 and Session Manager plugin:" >&2
    echo "  https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html" >&2
    exit 1
  }
}

need aws

if ! command -v session-manager-plugin >/dev/null 2>&1; then
  echo "session-manager-plugin not found on PATH." >&2
  echo "Install it, then re-run this script." >&2
  exit 1
fi

if [ -z "$INSTANCE_ID" ]; then
  echo "Looking up Online SSM instances in ASG: $ASG_NAME ($AWS_REGION)"
  mapfile -t ASG_IDS < <(aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names "$ASG_NAME" \
    --region "$AWS_REGION" \
    --query 'AutoScalingGroups[0].Instances[].InstanceId' \
    --output text 2>/dev/null | tr '\t' '\n' | grep -E '^i-' || true)

  if [ "${#ASG_IDS[@]}" -eq 0 ]; then
    echo "No instances found in ASG $ASG_NAME" >&2
    exit 1
  fi

  for id in "${ASG_IDS[@]}"; do
    ping=$(aws ssm describe-instance-information \
      --region "$AWS_REGION" \
      --filters "Key=InstanceIds,Values=$id" \
      --query 'InstanceInformationList[0].PingStatus' \
      --output text 2>/dev/null || echo "None")
    echo "  $id -> $ping"
    if [ "$ping" = "Online" ] && [ -z "$INSTANCE_ID" ]; then
      INSTANCE_ID="$id"
    fi
  done

  if [ -z "$INSTANCE_ID" ]; then
    echo "No Online SSM-managed instance in ASG. Check:" >&2
    echo "  1) amazon-ssm-agent running on EC2" >&2
    echo "  2) IAM AmazonSSMManagedInstanceCore attached" >&2
    echo "  3) VPC endpoints (ssm/ssmmessages/ec2messages) or NAT egress" >&2
    exit 1
  fi
fi

echo "Starting SSM session to $INSTANCE_ID ..."
exec aws ssm start-session --target "$INSTANCE_ID" --region "$AWS_REGION"
