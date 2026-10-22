terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.80" }
  }
  # Remote state template (placeholders; see README.md). Uncomment once the bucket/table exist.
  # backend "s3" {
  #   bucket         = "REPLACE-medilens-staging-tfstate"
  #   key            = "envs/staging/terraform.tfstate"
  #   region         = "ap-southeast-1"
  #   dynamodb_table = "REPLACE-medilens-staging-tflock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = "ap-southeast-1"
  default_tags {
    tags = { project = "medilens", env = "staging", managed_by = "terraform" }
  }
}
