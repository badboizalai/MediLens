# Serving options

| Option | Use in MediLens | Pros | Cons |
| --- | --- | --- | --- |
| Bedrock on-demand (VPC endpoint) | Default for Tier S/M/L | No ops, data stays in AWS, per-token | Model list varies by region; check ap-southeast-1 |
| Bedrock batch inference | Evals, reprocessing, synthetic data | ~50% cheaper for supported models | Hours of latency |
| Bedrock Custom Model Import | Distilled model (v2) | Managed serving of your weights | Supported architectures only; check region |
| vLLM on GPU (ECS/EC2) | Learning, distilled model if cheaper | Full control | GPU cost, ops, patching |
| CPU containers (Fargate) | PaddleOCR/VietOCR, embeddings (bge-m3) | Cheap, simple | Slower under load |
| GPU queue workers scaled to zero (ECS on EC2 GPU / AWS Batch / SageMaker async) | TotalSegmentator (v2) | Pay only when CT jobs run | Cold start minutes; capacity limits |

Selection: start managed; move a workload in-house only with a break-even analysis and an SRE runbook.
