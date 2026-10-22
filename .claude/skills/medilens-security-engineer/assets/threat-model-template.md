# Threat Model — <feature / system> (v<n>, <date>)

## Scope
## Data flow (actors, processes, stores, boundaries)
```mermaid
flowchart LR
  U[Patient browser] -->|TLS| E[CloudFront/WAF]
  E --> A[API]
  A --> D[(RDS)]
  A --> Q[[SQS]]
  W[Worker] --> S[(S3 PHI)]
  W --> B[Bedrock]
```
## Assets and data classes
## Threats
| ID | Element | STRIDE/LLM | Description | L | I | Score | Controls (SEC) | Residual | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
## New requirements
## Decision
Proceed / proceed with conditions / blocked — rationale
