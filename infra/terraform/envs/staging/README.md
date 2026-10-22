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
