# storage module

S3 buckets `quarantine`, `phi`, `assets` plus an access-log bucket (S4-T36).

- Per bucket: Block Public Access, BucketOwnerEnforced, versioning, SSE-KMS with a dedicated CMK per data class (rotation on, bucket key), TLS-only policy, deny PutObject with another KMS key, access logging.
- Key policies have no account-root statement: admin roles (`kms_admin_role_arns`, required) administer; the role lists per class may use. Roles are variables.
- Lifecycle: quarantine objects expire after `quarantine_expiration_days`; phi/assets keep current objects and expire noncurrent versions after 90 days.
- The log bucket uses SSE-S3 (S3 server access logging cannot write to KMS buckets).
- GuardDuty Malware Protection for S3 on quarantine (`enable_malware_protection`). VERIFY `aws_guardduty_malware_protection_plan` exists in the provider version in the lock file and the feature is available in ap-southeast-1.
- EventBridge rule sends scan results to `scan_result_queue_arn` (PLACEHOLDER). The queue owner must add a queue policy allowing `events.amazonaws.com` from `scan_result_rule_arn`.
- Never plan/apply from a workstation against AWS; CI only.
