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
