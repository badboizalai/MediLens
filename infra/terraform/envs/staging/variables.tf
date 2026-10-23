variable "api_image" {
  type        = string
  description = "Full ECR image URI (with tag or digest) for the api service."
}
variable "worker_image" {
  type        = string
  description = "Full ECR image URI (with tag or digest) for the worker service."
}
variable "certificate_arn" {
  type        = string
  description = "ACM certificate ARN for the ALB HTTPS listener."
}
variable "waf_web_acl_arn" {
  type        = string
  default     = null
  description = "WAFv2 web ACL ARN to associate with the ALB."
}
variable "rds_multi_az" {
  type    = bool
  default = false
}
variable "phi_bucket_arn" {
  type        = string
  default     = null
  description = "PHI bucket ARN (modules/storage output bucket_arns[\"phi\"]). When set, grants extractions/* access (ADR-0005)."
}
variable "phi_kms_key_arn" {
  type        = string
  default     = null
  description = "CMK ARN of the PHI bucket (modules/storage output kms_key_arns[\"phi\"]). Set together with phi_bucket_arn."
}
