# envs/staging

Composes network + RDS + SQS + ALB + api/worker ECS services.

## Remote state

State is local until a backend is configured. To enable:

1. Create (outside this stack) an S3 bucket (versioned, SSE-KMS, public access blocked) and a DynamoDB table with hash key `LockID` (string).
2. Uncomment the `backend "s3"` block in `main.tf` and replace the `REPLACE-...` placeholders.
3. Run `terraform init -migrate-state`.

## CD (`.github/workflows/deploy-staging.yml`)

Repo variables: `AWS_STAGING_ROLE_ARN`, `AWS_STAGING_ECR_REGISTRY`, `STAGING_CERTIFICATE_ARN`, `STAGING_WAF_WEB_ACL_ARN`.
If `AWS_STAGING_ROLE_ARN` is empty, the `plan` and `deploy` jobs are skipped (not green) and a
`not-configured` job writes "staging not configured" to the job summary.
`apply` only runs via manual `workflow_dispatch` under the `staging` environment.

## storage (S6-T58-F1/F2/F8)
`storage.tf` instantiates `modules/storage` (quarantine, phi, assets). Task roles get least-privilege access:
worker reads `quarantine/*` (GetObject, GetObjectTagging) and uses the phi bucket as its pages store (`raw/ pre/ ocr/`, put/get/list) plus `extractions/*` put;
API signs/gets/deletes `quarantine/*` and reads `extractions/*`. CMK use is limited to those two roles (key policy). Env: `MEDILENS_S3_BUCKET` (api), `WORKER_RAW_BUCKET`, `WORKER_PAGES_BUCKET`, `EXTRACTION_RESULTS_BUCKET`, `WORKER_REQUIRE_MALWARE_SCAN=true` (worker).
Quarantine expires after 1 day (U-08). Set `kms_admin_role_arns`.

Known limits: (F6) S3 policy cannot deny overwrite of an existing key; versioning is on, so an overwrite is recoverable, but SEC-AP-07a needs VersionId + sha256 pinning in app code. Object Lock is not enabled (needs a bucket-creation-time decision; it would block the 1-day expiry). The scan-results queue has no `events.amazonaws.com` policy yet (modules/sqs owns the policy); the worker reads scan verdicts from object tags, so this does not block uploads. The worker writes pages with SSE-S3 (`AES256`), which the phi bucket policy allows but is weaker than the CMK; fix in app code (S3PageStore._put).

## api-events (ADR-0005)
`module.api_events_queue` (+ DLQ and DLQ-not-empty alarm) carries worker status/result events (ids only). Tasks read `API_EVENTS_QUEUE_URL`; extraction results use `extractions/*` in the phi bucket. Not applied: no AWS credentials.
