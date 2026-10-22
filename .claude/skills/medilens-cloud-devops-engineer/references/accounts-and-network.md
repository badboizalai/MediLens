# Accounts and Network

## Accounts (AWS Organizations)
| Account | Purpose | Notes |
| --- | --- | --- |
| management | Organizations, billing, IAM Identity Center | No workloads |
| security | GuardDuty/Security Hub/Inspector delegated admin, Access Analyzer | Read-mostly |
| log-archive | CloudTrail org trail, Config, VPC Flow Logs, ALB/WAF logs, app audit export | S3 Object Lock |
| shared-services | ECR, Route 53 zones | Optional early |
| dev, staging | Non-prod, synthetic data only | Scheduled shutdown |
| prod | Real users | Multi-AZ, strict SCPs |
| backup-vault | Cross-account AWS Backup vault | Vault lock |

Start lean (management, nonprod, prod) and split as you harden. Control Tower can bootstrap this.

## Service Control Policies (minimum)
- Deny regions other than ap-southeast-1 (+ us-east-1 for global services like CloudFront/ACM/IAM).
- Deny disabling CloudTrail, GuardDuty, Config, Security Hub.
- Deny `iam:CreateAccessKey` for IAM users; deny creating IAM users except break-glass.
- Deny `rds:ModifyDBSnapshotAttribute` / `ec2:ModifySnapshotAttribute` sharing outside the org.
- Deny S3 `PutBucketPublicAccessBlock` changes that disable blocking; require encryption on `PutObject` for `phi-*`.

## VPC per environment
| Env | CIDR | AZs | NAT |
| --- | --- | --- | --- |
| dev | 10.10.0.0/16 | 2–3 | 1 (or none + endpoints) |
| staging | 10.20.0.0/16 | 3 | 1 |
| prod | 10.30.0.0/16 | 3 | 1 per AZ |

Subnets per AZ: public /24 (ALB, NAT), private-app /20 (ECS), private-data /24 (RDS, ElastiCache; no internet route).

## Security groups
| SG | Inbound | From |
| --- | --- | --- |
| alb | 443 | 0.0.0.0/0 (or CloudFront prefix list) |
| api | 8000 | alb |
| web | 3000 | alb |
| worker | none | — |
| rds | 5432 | api, worker, de-extract |
| cache | 6379 | api |
| vpce | 443 | api, worker |

## VPC endpoints
Gateway: S3 (and DynamoDB if used). Interface: SQS, Bedrock Runtime, Secrets Manager, KMS, ECR (api + dkr), CloudWatch Logs, STS, EventBridge, SSM (if used). Endpoint policies restrict to MediLens resources.

## Logging
VPC Flow Logs (reject + accept for prod) → log-archive; ALB access logs; WAF logs; Route 53 Resolver query logs (optional).
