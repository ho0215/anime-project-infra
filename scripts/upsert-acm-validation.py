#!/usr/bin/env python3
"""Upsert ACM DNS validation CNAMEs into the Route53 zone for the cert ARN.

Env:
  ACM_CERT_ARN, ZONE_ID (Route53 hosted zone id, without /hostedzone/), AWS_REGION
"""
from __future__ import annotations

import json
import os
import subprocess
import sys


def main() -> int:
    arn = os.environ["ACM_CERT_ARN"]
    zone = os.environ["ZONE_ID"]
    region = os.environ.get("AWS_REGION", "ap-northeast-2")

    raw = subprocess.check_output(
        [
            "aws",
            "acm",
            "describe-certificate",
            "--region",
            region,
            "--certificate-arn",
            arn,
            "--query",
            "Certificate.DomainValidationOptions",
            "--output",
            "json",
        ],
        text=True,
    )
    opts = json.loads(raw)
    changes = []
    for o in opts:
        rr = o.get("ResourceRecord") or {}
        if not rr.get("Name"):
            print(
                f"  skip {o.get('DomainName')}: no ResourceRecord yet "
                f"(ValidationStatus={o.get('ValidationStatus')})"
            )
            continue
        name = rr["Name"].rstrip(".") + "."
        value = rr["Value"].rstrip(".") + "."
        changes.append(
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": name,
                    "Type": rr.get("Type", "CNAME"),
                    "TTL": 60,
                    "ResourceRecords": [{"Value": value}],
                },
            }
        )
        print(
            f"  UPSERT {name} → {value} "
            f"({o.get('DomainName')} status={o.get('ValidationStatus')})"
        )

    if not changes:
        print("no validation CNAMEs to upsert yet", file=sys.stderr)
        return 0

    batch = json.dumps({"Comment": "ACM DNS validation", "Changes": changes})
    subprocess.check_call(
        [
            "aws",
            "route53",
            "change-resource-record-sets",
            "--hosted-zone-id",
            zone,
            "--change-batch",
            batch,
        ],
        stdout=subprocess.DEVNULL,
    )
    print(f"upserted {len(changes)} validation record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
