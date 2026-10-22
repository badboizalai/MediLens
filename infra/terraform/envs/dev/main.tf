terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.80" }
  }
  # backend "s3" {}  # configure remote state per account
}

provider "aws" {
  region = "ap-southeast-1"
  default_tags {
    tags = { project = "medilens", env = "dev", managed_by = "terraform" }
  }
}
