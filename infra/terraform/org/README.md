# AWS landing zone (organization)

Terraform for the AWS Organization: OUs (`security`, `nonprod`, `prod`), member accounts
(security, log-archive, nonprod, prod; management is the account you run this from),
baseline SCPs, IAM Identity Center permission sets and an organization CloudTrail that
writes to a KMS-encrypted, Object-Locked bucket in the log-archive account.

All emails, account ids and bucket names in `variables.tf` are placeholders
(`example.com`, `111111111111`). Supply real values in an untracked `*.tfvars`; never commit them.

## SCPs (`scp/`)
| File | Effect |
| --- | --- |
| `deny-leave-org.json` | Deny `organizations:LeaveOrganization` |
| `deny-disable-security-services.json` | Deny stopping/deleting CloudTrail, GuardDuty, Config, Security Hub |
| `deny-root.json` | Deny all actions by member-account root users |
| `region-allowlist.json.tftpl` | Deny outside `allowed_regions` (global services exempted) |

Region allowlist (`ap-southeast-1` + `us-east-1`) is **VERIFY per ADR-012** (Bedrock model
availability); confirm before the first apply. SCPs do not affect the management account.

## Apply order (manual, by the owner, from the management account)
CI never applies this stack and has no credentials for it.

1. Sign in to the management account with MFA, enable IAM Identity Center (region per ADR-012) and create the state bucket (versioned, CMK, Block Public Access).
2. `terraform init -backend-config="bucket=<state-bucket>" -backend-config="key=org/terraform.tfstate" -backend-config="region=<region>"`.
3. Stage 1, accounts first (the `log_archive` provider needs its account to exist):
   `terraform apply -target=aws_organizations_organization.this -target=aws_organizations_account.this -var-file=real.tfvars`
   (import the organization first if it already exists).
4. Stage 2, everything else: `terraform plan -var-file=real.tfvars`, review (security-engineer), then `terraform apply`.
5. In Identity Center create groups and assign `MediLensAdmin` to nonprod and `MediLensDeveloperReadOnly` to prod.
6. Verify the trail delivers a log file to the bucket, and that `LeaveOrganization` is denied from a member account.

## Local checks (no AWS access needed)
```
terraform fmt -check -recursive infra/terraform/org
terraform -chdir=infra/terraform/org init -backend=false
terraform -chdir=infra/terraform/org validate
```
