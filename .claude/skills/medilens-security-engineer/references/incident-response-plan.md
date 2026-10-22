# Incident Response Plan

## Severity
| Level | Examples | Response |
| --- | --- | --- |
| SEC-1 | Confirmed PHI exposure, active intrusion, leaked production credentials | Immediate; notification clock starts at detection (72 h under Decree 356/2025, Form 08) |
| SEC-2 | Suspected exposure, exploitable vuln in prod, malware upload executed | ≤ 1 h |
| SEC-3 | Vulnerability without evidence of exploitation | Per vuln SLA |
| SEC-4 | Policy deviation | Next sprint |

## Steps
1. **Detect & declare** — source (GuardDuty, alert, report); open incident record with timestamp (UTC).
2. **Triage** — what data, how many users, still ongoing? Assign severity.
3. **Contain** — revoke/rotate keys and sessions, block IPs/accounts in WAF/Cognito, disable feature flag, isolate task/instance (snapshot first), restrict bucket.
4. **Preserve evidence** — CloudTrail, VPC Flow Logs, ALB/WAF logs, app audit, snapshots; hash and store in log-archive (chain of custody).
5. **Eradicate** — patch, remove malicious artefacts, fix misconfiguration via Terraform.
6. **Recover** — restore from clean backups if needed, monitor closely 7 days.
7. **Notify** — the data protection authority within 72 hours of detection (Decree 356/2025, Form 08) when required; affected users with plain-language explanation, what data, what we did, what they can do; record decisions.
8. **Review** — blameless post-incident report within 5 days; action items with owners/dates; update threat model and runbooks.

## Notification template (users, VI summary)
"Ngày <date>, chúng tôi phát hiện <mô tả ngắn>. Dữ liệu có thể bị ảnh hưởng: <loại dữ liệu>. Chúng tôi đã <hành động>. Bạn nên <khuyến nghị>. Liên hệ: <kênh>."

## Drills
Tabletop every 6 months: scenarios — public PHI bucket; IDOR reported by user; leaked CI token; prompt injection extracting data.
