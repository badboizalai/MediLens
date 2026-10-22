module "network" {
  source = "../../modules/network"

  name     = "medilens-staging"
  region   = "ap-southeast-1"
  vpc_cidr = "10.20.0.0/16"
  az_count = 2
  nat_mode = "single"

  # VERIFY bedrock-runtime endpoint availability in ap-southeast-1 (ADR-012).
  enable_bedrock_endpoint = true

  tags = local.tags
}
