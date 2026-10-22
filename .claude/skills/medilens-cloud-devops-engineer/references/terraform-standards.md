# Terraform Standards

## Layout
```
infra/terraform/
├── modules/  network, ecs-cluster, ecs-service, rds-postgres, s3-bucket, sqs-queue, kms, cognito, cloudfront-waf, observability, backup, security-baseline
└── envs/
    ├── dev/ {network,data,app,observability}/main.tf  (+ backend.tf, terraform.tfvars)
    ├── staging/ …
    └── prod/ …
```
One state per env per stack; data via `terraform_remote_state` or SSM parameters.

## State
S3 bucket per account with versioning, CMK encryption, Block Public Access; locking via S3 native lockfile (`use_lockfile = true`) or DynamoDB table; access only to CI role and admins.

## Conventions
- Names: `medilens-<env>-<component>` (e.g., `medilens-prod-api`).
- Required tags via provider `default_tags`: project, env, owner, cost-center, managed-by=terraform; plus `data-class` on storage.
- Pin provider and module versions; Renovate updates.
- Variables typed with validation; no secrets in tfvars (use Secrets Manager + random_password).
- Outputs minimal; sensitive outputs marked `sensitive = true`.

## Module rules
- Secure defaults: encryption on, logging on, public access off, deletion protection on for prod data stores.
- Expose only needed inputs; document in README with example.
- Include `checkov` skip comments only with justification and ticket.

## Review checklist
- [ ] `plan` attached; no unexpected destroys
- [ ] IAM policies least privilege (no `*` actions on PHI resources)
- [ ] Encryption + CMK correct for data class
- [ ] Network exposure intended
- [ ] Tags present
- [ ] Cost impact noted
