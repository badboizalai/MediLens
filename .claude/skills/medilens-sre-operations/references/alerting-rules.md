# Alerting Rules (CloudWatch)

| Alarm | Condition | Severity | Runbook |
| --- | --- | --- | --- |
| api-slo-fast-burn | burn rate ≥ 14.4 (1 h & 5 min) | SEV2 page | RB-01 API errors |
| api-5xx-spike | 5xx rate > 2% for 5 min | SEV2 | RB-01 |
| api-latency | p95 > 600 ms for 10 min | SEV3 | RB-02 latency |
| alb-unhealthy-targets | healthy hosts < 1 for 2 min | SEV1 | RB-03 service down |
| queue-age-ocr | ApproximateAgeOfOldestMessage > 300 s | SEV2 | RB-04 pipeline backlog |
| dlq-not-empty | DLQ messages > 0 | SEV3 | RB-05 DLQ |
| provider-errors | Bedrock/OCR error rate > 20% for 5 min | SEV2 | RB-06 provider outage |
| rds-cpu | CPU > 80% for 15 min | SEV3 | RB-07 DB load |
| rds-storage | free storage < 15% | SEV3 | RB-08 storage |
| rds-connections | connections > 80% max | SEV3 | RB-07 |
| backup-missing | daily backup verify failed | SEV2 | RB-09 backups |
| cron-dead-man | job heartbeat missing past SLA | SEV3 | RB-10 scheduled jobs |
| cost-anomaly | Cost Anomaly Detection alert | SEV3 | RB-11 cost |
| guardduty-high | finding severity ≥ 7 | SEV2 → security | IR plan |
| waf-block-spike | blocked requests 10× baseline | SEV3 | RB-12 attack |
| break-glass-used | any break-glass grant | SEV3 info → security | IR plan |
| ai-correction-drift | correction rate +20% WoW | SEV3 | RB-13 AI drift |
| cert-expiry | ACM cert < 30 days (if not auto-renewing) | SEV3 | RB-14 |

Notification: SNS → email + chat (Telegram/Slack) for SEV1–2; ticket for SEV3–4. Quiet hours: SEV3–4 wait until morning.
