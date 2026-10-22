# AWS Service Catalog for MediLens

Region: ap-southeast-1 (Singapore) unless an ADR says otherwise. Verify current service/model availability per region before adopting.

| Need | Choose | Why | Alternatives (when) | Phase | PHI notes |
| --- | --- | --- | --- | --- | --- |
| DNS | Route 53 | Native, health checks | Cloudflare DNS | Foundation | — |
| CDN + TLS | CloudFront + ACM | Edge cache for GLB/SVG, free certs | Cloudflare | MVP | Never cache API responses with PHI (`Cache-Control: no-store`) |
| WAF | AWS WAF (managed rule groups + rate-based) | L7 protection | Cloudflare WAF | MVP | Log to S3 log-archive |
| Web (Next.js) | ECS Fargate behind ALB; static via S3/CloudFront | One deploy model | Amplify Hosting (fast), Vercel (outside AWS) | MVP | — |
| API | ECS Fargate + ALB | Serverless containers, autoscaling | App Runner (simpler), Lambda + API GW (spiky low traffic), EKS (learn K8s) | MVP | Private subnets; task role least privilege |
| AI worker | ECS Fargate (+ Spot) scaled on SQS depth | Long-running OCR, RAM-heavy | AWS Batch, ECS on EC2 GPU, SageMaker endpoints (self-hosted models) | MVP | Reads S3 PHI via VPC endpoint |
| Identity | Amazon Cognito user pool (OIDC, MFA, advanced security) | Managed, MAU pricing | Keycloak on ECS (learning), Auth0 | MVP | Store minimal attributes |
| Database | RDS PostgreSQL 16 (Multi-AZ prod) + RDS Proxy | pgvector, RLS, familiar | Aurora PostgreSQL (scale/serverless v2) | MVP | CMK, `rds.force_ssl`, PITR 35 d, no public access |
| Cache | ElastiCache (Valkey/Redis) | Rate limits, config cache | Skip in MVP | v1 | No PHI in cache |
| Object storage | S3 (Intelligent-Tiering), Object Lock for audit bucket | Durable, cheap | — | MVP | Separate `phi-*` buckets, CMK, Block Public Access, TLS-only policy, versioning |
| Queues | SQS Standard + DLQ (FIFO where order per document matters) | Managed, cheap | Amazon MQ | MVP | Payload IDs only; SSE-KMS |
| Events / scheduling | EventBridge bus + Scheduler | Domain events, cron replacement | Step Functions (multi-step stateful: DSR deletion) | MVP | — |
| LLM | Amazon Bedrock (Converse API, Guardrails) via interface VPC endpoint | Data stays in AWS, IAM, multiple models | Direct provider APIs, self-hosted | MVP | Redact PII; check model availability in region |
| OCR | PaddleOCR/VietOCR in worker; Bedrock vision; Textract (English only) | Vietnamese support | Google/Azure (outside AWS) | MVP | Textract does not support Vietnamese |
| PII detection | Comprehend (English) + custom rules/NER for Vietnamese | Layered | — | v1 | — |
| Email | Amazon SES | Cheap, DKIM | Resend | MVP | No PHI in email bodies (links only) |
| Secrets / keys | Secrets Manager (rotation), KMS CMKs per purpose | Rotation, audit | SSM Parameter Store (non-secret config) | MVP | Separate keys: `phi`, `app`, `logs`, `backup` |
| Feature flags | AWS AppConfig | Safe rollout, validators | Unleash | v1 | — |
| Registry | ECR (enhanced scanning via Inspector) | ECS integration | GHCR | Foundation | — |
| CI/CD | GitHub Actions + OIDC; ECS deploy, CodeDeploy blue/green | No stored keys | CodePipeline | Foundation | — |
| IaC | Terraform | Industry standard | CDK, Pulumi | Foundation | — |
| Observability | CloudWatch Logs/Metrics/Alarms, X-Ray via ADOT, CloudWatch RUM, Synthetics | Native | Managed Grafana/Prometheus, Datadog | MVP | Redact logs; restrict log groups with PHI risk |
| Security | GuardDuty (+ Malware Protection for S3), Security Hub, Config, Inspector, IAM Access Analyzer, CloudTrail org trail, Macie | Detection + compliance | — | Hardening | Macie scans for PII in unexpected buckets |
| Backup | AWS Backup (RDS, S3) + cross-account vault | Central, locked | Manual snapshots | Hardening | Vault lock |
| Analytics | S3 + Glue Catalog + Athena + Lake Formation; QuickSight | Serverless | Redshift Serverless | v1.5 | Pseudonymised only |
| Cost | Budgets, Cost Explorer, Cost Anomaly Detection | FinOps | — | Foundation | — |
