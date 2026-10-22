variable "home_region" {
  description = "Primary region. VERIFY per ADR-012 (Bedrock model availability) before first apply."
  type        = string
  default     = "ap-southeast-1"
}

variable "allowed_regions" {
  description = "Region allowlist for the SCP. us-east-1 is for global services (CloudFront/ACM/IAM). VERIFY per ADR-012."
  type        = list(string)
  default     = ["ap-southeast-1", "us-east-1"]
}

variable "account_emails" {
  description = "Unique root email per member account, keyed by account name. Placeholders only; supply real values via an untracked tfvars file."
  type        = map(string)
  default = {
    security    = "aws-security@example.com"
    log-archive = "aws-log-archive@example.com"
    nonprod     = "aws-nonprod@example.com"
    prod        = "aws-prod@example.com"
  }

  validation {
    condition     = toset(keys(var.account_emails)) == toset(["security", "log-archive", "nonprod", "prod"])
    error_message = "account_emails must have exactly the keys security, log-archive, nonprod, prod."
  }
}

variable "management_account_id" {
  description = "12-digit management account id (placeholder example)."
  type        = string
  default     = "111111111111"

  validation {
    condition     = can(regex("^[0-9]{12}$", var.management_account_id))
    error_message = "Must be a 12-digit account id."
  }
}

variable "org_trail_name" {
  type    = string
  default = "medilens-org-trail"
}

variable "trail_bucket_name" {
  description = "Globally unique S3 bucket name for organization CloudTrail logs (placeholder example)."
  type        = string
  default     = "medilens-example-org-cloudtrail"
}

variable "trail_retention_days" {
  description = "Days before CloudTrail log objects expire. Confirm against retention policy."
  type        = number
  default     = 2555
}

variable "sso_session_duration" {
  description = "ISO-8601 session duration for permission sets."
  type        = string
  default     = "PT4H"
}

variable "tags" {
  type = map(string)
  default = {
    project       = "medilens"
    env           = "org"
    owner         = "cloud-devops"
    "cost-center" = "platform"
    managed-by    = "terraform"
  }
}
