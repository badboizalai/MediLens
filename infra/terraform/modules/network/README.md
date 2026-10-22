# network module

VPC per environment (see `accounts-and-network.md`).

| Tier | CIDR | Route to internet |
| --- | --- | --- |
| public (ALB, NAT) | /24 per AZ | IGW |
| private-app (ECS api/web) | /20 per AZ | NAT per `nat_mode` (`none`, `single`, `per_az`) |
| private-worker (OCR/AI workers) | /20 per AZ | **None.** Only the S3 gateway endpoint and interface endpoints |

Endpoints: S3 (gateway); SQS, KMS, ECR api+dkr, CloudWatch Logs, Bedrock runtime (interface, ENIs in worker subnets).
VERIFY: `bedrock-runtime` endpoint availability in ap-southeast-1 (ADR-012); disable with `enable_bedrock_endpoint = false`.
Endpoint SG allows only TCP 443 from the `app` and `worker` client SGs (outputs; attach to tasks).
Endpoint policies (restrict to MediLens resources) are a follow-up; endpoints use the default policy for now.
Flow logs (ALL) go to CloudWatch; ship to log-archive for prod.

```hcl
module "network" {
  source   = "../../modules/network"
  name     = "medilens-dev"
  nat_mode = "single"
  tags     = { project = "medilens", env = "dev" }
}
```
