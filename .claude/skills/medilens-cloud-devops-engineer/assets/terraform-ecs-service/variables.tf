variable "env" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env must be dev, staging or prod."
  }
}
variable "service" { type = string }
variable "region" {
  type    = string
  default = "ap-southeast-1"
}
variable "image" { type = string }
variable "cluster_arn" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "target_group_arn" {
  type    = string
  default = null
}
variable "container_port" {
  type    = number
  default = null
}
variable "cpu" {
  type    = number
  default = 512
}
variable "memory" {
  type    = number
  default = 1024
}
variable "desired_count" {
  type    = number
  default = 1
}
variable "min_count" {
  type    = number
  default = 1
}
variable "max_count" {
  type    = number
  default = 4
}
variable "use_spot" {
  type    = bool
  default = false
}
variable "environment" {
  type    = map(string)
  default = {}
}
variable "secrets" {
  description = "Map of env var name to Secrets Manager ARN"
  type        = map(string)
  default     = {}
}
variable "task_policy_json" { type = string }
variable "logs_kms_key_arn" { type = string }
variable "log_retention_days" {
  type    = number
  default = 30
}
