variable "name" {
  description = "Name prefix, e.g. medilens-dev."
  type        = string
}

variable "tags" {
  description = "Tags applied to all resources."
  type        = map(string)
  default     = {}
}

variable "kms_admin_role_arns" {
  description = "Roles that may administer (not use) the CMKs. Required: keys have no account-root statement."
  type        = list(string)
  validation {
    condition     = length(var.kms_admin_role_arns) > 0
    error_message = "At least one KMS admin role is required."
  }
}

variable "quarantine_role_arns" {
  description = "Roles that may write/read the quarantine bucket and use its key (e.g. presign/upload role, scan worker)."
  type        = list(string)
  default     = []
}

variable "phi_role_arns" {
  description = "Roles that may use the PHI key (e.g. api task role, worker task role). Least privilege: do not add the web tier."
  type        = list(string)
  default     = []
}

variable "assets_role_arns" {
  description = "Roles that may use the assets key."
  type        = list(string)
  default     = []
}

variable "quarantine_expiration_days" {
  description = "Quarantine objects (and noncurrent versions) expire after N days."
  type        = number
  default     = 7
}

variable "log_retention_days" {
  description = "Access-log retention in days."
  type        = number
  default     = 365
}

variable "enable_malware_protection" {
  description = "GuardDuty Malware Protection for S3 on quarantine. VERIFY aws_guardduty_malware_protection_plan exists in the pinned provider (added in 5.7x) and the service in ap-southeast-1."
  type        = bool
  default     = true
}

variable "scan_result_queue_arn" {
  description = "PLACEHOLDER: SQS queue ARN receiving scan results. The queue policy must allow events.amazonaws.com SendMessage from the rule ARN (output scan_result_rule_arn)."
  type        = string
}
