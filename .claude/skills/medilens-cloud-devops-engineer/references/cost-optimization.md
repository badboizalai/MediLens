# Cost Optimisation

## Usual top drivers
NAT Gateway (hourly + per-GB processing), RDS Multi-AZ instance hours, Fargate tasks running 24/7, ALB hours + LCUs, CloudWatch Logs ingestion, data transfer, LLM tokens, Athena bytes scanned.

## Levers
| Lever | Saving idea | Risk |
| --- | --- | --- |
| Graviton (arm64) for Fargate/RDS | lower price-performance cost | build arm64 images |
| Fargate Spot for worker | large discount on interruptible jobs | jobs must be idempotent/retryable (they are) |
| Scale worker to zero when queue empty | pay only when processing | cold start latency |
| Schedule nonprod off (EventBridge Scheduler) | ~65% off nonprod hours | none |
| VPC endpoints for S3/SQS/ECR/Bedrock | reduce NAT processing | endpoint hourly cost (compare) |
| Log retention 30 d + filter debug logs | lower ingestion/storage | less history (archive to S3) |
| S3 Intelligent-Tiering + lifecycle | cheaper cold data | minimal |
| Savings Plans (Compute) after 3 stable months | commit discount | commitment |
| LLM: cache, smaller model for classification, page selection, quotas | lower tokens | quality check via eval |
| Athena: Parquet + partitions + workgroup limits | lower bytes scanned | — |

## Budgets & alerts
AWS Budgets per account: monthly cost with alerts at 50/80/100% (forecasted and actual); Cost Anomaly Detection daily digest; weekly `cost.report` job posts unit economics (USD/document, USD/MAU).

All cost figures should be checked with the AWS Pricing Calculator for the current region and date before committing a budget.
