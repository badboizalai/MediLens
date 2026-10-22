# ADR-012: AWS region and Bedrock model availability

- **Status:** Proposed
- **Date:** 2026-10-23
- **Deciders:** Solution Architect (reviewers: security-engineer, mlops-engineer)
- **Related:** NFR-01, NFR-07, NFR-09, NFR-14, NFR-15; ADR-006, ADR-007, ADR-020 (plan §16.3, §19)

## Context
Health data is sensitive and falls under Law 91/2025/QH15 and Decree 356/2025/ND-CP, including consent, DPIA and an overseas-transfer impact assessment. Hosting outside Vietnam is an overseas transfer; that obligation applies in any AWS region we pick. The region must offer our service set (ECS Fargate, RDS, S3, SQS, KMS, Cognito, WAF, VPC endpoint for Bedrock Runtime) and the Bedrock models the cascade needs (ADR-021), with low latency to Vietnamese users. The plan recommends Singapore; Thailand also has Bedrock, but model lists differ per region.

## Options considered
1. ap-southeast-1 (Singapore): mature, full service set, close to VN; model list and cross-region inference behaviour to be confirmed. HealthImaging is not available there (ADR-020).
2. ap-southeast-7 (Thailand): also close; newer region with possibly fewer services and models. VERIFY service parity.
3. Other region (e.g. us-east-1, ap-southeast-2): widest model catalogue; higher latency and a more distant transfer; inference-profile routing may move data across regions, complicating the transfer assessment.

## Decision
Provisionally Option 1 (ap-southeast-1) for all PHI storage and compute. Region is one Terraform variable so it can change before real data exists. Bedrock calls use in-region VPC endpoints through the AI Gateway only (ADR-017). If a required model is not in-region, prefer a different model over cross-region inference; use cross-region inference only after security-engineer and regulatory officer confirm the transfer assessment covers the destination regions.
- VERIFY: exact Bedrock models (text tiers S/M/L, vision, embeddings) available in ap-southeast-1 and ap-southeast-7 on the AWS regional availability page at decision time.
- VERIFY: whether available models are in-region or only via cross-region inference profiles, and which regions those route to.
- VERIFY: service parity (Fargate, RDS, Cognito, WAF, VPC endpoints) in ap-southeast-7.
- VERIFY: legal reading of Decree 356/2025 on overseas transfer for the chosen region (regulatory-privacy-officer).

## Consequences
- Positive: single region simplifies network, KMS and IAM; low latency; aligned with the plan.
- Negative / trade-offs: no data localisation in Vietnam; dependence on one region's Bedrock catalogue; a DR region needs its own transfer analysis.
- Follow-up tasks: complete the VERIFY items; record the overseas-transfer impact assessment; add an SCP restricting regions; decide DR region.

## Exit strategy
Infra is Terraform with region as a variable and restore from backups; migration costs re-provisioning plus data copy and a refreshed transfer assessment. Adapters isolate model IDs (NFR-14).

## Revisit when
A needed model is unavailable in-region, regulation requires localisation, or cost/latency changes materially.
