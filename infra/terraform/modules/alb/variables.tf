variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" {
  type        = list(string)
  description = "Public subnets."
}
variable "security_group_ids" { type = list(string) }
variable "certificate_arn" {
  type        = string
  description = "ACM certificate ARN for the HTTPS listener."
}
variable "waf_web_acl_arn" {
  type        = string
  default     = null
  description = "WAFv2 web ACL ARN to associate; null skips association."
}
variable "target_port" {
  type    = number
  default = 8000
}
variable "health_check_path" {
  type    = string
  default = "/healthz"
}
variable "tags" {
  type    = map(string)
  default = {}
}
