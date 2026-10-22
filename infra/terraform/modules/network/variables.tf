variable "name" {
  description = "Name prefix, e.g. medilens-dev."
  type        = string
}

variable "region" {
  description = "AWS region (ap-southeast-1 per ADR-004)."
  type        = string
  default     = "ap-southeast-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR."
  type        = string
  default     = "10.10.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid CIDR."
  }
}

variable "az_count" {
  description = "Number of AZs (2 or 3)."
  type        = number
  default     = 2
  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "az_count must be 2 or 3."
  }
}

variable "nat_mode" {
  description = "NAT for private-app subnets: none, single (one NAT, nonprod), per_az (prod). Worker subnets never get NAT."
  type        = string
  default     = "single"
  validation {
    condition     = contains(["none", "single", "per_az"], var.nat_mode)
    error_message = "nat_mode must be none, single or per_az."
  }
}

variable "enable_bedrock_endpoint" {
  description = "Create the bedrock-runtime interface endpoint. VERIFY availability in ap-southeast-1 per ADR-012 before apply."
  type        = bool
  default     = true
}

variable "flow_log_retention_days" {
  description = "CloudWatch retention for VPC flow logs (ship to log-archive in prod)."
  type        = number
  default     = 30
}

variable "flow_log_kms_key_arn" {
  description = "Optional CMK ARN for the flow log group."
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags merged onto all resources (project, env, owner, cost-center, managed_by)."
  type        = map(string)
  default     = {}
}
