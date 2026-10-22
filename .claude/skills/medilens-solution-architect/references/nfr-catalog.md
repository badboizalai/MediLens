# NFR Catalog

| Code | Attribute | Target | Mechanism | Verification | Owner |
| --- | --- | --- | --- | --- | --- |
| NFR-01 | Availability | API 99.5%/month | Multi-AZ ALB/ECS, RDS Multi-AZ prod, health checks | CloudWatch SLO, synthetic canary | sre |
| NFR-02 | Latency | Read API p95 ≤ 300 ms, p99 ≤ 1 s | Indexes, Redis cache for configs, pagination, RDS Proxy | k6 on staging, X-Ray | backend |
| NFR-03 | Throughput | 50 req/s sustained, 200 req/s 5-min peak | ECS autoscaling on CPU + ALB request count | k6 load test | devops |
| NFR-04 | Processing time | 95% documents < 2 min; 100 docs/hour | SQS + worker scaling on queue depth; separate OCR/LLM queues | pipeline load test | ai-ml |
| NFR-05 | Scalability | 10× users without re-architecture | Stateless API, S3, managed DB | design review | architect |
| NFR-06 | Durability | 0 loss of acknowledged uploads | S3, ack after DB write, outbox | chaos test (kill worker mid-job) | backend |
| NFR-07 | Recoverability | RPO ≤ 24 h (target 5 min PITR), RTO ≤ 4 h | AWS Backup, PITR, IaC rebuild | quarterly DR drill | sre |
| NFR-08 | Security | ASVS L2; 0 High past SLA | SEC catalog | security sign-off | security |
| NFR-09 | Privacy | PDPL 91/2025/QH15 + Decree 356/2025/ND-CP compliant | Consent, DPIA, DSR flows, redaction | compliance checklist | security |
| NFR-10 | Accessibility | WCAG 2.2 AA | Design system, axe in CI | audit | frontend |
| NFR-11 | Usability | SUS ≥ 70; main flow ≤ 5 min for first-timers | Design, usability tests | test report | ux |
| NFR-12 | Extensibility | New Unit ≤ 3 person-days, no core diff | Unit config + viewer plugin registry | PB-02 execution | architect |
| NFR-13 | Observability | 100% requests traced; every alarm has runbook | OpenTelemetry/ADOT, structured logs | review | sre |
| NFR-14 | Portability | Switch LLM/OCR provider ≤ 2 days | Provider adapters + eval harness | provider swap drill | ai-ml |
| NFR-15 | Cost | ≤ 100 USD/month at 100 MAU; AI ≤ 0.10 USD/doc | Fargate Spot, caching, quotas, Graviton | cost report | devops |
| NFR-16 | i18n | VI + EN complete; new locale without code change | next-intl, bilingual content model | review | frontend |
| NFR-17 | Compatibility | Last 2 Chrome/Safari/Firefox/Edge; iOS 16+, Android 10+ | Feature detection, 2D fallback | Playwright matrix | qa |

## Quality-attribute scenario template
Source · Stimulus · Environment · Artefact · Response · Response measure.
Example (NFR-06): Worker process (source) crashes (stimulus) during OCR at normal load (environment) on the AI worker (artefact); message becomes visible again after visibility timeout and is reprocessed idempotently (response); 0 documents lost, duplicate side-effects 0 (measure).
