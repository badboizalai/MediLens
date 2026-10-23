module "network" {
  source = "../../modules/network"

  name     = "medilens-dev"
  region   = "ap-southeast-1"
  vpc_cidr = "10.10.0.0/16"
  az_count = 2
  nat_mode = "single" # cost: one NAT in nonprod (cost-optimization.md)

  # VERIFY bedrock-runtime endpoint availability in ap-southeast-1 (ADR-012).
  enable_bedrock_endpoint = true

  tags = {
    project       = "medilens"
    env           = "dev"
    owner         = "platform"
    "cost-center" = "medilens-nonprod"
    managed_by    = "terraform"
  }
}
